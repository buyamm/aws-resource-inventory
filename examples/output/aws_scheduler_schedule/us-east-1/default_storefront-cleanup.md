# AWS Resource: `aws_scheduler_schedule` - `default_storefront-cleanup`

## Overview

| Property          | Value                                                                        |
| ----------------- | ---------------------------------------------------------------------------- |
| Resource Type     | aws_scheduler_schedule                                                       |
| ARN               | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup |
| Region            | us-east-1                                                                    |
| Account ID        | 123456789012                                                                 |
| Collected At      | 2026-10-15T16:40:03Z                                                         |
| Collector Version | 0.1.0                                                                        |


## Configuration Specifications

| Configuration Key    | Value                                                                        |
| -------------------- | ---------------------------------------------------------------------------- |
| Arn                  | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup |
| CreationDate         | 2026-10-15T23:40:02.856052+07:00                                             |
| Description          | Hourly cleanup message                                                       |
| GroupName            | default                                                                      |
| LastModificationDate | 2026-10-15T23:40:02.856052+07:00                                             |
| Name                 | storefront-cleanup                                                           |
| ScheduleExpression   | rate(1 hour)                                                                 |
| State                | ENABLED                                                                      |


### Flexibletimewindow

```json
{
  "Mode": "OFF"
}
```


### Target

```json
{
  "Arn": "arn:aws:sqs:us-east-1:123456789012:storefront-orders",
  "Input": "{\"task\": \"cleanup\"}",
  "RetryPolicy": {
    "MaximumEventAgeInSeconds": 86400,
    "MaximumRetryAttempts": 185
  },
  "RoleArn": "arn:aws:iam::123456789012:role/storefront-scheduler-role"
}
```

