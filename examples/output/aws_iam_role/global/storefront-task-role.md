# AWS Resource: `aws_iam_role` - `storefront-task-role`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_iam_role                                        |
| ARN               | arn:aws:iam::123456789012:role/storefront-task-role |
| Region            | global                                              |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-16T02:05:49Z                                |
| Collector Version | 0.1.0                                               |


## Configuration Specifications

| Configuration Key  | Value                                               |
| ------------------ | --------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-task-role |
| CreateDate         | 2026-10-16T02:05:48.669000+00:00                    |
| MaxSessionDuration | 3600                                                |
| Path               | /                                                   |
| RoleId             | AROARZPUZDIKKIKVH42PU                               |
| RoleName           | storefront-task-role                                |


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
        "Service": "ecs-tasks.amazonaws.com"
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

