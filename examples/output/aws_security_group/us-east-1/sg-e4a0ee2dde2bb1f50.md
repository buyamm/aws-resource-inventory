# AWS Resource: `aws_security_group` - `sg-e4a0ee2dde2bb1f50`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-e4a0ee2dde2bb1f50 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T02:05:49Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Public HTTPS         |
| GroupId           | sg-e4a0ee2dde2bb1f50 |
| GroupName         | storefront-alb-sg    |
| OwnerId           | 123456789012         |
| VpcId             | vpc-660d36ef         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | ---------------- |
| 443      | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 443    | []               |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Securitygrouprules

| CidrIpv4  | FromPort | GroupId              | GroupOwnerId | IpProtocol | IsEgress | SecurityGroupRuleId   | Tags | ToPort |
| --------- | -------- | -------------------- | ------------ | ---------- | -------- | --------------------- | ---- | ------ |
| 0.0.0.0/0 | -1       | sg-e4a0ee2dde2bb1f50 | 123456789012 | -1         | True     | sgr-c8fd2df3255a5027a | []   | -1     |
| 0.0.0.0/0 | 443      | sg-e4a0ee2dde2bb1f50 | 123456789012 | tcp        | False    | sgr-f9fbc468403bc6198 | []   | 443    |


### Tags

```json
[]
```

