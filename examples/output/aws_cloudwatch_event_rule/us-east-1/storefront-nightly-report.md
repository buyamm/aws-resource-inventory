# AWS Resource: `aws_cloudwatch_event_rule` - `storefront-nightly-report`

## Overview

| Property          | Value                                                                |
| ----------------- | -------------------------------------------------------------------- |
| Resource Type     | aws_cloudwatch_event_rule                                            |
| ARN               | arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report |
| Region            | us-east-1                                                            |
| Account ID        | 123456789012                                                         |
| Collected At      | 2026-10-16T01:29:14Z                                                 |
| Collector Version | 0.1.0                                                                |


## Configuration Specifications

| Configuration Key  | Value                                                                |
| ------------------ | -------------------------------------------------------------------- |
| Arn                | arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report |
| CreatedBy          | 123456789012                                                         |
| Description        | Nightly order report                                                 |
| EventBusName       | default                                                              |
| Name               | storefront-nightly-report                                            |
| ScheduleExpression | cron(0 2 * * ? *)                                                    |
| State              | ENABLED                                                              |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Targets

| Arn                                                            | Id              |
| -------------------------------------------------------------- | --------------- |
| arn:aws:lambda:us-east-1:123456789012:function:order-processor | order-processor |

