# AWS Resource: `aws_security_group` - `sg-eaaa2c57ac5ecc98e`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-eaaa2c57ac5ecc98e |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-15T16:40:03Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | Storefront tasks and cache |
| GroupId           | sg-eaaa2c57ac5ecc98e       |
| GroupName         | storefront-app-sg          |
| OwnerId           | 123456789012               |
| VpcId             | vpc-b6ee287f               |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-app |
| service | storefront     |


### Ippermissions

| FromPort | IpProtocol | IpRanges | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs                                                |
| -------- | ---------- | -------- | ---------- | ------------- | ------ | --------------------------------------------------------------- |
| 80       | tcp        | []       | []         | []            | 80     | [{'UserId': '123456789012', 'GroupId': 'sg-8c9c7f5f96b0d5fb1'}] |
| 6379     | tcp        | []       | []         | []            | 6379   | [{'UserId': '123456789012', 'GroupId': 'sg-eaaa2c57ac5ecc98e'}] |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |

