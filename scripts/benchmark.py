#!/usr/bin/env python3
"""
Benchmark of `aws-inventory collect` on a mocked account with simulated API latency.

The script starts the same moto mocks and fake credentials as ``scripts/demo.py``,
creates ``--resources`` resources spread over ``--regions`` regions (default: 1000
resources in 17 regions, the scale of Requirement 1.5), adds ``--latency-ms`` of delay
to every AWS API call the CLI makes (a botocore ``before-call`` hook on each client of
:class:`src.aws_session.InventorySession`; resource creation is not delayed), runs
``aws-inventory collect`` in-process and reads the phase timings from
``collection_report.json`` (Requirement 10.1, 10.2).

    python scripts/benchmark.py                               # 1000 resources, 17 regions, 100 ms
    python scripts/benchmark.py --latency-ms 0 --json result.json

Exit code: 0 when collect succeeded and the targets were met (discovery < 300 s,
collection >= 10 resources/s), 1 otherwise, 2 for invalid arguments.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import sys
import tempfile
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.aws_session import InventorySession  # noqa: E402
from src.sample_account import LAMBDA_ASSUME_POLICY, _lambda_zip  # noqa: E402

REGIONS = (
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "ca-central-1",
    "sa-east-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-central-1",
    "eu-north-1",
    "ap-south-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-southeast-1",
    "ap-southeast-2",
)
# moto creates a default VPC and its default security group in every region.
DEFAULTS_PER_REGION = 2
# Share of the created (non-default) resources per regional type; S3 buckets and IAM
# roles (global) take the remaining ~5 %.
REGIONAL_WEIGHTS = {
    "aws_instance": 10,
    "aws_security_group": 10,
    "aws_cloudwatch_log_group": 10,
    "aws_dynamodb_table": 10,
    "aws_lambda_function": 5,
    "aws_sfn_state_machine": 5,
    "aws_db_instance": 4,
}
GLOBAL_SHARE = 0.05
DISCOVERY_TARGET_SECONDS = 300.0  # Requirement 1.5
COLLECTION_TARGET_PER_SECOND = 10.0  # design.md "Performance"


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1].strip())
    parser.add_argument("--resources", type=int, default=1000, help="Total resources (1000).")
    parser.add_argument(
        "--regions", type=int, default=len(REGIONS), help=f"Regions (1-{len(REGIONS)}, 17)."
    )
    parser.add_argument("--latency-ms", type=float, default=100.0, help="Delay per API call (100).")
    parser.add_argument(
        "--output-dir", type=Path, help="Output_Dir for collect (default: a temporary dir)."
    )
    parser.add_argument("--json", type=Path, help="Also write the result as JSON here.")
    return parser.parse_args(argv)


def plan(resources: int, regions: int) -> tuple[dict[str, int], dict[str, int]]:
    """Per-region counts of created resources by type, and global bucket/role counts."""
    created = resources - DEFAULTS_PER_REGION * regions
    per_region = int(created * (1 - GLOBAL_SHARE)) // regions
    total_weight = sum(REGIONAL_WEIGHTS.values())
    shares = {t: per_region * w / total_weight for t, w in REGIONAL_WEIGHTS.items()}
    counts = {t: int(share) for t, share in shares.items()}
    by_remainder = sorted(shares, key=lambda t: shares[t] - counts[t], reverse=True)
    for resource_type in by_remainder[: per_region - sum(counts.values())]:
        counts[resource_type] += 1
    global_count = resources - regions * (DEFAULTS_PER_REGION + per_region)
    roles = max(1, global_count // 2)
    return counts, {"aws_iam_role": roles, "aws_s3_bucket": global_count - roles}


def build_account(
    session: Any, regions: list[str], regional: dict[str, int], glob: dict[str, int]
) -> None:
    """Create the planned resources in moto (no latency)."""
    iam = session.client("iam", region_name="us-east-1")
    role_arns = [
        iam.create_role(
            RoleName=f"bench-role-{i}", AssumeRolePolicyDocument=json.dumps(LAMBDA_ASSUME_POLICY)
        )["Role"]["Arn"]
        for i in range(glob["aws_iam_role"])
    ]
    s3 = session.client("s3", region_name="us-east-1")
    for i in range(glob["aws_s3_bucket"]):
        s3.create_bucket(Bucket=f"bench-bucket-{i}")

    code = _lambda_zip()
    for region in regions:
        ec2 = session.client("ec2", region_name=region)
        ec2.describe_vpcs()  # instantiates the region's default VPC and security group
        if regional["aws_instance"]:
            ec2.run_instances(
                ImageId="ami-12c6146b",
                InstanceType="t3.micro",
                MinCount=regional["aws_instance"],
                MaxCount=regional["aws_instance"],
            )
        for i in range(regional["aws_security_group"]):
            ec2.create_security_group(GroupName=f"bench-sg-{i}", Description="benchmark")
        logs = session.client("logs", region_name=region)
        for i in range(regional["aws_cloudwatch_log_group"]):
            logs.create_log_group(logGroupName=f"/bench/group-{i}")
        dynamodb = session.client("dynamodb", region_name=region)
        for i in range(regional["aws_dynamodb_table"]):
            dynamodb.create_table(
                TableName=f"bench-table-{i}",
                BillingMode="PAY_PER_REQUEST",
                KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            )
        lambda_client = session.client("lambda", region_name=region)
        for i in range(regional["aws_lambda_function"]):
            lambda_client.create_function(
                FunctionName=f"bench-fn-{i}",
                Runtime="python3.11",
                Role=role_arns[0],
                Handler="handler.handler",
                Code={"ZipFile": code},
            )
        sfn = session.client("stepfunctions", region_name=region)
        definition = json.dumps({"StartAt": "Done", "States": {"Done": {"Type": "Succeed"}}})
        for i in range(regional["aws_sfn_state_machine"]):
            sfn.create_state_machine(
                name=f"bench-flow-{i}", definition=definition, roleArn=role_arns[0]
            )
        rds = session.client("rds", region_name=region)
        for i in range(regional["aws_db_instance"]):
            rds.create_db_instance(
                DBInstanceIdentifier=f"bench-db-{i}",
                DBInstanceClass="db.t3.micro",
                Engine="postgres",
                AllocatedStorage=20,
                MasterUsername="bench",
                MasterUserPassword="bench-password-123",
            )


class LatencyInjector:
    """Delays every API call of clients created through InventorySession."""

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        self.calls = 0
        self._lock = threading.Lock()

    def _delay(self, **_: Any) -> None:
        with self._lock:
            self.calls += 1
        time.sleep(self.seconds)

    @contextlib.contextmanager
    def active(self) -> Iterator[None]:
        original = InventorySession.client

        def client(session: InventorySession, *args: Any, **kwargs: Any) -> Any:
            created = original(session, *args, **kwargs)
            created.meta.events.register("before-call", self._delay)
            return created

        with patch.object(InventorySession, "client", client):
            yield


def _load_demo() -> Any:
    spec = importlib.util.spec_from_file_location("demo", Path(__file__).with_name("demo.py"))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def mocked_aws() -> Iterator[None]:
    """demo.py's fake credentials and moto mocks, without the sample account."""
    import moto

    demo = _load_demo()
    with patch.dict("os.environ", demo.FAKE_CREDENTIALS):
        mocks = [getattr(moto, name)() for name in demo.MOCKED_SERVICES]
        for mock in mocks:
            mock.start()
        try:
            yield
        finally:
            for mock in reversed(mocks):
                mock.stop()


