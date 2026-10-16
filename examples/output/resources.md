# AWS Infrastructure Resource Inventory

**Generated:** 2026-10-16T02:05:50.043955Z  
**Total Resources Discovered:** 47

## Summary by Resource Type

| Resource Type                     | Count |
| --------------------------------- | ----- |
| aws_acm_certificate               | 1     |
| aws_autoscaling_group             | 1     |
| aws_cloudfront_distribution       | 1     |
| aws_cloudwatch_event_rule         | 1     |
| aws_cloudwatch_log_group          | 2     |
| aws_db_instance                   | 1     |
| aws_dynamodb_table                | 1     |
| aws_ecr_repository                | 1     |
| aws_ecs_cluster                   | 1     |
| aws_ecs_service                   | 1     |
| aws_ecs_task_definition           | 1     |
| aws_elasticache_replication_group | 1     |
| aws_iam_role                      | 5     |
| aws_instance                      | 2     |
| aws_internet_gateway              | 1     |
| aws_lambda_function               | 1     |
| aws_launch_template               | 1     |
| aws_lb                            | 1     |
| aws_lb_listener                   | 1     |
| aws_lb_target_group               | 1     |
| aws_nat_gateway                   | 1     |
| aws_route53_zone                  | 1     |
| aws_route_table                   | 3     |
| aws_s3_bucket                     | 2     |
| aws_scheduler_schedule            | 1     |
| aws_security_group                | 4     |
| aws_sfn_state_machine             | 1     |
| aws_sns_topic                     | 1     |
| aws_sqs_queue                     | 1     |
| aws_subnet                        | 3     |
| aws_vpc                           | 1     |
| aws_vpc_endpoint                  | 1     |
| aws_wafv2_web_acl                 | 1     |


## Regional Distribution

| Region    | Resource Count |
| --------- | -------------- |
| global    | 10             |
| us-east-1 | 37             |


## Discovered Resources List

| Resource Type                     | Identifier                                          | Region    | ARN                                                                                                                                      |
| --------------------------------- | --------------------------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| aws_instance                      | i-5e2db2f538089c39d                                 | us-east-1 | arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d                                                                          |
| aws_instance                      | i-b892b745a8c407b02                                 | us-east-1 | arn:aws:ec2:us-east-1:123456789012:instance/i-b892b745a8c407b02                                                                          |
| aws_vpc                           | vpc-660d36ef                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef                                                                                      |
| aws_security_group                | sg-156a39ed25de235cf                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-156a39ed25de235cf                                                                   |
| aws_security_group                | sg-2bf145296ea5159ab                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-2bf145296ea5159ab                                                                   |
| aws_security_group                | sg-e4a0ee2dde2bb1f50                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-e4a0ee2dde2bb1f50                                                                   |
| aws_security_group                | sg-12874fb82c9db66ed                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-12874fb82c9db66ed                                                                   |
| aws_lambda_function               | order-processor                                     | us-east-1 | arn:aws:lambda:us-east-1:123456789012:function:order-processor                                                                           |
| aws_db_instance                   | orders-db                                           | us-east-1 | arn:aws:rds:us-east-1:123456789012:db:orders-db                                                                                          |
| aws_cloudwatch_log_group          | aws_lambda_order-processor                          | us-east-1 | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor                                                                |
| aws_cloudwatch_log_group          | ecs_storefront-web                                  | us-east-1 | arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web                                                                        |
| aws_sfn_state_machine             | order-flow                                          | us-east-1 | arn:aws:states:us-east-1:123456789012:stateMachine:order-flow                                                                            |
| aws_dynamodb_table                | orders                                              | us-east-1 | arn:aws:dynamodb:us-east-1:123456789012:table/orders                                                                                     |
| aws_subnet                        | subnet-4d897e3d                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d                                                                                |
| aws_subnet                        | subnet-2cf4f53a                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a                                                                                |
| aws_subnet                        | subnet-4db17d3d                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4db17d3d                                                                                |
| aws_route_table                   | rtb-561c82c8                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-561c82c8                                                                              |
| aws_route_table                   | rtb-bf60be68                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68                                                                              |
| aws_route_table                   | rtb-e28b5541                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-e28b5541                                                                              |
| aws_internet_gateway              | igw-d045f4ab                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-d045f4ab                                                                         |
| aws_nat_gateway                   | nat-af9f73b40a8a4af4f                               | us-east-1 | arn:aws:ec2:us-east-1:123456789012:natgateway/nat-af9f73b40a8a4af4f                                                                      |
| aws_vpc_endpoint                  | vpce-40eb00b6                                       | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-40eb00b6                                                                            |
| aws_lb                            | app_storefront-alb_50dc6c495c0c9188                 | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188                                     |
| aws_lb_target_group               | storefront-tg_50dc6c495c0c9188                      | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188                                           |
| aws_acm_certificate               | a2f4311b-2bbd-4ca0-97e7-018106634454                | us-east-1 | arn:aws:acm:us-east-1:123456789012:certificate/a2f4311b-2bbd-4ca0-97e7-018106634454                                                      |
| aws_ecs_cluster                   | storefront                                          | us-east-1 | arn:aws:ecs:us-east-1:123456789012:cluster/storefront                                                                                    |
| aws_ecr_repository                | storefront-web                                      | us-east-1 | arn:aws:ecr:us-east-1:123456789012:repository/storefront-web                                                                             |
| aws_autoscaling_group             | storefront-workers                                  | us-east-1 | arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers |
| aws_launch_template               | lt-bad06a08aee200bf2                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:launch-template/lt-bad06a08aee200bf2                                                                  |
| aws_elasticache_replication_group | storefront-cache                                    | us-east-1 | arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache                                                             |
| aws_sqs_queue                     | storefront-orders                                   | us-east-1 | arn:aws:sqs:us-east-1:123456789012:storefront-orders                                                                                     |
| aws_sns_topic                     | storefront-events                                   | us-east-1 | arn:aws:sns:us-east-1:123456789012:storefront-events                                                                                     |
| aws_scheduler_schedule            | default_storefront-cleanup                          | us-east-1 | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup                                                             |
| aws_lb_listener                   | app_storefront-alb_50dc6c495c0c9188_4434501777232   | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232                           |
| aws_ecs_service                   | storefront_web                                      | us-east-1 | arn:aws:ecs:us-east-1:123456789012:service/storefront/web                                                                                |
| aws_ecs_task_definition           | storefront-web_1                                    | us-east-1 | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1                                                                      |
| aws_cloudwatch_event_rule         | storefront-nightly-report                           | us-east-1 | arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report                                                                     |
| aws_s3_bucket                     | orders-public-assets                                | global    | arn:aws:s3:::orders-public-assets                                                                                                        |
| aws_s3_bucket                     | storefront-static                                   | global    | arn:aws:s3:::storefront-static                                                                                                           |
| aws_iam_role                      | orders-app-role                                     | global    | arn:aws:iam::123456789012:role/orders-app-role                                                                                           |
| aws_iam_role                      | storefront-scheduler-role                           | global    | arn:aws:iam::123456789012:role/storefront-scheduler-role                                                                                 |
| aws_iam_role                      | storefront-task-role                                | global    | arn:aws:iam::123456789012:role/storefront-task-role                                                                                      |
| aws_iam_role                      | storefront-exec-role                                | global    | arn:aws:iam::123456789012:role/storefront-exec-role                                                                                      |
| aws_iam_role                      | order-lambda-role                                   | global    | arn:aws:iam::123456789012:role/order-lambda-role                                                                                         |
| aws_cloudfront_distribution       | X5E0C4JHPHC9C                                       | global    | arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C                                                                              |
| aws_route53_zone                  | ACA19C6IIUY2GFZ                                     | global    | arn:aws:route53:::hostedzone/ACA19C6IIUY2GFZ                                                                                             |
| aws_wafv2_web_acl                 | storefront-waf_d06f4b4d-1ec6-42a4-81fa-1582637eb32d | global    | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/d06f4b4d-1ec6-42a4-81fa-1582637eb32d                                      |


## Detailed Resource Specifications

# AWS Resource: `aws_instance` - `i-5e2db2f538089c39d`

## Overview

| Property          | Value                                                           |
| ----------------- | --------------------------------------------------------------- |
| Resource Type     | aws_instance                                                    |
| ARN               | arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d |
| Region            | us-east-1                                                       |
| Account ID        | 123456789012                                                    |
| Collected At      | 2026-10-16T02:05:49Z                                            |
| Collector Version | 0.1.0                                                           |


## Configuration Specifications

| Configuration Key     | Value                     |
| --------------------- | ------------------------- |
| AmiLaunchIndex        | 0                         |
| Architecture          | x86_64                    |
| ClientToken           | [REDACTED]                |
| EbsOptimized          | False                     |
| Hypervisor            | xen                       |
| ImageId               | ami-12c6146b              |
| InstanceId            | i-5e2db2f538089c39d       |
| InstanceType          | t3.micro                  |
| KernelId              | None                      |
| LaunchTime            | 2026-10-16T02:05:48+00:00 |
| Platform              | windows                   |
| PrivateDnsName        | ip-10-0-1-4.ec2.internal  |
| PrivateIpAddress      | 10.0.1.4                  |
| PublicDnsName         | None                      |
| RootDeviceName        | /dev/sda1                 |
| RootDeviceType        | ebs                       |
| SourceDestCheck       | True                      |
| StateTransitionReason |                           |
| SubnetId              | subnet-4d897e3d           |
| VirtualizationType    | hvm                       |
| VpcId                 | vpc-660d36ef              |


