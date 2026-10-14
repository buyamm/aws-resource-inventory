"""
Unit tests for src/aws_session.py.

Validates: Requirements 9.1, 9.3, 12.1
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_sts

from src.aws_session import SessionError, create_session, get_account_id


def test_session_uses_default_chain_req_9_1():
    with patch("src.aws_session.boto3.Session") as session_cls:
        create_session()
    session_cls.assert_called_once_with(profile_name=None, region_name=None)


def test_session_profile_passed_req_9_1():
    with patch("src.aws_session.boto3.Session") as session_cls:
        create_session(profile="dev")
    session_cls.assert_called_once_with(profile_name="dev", region_name=None)


def test_session_assume_role_req_9_3():
    base = MagicMock()
    base.client.return_value.assume_role.return_value = {
        "Credentials": {
            "AccessKeyId": "ASIATEMPORARYKEY0001",
            "SecretAccessKey": "temp-secret",
            "SessionToken": "temp-token",
        }
    }
    with patch("src.aws_session.boto3.Session", side_effect=[base, MagicMock()]) as session_cls:
        create_session(role_arn="arn:aws:iam::111122223333:role/ReadOnly", external_id="ext-1")

    base.client.return_value.assume_role.assert_called_once_with(
        RoleArn="arn:aws:iam::111122223333:role/ReadOnly",
        RoleSessionName="aws-resource-inventory",
        ExternalId="ext-1",
    )
    assert session_cls.call_args_list[1].kwargs == {
        "aws_access_key_id": "ASIATEMPORARYKEY0001",
        "aws_secret_access_key": "temp-secret",
        "aws_session_token": "temp-token",
    }


def test_session_assume_role_failure_raises_session_error_req_12_5():
    base = MagicMock()
    base.client.return_value.assume_role.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}}, "AssumeRole"
    )
    with patch("src.aws_session.boto3.Session", return_value=base):
        with pytest.raises(SessionError) as excinfo:
            create_session(role_arn="arn:aws:iam::111122223333:role/ReadOnly")
    assert "AssumeRole" in str(excinfo.value)


def test_session_disables_botocore_retries_req_12_1():
    session = create_session()
    client = session.client("s3", region_name="us-east-1")
    assert client.meta.config.retries["total_max_attempts"] == 1
    assert "aws-resource-inventory" in client.meta.config.user_agent_extra


def test_get_account_id_uses_sts():
    with mock_sts():
        session = create_session()
        assert get_account_id(session) == "123456789012"


def test_get_account_id_without_credentials_raises_session_error_req_12_5():
    session = create_session()
    session.boto3_session = boto3.Session(
        aws_access_key_id="x", aws_secret_access_key="y", region_name="us-east-1"
    )
    with patch.object(session, "client", side_effect=Exception("Unable to locate credentials")):
        with pytest.raises(SessionError):
            get_account_id(session)


def test_session_assume_role_scrubs_base_credentials_req_9_2():
    with mock_sts():
        base_secrets = create_session().secret_values()
        session = create_session(role_arn="arn:aws:iam::123456789012:role/ReadOnly")
        secrets = session.secret_values()
    assert base_secrets and set(base_secrets) <= set(secrets)
    assert len(secrets) > len(base_secrets)  # assumed-role key, secret and token too
