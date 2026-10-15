"""
aws-inventory command line interface.

Online commands (``discover``, ``collect``) call AWS through the default credential
chain; every other command works offline on an Output_Dir.

Requirements Coverage:
- Requirement 9.1: Credentials only through the boto3 default chain (``--profile``)
- Requirement 9.2: Every log record passes through DataSanitizer plus the session's own secrets
- Requirement 9.3: ``--role-arn`` / ``--external-id`` assume a role before any other call
- Requirement 10.1, 10.2, 10.5: Phase timings, run metrics, time savings printed after collect
- Requirement 12.4: ``collection_report.json`` lists every attempted operation
- Requirement 12.5: Exit codes 0 (ok), 1 (completed with errors), 2 (could not start)
- Requirement 13.1-13.5: ``--project-tag`` / ``--include-defaults`` scoping, recorded as
  the ``scope`` block of discovery.json, manifest.json and collection_report.json
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any, TextIO

import click
from botocore.exceptions import BotoCoreError

from src import __version__
from src.analysis_engine import AnalysisEngine, AnalysisReport
from src.aws_session import SessionError, create_session, get_account_id
from src.collector import CallStatus
from src.diagram_generator import DiagramGenerator, validate_with_drawio_ai
from src.discovery import DiscoveredResource, DiscoveryError, ResourceDiscovery
from src.documentation import generate_infrastructure_doc
from src.iac_generator import IaCGenerator
from src.integrity import ANALYSIS_FILE, pretty_json, verify_output_dir
from src.inventory import CollectionResult, InventoryCollector
from src.metrics import PhaseTimer, RunMetrics, files_size, time_savings
from src.output_generator import OutputGenerator
from src.parser import ResourceSpec
from src.sanitizer import DataSanitizer
from src.scope import (
    ScopeConfig,
    TagScopedDiscovery,
    exclude_defaults,
    parse_project_tags,
    scope_document,
    seed_regions,
)

logger = logging.getLogger("src.cli")

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
DEFAULT_OUTPUT_DIR = "./output"
EXIT_ERRORS = 1
EXIT_STARTUP = 2
NO_SPECS_MESSAGE = "no resource specifications found in {dir}; run `aws-inventory collect` first"

# ============================================================================
# Logging and sanitized output (Requirement 9.2)
# ============================================================================


class SanitizingFilter(logging.Filter):
    """Runs DataSanitizer on each record and removes the active session's secret values."""

    def __init__(self) -> None:
        super().__init__()
        self._sanitizer = DataSanitizer()
        self._secrets: set[str] = set()

    def add_secrets(self, values: Iterable[str]) -> None:
        self._secrets.update(v for v in values if v)

    def scrub(self, text: str) -> str:
        for secret in sorted(self._secrets, key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        return str(self._sanitizer.sanitize(text))

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self.scrub(record.getMessage())
        record.args = ()
        if record.exc_info:
            record.exc_text = self.scrub(logging.Formatter().formatException(record.exc_info))
            record.exc_info = None
        if record.stack_info:
            record.stack_info = self.scrub(record.stack_info)
        return True


class CliLogHandler(logging.StreamHandler):
    """Writes to the current ``sys.stderr`` (resolved per record, so redirection works)."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def stream(self) -> TextIO:
        return sys.stderr

    @stream.setter
    def stream(self, value: TextIO) -> None:  # StreamHandler.__init__ assigns it
        pass


SCRUBBER = SanitizingFilter()


def configure_logging(level: str) -> None:
    root = logging.getLogger()
    for handler in list(root.handlers):
        if isinstance(handler, CliLogHandler):
            root.removeHandler(handler)
    handler = CliLogHandler()
    handler.addFilter(SCRUBBER)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(handler)
    root.setLevel(level)


class StartupError(click.ClickException):
    """The command could not start (exit code 2)."""

    exit_code = EXIT_STARTUP

    def __init__(self, message: str) -> None:
        super().__init__(SCRUBBER.scrub(message))


class Console:
    """Results on stdout, progress and failures on stderr; all text is scrubbed."""

    def __init__(self, color: bool) -> None:
        self.color = color

    def _style(self, text: str, **styles: Any) -> str:
        return click.style(text, **styles) if self.color else text

    def out(self, text: str, **styles: Any) -> None:
        click.echo(self._style(SCRUBBER.scrub(text), **styles), color=self.color)

    def err(self, text: str, **styles: Any) -> None:
        click.echo(self._style(SCRUBBER.scrub(text), **styles), err=True, color=self.color)


def _console(ctx: click.Context) -> Console:
    console = ctx.find_object(Console)
    return console if console is not None else Console(color=False)


# ============================================================================
# Shared helpers
# ============================================================================


def _write_json(path: Path, value: Any, written: list[Path] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(DataSanitizer().sanitize(value)) + "\n", encoding="utf-8")
    if written is not None:
        written.append(path)
    return path


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(DataSanitizer().sanitize(text)), encoding="utf-8")
    return path


def _open_session(profile: str | None, role_arn: str | None, external_id: str | None) -> Any:
    try:
        session = create_session(profile=profile, role_arn=role_arn, external_id=external_id)
        SCRUBBER.add_secrets(session.secret_values())
        account_id = get_account_id(session)
    except (SessionError, BotoCoreError) as exc:
        raise StartupError(str(exc)) from exc
    return session, account_id


Discovery = ResourceDiscovery | TagScopedDiscovery


def _discover(
    console: Console,
    session: Any,
    account_id: str,
    regions: tuple[str, ...],
    max_workers: int,
    scope: ScopeConfig,
) -> tuple[Discovery, list[DiscoveredResource], list[DiscoveredResource]]:
    """Discover the seed resources; returns (discovery, kept, excluded defaults)."""

    def progress(region: str, done: int, total: int) -> None:
        console.err(f"Discovering: {done}/{total} regions ({region})")

    discovery: Discovery
    if scope.project_tags:
        discovery = TagScopedDiscovery(
            session,
            scope.project_tags,
            regions=list(regions) or None,
            max_workers=max_workers,
            progress_callback=progress,
            account_id=account_id,
        )
    else:
        discovery = ResourceDiscovery(
            session,
            regions=list(regions) or None,
            max_workers=max_workers,
            progress_callback=progress,
            account_id=account_id,
        )
    kept, excluded = exclude_defaults(discovery.discover_all_resources(), scope.include_defaults)
    if excluded:
        console.err(f"Excluded {len(excluded)} account defaults (use --include-defaults to keep)")
    return discovery, kept, excluded


def _discovery_document(
    account_id: str,
    discovery: Discovery,
    resources: list[DiscoveredResource],
    scope: dict[str, Any],
) -> dict[str, Any]:
    return {
        "account_id": account_id,
        "regions": sorted({r.region for r in resources}),
        "api_calls": discovery.get_api_calls(),
        "scope": scope,
        "resources": [asdict(r) for r in resources],
        "errors": [asdict(e) for e in discovery.get_errors()],
    }


def _load_specs_or_exit(output_dir: Path) -> tuple[list[ResourceSpec], int]:
    errors: list[str] = []
    specs = OutputGenerator.load_specs(output_dir, errors)
    for error in errors:
        logger.error("Skipping unreadable spec file %s", error)
    if not specs:
        raise StartupError(NO_SPECS_MESSAGE.format(dir=output_dir))
    return specs, EXIT_ERRORS if errors else 0


def _refresh_checksums(output_dir: Path) -> None:
    OutputGenerator(output_dir).generate_checksums()


region_option = click.option(
    "--region",
    "regions",
    multiple=True,
    help="Region to scan (repeatable). Default: every enabled region.",
)


def _project_tags_callback(
    ctx: click.Context, param: click.Parameter, values: tuple[str, ...]
) -> dict[str, str]:
    try:
        return parse_project_tags(values)
    except ValueError as exc:
        raise click.BadParameter(f"{exc} (format: KEY=VALUE)") from exc


project_tag_option = click.option(
    "--project-tag",
    "project_tags",
    multiple=True,
    metavar="KEY=VALUE",
    callback=_project_tags_callback,
    help="Only resources carrying this tag (repeatable, all must match), plus the "
    "resources they reference. Default: every resource of the supported types.",
)
include_defaults_option = click.option(
    "--include-defaults",
    is_flag=True,
    help="Keep default VPCs, their default security groups and service-linked roles "
    "even when nothing references them.",
)
profile_option = click.option("--profile", help="Named profile of the AWS credential chain.")
role_option = click.option("--role-arn", help="Role to assume (sts:AssumeRole) before scanning.")
external_id_option = click.option("--external-id", help="ExternalId passed to sts:AssumeRole.")
output_dir_option = click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    show_default=True,
    help="Output_Dir holding collected data.",
)
existing_output_dir_option = click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=DEFAULT_OUTPUT_DIR,
    show_default=True,
    help="Output_Dir written by `aws-inventory collect`.",
)


# ============================================================================
# Commands
# ============================================================================


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="""\b
Examples:
  aws-inventory collect --region us-east-1 --output-dir ./output
  aws-inventory analyze --output-dir ./output
  aws-inventory verify --output-dir ./output
  aws-inventory mcp-serve --cache-dir ./output""",
)
@click.option(
    "--log-level",
    type=click.Choice(LOG_LEVELS, case_sensitive=False),
    default="INFO",
    show_default=True,
    help="Log level of messages written to stderr.",
)
@click.option("--no-color", is_flag=True, help="Disable ANSI colors in terminal output.")
@click.version_option(__version__, prog_name="aws-inventory")
@click.pass_context
def cli(ctx: click.Context, log_level: str, no_color: bool) -> None:
    """Inventory, analyze and document an AWS account (read-only).

    `discover` and `collect` call AWS; all other commands work offline on the
    Output_Dir written by `collect`.
    """
    configure_logging(log_level.upper())
    ctx.obj = Console(color=not no_color)


@cli.command(epilog="""\b
Examples:
  aws-inventory discover --region us-east-1 --region eu-west-1 --profile prod
  aws-inventory discover --project-tag service=shop --project-tag environment=prod""")
@region_option
@project_tag_option
@include_defaults_option
@profile_option
@role_option
@external_id_option
@output_dir_option
@click.pass_context
def discover(
    ctx: click.Context,
    regions: tuple[str, ...],
    project_tags: dict[str, str],
    include_defaults: bool,
    profile: str | None,
    role_arn: str | None,
    external_id: str | None,
    output_dir: Path,
) -> None:
    """List resources of the supported types and write discovery.json."""
    console = _console(ctx)
    session, account_id = _open_session(profile, role_arn, external_id)
    scope = ScopeConfig(project_tags, include_defaults)
    discovery, resources, excluded = _discover(console, session, account_id, regions, 10, scope)
    scope_block = scope_document(scope, seed_regions(resources, regions), resources, excluded)
    path = _write_json(
        output_dir / "discovery.json",
        _discovery_document(account_id, discovery, resources, scope_block),
    )
    console.out(f"Discovered {len(resources)} resources in account {account_id} -> {path}")
    errors = discovery.get_errors()
    if errors:
        console.err(f"{len(errors)} discovery errors:", fg="red")
        for error in errors:
            console.err(f"  {error}")
        ctx.exit(EXIT_ERRORS)


def _operation_entries(result: CollectionResult) -> list[dict[str, Any]]:
    entries = []
    for op in result.operations:
        failed = op.status in (CallStatus.DENIED, CallStatus.FAILED)
        entries.append(
            {
                "resource_arn": op.resource_arn,
                "operation": op.operation,
                "status": "failed" if failed else "success",
                "outcome": str(op.status),
                "attempts": op.attempts,
                "error_type": op.error_type,
                "detail": op.detail,
                "timestamp": op.timestamp,
            }
        )
    return entries


def _summary_markdown(
    generator: OutputGenerator,
    specs: list[ResourceSpec],
    metrics: RunMetrics,
    timer: PhaseTimer,
) -> str:
    lines = ["# AWS Resource Inventory - Summary Report", "", "| Metric | Value |", "|---|---|"]
    lines += [f"| {key} | {value} |" for key, value in metrics.to_dict().items()]
    lines += ["", "| Phase | Duration (s) |", "|---|---|"]
    lines += [f"| {p.name} | {p.duration_seconds:.2f} |" for p in timer.phases]
    lines.append("")
    lines.append(
        generator.generate_summary_report(
            specs, timer.total_duration_seconds, resources_discovered=metrics.resources_discovered
        )
    )
    return "\n".join(lines)


@cli.command(epilog="""\b
Examples:
  aws-inventory collect --region us-east-1 --output-dir ./output
  aws-inventory collect --profile audit --role-arn arn:aws:iam::123456789012:role/Reader
  aws-inventory collect --project-tag service=shop --project-tag environment=prod""")
@region_option
@project_tag_option
@include_defaults_option
@profile_option
@role_option
@external_id_option
@output_dir_option
@click.option(
    "--max-workers",
    type=click.IntRange(min=1),
    default=10,
    show_default=True,
    help="Concurrent regions / resources.",
)
@click.pass_context
def collect(
    ctx: click.Context,
    regions: tuple[str, ...],
    project_tags: dict[str, str],
    include_defaults: bool,
    profile: str | None,
    role_arn: str | None,
    external_id: str | None,
    output_dir: Path,
    max_workers: int,
) -> None:
    """Discover and collect resource specifications into the Output_Dir."""
    console = _console(ctx)
    timer = PhaseTimer()
    session, account_id = _open_session(profile, role_arn, external_id)
    sts_calls = 2 if role_arn else 1

    scope = ScopeConfig(project_tags, include_defaults)
    with timer.phase("discovery"):
        discovery, resources, excluded = _discover(
            console, session, account_id, regions, max_workers, scope
        )

    step = max(1, len(resources) // 10)

    def progress(done: int, total: int) -> None:
        if done % step == 0 or done == total:
            console.err(f"Collecting: {done}/{total} resources")

    with timer.phase("collection"):
        result = InventoryCollector(
            session, account_id, max_workers=max_workers, progress_callback=progress
        ).collect_all(resources)

    scope_block = scope_document(
        scope, seed_regions(resources, regions), resources, excluded, result.referenced
    )
    in_scope = len(resources) + len(result.referenced)
    generator = OutputGenerator(output_dir)
    written: list[Path] = []
    with timer.phase("output"):
        written += generator.generate_json(result.specs)
        written += generator.generate_markdown(result.specs, timer.total_duration_seconds)
        written += generator.store_raw_responses(result.specs)
        written.append(
            generator.write_manifest(
                account_id,
                list(regions) or sorted({s.region for s in result.specs}),
                timer.phases[0].started_at,
                timer.phases[-1].ended_at,
                result.specs,
                scope=scope_block,
            )
        )
        _write_json(
            generator.output_dir / "discovery.json",
            _discovery_document(account_id, discovery, resources, scope_block),
            written,
        )

    metrics = RunMetrics(
        resources_discovered=in_scope,
        specs_collected=len(result.specs),
        specs_failed=in_scope - len(result.specs),
        api_calls=sts_calls + discovery.get_api_calls() + result.api_calls,
        data_volume_bytes=files_size(written),
    )
    savings = time_savings(in_scope, timer.total_duration_seconds)
    summary_path = _write_text(
        generator.output_dir / "summary_report.md",
        _summary_markdown(generator, result.specs, metrics, timer),
    )
    discovery_errors = discovery.get_errors()
    report = {
        "account_id": account_id,
        "regions": list(regions),
        "scope": scope_block,
        "started_at": timer.phases[0].started_at,
        "finished_at": timer.phases[-1].ended_at,
        "phases": timer.to_list(),
        "metrics": metrics.to_dict(),
        "time_savings": savings.to_dict(),
        "operations": _operation_entries(result),
        "discovery_errors": [asdict(e) for e in discovery_errors],
        "collection_errors": [asdict(e) for e in result.errors],
    }
    report_path = _write_json(generator.output_dir / "collection_report.json", report)
    generator.generate_checksums()

    console.out(
        f"Collected {metrics.specs_collected}/{metrics.resources_discovered} resources "
        f"in {timer.total_duration_seconds:.2f}s ({metrics.api_calls} API calls) -> {output_dir}"
    )
    console.out(
        f"Time saved: {savings.hours_saved:.2f} hours ({savings.percent_saved:.1f}%)",
        fg="green",
        bold=True,
    )
    console.out(f"Reports: {summary_path.name}, {report_path.name}")
    if discovery_errors or result.errors:
        _print_failures(console, discovery_errors, result)
        ctx.exit(EXIT_ERRORS)


def _print_failures(
    console: Console, discovery_errors: list[DiscoveryError], result: CollectionResult
) -> None:
    total = len(discovery_errors) + len(result.errors)
    console.err(f"Completed with {total} errors (see collection_report.json):", fg="red")
    for d_error in discovery_errors:
        console.err(f"  discovery {d_error}")
    for c_error in result.errors:
        console.err(
            f"  {c_error.resource_arn} {c_error.operation}: {c_error.error_type} "
            f"{c_error.error_message}"
        )


def _write_analysis(output_dir: Path, report: AnalysisReport) -> None:
    _write_json(output_dir / ANALYSIS_FILE, report.to_dict())
    _write_text(output_dir / "analysis" / "analysis.md", report.summary_markdown)


@cli.command(epilog="""\b
Example:
  aws-inventory analyze --output-dir ./output --validate-diagram""")
@existing_output_dir_option
@click.option(
    "--validate-diagram",
    is_flag=True,
    help="Validate the diagram with `drawio-ai validate` when that CLI is installed.",
)
@click.pass_context
def analyze(ctx: click.Context, output_dir: Path, validate_diagram: bool) -> None:
    """Write cited analysis (analysis/) and an architecture diagram (diagrams/)."""
    console = _console(ctx)
    specs, exit_code = _load_specs_or_exit(output_dir)
    report = AnalysisEngine().analyze(specs)
    _write_analysis(output_dir, report)
    diagram = DiagramGenerator().write_diagram(
        specs, output_dir / "diagrams" / "architecture.drawio", report.relationships
    )
    console.out(
        f"Analyzed {len(specs)} resources: {len(report.relationships)} relationships, "
        f"{len(report.patterns)} patterns, {len(report.security_findings)} security findings"
    )
    console.out(f"Diagram: {diagram}")
    if validate_diagram:
        passed, message = validate_with_drawio_ai(diagram)
        if passed is None:
            console.err(message, fg="yellow")
        elif passed:
            console.out("Diagram validation passed")
        else:
            console.err(f"Diagram validation failed:\n{message}", fg="red")
            exit_code = EXIT_ERRORS
    _refresh_checksums(output_dir)
    ctx.exit(exit_code)


@cli.command(
    "generate-iac",
    epilog="""\b
Example:
  aws-inventory generate-iac --output-dir ./output
  cd output/terraform && terraform init && ./import.sh && ./verify_state.sh""",
)
@existing_output_dir_option
@click.option(
    "--terraform-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Where to write Terraform. Default: <output-dir>/terraform.",
)
@click.pass_context
def generate_iac(ctx: click.Context, output_dir: Path, terraform_dir: Path | None) -> None:
    """Generate Terraform, import.sh and verify_state.sh from collected specs."""
    console = _console(ctx)
    specs, exit_code = _load_specs_or_exit(output_dir)
    target = terraform_dir or output_dir / "terraform"
    files = IaCGenerator().generate_terraform(specs, target)
    console.out(f"Generated {len(files)} Terraform files for {len(specs)} resources -> {target}")
    _refresh_checksums(output_dir)
    ctx.exit(exit_code)


@cli.command(
    "generate-docs",
    epilog="""\b
Example:
  aws-inventory generate-docs --output-dir ./output""",
)
@existing_output_dir_option
@click.pass_context
def generate_docs(ctx: click.Context, output_dir: Path) -> None:
    """Write docs/infrastructure.md; every statement carries a citation."""
    console = _console(ctx)
    specs, exit_code = _load_specs_or_exit(output_dir)
    report = AnalysisEngine().analyze(specs)
    path = _write_text(
        output_dir / "docs" / "infrastructure.md", generate_infrastructure_doc(report, specs)
    )
    console.out(f"Documentation: {path}")
    _refresh_checksums(output_dir)
    ctx.exit(exit_code)


@cli.command(epilog="""\b
Example:
  aws-inventory verify --output-dir ./output""")
@existing_output_dir_option
@click.pass_context
def verify(ctx: click.Context, output_dir: Path) -> None:
    """Check file checksums and every analysis citation against the spec files."""
    console = _console(ctx)
    if not output_dir.is_dir():
        raise StartupError(f"{output_dir} is not a directory")
    report = verify_output_dir(output_dir)
    if report.ok:
        console.out(report.summary())
        return
    for discrepancy in report.discrepancies:
        console.out(str(discrepancy))
    console.err(report.summary(), fg="red")
    ctx.exit(EXIT_ERRORS)


@cli.command(
    "mcp-serve",
    epilog="""\b
Example (.mcp.json):
  {"mcpServers": {"aws-inventory": {"command": "aws-inventory",
    "args": ["mcp-serve", "--cache-dir", "/abs/path/output"]}}}""",
)
@click.option(
    "--cache-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Output_Dir written by `aws-inventory collect`.",
)
def mcp_serve(cache_dir: str) -> None:
    """Serve the collected data to AI agents over MCP stdio (no AWS credentials)."""
    from src import mcp_stdio

    mcp_stdio.serve(cache_dir)


def main(argv: list[str] | None = None) -> None:
    cli.main(args=argv, prog_name="aws-inventory")


if __name__ == "__main__":
    main()
