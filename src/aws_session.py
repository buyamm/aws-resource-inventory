"""
AWS session handling for the online CLI commands.

Requirements Coverage:
- Requirement 9.1: Standard boto3 credential chain, optional named profile
- Requirement 9.2: Credentials are never logged or written (only passed to boto3)
- Requirement 9.3: STS AssumeRole with session name "aws-resource-inventory"
- Requirement 12.1: botocore retries disabled; SpecCollector is the only retry layer
"""

from __future__ import annotations

from typing import Any

import boto3
from botocore.config import Config

ROLE_SESSION_NAME = "aws-resource-inventory"

# total_max_attempts counts the initial call, so 1 disables botocore's retries.
# (The legacy "max_attempts" key counts retries only.)
CLIENT_CONFIG = Config(
    retries={"total_max_attempts": 1, "mode": "standard"},
    user_agent_extra="aws-resource-inventory",
)


class SessionError(Exception):
    """The AWS session could not be established (exit code 2)."""


class InventorySession:
    """Wraps a boto3.Session so every client gets :data:`CLIENT_CONFIG`."""

    def __init__(self, boto3_session: Any) -> None:
        self.boto3_session = boto3_session

    def client(self, service_name: str, region_name: str | None = None) -> Any:
        return self.boto3_session.client(
            service_name, region_name=region_name, config=CLIENT_CONFIG
        )

    def secret_values(self) -> list[str]:
        """Credential strings of this session, used only to scrub log output (Req 9.2)."""
        try:
            credentials = self.boto3_session.get_credentials()
        except Exception:  # noqa: BLE001 - no credentials means nothing to scrub
            return []
        if credentials is None:
            return []
        frozen = credentials.get_frozen_credentials()
        return [v for v in (frozen.access_key, frozen.secret_key, frozen.token) if v]


def create_session(
    profile: str | None = None,
    role_arn: str | None = None,
    external_id: str | None = None,
    region: str | None = None,
) -> InventorySession:
    """Build the session from the default chain, optionally assuming ``role_arn``."""
    base = boto3.Session(profile_name=profile, region_name=region)
    if not role_arn:
        return InventorySession(base)

    params: dict[str, str] = {"RoleArn": role_arn, "RoleSessionName": ROLE_SESSION_NAME}
    if external_id:
        params["ExternalId"] = external_id
    try:
        credentials = base.client("sts", config=CLIENT_CONFIG).assume_role(**params)["Credentials"]
    except Exception as exc:  # noqa: BLE001 - surfaced as a startup failure
        raise SessionError(f"AssumeRole failed for {role_arn}: {type(exc).__name__}") from exc

    assumed = boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )
    return InventorySession(assumed)


def get_account_id(session: InventorySession) -> str:
    """Account id of the session's principal via sts:GetCallerIdentity."""
    try:
        return str(session.client("sts", region_name="us-east-1").get_caller_identity()["Account"])
    except Exception as exc:  # noqa: BLE001 - surfaced as a startup failure
        raise SessionError(
            f"Unable to call sts:GetCallerIdentity ({type(exc).__name__}). "
            "Check that AWS credentials are configured."
        ) from exc
