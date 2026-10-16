# AWS Resource: `aws_elasticache_replication_group` - `storefront-cache`

## Overview

| Property          | Value                                                                        |
| ----------------- | ---------------------------------------------------------------------------- |
| Resource Type     | aws_elasticache_replication_group                                            |
| ARN               | arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache |
| Region            | us-east-1                                                                    |
| Account ID        | 123456789012                                                                 |
| Collected At      | 2026-10-16T02:30:23Z                                                         |
| Collector Version | 0.1.0                                                                        |


## Configuration Specifications

| Configuration Key          | Value                                                                        |
| -------------------------- | ---------------------------------------------------------------------------- |
| ARN                        | arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache |
| AtRestEncryptionEnabled    | True                                                                         |
| AuthTokenEnabled           | False                                                                        |
| AutoMinorVersionUpgrade    | True                                                                         |
| AutomaticFailover          | enabled                                                                      |
| CacheNodeType              | cache.t4g.micro                                                              |
| ClusterEnabled             | False                                                                        |
| ClusterMode                | disabled                                                                     |
| DataTiering                | disabled                                                                     |
| Description                | Storefront session cache                                                     |
| Engine                     | redis                                                                        |
| IpDiscovery                | ipv4                                                                         |
| MultiAZ                    | enabled                                                                      |
| NetworkType                | ipv4                                                                         |
| ReplicationGroupCreateTime | 2026-01-01T00:00:00+00:00                                                    |
| ReplicationGroupId         | storefront-cache                                                             |
| SnapshotRetentionLimit     | 0                                                                            |
| SnapshotWindow             | 05:00-06:00                                                                  |
| Status                     | available                                                                    |
| TransitEncryptionEnabled   | True                                                                         |


### Cachecluster

```json
{
  "ARN": "arn:aws:elasticache:us-east-1:123456789012:cluster:storefront-cache-001",
  "AtRestEncryptionEnabled": true,
  "AuthTokenEnabled": false,
  "AutoMinorVersionUpgrade": true,
  "CacheClusterCreateTime": "2026-01-01T00:00:00+00:00",
  "CacheClusterId": "storefront-cache-001",
  "CacheClusterStatus": "available",
  "CacheNodeType": "cache.t4g.micro",
  "CacheParameterGroup": {
    "CacheNodeIdsToReboot": [],
    "CacheParameterGroupName": "default.redis7",
    "ParameterApplyStatus": "in-sync"
  },
  "CacheSecurityGroups": [],
  "CacheSubnetGroupName": "storefront-cache-subnets",
  "Engine": "redis",
  "EngineVersion": "7.1",
  "IpDiscovery": "ipv4",
  "LogDeliveryConfigurations": [],
  "NetworkType": "ipv4",
  "NumCacheNodes": 1,
  "PendingModifiedValues": {},
  "PreferredAvailabilityZone": "us-east-1a",
  "PreferredMaintenanceWindow": "sun:23:00-mon:01:30",
  "ReplicationGroupId": "storefront-cache",
  "ReplicationGroupLogDeliveryEnabled": false,
  "SecurityGroups": [
    {
      "SecurityGroupId": "sg-b7692d5b41942a421",
      "Status": "active"
    }
  ],
  "SnapshotRetentionLimit": 0,
  "SnapshotWindow": "05:00-06:00",
  "TransitEncryptionEnabled": true
}
```


### Cachesubnetgroup

```json
{
  "ARN": "arn:aws:elasticache:us-east-1:123456789012:subnetgroup:storefront-cache-subnets",
  "CacheSubnetGroupDescription": "Storefront cache",
  "CacheSubnetGroupName": "storefront-cache-subnets",
  "Subnets": [
    {
      "SubnetAvailabilityZone": {
        "Name": "us-east-1a"
      },
      "SubnetIdentifier": "subnet-7f177dcb",
      "SupportedNetworkTypes": [
        "ipv4"
      ]
    }
  ],
  "SupportedNetworkTypes": [
    "ipv4"
  ],
  "VpcId": "vpc-040f0f81"
}
```


### Logdeliveryconfigurations

```json
[]
```


### Memberclusters

```json
[
  "storefront-cache-001",
  "storefront-cache-002"
]
```


### Nodegroups

| NodeGroupId | NodeGroupMembers                                                                                                                                                                                                                                                                 | PrimaryEndpoint                                                                            | ReaderEndpoint                                                                             | Status    |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | --------- |
| 0001        | [{'CacheClusterId': 'storefront-cache-001', 'CacheNodeId': '0001', 'PreferredAvailabilityZone': 'us-east-1a', 'CurrentRole': 'primary'}, {'CacheClusterId': 'storefront-cache-002', 'CacheNodeId': '0001', 'PreferredAvailabilityZone': 'us-east-1a', 'CurrentRole': 'replica'}] | {'Address': 'storefront-cache.abc123.ng.0001.us-east-1.cache.amazonaws.com', 'Port': 6379} | {'Address': 'storefront-cache.abc123.ro.0001.us-east-1.cache.amazonaws.com', 'Port': 6379} | available |


### Pendingmodifiedvalues

```json
{}
```


### Taglist

| Key     | Value      |
| ------- | ---------- |
| service | storefront |

