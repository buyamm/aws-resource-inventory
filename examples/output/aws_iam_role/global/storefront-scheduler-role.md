# AWS Resource: `aws_iam_role` - `storefront-scheduler-role`

## Overview

| Property          | Value                                                    |
| ----------------- | -------------------------------------------------------- |
| Resource Type     | aws_iam_role                                             |
| ARN               | arn:aws:iam::123456789012:role/storefront-scheduler-role |
| Region            | global                                                   |
| Account ID        | 123456789012                                             |
| Collected At      | 2026-10-15T16:40:03Z                                     |
| Collector Version | 0.1.0                                                    |


## Configuration Specifications

| Configuration Key  | Value                                                    |
| ------------------ | -------------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-scheduler-role |
| CreateDate         | 2026-10-15T16:40:02.594000+00:00                         |
| MaxSessionDuration | 3600                                                     |
| Path               | /                                                        |
| RoleId             | AROARZPUZDIKBTYRPCPMR                                    |
| RoleName           | storefront-scheduler-role                                |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Assumerolepolicydocument

```json
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "scheduler.amazonaws.com"
      }
    }
  ],
  "Version": "2012-10-17"
}
```


### Attachedpolicies

```json
[]
```


### Inlinepolicies

```json
{}
```


### Rolelastused

```json
{}
```

