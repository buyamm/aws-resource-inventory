# AWS Resource: `aws_security_group` - `sg-fb454a9efcd634f32`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-fb454a9efcd634f32 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-15T16:40:03Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Web tier             |
| GroupId           | sg-fb454a9efcd634f32 |
| GroupName         | orders-web-sg        |
| OwnerId           | 123456789012         |
| VpcId             | vpc-b6ee287f         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | ---------------- |
| 22       | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 22     | []               |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Tags

```json
[]
```