def run(args: argparse.Namespace, output_dir: Path) -> dict[str, Any]:
    import boto3

    regions = list(REGIONS[: args.regions])
    regional, glob = plan(args.resources, args.regions)
    injector = LatencyInjector(args.latency_ms / 1000)
    with mocked_aws():
        build_account(boto3.Session(region_name="us-east-1"), regions, regional, glob)
        # --include-defaults: the default VPCs/SGs count towards --resources.
        collect = ["--log-level", "ERROR", "--no-color", "collect", "--include-defaults"]
        collect += ["--output-dir", str(output_dir)]
        for region in regions:
            collect += ["--region", region]
        with injector.active():
            exit_code = _load_demo().run_cli(collect)

    report = json.loads((output_dir / "collection_report.json").read_text(encoding="utf-8"))
    phases = {p["name"]: p["duration_seconds"] for p in report["phases"]}
    metrics = report["metrics"]
    rate = metrics["specs_collected"] / phases["collection"] if phases["collection"] else 0.0
    return {
        "exit_code": exit_code,
        "regions": regions,
        "latency_ms": args.latency_ms,
        "planned_per_region": regional,
        "planned_global": glob,
        **metrics,
        "delayed_calls": injector.calls,
        "phases": phases,
        "collection_resources_per_second": round(rate, 2),
        "targets_met": exit_code == 0
        and phases["discovery"] < DISCOVERY_TARGET_SECONDS
        and rate >= COLLECTION_TARGET_PER_SECOND,
    }


def print_summary(result: dict[str, Any]) -> None:
    phases = result["phases"]
    print(
        f"{result['resources_discovered']} resources in {len(result['regions'])} regions, "
        f"{result['latency_ms']:g} ms per API call ({result['delayed_calls']} delayed calls)"
    )
    print("| Phase | Duration (s) | Target |")
    print("|---|---|---|")
    print(f"| discovery | {phases['discovery']:.2f} | < {DISCOVERY_TARGET_SECONDS:.0f} |")
    print(
        f"| collection | {phases['collection']:.2f} "
        f"({result['collection_resources_per_second']} resources/s) "
        f"| >= {COLLECTION_TARGET_PER_SECOND:.0f} resources/s |"
    )
    print(f"| output | {phases['output']:.2f} | - |")
    print(f"api_calls={result['api_calls']} specs_failed={result['specs_failed']}")
    print("targets met" if result["targets_met"] else "TARGETS NOT MET")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    minimum = (DEFAULTS_PER_REGION * args.regions) + 2
    if not 1 <= args.regions <= len(REGIONS) or args.resources < minimum:
        print(
            f"benchmark: need 1-{len(REGIONS)} regions and at least {minimum} resources "
            f"(default VPC + security group per region, one IAM role and one bucket)",
            file=sys.stderr,
        )
        return 2
    with contextlib.ExitStack() as stack:
        output_dir = args.output_dir or Path(stack.enter_context(tempfile.TemporaryDirectory()))
        result = run(args, output_dir)
    print_summary(result)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["targets_met"] else 1


if __name__ == "__main__":
    sys.exit(main())
