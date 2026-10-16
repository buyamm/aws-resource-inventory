# AWS Resource: `aws_autoscaling_group` - `storefront-workers`

## Overview

| Property          | Value                                                                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_autoscaling_group                                                                                                                    |
| ARN               | arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers |
| Region            | us-east-1                                                                                                                                |
| Account ID        | 123456789012                                                                                                                             |
| Collected At      | 2026-10-16T02:05:49Z                                                                                                                     |
| Collector Version | 0.1.0                                                                                                                                    |


## Configuration Specifications

| Configuration Key                | Value                                                                                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| AutoScalingGroupARN              | arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers |
| AutoScalingGroupName             | storefront-workers                                                                                                                       |
| CapacityRebalance                | False                                                                                                                                    |
| CreatedTime                      | 2013-05-06T17:47:15.107000+00:00                                                                                                         |
| DefaultCooldown                  | 300                                                                                                                                      |
| DesiredCapacity                  | 1                                                                                                                                        |
| HealthCheckGracePeriod           | 300                                                                                                                                      |
| HealthCheckType                  | EC2                                                                                                                                      |
| MaxSize                          | 2                                                                                                                                        |
| MinSize                          | 1                                                                                                                                        |
| NewInstancesProtectedFromScaleIn | False                                                                                                                                    |
| ServiceLinkedRoleARN             | arn:aws:iam::123456789012:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling                                   |
| VPCZoneIdentifier                | subnet-4d897e3d                                                                                                                          |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Availabilityzones

```json
[
  "us-east-1a"
]
```


### Instances

| AvailabilityZone | HealthStatus | InstanceId          | InstanceType | LaunchTemplate                                                                                                 | LifecycleState | ProtectedFromScaleIn |
| ---------------- | ------------ | ------------------- | ------------ | -------------------------------------------------------------------------------------------------------------- | -------------- | -------------------- |
| us-east-1a       | Healthy      | i-b892b745a8c407b02 | t3.small     | {'LaunchTemplateId': 'lt-bad06a08aee200bf2', 'LaunchTemplateName': 'storefront-worker', 'Version': '$Default'} | InService      | False                |


### Launchtemplate

```json
{
  "LaunchTemplateId": "lt-bad06a08aee200bf2",
  "LaunchTemplateName": "storefront-worker",
  "Version": "$Default"
}
```


### Loadbalancernames

```json
[]
```


### Suspendedprocesses

```json
[]
```


### Targetgrouparns

```json
[]
```


### Terminationpolicies

```json
[
  "Default"
]
```

