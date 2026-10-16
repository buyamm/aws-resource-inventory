# AWS Resource: `aws_iam_role` - `storefront-exec-role`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_iam_role                                        |
| ARN               | arn:aws:iam::123456789012:role/storefront-exec-role |
| Region            | global                                              |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-16T02:30:23Z                                |
| Collector Version | 0.1.0                                               |


## Configuration Specifications

| Configuration Key  | Value                                               |
| ------------------ | --------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-exec-role |
| CreateDate         | 2026-10-16T02:30:22.712000+00:00                    |
| MaxSessionDuration | 3600                                                |
| Path               | /                                                   |
| RoleId             | AROARZPUZDIKLG5TZD65B                               |
| RoleName           | storefront-exec-role                                |


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

| PolicyArn                                                             | PolicyName                       |
| --------------------------------------------------------------------- | -------------------------------- |
| arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy | AmazonECSTaskExecutionRolePolicy |


### Inlinepolicies

```json
{}
```


### Rolelastused

```json
{}
```

