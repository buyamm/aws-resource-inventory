# AWS Resource: `aws_security_group` - `sg-1f2b0a4eff89696aa`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-1f2b0a4eff89696aa |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T02:30:23Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | default VPC security group |
| GroupId           | sg-1f2b0a4eff89696aa       |
| GroupName         | default                    |
| OwnerId           | 123456789012               |
| VpcId             | vpc-040f0f81               |


### Ippermissions

```json
[]
```


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Securitygrouprules

| CidrIpv4  | FromPort | GroupId              | GroupOwnerId | IpProtocol | IsEgress | SecurityGroupRuleId   | Tags | ToPort |
| --------- | -------- | -------------------- | ------------ | ---------- | -------- | --------------------- | ---- | ------ |
| 0.0.0.0/0 | -1       | sg-1f2b0a4eff89696aa | 123456789012 | -1         | True     | sgr-3d9b8032b1879d361 | []   | -1     |


### Tags

```json
[]
```

