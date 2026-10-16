# AWS Resource: `aws_ecs_task_definition` - `storefront-web_1`

## Overview

| Property          | Value                                                               |
| ----------------- | ------------------------------------------------------------------- |
| Resource Type     | aws_ecs_task_definition                                             |
| ARN               | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1 |
| Region            | us-east-1                                                           |
| Account ID        | 123456789012                                                        |
| Collected At      | 2026-10-16T02:30:23Z                                                |
| Collector Version | 0.1.0                                                               |


## Configuration Specifications

| Configuration Key | Value                                                               |
| ----------------- | ------------------------------------------------------------------- |
| cpu               | 256                                                                 |
| executionRoleArn  | arn:aws:iam::123456789012:role/storefront-exec-role                 |
| family            | storefront-web                                                      |
| memory            | 512                                                                 |
| networkMode       | awsvpc                                                              |
| revision          | 1                                                                   |
| status            | ACTIVE                                                              |
| taskDefinitionArn | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1 |
| taskRoleArn       | arn:aws:iam::123456789012:role/storefront-task-role                 |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Compatibilities

```json
[
  "EC2",
  "FARGATE"
]
```


### Containerdefinitions

| cpu | environment                                                                                              | essential | image                                                             | logConfiguration                                                                                                                             | mountPoints | name | portMappings                               | volumesFrom |
| --- | -------------------------------------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ---- | ------------------------------------------ | ----------- |
| 0   | [{'name': 'CACHE_HOST', 'value': 'storefront-cache'}, {'name': 'SESSION_SECRET', 'value': '[REDACTED]'}] | True      | 123456789012.dkr.ecr.us-east-1.amazonaws.com/storefront-web:1.4.2 | {'logDriver': 'awslogs', 'options': {'awslogs-group': '/ecs/storefront-web', 'awslogs-region': 'us-east-1', 'awslogs-stream-prefix': 'web'}} | []          | web  | [{'containerPort': 80, 'protocol': 'tcp'}] | []          |


### Placementconstraints

```json
[]
```


### Requirescompatibilities

```json
[
  "FARGATE"
]
```


### Volumes

```json
[]
```

