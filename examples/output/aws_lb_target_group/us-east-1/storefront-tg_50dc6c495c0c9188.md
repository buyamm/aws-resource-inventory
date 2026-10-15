# AWS Resource: `aws_lb_target_group` - `storefront-tg_50dc6c495c0c9188`

## Overview

| Property          | Value                                                                                          |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| Resource Type     | aws_lb_target_group                                                                            |
| ARN               | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188 |
| Region            | us-east-1                                                                                      |
| Account ID        | 123456789012                                                                                   |
| Collected At      | 2026-10-15T16:40:03Z                                                                           |
| Collector Version | 0.1.0                                                                                          |


## Configuration Specifications

| Configuration Key          | Value                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------- |
| HealthCheckEnabled         | True                                                                                           |
| HealthCheckIntervalSeconds | 30                                                                                             |
| HealthCheckPath            | /health                                                                                        |
| HealthCheckPort            | traffic-port                                                                                   |
| HealthCheckProtocol        | HTTP                                                                                           |
| HealthCheckTimeoutSeconds  | 5                                                                                              |
| HealthyThresholdCount      | 5                                                                                              |
| IpAddressType              | ipv4                                                                                           |
| Port                       | 80                                                                                             |
| Protocol                   | HTTP                                                                                           |
| ProtocolVersion            | HTTP1                                                                                          |
| TargetGroupArn             | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188 |
| TargetGroupName            | storefront-tg                                                                                  |
| TargetType                 | ip                                                                                             |
| UnhealthyThresholdCount    | 2                                                                                              |
| VpcId                      | vpc-b6ee287f                                                                                   |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Attributes

| Key                                  | Value                           |
| ------------------------------------ | ------------------------------- |
| deregistration_delay.timeout_seconds | 300                             |
| stickiness.enabled                   | false                           |
| load_balancing.algorithm.type        | round_robin                     |
| load_balancing.cross_zone.enabled    | use_load_balancer_configuration |
| slow_start.duration_seconds          | 0                               |
| waf.fail_open.enabled                | false                           |
| stickiness.type                      | lb_cookie                       |


### Loadbalancerarns

```json
[
  "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188"
]
```


### Matcher

```json
{
  "HttpCode": "200"
}
```

