#!/usr/bin/env python3
"""
End-to-end demo of aws-inventory: collect -> analyze -> generate-iac -> generate-docs -> verify.

By default the demo starts moto mocks, creates the sample account of
``src/sample_account.py`` (one resource of each Supported_Resource_Type, with a few
deliberately insecure settings) and runs every step against it. Nothing leaves the
process and fake credentials are forced, so no real account can be reached.

With ``--live`` the same steps run against the account of the current AWS credential
chain (read-only calls only; nothing is created).

    python scripts/demo.py                                   # moto, writes ./demo-output
    python scripts/demo.py --output-dir examples/output      # regenerate the committed example
    python scripts/demo.py --live --profile audit --region eu-west-1

Requirement 11.3. Exit code: 0 when every step succeeded, otherwise the exit code of
the first failing step (2 when the demo could not start).
"""

from __future__ import annotations

import argparse
import contextlib
import os
import shutil
import sys
import warnings
from collections.abc import Iterator
from pathlib import Path

import click

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cli import cli  # noqa: E402
from src.sample_account import SAMPLE_REGION  # noqa: E402

DEFAULT_OUTPUT_DIR = "./demo-output"
FAKE_CREDENTIALS = {
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
    "AWS_SESSION_TOKEN": "testing",
    "AWS_SECURITY_TOKEN": "testing",
    "AWS_DEFAULT_REGION": SAMPLE_REGION,
    # botocore's account-id based endpoints (DynamoDB) bypass moto 4.x's URL matching
    # and would reach real AWS; force the classic regional endpoints.
    "AWS_ACCOUNT_ID_ENDPOINT_MODE": "disabled",
}
MOCKED_SERVICES = (
    "mock_ec2",
    "mock_iam",
    "mock_lambda",
    "mock_logs",
    "mock_s3",
    "mock_stepfunctions",
    "mock_rds",
    "mock_dynamodb",
    "mock_sts",
    "mock_elbv2",
    "mock_cloudfront",
    "mock_route53",
    "mock_acm",
    "mock_wafv2",
)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run collect -> analyze -> generate-iac -> generate-docs -> verify.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(DEFAULT_OUTPUT_DIR),
        help=f"Output_Dir to (re)create (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use the real account of the AWS credential chain instead of moto.",
    )
    parser.add_argument("--profile", help="Named AWS profile (--live only).")
    parser.add_argument(
        "--region",
        action="append",
        dest="regions",
        default=None,
        help="Region to scan, repeatable (default: us-east-1 with moto, all regions with --live).",
    )
    return parser.parse_args(argv)


def prepare_output_dir(output_dir: Path) -> str | None:
    """Empty a previous Output_Dir; refuse to touch any other non-empty directory."""
    if not output_dir.exists():
        return None
    if not output_dir.is_dir():
        return f"{output_dir} exists and is not a directory"
    if not any(output_dir.iterdir()):
        return None
    if not (output_dir / "manifest.json").is_file():
        return f"{output_dir} is not empty and is not an aws-inventory Output_Dir; refusing to delete it"
    shutil.rmtree(output_dir)
    return None


@contextlib.contextmanager
def moto_account() -> Iterator[None]:
    """Fake credentials + moto mocks for every service, populated with the sample account."""
    import boto3
    import moto

    from src.sample_account import build_sample_account

    saved = {key: os.environ.get(key) for key in FAKE_CREDENTIALS}
    for key in [k for k in os.environ if k.startswith("AWS_") and k not in FAKE_CREDENTIALS]:
        saved[key] = os.environ.pop(key)
    os.environ.update(FAKE_CREDENTIALS)
    mocks = [getattr(moto, name)() for name in MOCKED_SERVICES]
    for mock in mocks:
        mock.start()
    try:
        with warnings.catch_warnings():
            # moto 4.x's ACM mock uses deprecated cryptography datetime properties.
            warnings.filterwarnings("ignore", category=UserWarning, module=r"moto\.acm")
            build_sample_account(boto3.Session(region_name=SAMPLE_REGION))
            yield
    finally:
        for mock in reversed(mocks):
            mock.stop()
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def run_cli(args: list[str]) -> int:
    """Run one aws-inventory command in-process (moto mocks only exist in this process)."""
    try:
        result = cli.main(args=args, prog_name="aws-inventory", standalone_mode=False)
    except click.exceptions.Exit as exc:
        return int(exc.exit_code)
    except click.ClickException as exc:
        exc.show()
        return int(exc.exit_code)
    return result if isinstance(result, int) else 0


def run_steps(output_dir: Path, regions: list[str], profile: str | None) -> int:
    out = str(output_dir)
    collect = ["collect", "--output-dir", out]
    for region in regions:
        collect += ["--region", region]
    if profile:
        collect += ["--profile", profile]
    steps = [
        collect,
        ["analyze", "--output-dir", out],
        ["generate-iac", "--output-dir", out],
        ["generate-docs", "--output-dir", out],
        ["verify", "--output-dir", out],
    ]
    for step in steps:
        print(f"\n$ aws-inventory {' '.join(step)}", flush=True)
        code = run_cli(["--log-level", "WARNING", "--no-color", *step])
        if code != 0:
            print(f"Step `{step[0]}` failed with exit code {code}", file=sys.stderr)
            return code
    print(f"\nDemo complete. Browse {output_dir}/ (start with summary_report.md).")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    problem = prepare_output_dir(args.output_dir)
    if problem:
        print(f"demo: {problem}", file=sys.stderr)
        return 2
    if args.live:
        return run_steps(args.output_dir, args.regions or [], args.profile)
    if args.profile:
        print("demo: --profile requires --live", file=sys.stderr)
        return 2
    with moto_account():
        return run_steps(args.output_dir, args.regions or [SAMPLE_REGION], None)


if __name__ == "__main__":
    sys.exit(main())
