# AWS Resource: `aws_security_group` - `sg-2edfb301c8a045aa8`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-2edfb301c8a045aa8 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T01:29:14Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Web tier             |
| GroupId           | sg-2edfb301c8a045aa8 |
| GroupName         | orders-web-sg        |
| OwnerId           | 123456789012         |
| VpcId             | vpc-7c4f2f1d         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs                                                |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | --------------------------------------------------------------- |
| 22       | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 22     | []                                                              |
| 5432     | tcp        | []                        | []         | []            | 5432   | [{'UserId': '123456789012', 'GroupId': 'sg-7c3a665620cbf02dc'}] |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Tags

```json
[]
```

