"""
ElastiCache replication groups for moto 4.x (demo and test support only).

moto 4.2 implements ElastiCache cache clusters and users but not replication groups or
cache subnet groups, so ``DescribeReplicationGroups`` raises ``NotImplementedError``
inside a mock. Inside :func:`mock_elasticache_replication_groups` this module answers
these operations from an in-memory store instead (a botocore ``before-call`` handler, so
no request is sent anywhere):

- ``CreateCacheSubnetGroup``, ``DescribeCacheSubnetGroups``
- ``CreateReplicationGroup``, ``DescribeReplicationGroups``
- ``DescribeCacheClusters`` (member clusters of the stored groups)
- ``ListTagsForResource`` (tags given at creation)

Responses follow the shapes of the ElastiCache API reference. Every other ElastiCache
operation is left to moto. The handlers are registered in ``botocore.handlers`` when this
module is imported, so only botocore sessions created afterwards see it; import it
before creating sessions (``tests/conftest.py`` and ``scripts/demo.py`` do).

Like moto, the store is per account (resolved from the caller's access key, so assumed
roles see their own account) and per region.

Never use this module against a real account: outside the context manager the handler
does nothing.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from botocore import handlers
from botocore.awsrequest import AWSResponse, HTTPHeaders

DEFAULT_ACCOUNT = "123456789012"
_SERVICE = "elasticache"


class _Store:
    def __init__(self) -> None:
        self.active = 0
        self.lock = threading.Lock()
        # Keyed by ((account, region), name).
        self.subnet_groups: dict[tuple[tuple[str, str], str], dict[str, Any]] = {}
        self.groups: dict[tuple[tuple[str, str], str], dict[str, Any]] = {}
        self.clusters: dict[tuple[tuple[str, str], str], dict[str, Any]] = {}
        self.tags: dict[str, list[dict[str, str]]] = {}

    def reset(self) -> None:
        self.subnet_groups.clear()
        self.groups.clear()
        self.clusters.clear()
        self.tags.clear()


_STORE = _Store()
_PARAMS_KEY = "moto_compat_api_params"


@contextmanager
def mock_elasticache_replication_groups() -> Iterator[None]:
    """Serve the replication-group operations from memory while the context is active."""
    with _STORE.lock:
        _STORE.active += 1
    try:
        yield
    finally:
        with _STORE.lock:
            _STORE.active -= 1
            if not _STORE.active:
                _STORE.reset()


# ============================================================================
# botocore handlers
# ============================================================================


def _capture_params(params: dict[str, Any], context: dict[str, Any], **_: Any) -> None:
    """Keep the unserialized API parameters for the before-call handler."""
    if _STORE.active:
        context[_PARAMS_KEY] = dict(params)


def _account(request_signer: Any) -> str:
    """The moto account of the caller (same resolution order as moto's responses)."""
    if "MOTO_ACCOUNT_ID" in os.environ:
        return os.environ["MOTO_ACCOUNT_ID"]
    try:
        from moto.iam.models import get_account_id_from

        credentials = request_signer._credentials.get_frozen_credentials()
        return str(get_account_id_from(credentials.access_key))
    except Exception:  # noqa: BLE001 - unsigned or unknown callers use the default
        return DEFAULT_ACCOUNT


def _respond(
    model: Any, context: dict[str, Any], request_signer: Any = None, **_: Any
) -> tuple[AWSResponse, Any] | None:
    if not _STORE.active or getattr(model.service_model, "service_name", "") != _SERVICE:
        return None
    operation = getattr(model, "name", "")
    implementation = _OPERATIONS.get(operation)
    if implementation is None:
        return None
    region = str(context.get("client_region") or "us-east-1")
    params = context.get(_PARAMS_KEY) or {}
    with _STORE.lock:
        outcome = implementation((_account(request_signer), region), params)
    if outcome is None:
        return None
    status, body = outcome
    body["ResponseMetadata"] = {
        "RequestId": "moto-compat",
        "HTTPStatusCode": status,
        "HTTPHeaders": {"server": "amazon.com"},
        "RetryAttempts": 0,
    }
    url = f"https://{_SERVICE}.{region}.amazonaws.com/"
    return AWSResponse(url, status, HTTPHeaders(), None), body


def _error(code: str, message: str, status: int = 404) -> tuple[int, dict[str, Any]]:
    return status, {"Error": {"Code": code, "Message": message, "Type": "Sender"}}


def _now() -> datetime:
    return datetime(2026, 1, 1, tzinfo=UTC)


Scope = tuple[str, str]  # (account, region)
_Outcome = tuple[int, dict[str, Any]] | None


def _arn(scope: Scope, kind: str, name: str) -> str:
    account, region = scope
    return f"arn:aws:elasticache:{region}:{account}:{kind}:{name}"


def _subnet_details(scope: Scope, subnet_ids: list[str]) -> tuple[str, list[dict[str, Any]]]:
    """VPC id and ``Subnets`` entries from moto's EC2 backend (empty when unknown)."""
    try:
        from moto.ec2.models import ec2_backends

        backend = ec2_backends[scope[0]][scope[1]]
        subnets = [backend.get_subnet(subnet_id) for subnet_id in subnet_ids]
    except Exception:  # noqa: BLE001 - unknown subnets keep their id only
        return "", [{"SubnetIdentifier": s, "SubnetAvailabilityZone": {}} for s in subnet_ids]
    vpc_id = subnets[0].vpc_id if subnets else ""
    return vpc_id, [
        {
            "SubnetIdentifier": subnet.id,
            "SubnetAvailabilityZone": {"Name": subnet.availability_zone},
            "SupportedNetworkTypes": ["ipv4"],
        }
        for subnet in subnets
    ]


def _create_cache_subnet_group(scope: Scope, params: dict[str, Any]) -> _Outcome:
    name = str(params["CacheSubnetGroupName"])
    vpc_id, subnets = _subnet_details(scope, list(params.get("SubnetIds", [])))
    group = {
        "CacheSubnetGroupName": name,
        "CacheSubnetGroupDescription": params.get("CacheSubnetGroupDescription", ""),
        "VpcId": vpc_id,
        "Subnets": subnets,
        "ARN": _arn(scope, "subnetgroup", name),
        "SupportedNetworkTypes": ["ipv4"],
    }
    _STORE.subnet_groups[(scope, name)] = group
    _STORE.tags[group["ARN"]] = list(params.get("Tags", []))
    return 200, {"CacheSubnetGroup": group}


def _describe_cache_subnet_groups(scope: Scope, params: dict[str, Any]) -> _Outcome:
    name = params.get("CacheSubnetGroupName")
    groups = [g for (key, _), g in sorted(_STORE.subnet_groups.items()) if key == scope]
    if name:
        groups = [g for g in groups if g["CacheSubnetGroupName"] == name]
        if not groups:
            return _error("CacheSubnetGroupNotFoundFault", f"{name} not found")
    return 200, {"CacheSubnetGroups": groups}


def _create_replication_group(scope: Scope, params: dict[str, Any]) -> _Outcome:
    region = scope[1]
    group_id = str(params["ReplicationGroupId"])
    engine = str(params.get("Engine") or "redis")
    port = int(params.get("Port") or 6379)
    count = int(params.get("NumCacheClusters") or 1)
    node_type = str(params.get("CacheNodeType") or "cache.t3.micro")
    failover = "enabled" if params.get("AutomaticFailoverEnabled") else "disabled"
    multi_az = "enabled" if params.get("MultiAZEnabled") else "disabled"
    transit = bool(params.get("TransitEncryptionEnabled", False))
    at_rest = bool(params.get("AtRestEncryptionEnabled", False))
    subnet_group = str(params.get("CacheSubnetGroupName") or "default")
    zones = [
        s["SubnetAvailabilityZone"].get("Name", f"{region}a")
        for s in _STORE.subnet_groups.get((scope, subnet_group), {}).get("Subnets", [])
    ] or [f"{region}a"]
    members = [f"{group_id}-{i:03d}" for i in range(1, count + 1)]
    host = f"{group_id}.abc123.ng.0001.{region}.cache.amazonaws.com"
    group = {
        "ReplicationGroupId": group_id,
        "Description": params.get("ReplicationGroupDescription", ""),
        "Status": "available",
        "PendingModifiedValues": {},
        "MemberClusters": members,
        "NodeGroups": [
            {
                "NodeGroupId": "0001",
                "Status": "available",
                "PrimaryEndpoint": {"Address": host, "Port": port},
                "ReaderEndpoint": {"Address": host.replace(".ng.", ".ro."), "Port": port},
                "NodeGroupMembers": [
                    {
                        "CacheClusterId": member,
                        "CacheNodeId": "0001",
                        "PreferredAvailabilityZone": zones[i % len(zones)],
                        "CurrentRole": "primary" if i == 0 else "replica",
                    }
                    for i, member in enumerate(members)
                ],
            }
        ],
        "AutomaticFailover": failover,
        "MultiAZ": multi_az,
        "SnapshotRetentionLimit": int(params.get("SnapshotRetentionLimit") or 0),
        "SnapshotWindow": params.get("SnapshotWindow") or "05:00-06:00",
        "ClusterEnabled": False,
        "CacheNodeType": node_type,
        "AuthTokenEnabled": False,
        "TransitEncryptionEnabled": transit,
        "AtRestEncryptionEnabled": at_rest,
        "ARN": _arn(scope, "replicationgroup", group_id),
        "LogDeliveryConfigurations": [],
        "ReplicationGroupCreateTime": _now(),
        "DataTiering": "disabled",
        "AutoMinorVersionUpgrade": True,
        "NetworkType": "ipv4",
        "IpDiscovery": "ipv4",
        "ClusterMode": "disabled",
        "Engine": engine,
    }
    if params.get("KmsKeyId"):
        group["KmsKeyId"] = params["KmsKeyId"]
    version = str(params.get("EngineVersion") or "7.1")
    for i, member in enumerate(members):
        cluster = {
            "CacheClusterId": member,
            "CacheNodeType": node_type,
            "Engine": engine,
            "EngineVersion": version,
            "CacheClusterStatus": "available",
            "NumCacheNodes": 1,
            "PreferredAvailabilityZone": zones[i % len(zones)],
            "CacheClusterCreateTime": _now(),
            "PreferredMaintenanceWindow": params.get("PreferredMaintenanceWindow")
            or "sun:23:00-mon:01:30",
            "PendingModifiedValues": {},
            "CacheSecurityGroups": [],
            "CacheParameterGroup": {
                "CacheParameterGroupName": params.get("CacheParameterGroupName")
                or f"default.{engine}{version.split('.')[0]}",
                "ParameterApplyStatus": "in-sync",
                "CacheNodeIdsToReboot": [],
            },
            "CacheSubnetGroupName": subnet_group,
            "AutoMinorVersionUpgrade": True,
            "SecurityGroups": [
                {"SecurityGroupId": sg, "Status": "active"}
                for sg in params.get("SecurityGroupIds", [])
            ],
            "ReplicationGroupId": group_id,
            "SnapshotRetentionLimit": group["SnapshotRetentionLimit"],
            "SnapshotWindow": group["SnapshotWindow"],
            "AuthTokenEnabled": False,
            "TransitEncryptionEnabled": transit,
            "AtRestEncryptionEnabled": at_rest,
            "ARN": _arn(scope, "cluster", member),
            "ReplicationGroupLogDeliveryEnabled": False,
            "LogDeliveryConfigurations": [],
            "NetworkType": "ipv4",
            "IpDiscovery": "ipv4",
        }
        _STORE.clusters[(scope, member)] = cluster
    _STORE.groups[(scope, group_id)] = group
    _STORE.tags[group["ARN"]] = list(params.get("Tags", []))
    return 200, {"ReplicationGroup": group}


def _describe_replication_groups(scope: Scope, params: dict[str, Any]) -> _Outcome:
    group_id = params.get("ReplicationGroupId")
    groups = [g for (key, _), g in sorted(_STORE.groups.items()) if key == scope]
    if group_id:
        groups = [g for g in groups if g["ReplicationGroupId"] == group_id]
        if not groups:
            return _error("ReplicationGroupNotFoundFault", f"{group_id} not found")
    return 200, {"ReplicationGroups": groups}


def _describe_cache_clusters(scope: Scope, params: dict[str, Any]) -> _Outcome:
    cluster_id = params.get("CacheClusterId")
    if not cluster_id or (scope, cluster_id) not in _STORE.clusters:
        return None  # not a member cluster of a stored group: moto answers
    return 200, {"CacheClusters": [_STORE.clusters[(scope, cluster_id)]]}


def _list_tags_for_resource(scope: Scope, params: dict[str, Any]) -> _Outcome:
    return 200, {"TagList": list(_STORE.tags.get(str(params.get("ResourceName")), []))}


_OPERATIONS: dict[str, Callable[[Scope, dict[str, Any]], _Outcome]] = {
    "CreateCacheSubnetGroup": _create_cache_subnet_group,
    "DescribeCacheSubnetGroups": _describe_cache_subnet_groups,
    "CreateReplicationGroup": _create_replication_group,
    "DescribeReplicationGroups": _describe_replication_groups,
    "DescribeCacheClusters": _describe_cache_clusters,
    "ListTagsForResource": _list_tags_for_resource,
}

# The response handler is registered last on every "before-call", so other before-call
# handlers (the benchmark's latency injector) still run for these operations.
_HANDLERS: list[tuple[Any, ...]] = [
    (f"before-parameter-build.{_SERVICE}", _capture_params),
    ("before-call", _respond, handlers.REGISTER_LAST),
]
for _handler in _HANDLERS:
    if _handler not in handlers.BUILTIN_HANDLERS:
        handlers.BUILTIN_HANDLERS.append(_handler)