## Resource Tags

| Tag Key | Tag Value    |
| ------- | ------------ |
| Name    | orders-web-1 |


### Blockdevicemappings

| DeviceName | Ebs                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| /dev/sda1  | {'AttachTime': '2026-10-16T02:05:48+00:00', 'DeleteOnTermination': True, 'Status': 'in-use', 'VolumeId': 'vol-dc2a6394'} |


### Iaminstanceprofile

```json
{
  "Arn": "arn:aws:iam::123456789012:instance-profile/orders-app-role",
  "Id": "iip-assoc-4f99f1d4"
}
```


### Monitoring

```json
{
  "State": "disabled"
}
```


### Networkinterfaces

| Attachment                                                                                                                                              | Description               | Groups                                                              | MacAddress        | NetworkInterfaceId | OwnerId      | PrivateIpAddress | PrivateIpAddresses                                  | SourceDestCheck | Status | SubnetId        | VpcId        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------------- | ----------------- | ------------------ | ------------ | ---------------- | --------------------------------------------------- | --------------- | ------ | --------------- | ------------ |
| {'AttachTime': '2015-01-01T00:00:00+00:00', 'AttachmentId': 'eni-attach-14e5c732', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'} | Primary network interface | [{'GroupId': 'sg-2bf145296ea5159ab', 'GroupName': 'orders-web-sg'}] | 1b:2b:3c:4d:5e:6f | eni-02024ebc       | 123456789012 | 10.0.1.4         | [{'Primary': True, 'PrivateIpAddress': '10.0.1.4'}] | True            | in-use | subnet-4d897e3d | vpc-660d36ef |


### Placement

```json
{
  "AvailabilityZone": "us-east-1a",
  "GroupName": "",
  "Tenancy": "default"
}
```


### Securitygroups

| GroupId              | GroupName     |
| -------------------- | ------------- |
| sg-2bf145296ea5159ab | orders-web-sg |


### State

```json
{
  "Code": 16,
  "Name": "running"
}
```


### Statereason

```json
{
  "Code": "",
  "Message": ""
}
```



---

# AWS Resource: `aws_instance` - `i-b892b745a8c407b02`

## Overview

| Property          | Value                                                           |
| ----------------- | --------------------------------------------------------------- |
| Resource Type     | aws_instance                                                    |
| ARN               | arn:aws:ec2:us-east-1:123456789012:instance/i-b892b745a8c407b02 |
| Region            | us-east-1                                                       |
| Account ID        | 123456789012                                                    |
| Collected At      | 2026-10-16T02:05:49Z                                            |
| Collector Version | 0.1.0                                                           |


## Configuration Specifications

| Configuration Key     | Value                     |
| --------------------- | ------------------------- |
| AmiLaunchIndex        | 0                         |
| Architecture          | x86_64                    |
| ClientToken           | [REDACTED]                |
| EbsOptimized          | False                     |
| Hypervisor            | xen                       |
| ImageId               | ami-12c6146b              |
| InstanceId            | i-b892b745a8c407b02       |
| InstanceType          | t3.small                  |
| KernelId              | None                      |
| LaunchTime            | 2026-10-16T02:05:48+00:00 |
| Platform              | windows                   |
| PrivateDnsName        | ip-10-0-1-5.ec2.internal  |
| PrivateIpAddress      | 10.0.1.5                  |
| PublicDnsName         | None                      |
| RootDeviceName        | /dev/sda1                 |
| RootDeviceType        | ebs                       |
| SourceDestCheck       | True                      |
| StateTransitionReason |                           |
| SubnetId              | subnet-4d897e3d           |
| VirtualizationType    | hvm                       |
| VpcId                 | vpc-660d36ef              |


## Resource Tags

| Tag Key                   | Tag Value          |
| ------------------------- | ------------------ |
| aws:autoscaling:groupName | storefront-workers |
| service                   | storefront         |


### Blockdevicemappings

| DeviceName | Ebs                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| /dev/sda1  | {'AttachTime': '2026-10-16T02:05:48+00:00', 'DeleteOnTermination': True, 'Status': 'in-use', 'VolumeId': 'vol-c93f30ac'} |


### Monitoring

```json
{
  "State": "disabled"
}
```


### Networkinterfaces

| Attachment                                                                                                                                              | Description               | Groups                                                        | MacAddress        | NetworkInterfaceId | OwnerId      | PrivateIpAddress | PrivateIpAddresses                                  | SourceDestCheck | Status | SubnetId        | VpcId        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------- | ----------------- | ------------------ | ------------ | ---------------- | --------------------------------------------------- | --------------- | ------ | --------------- | ------------ |
| {'AttachTime': '2015-01-01T00:00:00+00:00', 'AttachmentId': 'eni-attach-f1cf0b7b', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'} | Primary network interface | [{'GroupId': 'sg-156a39ed25de235cf', 'GroupName': 'default'}] | 1b:2b:3c:4d:5e:6f | eni-91e0e6e4       | 123456789012 | 10.0.1.5         | [{'Primary': True, 'PrivateIpAddress': '10.0.1.5'}] | True            | in-use | subnet-4d897e3d | vpc-660d36ef |


### Placement

```json
{
  "AvailabilityZone": "us-east-1a",
  "GroupName": "",
  "Tenancy": "default"
}
```


### Securitygroups

```json
[]
```


### State

```json
{
  "Code": 16,
  "Name": "running"
}
```


### Statereason

```json
{
  "Code": "",
  "Message": ""
}
```



---

# AWS Resource: `aws_vpc` - `vpc-660d36ef`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_vpc                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef |
| Region            | us-east-1                                           |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-16T02:05:49Z                                |
| Collector Version | 0.1.0                                               |


## Configuration Specifications

| Configuration Key  | Value        |
| ------------------ | ------------ |
| CidrBlock          | 10.0.0.0/16  |
| DhcpOptionsId      | default      |
| EnableDnsHostnames | False        |
| EnableDnsSupport   | True         |
| InstanceTenancy    | default      |
| IsDefault          | False        |
| OwnerId            | 123456789012 |
| State              | available    |
| VpcId              | vpc-660d36ef |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| Name    | orders-vpc |


### Cidrblockassociationset

| AssociationId           | CidrBlock   | CidrBlockState          |
| ----------------------- | ----------- | ----------------------- |
| vpc-cidr-assoc-6d76e342 | 10.0.0.0/16 | {'State': 'associated'} |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-156a39ed25de235cf`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-156a39ed25de235cf |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T02:05:49Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | default VPC security group |
| GroupId           | sg-156a39ed25de235cf       |
| GroupName         | default                    |
| OwnerId           | 123456789012               |
| VpcId             | vpc-660d36ef               |


### Ippermissions

```json
[]
```


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Securitygrouprules

| CidrIpv4  | FromPort | GroupId              | GroupOwnerId | IpProtocol | IsEgress | SecurityGroupRuleId   | Tags | ToPort |
| --------- | -------- | -------------------- | ------------ | ---------- | -------- | --------------------- | ---- | ------ |
| 0.0.0.0/0 | -1       | sg-156a39ed25de235cf | 123456789012 | -1         | True     | sgr-9b10765766bf92534 | []   | -1     |


### Tags

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-2bf145296ea5159ab`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-2bf145296ea5159ab |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T02:05:49Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Web tier             |
| GroupId           | sg-2bf145296ea5159ab |
| GroupName         | orders-web-sg        |
| OwnerId           | 123456789012         |
| VpcId             | vpc-660d36ef         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs                                                |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | --------------------------------------------------------------- |
| 22       | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 22     | []                                                              |
| 5432     | tcp        | []                        | []         | []            | 5432   | [{'UserId': '123456789012', 'GroupId': 'sg-12874fb82c9db66ed'}] |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Securitygrouprules

| CidrIpv4  | FromPort | GroupId              | GroupOwnerId | IpProtocol | IsEgress | ReferencedGroupInfo                                           | SecurityGroupRuleId   | Tags | ToPort |
| --------- | -------- | -------------------- | ------------ | ---------- | -------- | ------------------------------------------------------------- | --------------------- | ---- | ------ |
|           | 5432     | sg-2bf145296ea5159ab | 123456789012 | tcp        | False    | {'GroupId': 'sg-12874fb82c9db66ed', 'UserId': '123456789012'} | sgr-0b71b21c710e9b06f | []   | 5432   |
| 0.0.0.0/0 | 22       | sg-2bf145296ea5159ab | 123456789012 | tcp        | False    |                                                               | sgr-10daa5d732bb0dd4f | []   | 22     |
| 0.0.0.0/0 | -1       | sg-2bf145296ea5159ab | 123456789012 | -1         | True     |                                                               | sgr-83596752ef1fde5e1 | []   | -1     |


### Tags

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-e4a0ee2dde2bb1f50`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-e4a0ee2dde2bb1f50 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T02:05:49Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Public HTTPS         |
| GroupId           | sg-e4a0ee2dde2bb1f50 |
| GroupName         | storefront-alb-sg    |
| OwnerId           | 123456789012         |
| VpcId             | vpc-660d36ef         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | ---------------- |
| 443      | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 443    | []               |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Securitygrouprules

| CidrIpv4  | FromPort | GroupId              | GroupOwnerId | IpProtocol | IsEgress | SecurityGroupRuleId   | Tags | ToPort |
| --------- | -------- | -------------------- | ------------ | ---------- | -------- | --------------------- | ---- | ------ |
| 0.0.0.0/0 | -1       | sg-e4a0ee2dde2bb1f50 | 123456789012 | -1         | True     | sgr-c8fd2df3255a5027a | []   | -1     |
| 0.0.0.0/0 | 443      | sg-e4a0ee2dde2bb1f50 | 123456789012 | tcp        | False    | sgr-f9fbc468403bc6198 | []   | 443    |


### Tags

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-12874fb82c9db66ed`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-12874fb82c9db66ed |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T02:05:49Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | Storefront tasks and cache |
| GroupId           | sg-12874fb82c9db66ed       |
| GroupName         | storefront-app-sg          |
| OwnerId           | 123456789012               |
| VpcId             | vpc-660d36ef               |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-app |
| service | storefront     |


### Ippermissions

| FromPort | IpProtocol | IpRanges | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs                                                |
| -------- | ---------- | -------- | ---------- | ------------- | ------ | --------------------------------------------------------------- |
| 80       | tcp        | []       | []         | []            | 80     | [{'UserId': '123456789012', 'GroupId': 'sg-e4a0ee2dde2bb1f50'}] |
| 6379     | tcp        | []       | []         | []            | 6379   | [{'UserId': '123456789012', 'GroupId': 'sg-12874fb82c9db66ed'}] |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Securitygrouprules

| CidrIpv4  | FromPort | GroupId              | GroupOwnerId | IpProtocol | IsEgress | ReferencedGroupInfo                                           | SecurityGroupRuleId   | Tags | ToPort |
| --------- | -------- | -------------------- | ------------ | ---------- | -------- | ------------------------------------------------------------- | --------------------- | ---- | ------ |
| 0.0.0.0/0 | -1       | sg-12874fb82c9db66ed | 123456789012 | -1         | True     |                                                               | sgr-b954df3a54b41ff12 | []   | -1     |
|           | 80       | sg-12874fb82c9db66ed | 123456789012 | tcp        | False    | {'GroupId': 'sg-e4a0ee2dde2bb1f50', 'UserId': '123456789012'} | sgr-d9900cda6419d64e8 | []   | 80     |
|           | 6379     | sg-12874fb82c9db66ed | 123456789012 | tcp        | False    | {'GroupId': 'sg-12874fb82c9db66ed', 'UserId': '123456789012'} | sgr-ebb5cd8ffaaf837d6 | []   | 6379   |



---

# AWS Resource: `aws_lambda_function` - `order-processor`

## Overview

| Property          | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| Resource Type     | aws_lambda_function                                            |
| ARN               | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| Region            | us-east-1                                                      |
| Account ID        | 123456789012                                                   |
| Collected At      | 2026-10-16T02:05:49Z                                           |
| Collector Version | 0.1.0                                                          |


## Configuration Specifications

| Configuration Key | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| CodeSha256        | 7lkn8531C+XxS7wd8KVRAtABr9F1HQuS88AF7iSN4PE=                   |
| CodeSize          | 164                                                            |
| Description       |                                                                |
| FunctionArn       | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| FunctionName      | order-processor                                                |
| Handler           | handler.handler                                                |
| LastModified      | 2026-10-16T02:05:48.237161000Z                                 |
| LastUpdateStatus  | Successful                                                     |
| MemorySize        | 256                                                            |
| PackageType       | Zip                                                            |
| Role              | arn:aws:iam::123456789012:role/order-lambda-role               |
| Runtime           | python3.11                                                     |
| State             | Active                                                         |
| Timeout           | 30                                                             |
| Version           | $LATEST                                                        |


## Resource Tags

| Tag Key | Tag Value |
| ------- | --------- |
| team    | orders    |


### Architectures

```json
[
  "x86_64"
]
```


### Environment

```json
{
  "Variables": {
    "DB_PASSWORD": "[REDACTED]",
    "TABLE_NAME": "orders"
  }
}
```


### Ephemeralstorage

```json
{
  "Size": 512
}
```


### Layers

```json
[]
```


### Snapstart

```json
{
  "ApplyOn": "None",
  "OptimizationStatus": "Off"
}
```


### Tracingconfig

```json
{
  "Mode": "PassThrough"
}
```


### Vpcconfig

```json
{
  "SecurityGroupIds": [],
  "SubnetIds": []
}
```



---

# AWS Resource: `aws_db_instance` - `orders-db`

## Overview

| Property          | Value                                           |
| ----------------- | ----------------------------------------------- |
| Resource Type     | aws_db_instance                                 |
| ARN               | arn:aws:rds:us-east-1:123456789012:db:orders-db |
| Region            | us-east-1                                       |
| Account ID        | 123456789012                                    |
| Collected At      | 2026-10-16T02:05:49Z                            |
| Collector Version | 0.1.0                                           |


## Configuration Specifications

| Configuration Key                | Value                                           |
| -------------------------------- | ----------------------------------------------- |
| AllocatedStorage                 | 20                                              |
| AutoMinorVersionUpgrade          | False                                           |
| AvailabilityZone                 | us-east-1a                                      |
| BackupRetentionPeriod            | 1                                               |
| CopyTagsToSnapshot               | False                                           |
| DBInstanceArn                    | arn:aws:rds:us-east-1:123456789012:db:orders-db |
| DBInstanceClass                  | db.t3.micro                                     |
| DBInstanceIdentifier             | orders-db                                       |
| DBInstanceStatus                 | available                                       |
| DbInstancePort                   | 5432                                            |
| DbiResourceId                    | db-M5ENSHXFPU6XHZ4G4ZEI5QIO2U                   |
| DeletionProtection               | False                                           |
| Engine                           | postgres                                        |
| EngineVersion                    | 9.3.3                                           |
| IAMDatabaseAuthenticationEnabled | False                                           |
| InstanceCreateTime               | 2026-10-16T02:05:48.380000+00:00                |
| LicenseModel                     | None                                            |
| MasterUsername                   | orders_admin                                    |
| MultiAZ                          | False                                           |
| PreferredBackupWindow            | 13:14-13:44                                     |
| PreferredMaintenanceWindow       | wed:06:38-wed:07:08                             |
| PubliclyAccessible               | False                                           |
| StorageEncrypted                 | False                                           |
| StorageType                      | gp2                                             |


### Dbparametergroups

| DBParameterGroupName | ParameterApplyStatus |
| -------------------- | -------------------- |
| default.postgres9.3  | in-sync              |


### Dbsecuritygroups

```json
[]
```


### Dbsubnetgroup

```json
{
  "DBSubnetGroupDescription": "Orders database",
  "DBSubnetGroupName": "orders-db-subnets",
  "SubnetGroupStatus": "Complete",
  "Subnets": [
    {
      "SubnetAvailabilityZone": {
        "Name": "us-east-1a"
      },
      "SubnetIdentifier": "subnet-4d897e3d",
      "SubnetStatus": "Active"
    }
  ],
  "VpcId": "vpc-660d36ef"
}
```


### Enabledcloudwatchlogsexports

```json
[]
```


### Endpoint

```json
{
  "Address": "orders-db.aaaaaaaaaa.us-east-1.rds.amazonaws.com",
  "Port": 5432
}
```


### Optiongroupmemberships

| OptionGroupName     | Status  |
| ------------------- | ------- |
| default.postgres9.3 | in-sync |


### Readreplicadbinstanceidentifiers

```json
[]
```


### Statusinfos

```json
[]
```


### Taglist

| Key  | Value  |
| ---- | ------ |
| team | orders |


### Vpcsecuritygroups

| Status | VpcSecurityGroupId   |
| ------ | -------------------- |
| active | sg-2bf145296ea5159ab |



---

# AWS Resource: `aws_cloudwatch_log_group` - `aws_lambda_order-processor`

## Overview

| Property          | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| Resource Type     | aws_cloudwatch_log_group                                                  |
| ARN               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| Region            | us-east-1                                                                 |
| Account ID        | 123456789012                                                              |
| Collected At      | 2026-10-16T02:05:49Z                                                      |
| Collector Version | 0.1.0                                                                     |


## Configuration Specifications

| Configuration Key | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| arn               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| creationTime      | 1792116348246                                                             |
| logGroupName      | /aws/lambda/order-processor                                               |
| metricFilterCount | 0                                                                         |
| retentionInDays   | 14                                                                        |
| storedBytes       | 0                                                                         |


## Resource Tags

| Tag Key | Tag Value |
| ------- | --------- |
| team    | orders    |



---

# AWS Resource: `aws_cloudwatch_log_group` - `ecs_storefront-web`

## Overview

| Property          | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| Resource Type     | aws_cloudwatch_log_group                                          |
| ARN               | arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web |
| Region            | us-east-1                                                         |
| Account ID        | 123456789012                                                      |
| Collected At      | 2026-10-16T02:05:49Z                                              |
| Collector Version | 0.1.0                                                             |


## Configuration Specifications

| Configuration Key | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| arn               | arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web |
| creationTime      | 1792116348681                                                     |
| logGroupName      | /ecs/storefront-web                                               |
| metricFilterCount | 0                                                                 |
| retentionInDays   | 30                                                                |
| storedBytes       | 0                                                                 |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |



---

# AWS Resource: `aws_sfn_state_machine` - `order-flow`

## Overview

| Property          | Value                                                         |
| ----------------- | ------------------------------------------------------------- |
| Resource Type     | aws_sfn_state_machine                                         |
| ARN               | arn:aws:states:us-east-1:123456789012:stateMachine:order-flow |
| Region            | us-east-1                                                     |
| Account ID        | 123456789012                                                  |
| Collected At      | 2026-10-16T02:05:49Z                                          |
| Collector Version | 0.1.0                                                         |


## Configuration Specifications

| Configuration Key | Value                                                                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| creationDate      | 2026-10-16T02:05:48.364000+00:00                                                                                                                           |
| definition        | {"StartAt": "Process", "States": {"Process": {"Type": "Task", "Resource": "arn:aws:lambda:us-east-1:123456789012:function:order-processor", "End": true}}} |
| name              | order-flow                                                                                                                                                 |
| roleArn           | arn:aws:iam::123456789012:role/order-lambda-role                                                                                                           |
| stateMachineArn   | arn:aws:states:us-east-1:123456789012:stateMachine:order-flow                                                                                              |
| status            | ACTIVE                                                                                                                                                     |


## Resource Tags

| Tag Key | Tag Value |
| ------- | --------- |
| team    | orders    |



---

# AWS Resource: `aws_dynamodb_table` - `orders`

## Overview

| Property          | Value                                                |
| ----------------- | ---------------------------------------------------- |
| Resource Type     | aws_dynamodb_table                                   |
| ARN               | arn:aws:dynamodb:us-east-1:123456789012:table/orders |
| Region            | us-east-1                                            |
| Account ID        | 123456789012                                         |
| Collected At      | 2026-10-16T02:05:49Z                                 |
| Collector Version | 0.1.0                                                |


## Configuration Specifications

| Configuration Key | Value                                                |
| ----------------- | ---------------------------------------------------- |
| CreationDateTime  | 2026-10-16T09:05:48.228366+07:00                     |
| ItemCount         | 0                                                    |
| TableArn          | arn:aws:dynamodb:us-east-1:123456789012:table/orders |
| TableName         | orders                                               |
| TableSizeBytes    | 0                                                    |
| TableStatus       | ACTIVE                                               |


## Resource Tags

| Tag Key | Tag Value |
| ------- | --------- |
| team    | orders    |


### Attributedefinitions

| AttributeName | AttributeType |
| ------------- | ------------- |
| order_id      | S             |


### Billingmodesummary

```json
{
  "BillingMode": "PAY_PER_REQUEST"
}
```


### Globalsecondaryindexes

```json
[]
```


### Keyschema

| AttributeName | KeyType |
| ------------- | ------- |
| order_id      | HASH    |


### Localsecondaryindexes

```json
[]
```


### Provisionedthroughput

```json
{
  "NumberOfDecreasesToday": 0,
  "ReadCapacityUnits": 0,
  "WriteCapacityUnits": 0
}
```



---

# AWS Resource: `aws_subnet` - `subnet-4d897e3d`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-16T02:05:49Z                                      |
| Collector Version | 0.1.0                                                     |


## Configuration Specifications

| Configuration Key           | Value                                                     |
| --------------------------- | --------------------------------------------------------- |
| AssignIpv6AddressOnCreation | False                                                     |
| AvailabilityZone            | us-east-1a                                                |
| AvailabilityZoneId          | use1-az6                                                  |
| AvailableIpAddressCount     | 249                                                       |
| CidrBlock                   | 10.0.1.0/24                                               |
| DefaultForAz                | False                                                     |
| Ipv6Native                  | False                                                     |
| MapPublicIpOnLaunch         | False                                                     |
| OwnerId                     | 123456789012                                              |
| State                       | available                                                 |
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d |
| SubnetId                    | subnet-4d897e3d                                           |
| VpcId                       | vpc-660d36ef                                              |


## Resource Tags

| Tag Key | Tag Value        |
| ------- | ---------------- |
| Name    | orders-private-a |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_subnet` - `subnet-2cf4f53a`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-16T02:05:49Z                                      |
| Collector Version | 0.1.0                                                     |


## Configuration Specifications

| Configuration Key           | Value                                                     |
| --------------------------- | --------------------------------------------------------- |
| AssignIpv6AddressOnCreation | False                                                     |
| AvailabilityZone            | us-east-1a                                                |
| AvailabilityZoneId          | use1-az6                                                  |
| AvailableIpAddressCount     | 250                                                       |
| CidrBlock                   | 10.0.10.0/24                                              |
| DefaultForAz                | False                                                     |
| Ipv6Native                  | False                                                     |
| MapPublicIpOnLaunch         | False                                                     |
| OwnerId                     | 123456789012                                              |
| State                       | available                                                 |
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a |
| SubnetId                    | subnet-2cf4f53a                                           |
| VpcId                       | vpc-660d36ef                                              |


## Resource Tags

| Tag Key | Tag Value           |
| ------- | ------------------- |
| Name    | storefront-public-a |
| service | storefront          |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_subnet` - `subnet-4db17d3d`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4db17d3d |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-16T02:05:49Z                                      |
| Collector Version | 0.1.0                                                     |


## Configuration Specifications

| Configuration Key           | Value                                                     |
| --------------------------- | --------------------------------------------------------- |
| AssignIpv6AddressOnCreation | False                                                     |
| AvailabilityZone            | us-east-1b                                                |
| AvailabilityZoneId          | use1-az1                                                  |
| AvailableIpAddressCount     | 251                                                       |
| CidrBlock                   | 10.0.11.0/24                                              |
| DefaultForAz                | False                                                     |
| Ipv6Native                  | False                                                     |
| MapPublicIpOnLaunch         | False                                                     |
| OwnerId                     | 123456789012                                              |
| State                       | available                                                 |
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4db17d3d |
| SubnetId                    | subnet-4db17d3d                                           |
| VpcId                       | vpc-660d36ef                                              |


## Resource Tags

| Tag Key | Tag Value           |
| ------- | ------------------- |
| Name    | storefront-public-b |
| service | storefront          |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_route_table` - `rtb-561c82c8`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-561c82c8 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T02:05:49Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-561c82c8 |
| VpcId             | vpc-660d36ef |


### Associations

| AssociationState        | Main | RouteTableAssociationId | RouteTableId |
| ----------------------- | ---- | ----------------------- | ------------ |
| {'State': 'associated'} | True | rtbassoc-b7fe45d0       | rtb-561c82c8 |


### Routes

| DestinationCidrBlock | GatewayId | Origin           | State  |
| -------------------- | --------- | ---------------- | ------ |
| 10.0.0.0/16          | local     | CreateRouteTable | active |


### Tags

```json
[]
```



---

# AWS Resource: `aws_route_table` - `rtb-bf60be68`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T02:05:49Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-bf60be68 |
| VpcId             | vpc-660d36ef |


## Resource Tags

| Tag Key | Tag Value         |
| ------- | ----------------- |
| Name    | storefront-public |
| service | storefront        |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-16e988c5       | rtb-bf60be68 | subnet-2cf4f53a |
| {'State': 'associated'} | False | rtbassoc-ab796c06       | rtb-bf60be68 | subnet-4db17d3d |


### Routes

| DestinationCidrBlock | GatewayId    | Origin           | State  |
| -------------------- | ------------ | ---------------- | ------ |
| 10.0.0.0/16          | local        | CreateRouteTable | active |
| 0.0.0.0/0            | igw-d045f4ab | CreateRoute      | active |



---

# AWS Resource: `aws_route_table` - `rtb-e28b5541`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-e28b5541 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T02:05:49Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-e28b5541 |
| VpcId             | vpc-660d36ef |


## Resource Tags

| Tag Key | Tag Value          |
| ------- | ------------------ |
| Name    | storefront-private |
| service | storefront         |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-92e826c8       | rtb-e28b5541 | subnet-4d897e3d |


### Routes

| DestinationCidrBlock | DestinationPrefixListId | GatewayId     | NatGatewayId          | Origin           | State  |
| -------------------- | ----------------------- | ------------- | --------------------- | ---------------- | ------ |
| 10.0.0.0/16          |                         | local         |                       | CreateRouteTable | active |
| 0.0.0.0/0            |                         |               | nat-af9f73b40a8a4af4f | CreateRoute      | active |
|                      | pl-51417e29             | vpce-40eb00b6 |                       | CreateRoute      | active |



---

# AWS Resource: `aws_internet_gateway` - `igw-d045f4ab`

## Overview

| Property          | Value                                                            |
| ----------------- | ---------------------------------------------------------------- |
| Resource Type     | aws_internet_gateway                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-d045f4ab |
| Region            | us-east-1                                                        |
| Account ID        | 123456789012                                                     |
| Collected At      | 2026-10-16T02:05:49Z                                             |
| Collector Version | 0.1.0                                                            |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| InternetGatewayId | igw-d045f4ab |
| OwnerId           | 123456789012 |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-igw |
| service | storefront     |


### Attachments

| State     | VpcId        |
| --------- | ------------ |
| available | vpc-660d36ef |



---

# AWS Resource: `aws_nat_gateway` - `nat-af9f73b40a8a4af4f`

## Overview

| Property          | Value                                                               |
| ----------------- | ------------------------------------------------------------------- |
| Resource Type     | aws_nat_gateway                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:natgateway/nat-af9f73b40a8a4af4f |
| Region            | us-east-1                                                           |
| Account ID        | 123456789012                                                        |
| Collected At      | 2026-10-16T02:05:49Z                                                |
| Collector Version | 0.1.0                                                               |


## Configuration Specifications

| Configuration Key | Value                            |
| ----------------- | -------------------------------- |
| ConnectivityType  | None                             |
| CreateTime        | 2026-10-16T02:05:48.410000+00:00 |
| NatGatewayId      | nat-af9f73b40a8a4af4f            |
| State             | available                        |
| SubnetId          | subnet-2cf4f53a                  |
| VpcId             | vpc-660d36ef                     |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-nat |
| service | storefront     |


### Natgatewayaddresses

| AllocationId      | AssociationId     | NetworkInterfaceId | PrivateIp     | PublicIp       |
| ----------------- | ----------------- | ------------------ | ------------- | -------------- |
| eipalloc-1b6897fd | eipassoc-0ea4b721 | eni-f5aeb862       | 10.194.230.82 | 127.176.30.219 |



---

# AWS Resource: `aws_vpc_endpoint` - `vpce-40eb00b6`

## Overview

| Property          | Value                                                         |
| ----------------- | ------------------------------------------------------------- |
| Resource Type     | aws_vpc_endpoint                                              |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-40eb00b6 |
| Region            | us-east-1                                                     |
| Account ID        | 123456789012                                                  |
| Collected At      | 2026-10-16T02:05:49Z                                          |
| Collector Version | 0.1.0                                                         |


## Configuration Specifications

| Configuration Key | Value                                                                                                           |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| CreationTimestamp | 2026-10-16T02:05:48+00:00                                                                                       |
| OwnerId           | 123456789012                                                                                                    |
| PolicyDocument    | {"Version": "2008-10-17", "Statement": [{"Effect": "Allow", "Principal": "*", "Action": "*", "Resource": "*"}]} |
| PrivateDnsEnabled | True                                                                                                            |
| ServiceName       | com.amazonaws.us-east-1.s3                                                                                      |
| State             | available                                                                                                       |
| VpcEndpointId     | vpce-40eb00b6                                                                                                   |
| VpcEndpointType   | Gateway                                                                                                         |
| VpcId             | vpc-660d36ef                                                                                                    |


## Resource Tags

| Tag Key | Tag Value     |
| ------- | ------------- |
| Name    | storefront-s3 |
| service | storefront    |


### Dnsentries

```json
[]
```


### Routetableids

```json
[
  "rtb-e28b5541"
]
```



---

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



---

# AWS Resource: `aws_lb_target_group` - `storefront-tg_50dc6c495c0c9188`

## Overview

| Property          | Value                                                                                          |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| Resource Type     | aws_lb_target_group                                                                            |
| ARN               | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188 |
| Region            | us-east-1                                                                                      |
| Account ID        | 123456789012                                                                                   |
| Collected At      | 2026-10-16T02:05:49Z                                                                           |
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
| VpcId                      | vpc-660d36ef                                                                                   |


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



---

# AWS Resource: `aws_acm_certificate` - `a2f4311b-2bbd-4ca0-97e7-018106634454`

## Overview

| Property          | Value                                                                               |
| ----------------- | ----------------------------------------------------------------------------------- |
| Resource Type     | aws_acm_certificate                                                                 |
| ARN               | arn:aws:acm:us-east-1:123456789012:certificate/a2f4311b-2bbd-4ca0-97e7-018106634454 |
| Region            | us-east-1                                                                           |
| Account ID        | 123456789012                                                                        |
| Collected At      | 2026-10-16T02:05:49Z                                                                |
| Collector Version | 0.1.0                                                                               |


## Configuration Specifications

| Configuration Key  | Value                                                                               |
| ------------------ | ----------------------------------------------------------------------------------- |
| CertificateArn     | arn:aws:acm:us-east-1:123456789012:certificate/a2f4311b-2bbd-4ca0-97e7-018106634454 |
| CreatedAt          | 2026-10-16T02:05:48.534219+07:00                                                    |
| DomainName         | shop.example.com                                                                    |
| IssuedAt           | 2026-10-16T02:05:48.534219+07:00                                                    |
| Issuer             | Amazon                                                                              |
| KeyAlgorithm       | RSA_2048                                                                            |
| NotAfter           | 2027-10-16T02:05:48+07:00                                                           |
| NotBefore          | 2026-10-16T02:05:48+07:00                                                           |
| RenewalEligibility | INELIGIBLE                                                                          |
| Serial             | 193746196831395315679682213309026386579125191715                                    |
| SignatureAlgorithm | SHA512WITHRSA                                                                       |
| Status             | PENDING_VALIDATION                                                                  |
| Subject            | CN=shop.example.com                                                                 |
| Type               | AMAZON_ISSUED                                                                       |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Domainvalidationoptions

| DomainName       | ResourceRecord                                                                                                                                                 | ValidationDomain | ValidationMethod | ValidationStatus   |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ---------------- | ------------------ |
| shop.example.com | {'Name': '_d930b28be6c5927595552b219965053e.shop.example.com.', 'Type': 'CNAME', 'Value': '_c9edd76ee4a0e2a74388032f3861cc50.ykybfrwcxw.acm-validations.aws.'} | shop.example.com | DNS              | PENDING_VALIDATION |
| api.example.com  | {'Name': '_d930b28be6c5927595552b219965053e.api.example.com.', 'Type': 'CNAME', 'Value': '_c9edd76ee4a0e2a74388032f3861cc50.ykybfrwcxw.acm-validations.aws.'}  | api.example.com  | DNS              | PENDING_VALIDATION |


### Extendedkeyusages

```json
[]
```


### Inuseby

```json
[]
```


### Options

```json
{
  "CertificateTransparencyLoggingPreference": "ENABLED"
}
```


### Subjectalternativenames

```json
[
  "shop.example.com",
  "api.example.com"
]
```



---

# AWS Resource: `aws_ecs_cluster` - `storefront`

## Overview

| Property          | Value                                                 |
| ----------------- | ----------------------------------------------------- |
| Resource Type     | aws_ecs_cluster                                       |
| ARN               | arn:aws:ecs:us-east-1:123456789012:cluster/storefront |
| Region            | us-east-1                                             |
| Account ID        | 123456789012                                          |
| Collected At      | 2026-10-16T02:05:49Z                                  |
| Collector Version | 0.1.0                                                 |


## Configuration Specifications

| Configuration Key                 | Value                                                 |
| --------------------------------- | ----------------------------------------------------- |
| activeServicesCount               | 0                                                     |
| clusterArn                        | arn:aws:ecs:us-east-1:123456789012:cluster/storefront |
| clusterName                       | storefront                                            |
| pendingTasksCount                 | 0                                                     |
| registeredContainerInstancesCount | 0                                                     |
| runningTasksCount                 | 0                                                     |
| status                            | ACTIVE                                                |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Settings

| name              | value   |
| ----------------- | ------- |
| containerInsights | enabled |



---

# AWS Resource: `aws_ecr_repository` - `storefront-web`

## Overview

| Property          | Value                                                        |
| ----------------- | ------------------------------------------------------------ |
| Resource Type     | aws_ecr_repository                                           |
| ARN               | arn:aws:ecr:us-east-1:123456789012:repository/storefront-web |
| Region            | us-east-1                                                    |
| Account ID        | 123456789012                                                 |
| Collected At      | 2026-10-16T02:05:49Z                                         |
| Collector Version | 0.1.0                                                        |


## Configuration Specifications

| Configuration Key  | Value                                                        |
| ------------------ | ------------------------------------------------------------ |
| createdAt          | 2026-10-16T02:05:48+00:00                                    |
| imageTagMutability | IMMUTABLE                                                    |
| registryId         | 123456789012                                                 |
| repositoryArn      | arn:aws:ecr:us-east-1:123456789012:repository/storefront-web |
| repositoryName     | storefront-web                                               |
| repositoryUri      | 123456789012.dkr.ecr.us-east-1.amazonaws.com/storefront-web  |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Encryptionconfiguration

```json
{
  "encryptionType": "AES256"
}
```


### Imagescanningconfiguration

```json
{
  "scanOnPush": true
}
```



---

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



---

# AWS Resource: `aws_launch_template` - `lt-bad06a08aee200bf2`

## Overview

| Property          | Value                                                                   |
| ----------------- | ----------------------------------------------------------------------- |
| Resource Type     | aws_launch_template                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:launch-template/lt-bad06a08aee200bf2 |
| Region            | us-east-1                                                               |
| Account ID        | 123456789012                                                            |
| Collected At      | 2026-10-16T02:05:49Z                                                    |
| Collector Version | 0.1.0                                                                   |


## Configuration Specifications

| Configuration Key    | Value                          |
| -------------------- | ------------------------------ |
| CreateTime           | 2026-10-16T02:05:48+00:00      |
| CreatedBy            | arn:aws:iam::123456789012:root |
| DefaultVersionNumber | 1                              |
| LatestVersionNumber  | 1                              |
| LaunchTemplateId     | lt-bad06a08aee200bf2           |
| LaunchTemplateName   | storefront-worker              |


## Resource Tags

| Tag Key | Tag Value         |
| ------- | ----------------- |
| Name    | storefront-worker |
| service | storefront        |


### Launchtemplatedata

```json
{
  "IamInstanceProfile": {
    "Name": "orders-app-role"
  },
  "ImageId": "ami-12c6146b",
  "InstanceType": "t3.small",
  "SecurityGroupIds": [
    "sg-12874fb82c9db66ed"
  ],
  "TagSpecifications": [
    {
      "ResourceType": "launch-template",
      "Tags": [
        {
          "Key": "Name",
          "Value": "storefront-worker"
        },
        {
          "Key": "service",
          "Value": "storefront"
        }
      ]
    }
  ]
}
```



---

# AWS Resource: `aws_elasticache_replication_group` - `storefront-cache`

## Overview

| Property          | Value                                                                        |
| ----------------- | ---------------------------------------------------------------------------- |
| Resource Type     | aws_elasticache_replication_group                                            |
| ARN               | arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache |
| Region            | us-east-1                                                                    |
| Account ID        | 123456789012                                                                 |
| Collected At      | 2026-10-16T02:05:49Z                                                         |
| Collector Version | 0.1.0                                                                        |


## Configuration Specifications

| Configuration Key          | Value                                                                        |
| -------------------------- | ---------------------------------------------------------------------------- |
| ARN                        | arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache |
| AtRestEncryptionEnabled    | True                                                                         |
| AuthTokenEnabled           | False                                                                        |
| AutoMinorVersionUpgrade    | True                                                                         |
| AutomaticFailover          | enabled                                                                      |
| CacheNodeType              | cache.t4g.micro                                                              |
| ClusterEnabled             | False                                                                        |
| ClusterMode                | disabled                                                                     |
| DataTiering                | disabled                                                                     |
| Description                | Storefront session cache                                                     |
| Engine                     | redis                                                                        |
| IpDiscovery                | ipv4                                                                         |
| MultiAZ                    | enabled                                                                      |
| NetworkType                | ipv4                                                                         |
| ReplicationGroupCreateTime | 2026-01-01T00:00:00+00:00                                                    |
| ReplicationGroupId         | storefront-cache                                                             |
| SnapshotRetentionLimit     | 0                                                                            |
| SnapshotWindow             | 05:00-06:00                                                                  |
| Status                     | available                                                                    |
| TransitEncryptionEnabled   | True                                                                         |


### Cachecluster

```json
{
  "ARN": "arn:aws:elasticache:us-east-1:123456789012:cluster:storefront-cache-001",
  "AtRestEncryptionEnabled": true,
  "AuthTokenEnabled": false,
  "AutoMinorVersionUpgrade": true,
  "CacheClusterCreateTime": "2026-01-01T00:00:00+00:00",
  "CacheClusterId": "storefront-cache-001",
  "CacheClusterStatus": "available",
  "CacheNodeType": "cache.t4g.micro",
  "CacheParameterGroup": {
    "CacheNodeIdsToReboot": [],
    "CacheParameterGroupName": "default.redis7",
    "ParameterApplyStatus": "in-sync"
  },
  "CacheSecurityGroups": [],
  "CacheSubnetGroupName": "storefront-cache-subnets",
  "Engine": "redis",
  "EngineVersion": "7.1",
  "IpDiscovery": "ipv4",
  "LogDeliveryConfigurations": [],
  "NetworkType": "ipv4",
  "NumCacheNodes": 1,
  "PendingModifiedValues": {},
  "PreferredAvailabilityZone": "us-east-1a",
  "PreferredMaintenanceWindow": "sun:23:00-mon:01:30",
  "ReplicationGroupId": "storefront-cache",
  "ReplicationGroupLogDeliveryEnabled": false,
  "SecurityGroups": [
    {
      "SecurityGroupId": "sg-12874fb82c9db66ed",
      "Status": "active"
    }
  ],
  "SnapshotRetentionLimit": 0,
  "SnapshotWindow": "05:00-06:00",
  "TransitEncryptionEnabled": true
}
```


### Cachesubnetgroup

```json
{
  "ARN": "arn:aws:elasticache:us-east-1:123456789012:subnetgroup:storefront-cache-subnets",
  "CacheSubnetGroupDescription": "Storefront cache",
  "CacheSubnetGroupName": "storefront-cache-subnets",
  "Subnets": [
    {
      "SubnetAvailabilityZone": {
        "Name": "us-east-1a"
      },
      "SubnetIdentifier": "subnet-4d897e3d",
      "SupportedNetworkTypes": [
        "ipv4"
      ]
    }
  ],
  "SupportedNetworkTypes": [
    "ipv4"
  ],
  "VpcId": "vpc-660d36ef"
}
```


### Logdeliveryconfigurations

```json
[]
```


### Memberclusters

```json
[
  "storefront-cache-001",
  "storefront-cache-002"
]
```


### Nodegroups

| NodeGroupId | NodeGroupMembers                                                                                                                                                                                                                                                                 | PrimaryEndpoint                                                                            | ReaderEndpoint                                                                             | Status    |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | --------- |
| 0001        | [{'CacheClusterId': 'storefront-cache-001', 'CacheNodeId': '0001', 'PreferredAvailabilityZone': 'us-east-1a', 'CurrentRole': 'primary'}, {'CacheClusterId': 'storefront-cache-002', 'CacheNodeId': '0001', 'PreferredAvailabilityZone': 'us-east-1a', 'CurrentRole': 'replica'}] | {'Address': 'storefront-cache.abc123.ng.0001.us-east-1.cache.amazonaws.com', 'Port': 6379} | {'Address': 'storefront-cache.abc123.ro.0001.us-east-1.cache.amazonaws.com', 'Port': 6379} | available |


### Pendingmodifiedvalues

```json
{}
```


### Taglist

| Key     | Value      |
| ------- | ---------- |
| service | storefront |



---

# AWS Resource: `aws_sqs_queue` - `storefront-orders`

## Overview

| Property          | Value                                                |
| ----------------- | ---------------------------------------------------- |
| Resource Type     | aws_sqs_queue                                        |
| ARN               | arn:aws:sqs:us-east-1:123456789012:storefront-orders |
| Region            | us-east-1                                            |
| Account ID        | 123456789012                                         |
| Collected At      | 2026-10-16T02:05:49Z                                 |
| Collector Version | 0.1.0                                                |


## Configuration Specifications

| Configuration Key | Value                                                              |
| ----------------- | ------------------------------------------------------------------ |
| QueueUrl          | https://sqs.us-east-1.amazonaws.com/123456789012/storefront-orders |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Attributes

```json
{
  "ApproximateNumberOfMessages": "0",
  "ApproximateNumberOfMessagesDelayed": "0",
  "ApproximateNumberOfMessagesNotVisible": "0",
  "CreatedTimestamp": "1792116348.740304",
  "DelaySeconds": "0",
  "LastModifiedTimestamp": "1792116348.740304",
  "MaximumMessageSize": "262144",
  "MessageRetentionPeriod": "345600",
  "QueueArn": "arn:aws:sqs:us-east-1:123456789012:storefront-orders",
  "ReceiveMessageWaitTimeSeconds": "0",
  "VisibilityTimeout": "60"
}
```



---

# AWS Resource: `aws_sns_topic` - `storefront-events`

## Overview

| Property          | Value                                                |
| ----------------- | ---------------------------------------------------- |
| Resource Type     | aws_sns_topic                                        |
| ARN               | arn:aws:sns:us-east-1:123456789012:storefront-events |
| Region            | us-east-1                                            |
| Account ID        | 123456789012                                         |
| Collected At      | 2026-10-16T02:05:49Z                                 |
| Collector Version | 0.1.0                                                |


## Configuration Specifications

## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Attributes

```json
{
  "DeliveryPolicy": "",
  "DisplayName": "Storefront events",
  "EffectiveDeliveryPolicy": "{\"defaultHealthyRetryPolicy\": {\"numNoDelayRetries\": 0, \"numMinDelayRetries\": 0, \"minDelayTarget\": 20, \"maxDelayTarget\": 20, \"numMaxDelayRetries\": 0, \"numRetries\": 3, \"backoffFunction\": \"linear\"}, \"sicklyRetryPolicy\": null, \"throttlePolicy\": null, \"guaranteed\": false}",
  "Owner": "123456789012",
  "Policy": "{\"Version\":\"2008-10-17\",\"Id\":\"__default_policy_ID\",\"Statement\":[{\"Effect\":\"Allow\",\"Sid\":\"__default_statement_ID\",\"Principal\":{\"AWS\":\"*\"},\"Action\":[\"SNS:GetTopicAttributes\",\"SNS:SetTopicAttributes\",\"SNS:AddPermission\",\"SNS:RemovePermission\",\"SNS:DeleteTopic\",\"SNS:Subscribe\",\"SNS:ListSubscriptionsByTopic\",\"SNS:Publish\",\"SNS:Receive\"],\"Resource\":\"arn:aws:sns:us-east-1:123456789012:storefront-events\",\"Condition\":{\"StringEquals\":{\"AWS:SourceOwner\":\"123456789012\"}}}]}",
  "SubscriptionsConfirmed": "0",
  "SubscriptionsDeleted": "0",
  "SubscriptionsPending": "0",
  "TopicArn": "arn:aws:sns:us-east-1:123456789012:storefront-events"
}
```


### Subscriptions

| Endpoint                                             | Owner        | Protocol | SubscriptionArn                                                                           | TopicArn                                             |
| ---------------------------------------------------- | ------------ | -------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| arn:aws:sqs:us-east-1:123456789012:storefront-orders | 123456789012 | sqs      | arn:aws:sns:us-east-1:123456789012:storefront-events:54573983-ec87-4ceb-8724-f04719e8c78c | arn:aws:sns:us-east-1:123456789012:storefront-events |



---

# AWS Resource: `aws_scheduler_schedule` - `default_storefront-cleanup`

## Overview

| Property          | Value                                                                        |
| ----------------- | ---------------------------------------------------------------------------- |
| Resource Type     | aws_scheduler_schedule                                                       |
| ARN               | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup |
| Region            | us-east-1                                                                    |
| Account ID        | 123456789012                                                                 |
| Collected At      | 2026-10-16T02:05:49Z                                                         |
| Collector Version | 0.1.0                                                                        |


## Configuration Specifications

| Configuration Key    | Value                                                                        |
| -------------------- | ---------------------------------------------------------------------------- |
| Arn                  | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup |
| CreationDate         | 2026-10-16T09:05:48.927260+07:00                                             |
| Description          | Hourly cleanup message                                                       |
| GroupName            | default                                                                      |
| LastModificationDate | 2026-10-16T09:05:48.927260+07:00                                             |
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



---

# AWS Resource: `aws_lb_listener` - `app_storefront-alb_50dc6c495c0c9188_4434501777232`

## Overview

| Property          | Value                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_lb_listener                                                                                                |
| ARN               | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232 |
| Region            | us-east-1                                                                                                      |
| Account ID        | 123456789012                                                                                                   |
| Collected At      | 2026-10-16T02:05:49Z                                                                                           |
| Collector Version | 0.1.0                                                                                                          |


## Configuration Specifications

| Configuration Key | Value                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| ListenerArn       | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232 |
| LoadBalancerArn   | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188           |
| Port              | 443                                                                                                            |
| Protocol          | HTTPS                                                                                                          |
| SslPolicy         | ELBSecurityPolicy-2016-08                                                                                      |


### Alpnpolicy

```json
[]
```


### Certificates

| CertificateArn                                                                      |
| ----------------------------------------------------------------------------------- |
| arn:aws:acm:us-east-1:123456789012:certificate/a2f4311b-2bbd-4ca0-97e7-018106634454 |


### Defaultactions

| TargetGroupArn                                                                                 | Type    |
| ---------------------------------------------------------------------------------------------- | ------- |
| arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188 | forward |


### Tags

```json
[]
```



---

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



---

# AWS Resource: `aws_ecs_task_definition` - `storefront-web_1`

## Overview

| Property          | Value                                                               |
| ----------------- | ------------------------------------------------------------------- |
| Resource Type     | aws_ecs_task_definition                                             |
| ARN               | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1 |
| Region            | us-east-1                                                           |
| Account ID        | 123456789012                                                        |
| Collected At      | 2026-10-16T02:05:49Z                                                |
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



---

# AWS Resource: `aws_cloudwatch_event_rule` - `storefront-nightly-report`

## Overview

| Property          | Value                                                                |
| ----------------- | -------------------------------------------------------------------- |
| Resource Type     | aws_cloudwatch_event_rule                                            |
| ARN               | arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report |
| Region            | us-east-1                                                            |
| Account ID        | 123456789012                                                         |
| Collected At      | 2026-10-16T02:05:49Z                                                 |
| Collector Version | 0.1.0                                                                |


## Configuration Specifications

| Configuration Key  | Value                                                                |
| ------------------ | -------------------------------------------------------------------- |
| Arn                | arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report |
| CreatedBy          | 123456789012                                                         |
| Description        | Nightly order report                                                 |
| EventBusName       | default                                                              |
| Name               | storefront-nightly-report                                            |
| ScheduleExpression | cron(0 2 * * ? *)                                                    |
| State              | ENABLED                                                              |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Targets

| Arn                                                            | Id              |
| -------------------------------------------------------------- | --------------- |
| arn:aws:lambda:us-east-1:123456789012:function:order-processor | order-processor |



---

# AWS Resource: `aws_s3_bucket` - `orders-public-assets`

## Overview

| Property          | Value                             |
| ----------------- | --------------------------------- |
| Resource Type     | aws_s3_bucket                     |
| ARN               | arn:aws:s3:::orders-public-assets |
| Region            | global                            |
| Account ID        | 123456789012                      |
| Collected At      | 2026-10-16T02:05:49Z              |
| Collector Version | 0.1.0                             |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Name              | orders-public-assets |


### Bucket-Acl

```json
{
  "Grants": [
    {
      "Grantee": {
        "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a",
        "Type": "CanonicalUser"
      },
      "Permission": "FULL_CONTROL"
    },
    {
      "Grantee": {
        "Type": "Group",
        "URI": "http://acs.amazonaws.com/groups/global/AllUsers"
      },
      "Permission": "READ"
    }
  ],
  "Owner": {
    "DisplayName": "webfile",
    "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
  }
}
```


### Bucket-Tagging

```json
{
  "TagSet": [
    {
      "Key": "team",
      "Value": "orders"
    }
  ]
}
```


### Bucket-Versioning

```json
{
  "Status": "Enabled"
}
```



---

# AWS Resource: `aws_s3_bucket` - `storefront-static`

## Overview

| Property          | Value                          |
| ----------------- | ------------------------------ |
| Resource Type     | aws_s3_bucket                  |
| ARN               | arn:aws:s3:::storefront-static |
| Region            | global                         |
| Account ID        | 123456789012                   |
| Collected At      | 2026-10-16T02:05:49Z           |
| Collector Version | 0.1.0                          |


## Configuration Specifications

| Configuration Key | Value             |
| ----------------- | ----------------- |
| Name              | storefront-static |


### Bucket-Acl

```json
{
  "Grants": [
    {
      "Grantee": {
        "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a",
        "Type": "CanonicalUser"
      },
      "Permission": "FULL_CONTROL"
    }
  ],
  "Owner": {
    "DisplayName": "webfile",
    "ID": "75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a"
  }
}
```


### Bucket-Tagging

```json
{
  "TagSet": [
    {
      "Key": "service",
      "Value": "storefront"
    }
  ]
}
```


### Bucket-Versioning

```json
{}
```



---

# AWS Resource: `aws_iam_role` - `orders-app-role`

## Overview

| Property          | Value                                          |
| ----------------- | ---------------------------------------------- |
| Resource Type     | aws_iam_role                                   |
| ARN               | arn:aws:iam::123456789012:role/orders-app-role |
| Region            | global                                         |
| Account ID        | 123456789012                                   |
| Collected At      | 2026-10-16T02:05:49Z                           |
| Collector Version | 0.1.0                                          |


## Configuration Specifications

| Configuration Key  | Value                                          |
| ------------------ | ---------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/orders-app-role |
| CreateDate         | 2026-10-16T02:05:48.192000+00:00               |
| MaxSessionDuration | 3600                                           |
| Path               | /                                              |
| RoleId             | AROARZPUZDIKEG2US3K5X                          |
| RoleName           | orders-app-role                                |


### Assumerolepolicydocument

```json
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
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



---

# AWS Resource: `aws_iam_role` - `storefront-scheduler-role`

## Overview

| Property          | Value                                                    |
| ----------------- | -------------------------------------------------------- |
| Resource Type     | aws_iam_role                                             |
| ARN               | arn:aws:iam::123456789012:role/storefront-scheduler-role |
| Region            | global                                                   |
| Account ID        | 123456789012                                             |
| Collected At      | 2026-10-16T02:05:49Z                                     |
| Collector Version | 0.1.0                                                    |


## Configuration Specifications

| Configuration Key  | Value                                                    |
| ------------------ | -------------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-scheduler-role |
| CreateDate         | 2026-10-16T02:05:48.676000+00:00                         |
| MaxSessionDuration | 3600                                                     |
| Path               | /                                                        |
| RoleId             | AROARZPUZDIKK7VWUBKWN                                    |
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



---

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



---

# AWS Resource: `aws_iam_role` - `storefront-exec-role`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_iam_role                                        |
| ARN               | arn:aws:iam::123456789012:role/storefront-exec-role |
| Region            | global                                              |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-16T02:05:49Z                                |
| Collector Version | 0.1.0                                               |


## Configuration Specifications

| Configuration Key  | Value                                               |
| ------------------ | --------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-exec-role |
| CreateDate         | 2026-10-16T02:05:48.672000+00:00                    |
| MaxSessionDuration | 3600                                                |
| Path               | /                                                   |
| RoleId             | AROARZPUZDIKKYEHB7LX6                               |
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



---

# AWS Resource: `aws_iam_role` - `order-lambda-role`

## Overview

| Property          | Value                                            |
| ----------------- | ------------------------------------------------ |
| Resource Type     | aws_iam_role                                     |
| ARN               | arn:aws:iam::123456789012:role/order-lambda-role |
| Region            | global                                           |
| Account ID        | 123456789012                                     |
| Collected At      | 2026-10-16T02:05:49Z                             |
| Collector Version | 0.1.0                                            |


## Configuration Specifications

| Configuration Key  | Value                                            |
| ------------------ | ------------------------------------------------ |
| Arn                | arn:aws:iam::123456789012:role/order-lambda-role |
| CreateDate         | 2026-10-16T02:05:48.200000+00:00                 |
| Description        | Execution role for order-processor               |
| MaxSessionDuration | 3600                                             |
| Path               | /                                                |
| RoleId             | AROARZPUZDIKMAF3QCWFB                            |
| RoleName           | order-lambda-role                                |


### Assumerolepolicydocument

```json
{
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
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
{
  "too-broad": {
    "Statement": [
      {
        "Action": "*",
        "Effect": "Allow",
        "Resource": "*"
      }
    ],
    "Version": "2012-10-17"
  }
}
```


### Rolelastused

```json
{}
```



---

# AWS Resource: `aws_cloudfront_distribution` - `X5E0C4JHPHC9C`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_cloudfront_distribution                                 |
| ARN               | arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C |
| Region            | global                                                      |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T02:05:49Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key             | Value                                                      |
| ----------------------------- | ---------------------------------------------------------- |
| ARN                           | arn:aws:cloudfront:123456789012:distribution/X5E0C4JHPHC9C |
| DomainName                    | uyrz52o28gvy9.cloudfront.net                               |
| Id                            | X5E0C4JHPHC9C                                              |
| InProgressInvalidationBatches | 0                                                          |
| LastModifiedTime              | 2021-11-27T10:34:26.802000+00:00                           |
| Status                        | Deployed                                                   |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Activetrustedkeygroups

```json
{
  "Enabled": false,
  "Items": [],
  "Quantity": 0
}
```


### Activetrustedsigners

```json
{
  "Enabled": false,
  "Items": [],
  "Quantity": 0
}
```


### Aliasicprecordals

```json
[]
```


### Distributionconfig

```json
{
  "Aliases": {
    "Items": [
      "shop.example.com"
    ],
    "Quantity": 1
  },
  "CacheBehaviors": {
    "Quantity": 0
  },
  "CallerReference": "storefront",
  "Comment": "storefront",
  "CustomErrorResponses": {
    "Quantity": 0
  },
  "DefaultCacheBehavior": {
    "AllowedMethods": {
      "CachedMethods": {
        "Items": [
          "GET",
          "HEAD"
        ],
        "Quantity": 2
      },
      "Items": [
        "HEAD",
        "GET"
      ],
      "Quantity": 2
    },
    "CachePolicyId": "",
    "Compress": true,
    "DefaultTTL": 0,
    "FieldLevelEncryptionId": "",
    "ForwardedValues": {
      "Cookies": {
        "Forward": "none",
        "WhitelistedNames": {
          "Items": [],
          "Quantity": 0
        }
      },
      "Headers": {
        "Items": [],
        "Quantity": 0
      },
      "QueryString": false,
      "QueryStringCacheKeys": {
        "Items": [],
        "Quantity": 0
      }
    },
    "FunctionAssociations": {
      "Quantity": 0
    },
    "LambdaFunctionAssociations": {
      "Quantity": 0
    },
    "MaxTTL": 0,
    "MinTTL": 0,
    "OriginRequestPolicyId": "",
    "RealtimeLogConfigArn": "",
    "ResponseHeadersPolicyId": "",
    "SmoothStreaming": false,
    "TargetOriginId": "web-alb",
    "TrustedKeyGroups": {
      "Enabled": false,
      "Items": [],
      "Quantity": 0
    },
    "TrustedSigners": {
      "Enabled": false,
      "Items": [],
      "Quantity": 0
    },
    "ViewerProtocolPolicy": "redirect-to-https"
  },
  "DefaultRootObject": "",
  "Enabled": true,
  "HttpVersion": "http2",
  "IsIPV6Enabled": true,
  "Logging": {
    "Bucket": "",
    "Enabled": false,
    "IncludeCookies": false,
    "Prefix": ""
  },
  "OriginGroups": {
    "Quantity": 0
  },
  "Origins": {
    "Items": [
      {
        "ConnectionAttempts": 3,
        "ConnectionTimeout": 10,
        "CustomHeaders": {
          "Items": [],
          "Quantity": 0
        },
        "DomainName": "storefront-static.s3.us-east-1.amazonaws.com",
        "Id": "static-s3",
        "OriginPath": "",
        "OriginShield": {
          "Enabled": false
        }
      },
      {
        "ConnectionAttempts": 3,
        "ConnectionTimeout": 10,
        "CustomHeaders": {
          "Items": [],
          "Quantity": 0
        },
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginKeepaliveTimeout": 5,
          "OriginProtocolPolicy": "https-only",
          "OriginReadTimeout": 30,
          "OriginSslProtocols": {
            "Items": [
              "TLSv1.2"
            ],
            "Quantity": 1
          }
        },
        "DomainName": "storefront-alb-1.us-east-1.elb.amazonaws.com",
        "Id": "web-alb",
        "OriginPath": "",
        "OriginShield": {
          "Enabled": false
        }
      }
    ],
    "Quantity": 2
  },
  "PriceClass": "PriceClass_All",
  "Restrictions": {
    "GeoRestriction": {
      "Quantity": 0,
      "RestrictionType": "none"
    }
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "",
    "Certificate": "",
    "CertificateSource": "cloudfront",
    "CloudFrontDefaultCertificate": true,
    "IAMCertificateId": "",
    "MinimumProtocolVersion": "TLSv1",
    "SSLSupportMethod": ""
  },
  "WebACLId": "arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/d06f4b4d-1ec6-42a4-81fa-1582637eb32d"
}
```



---

# AWS Resource: `aws_route53_zone` - `ACA19C6IIUY2GFZ`

## Overview

| Property          | Value                                        |
| ----------------- | -------------------------------------------- |
| Resource Type     | aws_route53_zone                             |
| ARN               | arn:aws:route53:::hostedzone/ACA19C6IIUY2GFZ |
| Region            | global                                       |
| Account ID        | 123456789012                                 |
| Collected At      | 2026-10-16T02:05:49Z                         |
| Collector Version | 0.1.0                                        |


## Configuration Specifications

| Configuration Key      | Value                       |
| ---------------------- | --------------------------- |
| CallerReference        | storefront                  |
| Id                     | /hostedzone/ACA19C6IIUY2GFZ |
| Name                   | example.com.                |
| ResourceRecordSetCount | 4                           |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Config

```json
{
  "PrivateZone": false
}
```


### Delegationset

```json
{
  "Id": "",
  "NameServers": [
    "ns-2048.awsdns-64.com",
    "ns-2049.awsdns-65.net",
    "ns-2050.awsdns-66.org",
    "ns-2051.awsdns-67.co.uk"
  ]
}
```


### Resourcerecordsets

| AliasTarget                                                                                                                           | Name              | ResourceRecords                                                                                                                                    | TTL    | Type |
| ------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ---- |
|                                                                                                                                       | example.com.      | [{'Value': 'ns-2048.awsdns-64.com'}, {'Value': 'ns-2049.awsdns-65.net'}, {'Value': 'ns-2050.awsdns-66.org'}, {'Value': 'ns-2051.awsdns-67.co.uk'}] | 172800 | NS   |
|                                                                                                                                       | example.com.      | [{'Value': "{'Value': 'ns-2048.awsdns-64.com. hostmaster.example.com. 1 7200 900 1209600 86400'}"}]                                                | 900    | SOA  |
| {'HostedZoneId': 'Z2P70J7EXAMPLE', 'DNSName': 'dualstack.storefront-alb-1.us-east-1.elb.amazonaws.com', 'EvaluateTargetHealth': True} | api.example.com.  |                                                                                                                                                    |        | A    |
| {'HostedZoneId': 'Z2FDTNDATAQYW2', 'DNSName': 'uyrz52o28gvy9.cloudfront.net', 'EvaluateTargetHealth': False}                          | shop.example.com. |                                                                                                                                                    |        | A    |



---

# AWS Resource: `aws_wafv2_web_acl` - `storefront-waf_d06f4b4d-1ec6-42a4-81fa-1582637eb32d`

## Overview

| Property          | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_wafv2_web_acl                                                                                   |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/d06f4b4d-1ec6-42a4-81fa-1582637eb32d |
| Region            | global                                                                                              |
| Account ID        | 123456789012                                                                                        |
| Collected At      | 2026-10-16T02:05:49Z                                                                                |
| Collector Version | 0.1.0                                                                                               |


## Configuration Specifications

| Configuration Key | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/d06f4b4d-1ec6-42a4-81fa-1582637eb32d |
| Description       | Edge protection for the storefront                                                                  |
| Id                | d06f4b4d-1ec6-42a4-81fa-1582637eb32d                                                                |
| Name              | storefront-waf                                                                                      |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| service | storefront |


### Defaultaction

```json
{
  "Allow": {}
}
```


### Rules

```json
[]
```


### Visibilityconfig

```json
{
  "CloudWatchMetricsEnabled": true,
  "MetricName": "storefront-waf",
  "SampledRequestsEnabled": true
}
```



---

## Performance & Time Savings Summary Report

> [!NOTE]
> Based on industry baseline calculation of 5 minutes per resource for manual documentation.

| Metric          | Manual Effort (Baseline) | Automated Collection      | Savings           |
| --------------- | ------------------------ | ------------------------- | ----------------- |
| Baseline Rate   | 5 minutes / resource     | N/A                       | -                 |
| Total Resources | 47                       | 47                        | -                 |
| Total Duration  | 3.92 hours (235 min)     | 1.00 seconds (0.0003 hrs) | 3.92 hours saved  |
| Efficiency Gain | Baseline (100%)          | +100.0% faster            | 100.0% time saved |
