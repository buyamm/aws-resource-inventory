# AWS Resource: `aws_ecs_service` - `storefront_web`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_ecs_service                                           |
| ARN               | arn:aws:ecs:us-east-1:123456789012:service/storefront/web |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-16T02:05:49Z                                      |
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
| 2026-10-16T09:05:48.701159+07:00 | 2            | ecs-svc/973443177218465221 | FARGATE    | 2            | 0            | PRIMARY | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1 | 2026-10-16T09:05:48.701164+07:00 |


### Loadbalancers

| containerName | containerPort | targetGroupArn                                                                                 |
| ------------- | ------------- | ---------------------------------------------------------------------------------------------- |
| web           | 80            | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188 |


### Networkconfiguration

```json
{
  "awsvpcConfiguration": {
    "assignPublicIp": "DISABLED",
    "securityGroups": [
      "sg-12874fb82c9db66ed"
    ],
    "subnets": [
      "subnet-4d897e3d"
    ]
  }
}
```


### Serviceregistries

```json
[]
```

