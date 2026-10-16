# AWS Resource: `aws_lb` - `app_storefront-alb_50dc6c495c0c9188`

## Overview

| Property          | Value                                                                                                |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_lb                                                                                               |
| ARN               | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188 |
| Region            | us-east-1                                                                                            |
| Account ID        | 123456789012                                                                                         |
| Collected At      | 2026-10-16T02:05:49Z                                                                                 |
| Collector Version | 0.1.0                                                                                                |


## Configuration Specifications

| Configuration Key     | Value                                                                                                |
| --------------------- | ---------------------------------------------------------------------------------------------------- |
| CanonicalHostedZoneId | Z2P70J7EXAMPLE                                                                                       |
| CreatedTime           | 2026-10-16T02:05:48.575000+00:00                                                                     |
| DNSName               | storefront-alb-1.us-east-1.elb.amazonaws.com                                                         |
| IpAddressType         | ipv4                                                                                                 |
| LoadBalancerArn       | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188 |
| LoadBalancerName      | storefront-alb                                                                                       |
| Scheme                | internet-facing                                                                                      |
| Type                  | application                                                                                          |
| VpcId                 | vpc-660d36ef                                                                                         |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Attributes

| Key                               | Value |
| --------------------------------- | ----- |
| access_logs.s3.bucket             |       |
| access_logs.s3.prefix             |       |
| deletion_protection.enabled       | false |
| load_balancing.cross_zone.enabled | false |


### Availabilityzones

| SubnetId        | ZoneName   |
| --------------- | ---------- |
| subnet-2cf4f53a | us-east-1a |
| subnet-4db17d3d | us-east-1b |


### Listeners

| AlpnPolicy | Certificates                                                                                                | DefaultActions                                                                                                                            | ListenerArn                                                                                                    | LoadBalancerArn                                                                                      | Port | Protocol | SslPolicy                 |
| ---------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---- | -------- | ------------------------- |
| []         | [{'CertificateArn': 'arn:aws:acm:us-east-1:123456789012:certificate/a2f4311b-2bbd-4ca0-97e7-018106634454'}] | [{'Type': 'forward', 'TargetGroupArn': 'arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188'}] | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232 | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188 | 443  | HTTPS    | ELBSecurityPolicy-2016-08 |


### Securitygroups

```json
[
  "sg-e4a0ee2dde2bb1f50"
]
```


### State

```json
{
  "Code": "active"
}
```

