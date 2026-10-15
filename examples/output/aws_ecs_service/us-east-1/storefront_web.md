# AWS Resource: `aws_ecs_service` - `storefront_web`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_ecs_service                                           |
| ARN               | arn:aws:ecs:us-east-1:123456789012:service/storefront/web |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-15T16:40:03Z                                      |
| Collector Version | 0.1.0                                                     |


## Configuration Specifications

| Configuration Key  | Value                                                               |
| ------------------ | ------------------------------------------------------------------- |
| clusterArn         | arn:aws:ecs:us-east-1:123456789012:cluster/storefront               |
| desiredCount       | 2                                                                   |
| launchType         | FARGATE                                                             |
| pendingCount       | 2                                                                   |
| runningCount       | 0                                                                   |
| schedulingStrategy | REPLICA                                                             |
| serviceArn         | arn:aws:ecs:us-east-1:123456789012:service/storefront/web           |
| serviceName        | web                                                                 |
| status             | ACTIVE                                                              |
| taskDefinition     | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1 |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Deployments

| createdAt                        | desiredCount | id                         | launchType | pendingCount | runningCount | status  | taskDefinition                                                      | updatedAt                        |
| -------------------------------- | ------------ | -------------------------- | ---------- | ------------ | ------------ | ------- | ------------------------------------------------------------------- | -------------------------------- |
| 2026-10-15T23:40:02.617837+07:00 | 2            | ecs-svc/614225609518633782 | FARGATE    | 2            | 0            | PRIMARY | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1 | 2026-10-15T23:40:02.617843+07:00 |


### Loadbalancers

| containerName | containerPort | targetGroupArn                                                                                 |
| ------------- | ------------- | ---------------------------------------------------------------------------------------------- |
| web           | 80            | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188 |


### Serviceregistries

```json
[]
```

