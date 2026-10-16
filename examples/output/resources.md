# AWS Infrastructure Resource Inventory

**Generated:** 2026-10-16T01:29:14.656151Z  
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
| aws_instance                      | i-47f9de669501b27af                                 | us-east-1 | arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af                                                                          |
| aws_instance                      | i-7c15a7e2df90fa017                                 | us-east-1 | arn:aws:ec2:us-east-1:123456789012:instance/i-7c15a7e2df90fa017                                                                          |
| aws_vpc                           | vpc-7c4f2f1d                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d                                                                                      |
| aws_security_group                | sg-71a3ac0ec6bbd92b7                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-71a3ac0ec6bbd92b7                                                                   |
| aws_security_group                | sg-2edfb301c8a045aa8                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-2edfb301c8a045aa8                                                                   |
| aws_security_group                | sg-c6ec367b2a800f7fe                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-c6ec367b2a800f7fe                                                                   |
| aws_security_group                | sg-7c3a665620cbf02dc                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c3a665620cbf02dc                                                                   |
| aws_lambda_function               | order-processor                                     | us-east-1 | arn:aws:lambda:us-east-1:123456789012:function:order-processor                                                                           |
| aws_db_instance                   | orders-db                                           | us-east-1 | arn:aws:rds:us-east-1:123456789012:db:orders-db                                                                                          |
| aws_cloudwatch_log_group          | aws_lambda_order-processor                          | us-east-1 | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor                                                                |
| aws_cloudwatch_log_group          | ecs_storefront-web                                  | us-east-1 | arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web                                                                        |
| aws_sfn_state_machine             | order-flow                                          | us-east-1 | arn:aws:states:us-east-1:123456789012:stateMachine:order-flow                                                                            |
| aws_dynamodb_table                | orders                                              | us-east-1 | arn:aws:dynamodb:us-east-1:123456789012:table/orders                                                                                     |
| aws_subnet                        | subnet-30a75c4f                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f                                                                                |
| aws_subnet                        | subnet-91c2dcc6                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6                                                                                |
| aws_subnet                        | subnet-9134f3a5                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-9134f3a5                                                                                |
| aws_route_table                   | rtb-7bfbfaee                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-7bfbfaee                                                                              |
| aws_route_table                   | rtb-260c9780                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-260c9780                                                                              |
| aws_route_table                   | rtb-abf4c4b4                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4                                                                              |
| aws_internet_gateway              | igw-dbc38f85                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-dbc38f85                                                                         |
| aws_nat_gateway                   | nat-60d1a0cf8c8f398eb                               | us-east-1 | arn:aws:ec2:us-east-1:123456789012:natgateway/nat-60d1a0cf8c8f398eb                                                                      |
| aws_vpc_endpoint                  | vpce-55746589                                       | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-55746589                                                                            |
| aws_lb                            | app_storefront-alb_50dc6c495c0c9188                 | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188                                     |
| aws_lb_target_group               | storefront-tg_50dc6c495c0c9188                      | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188                                           |
| aws_acm_certificate               | 8f72f034-ca75-4120-acc5-f35a9fd3885d                | us-east-1 | arn:aws:acm:us-east-1:123456789012:certificate/8f72f034-ca75-4120-acc5-f35a9fd3885d                                                      |
| aws_ecs_cluster                   | storefront                                          | us-east-1 | arn:aws:ecs:us-east-1:123456789012:cluster/storefront                                                                                    |
| aws_ecr_repository                | storefront-web                                      | us-east-1 | arn:aws:ecr:us-east-1:123456789012:repository/storefront-web                                                                             |
| aws_autoscaling_group             | storefront-workers                                  | us-east-1 | arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers |
| aws_launch_template               | lt-c743f2f076e986059                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:launch-template/lt-c743f2f076e986059                                                                  |
| aws_elasticache_replication_group | storefront-cache                                    | us-east-1 | arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache                                                             |
| aws_sqs_queue                     | storefront-orders                                   | us-east-1 | arn:aws:sqs:us-east-1:123456789012:storefront-orders                                                                                     |
| aws_sns_topic                     | storefront-events                                   | us-east-1 | arn:aws:sns:us-east-1:123456789012:storefront-events                                                                                     |
| aws_scheduler_schedule            | default_storefront-cleanup                          | us-east-1 | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup                                                             |
| aws_lb_listener                   | app_storefront-alb_50dc6c495c0c9188_4434536313232   | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232                           |
| aws_ecs_service                   | storefront_web                                      | us-east-1 | arn:aws:ecs:us-east-1:123456789012:service/storefront/web                                                                                |
| aws_ecs_task_definition           | storefront-web_1                                    | us-east-1 | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1                                                                      |
| aws_cloudwatch_event_rule         | storefront-nightly-report                           | us-east-1 | arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report                                                                     |
| aws_s3_bucket                     | orders-public-assets                                | global    | arn:aws:s3:::orders-public-assets                                                                                                        |
| aws_s3_bucket                     | storefront-static                                   | global    | arn:aws:s3:::storefront-static                                                                                                           |
| aws_iam_role                      | order-lambda-role                                   | global    | arn:aws:iam::123456789012:role/order-lambda-role                                                                                         |
| aws_iam_role                      | storefront-task-role                                | global    | arn:aws:iam::123456789012:role/storefront-task-role                                                                                      |
| aws_iam_role                      | storefront-exec-role                                | global    | arn:aws:iam::123456789012:role/storefront-exec-role                                                                                      |
| aws_iam_role                      | storefront-scheduler-role                           | global    | arn:aws:iam::123456789012:role/storefront-scheduler-role                                                                                 |
| aws_iam_role                      | orders-app-role                                     | global    | arn:aws:iam::123456789012:role/orders-app-role                                                                                           |
| aws_cloudfront_distribution       | S8ZTDFP8H8PGF                                       | global    | arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF                                                                              |
| aws_route53_zone                  | 2VX36NXN28FIY7F                                     | global    | arn:aws:route53:::hostedzone/2VX36NXN28FIY7F                                                                                             |
| aws_wafv2_web_acl                 | storefront-waf_1cbd8645-1348-4072-8b2e-633711042db1 | global    | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/1cbd8645-1348-4072-8b2e-633711042db1                                      |


## Detailed Resource Specifications

# AWS Resource: `aws_instance` - `i-47f9de669501b27af`

## Overview

| Property          | Value                                                           |
| ----------------- | --------------------------------------------------------------- |
| Resource Type     | aws_instance                                                    |
| ARN               | arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af |
| Region            | us-east-1                                                       |
| Account ID        | 123456789012                                                    |
| Collected At      | 2026-10-16T01:29:14Z                                            |
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
| InstanceId            | i-47f9de669501b27af       |
| InstanceType          | t3.micro                  |
| KernelId              | None                      |
| LaunchTime            | 2026-10-16T01:29:12+00:00 |
| Platform              | windows                   |
| PrivateDnsName        | ip-10-0-1-4.ec2.internal  |
| PrivateIpAddress      | 10.0.1.4                  |
| PublicDnsName         | None                      |
| RootDeviceName        | /dev/sda1                 |
| RootDeviceType        | ebs                       |
| SourceDestCheck       | True                      |
| StateTransitionReason |                           |
| SubnetId              | subnet-30a75c4f           |
| VirtualizationType    | hvm                       |
| VpcId                 | vpc-7c4f2f1d              |


## Resource Tags

| Tag Key | Tag Value    |
| ------- | ------------ |
| Name    | orders-web-1 |


### Blockdevicemappings

| DeviceName | Ebs                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| /dev/sda1  | {'AttachTime': '2026-10-16T01:29:12+00:00', 'DeleteOnTermination': True, 'Status': 'in-use', 'VolumeId': 'vol-a5de2498'} |


### Iaminstanceprofile

```json
{
  "Arn": "arn:aws:iam::123456789012:instance-profile/orders-app-role",
  "Id": "iip-assoc-28071f6e"
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
| {'AttachTime': '2015-01-01T00:00:00+00:00', 'AttachmentId': 'eni-attach-bcd2af88', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'} | Primary network interface | [{'GroupId': 'sg-2edfb301c8a045aa8', 'GroupName': 'orders-web-sg'}] | 1b:2b:3c:4d:5e:6f | eni-52ca70e6       | 123456789012 | 10.0.1.4         | [{'Primary': True, 'PrivateIpAddress': '10.0.1.4'}] | True            | in-use | subnet-30a75c4f | vpc-7c4f2f1d |


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
| sg-2edfb301c8a045aa8 | orders-web-sg |


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

# AWS Resource: `aws_instance` - `i-7c15a7e2df90fa017`

## Overview

| Property          | Value                                                           |
| ----------------- | --------------------------------------------------------------- |
| Resource Type     | aws_instance                                                    |
| ARN               | arn:aws:ec2:us-east-1:123456789012:instance/i-7c15a7e2df90fa017 |
| Region            | us-east-1                                                       |
| Account ID        | 123456789012                                                    |
| Collected At      | 2026-10-16T01:29:14Z                                            |
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
| InstanceId            | i-7c15a7e2df90fa017       |
| InstanceType          | t3.small                  |
| KernelId              | None                      |
| LaunchTime            | 2026-10-16T01:29:13+00:00 |
| Platform              | windows                   |
| PrivateDnsName        | ip-10-0-1-5.ec2.internal  |
| PrivateIpAddress      | 10.0.1.5                  |
| PublicDnsName         | None                      |
| RootDeviceName        | /dev/sda1                 |
| RootDeviceType        | ebs                       |
| SourceDestCheck       | True                      |
| StateTransitionReason |                           |
| SubnetId              | subnet-30a75c4f           |
| VirtualizationType    | hvm                       |
| VpcId                 | vpc-7c4f2f1d              |


## Resource Tags

| Tag Key                   | Tag Value          |
| ------------------------- | ------------------ |
| aws:autoscaling:groupName | storefront-workers |
| service                   | storefront         |


### Blockdevicemappings

| DeviceName | Ebs                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| /dev/sda1  | {'AttachTime': '2026-10-16T01:29:13+00:00', 'DeleteOnTermination': True, 'Status': 'in-use', 'VolumeId': 'vol-2ccae71c'} |


### Monitoring

```json
{
  "State": "disabled"
}
```


### Networkinterfaces

| Attachment                                                                                                                                              | Description               | Groups                                                        | MacAddress        | NetworkInterfaceId | OwnerId      | PrivateIpAddress | PrivateIpAddresses                                  | SourceDestCheck | Status | SubnetId        | VpcId        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------- | ----------------- | ------------------ | ------------ | ---------------- | --------------------------------------------------- | --------------- | ------ | --------------- | ------------ |
| {'AttachTime': '2015-01-01T00:00:00+00:00', 'AttachmentId': 'eni-attach-44f95493', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'} | Primary network interface | [{'GroupId': 'sg-71a3ac0ec6bbd92b7', 'GroupName': 'default'}] | 1b:2b:3c:4d:5e:6f | eni-c468e79a       | 123456789012 | 10.0.1.5         | [{'Primary': True, 'PrivateIpAddress': '10.0.1.5'}] | True            | in-use | subnet-30a75c4f | vpc-7c4f2f1d |


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

# AWS Resource: `aws_vpc` - `vpc-7c4f2f1d`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_vpc                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d |
| Region            | us-east-1                                           |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-16T01:29:14Z                                |
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
| VpcId              | vpc-7c4f2f1d |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| Name    | orders-vpc |


### Cidrblockassociationset

| AssociationId           | CidrBlock   | CidrBlockState          |
| ----------------------- | ----------- | ----------------------- |
| vpc-cidr-assoc-3b8c2b77 | 10.0.0.0/16 | {'State': 'associated'} |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-71a3ac0ec6bbd92b7`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-71a3ac0ec6bbd92b7 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T01:29:14Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | default VPC security group |
| GroupId           | sg-71a3ac0ec6bbd92b7       |
| GroupName         | default                    |
| OwnerId           | 123456789012               |
| VpcId             | vpc-7c4f2f1d               |


### Ippermissions

```json
[]
```


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Tags

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-2edfb301c8a045aa8`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-2edfb301c8a045aa8 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T01:29:14Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Web tier             |
| GroupId           | sg-2edfb301c8a045aa8 |
| GroupName         | orders-web-sg        |
| OwnerId           | 123456789012         |
| VpcId             | vpc-7c4f2f1d         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs                                                |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | --------------------------------------------------------------- |
| 22       | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 22     | []                                                              |
| 5432     | tcp        | []                        | []         | []            | 5432   | [{'UserId': '123456789012', 'GroupId': 'sg-7c3a665620cbf02dc'}] |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Tags

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-c6ec367b2a800f7fe`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-c6ec367b2a800f7fe |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T01:29:14Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Public HTTPS         |
| GroupId           | sg-c6ec367b2a800f7fe |
| GroupName         | storefront-alb-sg    |
| OwnerId           | 123456789012         |
| VpcId             | vpc-7c4f2f1d         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | ---------------- |
| 443      | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 443    | []               |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Tags

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-7c3a665620cbf02dc`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c3a665620cbf02dc |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-16T01:29:14Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | Storefront tasks and cache |
| GroupId           | sg-7c3a665620cbf02dc       |
| GroupName         | storefront-app-sg          |
| OwnerId           | 123456789012               |
| VpcId             | vpc-7c4f2f1d               |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-app |
| service | storefront     |


### Ippermissions

| FromPort | IpProtocol | IpRanges | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs                                                |
| -------- | ---------- | -------- | ---------- | ------------- | ------ | --------------------------------------------------------------- |
| 80       | tcp        | []       | []         | []            | 80     | [{'UserId': '123456789012', 'GroupId': 'sg-c6ec367b2a800f7fe'}] |
| 6379     | tcp        | []       | []         | []            | 6379   | [{'UserId': '123456789012', 'GroupId': 'sg-7c3a665620cbf02dc'}] |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |



---

# AWS Resource: `aws_lambda_function` - `order-processor`

## Overview

| Property          | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| Resource Type     | aws_lambda_function                                            |
| ARN               | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| Region            | us-east-1                                                      |
| Account ID        | 123456789012                                                   |
| Collected At      | 2026-10-16T01:29:14Z                                           |
| Collector Version | 0.1.0                                                          |


## Configuration Specifications

| Configuration Key | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| CodeSha256        | 3oiA3dMfo6wNQA75emS05PR4Q703d3KNXUpZ1ykz1uU=                   |
| CodeSize          | 164                                                            |
| Description       |                                                                |
| FunctionArn       | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| FunctionName      | order-processor                                                |
| Handler           | handler.handler                                                |
| LastModified      | 2026-10-16T01:29:12.774833000Z                                 |
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
| Collected At      | 2026-10-16T01:29:14Z                            |
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
| InstanceCreateTime               | 2026-10-16T01:29:12.979000+00:00                |
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
      "SubnetIdentifier": "subnet-30a75c4f",
      "SubnetStatus": "Active"
    }
  ],
  "VpcId": "vpc-7c4f2f1d"
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
| active | sg-2edfb301c8a045aa8 |



---

# AWS Resource: `aws_cloudwatch_log_group` - `aws_lambda_order-processor`

## Overview

| Property          | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| Resource Type     | aws_cloudwatch_log_group                                                  |
| ARN               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| Region            | us-east-1                                                                 |
| Account ID        | 123456789012                                                              |
| Collected At      | 2026-10-16T01:29:14Z                                                      |
| Collector Version | 0.1.0                                                                     |


## Configuration Specifications

| Configuration Key | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| arn               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| creationTime      | 1792114152786                                                             |
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
| Collected At      | 2026-10-16T01:29:14Z                                              |
| Collector Version | 0.1.0                                                             |


## Configuration Specifications

| Configuration Key | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| arn               | arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web |
| creationTime      | 1792114153257                                                     |
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
| Collected At      | 2026-10-16T01:29:14Z                                          |
| Collector Version | 0.1.0                                                         |


## Configuration Specifications

| Configuration Key | Value                                                                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| creationDate      | 2026-10-16T01:29:12.824000+00:00                                                                                                                           |
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
| Collected At      | 2026-10-16T01:29:14Z                                 |
| Collector Version | 0.1.0                                                |


## Configuration Specifications

| Configuration Key | Value                                                |
| ----------------- | ---------------------------------------------------- |
| CreationDateTime  | 2026-10-16T08:29:12.764973+07:00                     |
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

# AWS Resource: `aws_subnet` - `subnet-30a75c4f`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-16T01:29:14Z                                      |
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
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f |
| SubnetId                    | subnet-30a75c4f                                           |
| VpcId                       | vpc-7c4f2f1d                                              |


## Resource Tags

| Tag Key | Tag Value        |
| ------- | ---------------- |
| Name    | orders-private-a |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_subnet` - `subnet-91c2dcc6`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6 |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-16T01:29:14Z                                      |
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
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6 |
| SubnetId                    | subnet-91c2dcc6                                           |
| VpcId                       | vpc-7c4f2f1d                                              |


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

# AWS Resource: `aws_subnet` - `subnet-9134f3a5`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-9134f3a5 |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-16T01:29:14Z                                      |
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
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-9134f3a5 |
| SubnetId                    | subnet-9134f3a5                                           |
| VpcId                       | vpc-7c4f2f1d                                              |


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

# AWS Resource: `aws_route_table` - `rtb-7bfbfaee`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-7bfbfaee |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T01:29:14Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-7bfbfaee |
| VpcId             | vpc-7c4f2f1d |


### Associations

| AssociationState        | Main | RouteTableAssociationId | RouteTableId |
| ----------------------- | ---- | ----------------------- | ------------ |
| {'State': 'associated'} | True | rtbassoc-69e3b0e3       | rtb-7bfbfaee |


### Routes

| DestinationCidrBlock | GatewayId | Origin           | State  |
| -------------------- | --------- | ---------------- | ------ |
| 10.0.0.0/16          | local     | CreateRouteTable | active |


### Tags

```json
[]
```



---

# AWS Resource: `aws_route_table` - `rtb-260c9780`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-260c9780 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T01:29:14Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-260c9780 |
| VpcId             | vpc-7c4f2f1d |


## Resource Tags

| Tag Key | Tag Value         |
| ------- | ----------------- |
| Name    | storefront-public |
| service | storefront        |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-f25d1101       | rtb-260c9780 | subnet-91c2dcc6 |
| {'State': 'associated'} | False | rtbassoc-51cd429a       | rtb-260c9780 | subnet-9134f3a5 |


### Routes

| DestinationCidrBlock | GatewayId    | Origin           | State  |
| -------------------- | ------------ | ---------------- | ------ |
| 10.0.0.0/16          | local        | CreateRouteTable | active |
| 0.0.0.0/0            | igw-dbc38f85 | CreateRoute      | active |



---

# AWS Resource: `aws_route_table` - `rtb-abf4c4b4`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T01:29:14Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-abf4c4b4 |
| VpcId             | vpc-7c4f2f1d |


## Resource Tags

| Tag Key | Tag Value          |
| ------- | ------------------ |
| Name    | storefront-private |
| service | storefront         |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-85544a58       | rtb-abf4c4b4 | subnet-30a75c4f |


### Routes

| DestinationCidrBlock | DestinationPrefixListId | GatewayId     | NatGatewayId          | Origin           | State  |
| -------------------- | ----------------------- | ------------- | --------------------- | ---------------- | ------ |
| 10.0.0.0/16          |                         | local         |                       | CreateRouteTable | active |
| 0.0.0.0/0            |                         |               | nat-60d1a0cf8c8f398eb | CreateRoute      | active |
|                      | pl-c6e0eb33             | vpce-55746589 |                       | CreateRoute      | active |



---

# AWS Resource: `aws_internet_gateway` - `igw-dbc38f85`

## Overview

| Property          | Value                                                            |
| ----------------- | ---------------------------------------------------------------- |
| Resource Type     | aws_internet_gateway                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-dbc38f85 |
| Region            | us-east-1                                                        |
| Account ID        | 123456789012                                                     |
| Collected At      | 2026-10-16T01:29:14Z                                             |
| Collector Version | 0.1.0                                                            |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| InternetGatewayId | igw-dbc38f85 |
| OwnerId           | 123456789012 |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-igw |
| service | storefront     |


### Attachments

| State     | VpcId        |
| --------- | ------------ |
| available | vpc-7c4f2f1d |



---

# AWS Resource: `aws_nat_gateway` - `nat-60d1a0cf8c8f398eb`

## Overview

| Property          | Value                                                               |
| ----------------- | ------------------------------------------------------------------- |
| Resource Type     | aws_nat_gateway                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:natgateway/nat-60d1a0cf8c8f398eb |
| Region            | us-east-1                                                           |
| Account ID        | 123456789012                                                        |
| Collected At      | 2026-10-16T01:29:14Z                                                |
| Collector Version | 0.1.0                                                               |


## Configuration Specifications

| Configuration Key | Value                            |
| ----------------- | -------------------------------- |
| ConnectivityType  | None                             |
| CreateTime        | 2026-10-16T01:29:13.013000+00:00 |
| NatGatewayId      | nat-60d1a0cf8c8f398eb            |
| State             | available                        |
| SubnetId          | subnet-91c2dcc6                  |
| VpcId             | vpc-7c4f2f1d                     |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-nat |
| service | storefront     |


### Natgatewayaddresses

| AllocationId      | AssociationId     | NetworkInterfaceId | PrivateIp     | PublicIp      |
| ----------------- | ----------------- | ------------------ | ------------- | ------------- |
| eipalloc-02aeeac1 | eipassoc-e467c180 | eni-6fe11400       | 10.190.162.51 | 127.97.164.56 |



---

# AWS Resource: `aws_vpc_endpoint` - `vpce-55746589`

## Overview

| Property          | Value                                                         |
| ----------------- | ------------------------------------------------------------- |
| Resource Type     | aws_vpc_endpoint                                              |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-55746589 |
| Region            | us-east-1                                                     |
| Account ID        | 123456789012                                                  |
| Collected At      | 2026-10-16T01:29:14Z                                          |
| Collector Version | 0.1.0                                                         |


## Configuration Specifications

| Configuration Key | Value                                                                                                           |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| CreationTimestamp | 2026-10-16T01:29:13+00:00                                                                                       |
| OwnerId           | 123456789012                                                                                                    |
| PolicyDocument    | {"Version": "2008-10-17", "Statement": [{"Effect": "Allow", "Principal": "*", "Action": "*", "Resource": "*"}]} |
| PrivateDnsEnabled | True                                                                                                            |
| ServiceName       | com.amazonaws.us-east-1.s3                                                                                      |
| State             | available                                                                                                       |
| VpcEndpointId     | vpce-55746589                                                                                                   |
| VpcEndpointType   | Gateway                                                                                                         |
| VpcId             | vpc-7c4f2f1d                                                                                                    |


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
  "rtb-abf4c4b4"
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
| Collected At      | 2026-10-16T01:29:14Z                                                                                 |
| Collector Version | 0.1.0                                                                                                |


## Configuration Specifications

| Configuration Key     | Value                                                                                                |
| --------------------- | ---------------------------------------------------------------------------------------------------- |
| CanonicalHostedZoneId | Z2P70J7EXAMPLE                                                                                       |
| CreatedTime           | 2026-10-16T01:29:13.124000+00:00                                                                     |
| DNSName               | storefront-alb-1.us-east-1.elb.amazonaws.com                                                         |
| IpAddressType         | ipv4                                                                                                 |
| LoadBalancerArn       | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188 |
| LoadBalancerName      | storefront-alb                                                                                       |
| Scheme                | internet-facing                                                                                      |
| Type                  | application                                                                                          |
| VpcId                 | vpc-7c4f2f1d                                                                                         |


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
| subnet-91c2dcc6 | us-east-1a |
| subnet-9134f3a5 | us-east-1b |


### Listeners

| AlpnPolicy | Certificates                                                                                                | DefaultActions                                                                                                                            | ListenerArn                                                                                                    | LoadBalancerArn                                                                                      | Port | Protocol | SslPolicy                 |
| ---------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---- | -------- | ------------------------- |
| []         | [{'CertificateArn': 'arn:aws:acm:us-east-1:123456789012:certificate/8f72f034-ca75-4120-acc5-f35a9fd3885d'}] | [{'Type': 'forward', 'TargetGroupArn': 'arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188'}] | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232 | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188 | 443  | HTTPS    | ELBSecurityPolicy-2016-08 |


### Securitygroups

```json
[
  "sg-c6ec367b2a800f7fe"
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
| Collected At      | 2026-10-16T01:29:14Z                                                                           |
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
| VpcId                      | vpc-7c4f2f1d                                                                                   |


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

# AWS Resource: `aws_acm_certificate` - `8f72f034-ca75-4120-acc5-f35a9fd3885d`

## Overview

| Property          | Value                                                                               |
| ----------------- | ----------------------------------------------------------------------------------- |
| Resource Type     | aws_acm_certificate                                                                 |
| ARN               | arn:aws:acm:us-east-1:123456789012:certificate/8f72f034-ca75-4120-acc5-f35a9fd3885d |
| Region            | us-east-1                                                                           |
| Account ID        | 123456789012                                                                        |
| Collected At      | 2026-10-16T01:29:14Z                                                                |
| Collector Version | 0.1.0                                                                               |


## Configuration Specifications

| Configuration Key  | Value                                                                               |
| ------------------ | ----------------------------------------------------------------------------------- |
| CertificateArn     | arn:aws:acm:us-east-1:123456789012:certificate/8f72f034-ca75-4120-acc5-f35a9fd3885d |
| CreatedAt          | 2026-10-16T01:29:13.081602+07:00                                                    |
| DomainName         | shop.example.com                                                                    |
| IssuedAt           | 2026-10-16T01:29:13.081602+07:00                                                    |
| Issuer             | Amazon                                                                              |
| KeyAlgorithm       | RSA_2048                                                                            |
| NotAfter           | 2027-10-16T01:29:13+07:00                                                           |
| NotBefore          | 2026-10-16T01:29:13+07:00                                                           |
| RenewalEligibility | INELIGIBLE                                                                          |
| Serial             | 355360776359447352577562696603512747964165224238                                    |
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
| api.example.com  | {'Name': '_d930b28be6c5927595552b219965053e.api.example.com.', 'Type': 'CNAME', 'Value': '_c9edd76ee4a0e2a74388032f3861cc50.ykybfrwcxw.acm-validations.aws.'}  | api.example.com  | DNS              | PENDING_VALIDATION |
| shop.example.com | {'Name': '_d930b28be6c5927595552b219965053e.shop.example.com.', 'Type': 'CNAME', 'Value': '_c9edd76ee4a0e2a74388032f3861cc50.ykybfrwcxw.acm-validations.aws.'} | shop.example.com | DNS              | PENDING_VALIDATION |


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
  "api.example.com",
  "shop.example.com"
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
| Collected At      | 2026-10-16T01:29:14Z                                  |
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
| Collected At      | 2026-10-16T01:29:14Z                                         |
| Collector Version | 0.1.0                                                        |


## Configuration Specifications

| Configuration Key  | Value                                                        |
| ------------------ | ------------------------------------------------------------ |
| createdAt          | 2026-10-16T01:29:13+00:00                                    |
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
| ARN               | arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers |
| Region            | us-east-1                                                                                                                                |
| Account ID        | 123456789012                                                                                                                             |
| Collected At      | 2026-10-16T01:29:14Z                                                                                                                     |
| Collector Version | 0.1.0                                                                                                                                    |


## Configuration Specifications

| Configuration Key                | Value                                                                                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| AutoScalingGroupARN              | arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers |
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
| VPCZoneIdentifier                | subnet-30a75c4f                                                                                                                          |


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
| us-east-1a       | Healthy      | i-7c15a7e2df90fa017 | t3.small     | {'LaunchTemplateId': 'lt-c743f2f076e986059', 'LaunchTemplateName': 'storefront-worker', 'Version': '$Default'} | InService      | False                |


### Launchtemplate

```json
{
  "LaunchTemplateId": "lt-c743f2f076e986059",
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

# AWS Resource: `aws_launch_template` - `lt-c743f2f076e986059`

## Overview

| Property          | Value                                                                   |
| ----------------- | ----------------------------------------------------------------------- |
| Resource Type     | aws_launch_template                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:launch-template/lt-c743f2f076e986059 |
| Region            | us-east-1                                                               |
| Account ID        | 123456789012                                                            |
| Collected At      | 2026-10-16T01:29:14Z                                                    |
| Collector Version | 0.1.0                                                                   |


## Configuration Specifications

| Configuration Key    | Value                          |
| -------------------- | ------------------------------ |
| CreateTime           | 2026-10-16T01:29:13+00:00      |
| CreatedBy            | arn:aws:iam::123456789012:root |
| DefaultVersionNumber | 1                              |
| LatestVersionNumber  | 1                              |
| LaunchTemplateId     | lt-c743f2f076e986059           |
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
    "sg-7c3a665620cbf02dc"
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
| Collected At      | 2026-10-16T01:29:14Z                                                         |
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
      "SecurityGroupId": "sg-7c3a665620cbf02dc",
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
      "SubnetIdentifier": "subnet-30a75c4f",
      "SupportedNetworkTypes": [
        "ipv4"
      ]
    }
  ],
  "SupportedNetworkTypes": [
    "ipv4"
  ],
  "VpcId": "vpc-7c4f2f1d"
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
| Collected At      | 2026-10-16T01:29:14Z                                 |
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
  "CreatedTimestamp": "1792114153.328186",
  "DelaySeconds": "0",
  "LastModifiedTimestamp": "1792114153.328186",
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
| Collected At      | 2026-10-16T01:29:14Z                                 |
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
| arn:aws:sqs:us-east-1:123456789012:storefront-orders | 123456789012 | sqs      | arn:aws:sns:us-east-1:123456789012:storefront-events:1803154f-633d-4e9c-bd9a-d16d528a9ee3 | arn:aws:sns:us-east-1:123456789012:storefront-events |



---

# AWS Resource: `aws_scheduler_schedule` - `default_storefront-cleanup`

## Overview

| Property          | Value                                                                        |
| ----------------- | ---------------------------------------------------------------------------- |
| Resource Type     | aws_scheduler_schedule                                                       |
| ARN               | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup |
| Region            | us-east-1                                                                    |
| Account ID        | 123456789012                                                                 |
| Collected At      | 2026-10-16T01:29:14Z                                                         |
| Collector Version | 0.1.0                                                                        |


## Configuration Specifications

| Configuration Key    | Value                                                                        |
| -------------------- | ---------------------------------------------------------------------------- |
| Arn                  | arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup |
| CreationDate         | 2026-10-16T08:29:13.520641+07:00                                             |
| Description          | Hourly cleanup message                                                       |
| GroupName            | default                                                                      |
| LastModificationDate | 2026-10-16T08:29:13.520641+07:00                                             |
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

# AWS Resource: `aws_lb_listener` - `app_storefront-alb_50dc6c495c0c9188_4434536313232`

## Overview

| Property          | Value                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_lb_listener                                                                                                |
| ARN               | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232 |
| Region            | us-east-1                                                                                                      |
| Account ID        | 123456789012                                                                                                   |
| Collected At      | 2026-10-16T01:29:14Z                                                                                           |
| Collector Version | 0.1.0                                                                                                          |


## Configuration Specifications

| Configuration Key | Value                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| ListenerArn       | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232 |
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
| arn:aws:acm:us-east-1:123456789012:certificate/8f72f034-ca75-4120-acc5-f35a9fd3885d |


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
| Collected At      | 2026-10-16T01:29:14Z                                      |
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
| 2026-10-16T08:29:13.277437+07:00 | 2            | ecs-svc/487704048739958131 | FARGATE    | 2            | 0            | PRIMARY | arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1 | 2026-10-16T08:29:13.277442+07:00 |


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
      "sg-7c3a665620cbf02dc"
    ],
    "subnets": [
      "subnet-30a75c4f"
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
| Collected At      | 2026-10-16T01:29:14Z                                                |
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
| Collected At      | 2026-10-16T01:29:14Z                                                 |
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
| Collected At      | 2026-10-16T01:29:14Z              |
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
| Collected At      | 2026-10-16T01:29:14Z           |
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

# AWS Resource: `aws_iam_role` - `order-lambda-role`

## Overview

| Property          | Value                                            |
| ----------------- | ------------------------------------------------ |
| Resource Type     | aws_iam_role                                     |
| ARN               | arn:aws:iam::123456789012:role/order-lambda-role |
| Region            | global                                           |
| Account ID        | 123456789012                                     |
| Collected At      | 2026-10-16T01:29:14Z                             |
| Collector Version | 0.1.0                                            |


## Configuration Specifications

| Configuration Key  | Value                                            |
| ------------------ | ------------------------------------------------ |
| Arn                | arn:aws:iam::123456789012:role/order-lambda-role |
| CreateDate         | 2026-10-16T01:29:12.737000+00:00                 |
| Description        | Execution role for order-processor               |
| MaxSessionDuration | 3600                                             |
| Path               | /                                                |
| RoleId             | AROARZPUZDIKDRE7FWEIT                            |
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

# AWS Resource: `aws_iam_role` - `storefront-task-role`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_iam_role                                        |
| ARN               | arn:aws:iam::123456789012:role/storefront-task-role |
| Region            | global                                              |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-16T01:29:14Z                                |
| Collector Version | 0.1.0                                               |


## Configuration Specifications

| Configuration Key  | Value                                               |
| ------------------ | --------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-task-role |
| CreateDate         | 2026-10-16T01:29:13.243000+00:00                    |
| MaxSessionDuration | 3600                                                |
| Path               | /                                                   |
| RoleId             | AROARZPUZDIKEO4SY26UU                               |
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
| Collected At      | 2026-10-16T01:29:14Z                                |
| Collector Version | 0.1.0                                               |


## Configuration Specifications

| Configuration Key  | Value                                               |
| ------------------ | --------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-exec-role |
| CreateDate         | 2026-10-16T01:29:13.247000+00:00                    |
| MaxSessionDuration | 3600                                                |
| Path               | /                                                   |
| RoleId             | AROARZPUZDIKHRFGVZ7IB                               |
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

# AWS Resource: `aws_iam_role` - `storefront-scheduler-role`

## Overview

| Property          | Value                                                    |
| ----------------- | -------------------------------------------------------- |
| Resource Type     | aws_iam_role                                             |
| ARN               | arn:aws:iam::123456789012:role/storefront-scheduler-role |
| Region            | global                                                   |
| Account ID        | 123456789012                                             |
| Collected At      | 2026-10-16T01:29:14Z                                     |
| Collector Version | 0.1.0                                                    |


## Configuration Specifications

| Configuration Key  | Value                                                    |
| ------------------ | -------------------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/storefront-scheduler-role |
| CreateDate         | 2026-10-16T01:29:13.251000+00:00                         |
| MaxSessionDuration | 3600                                                     |
| Path               | /                                                        |
| RoleId             | AROARZPUZDIKNQYKGUS4K                                    |
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

# AWS Resource: `aws_iam_role` - `orders-app-role`

## Overview

| Property          | Value                                          |
| ----------------- | ---------------------------------------------- |
| Resource Type     | aws_iam_role                                   |
| ARN               | arn:aws:iam::123456789012:role/orders-app-role |
| Region            | global                                         |
| Account ID        | 123456789012                                   |
| Collected At      | 2026-10-16T01:29:14Z                           |
| Collector Version | 0.1.0                                          |


## Configuration Specifications

| Configuration Key  | Value                                          |
| ------------------ | ---------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/orders-app-role |
| CreateDate         | 2026-10-16T01:29:12.729000+00:00               |
| MaxSessionDuration | 3600                                           |
| Path               | /                                              |
| RoleId             | AROARZPUZDIKNWJW7QSDR                          |
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

# AWS Resource: `aws_cloudfront_distribution` - `S8ZTDFP8H8PGF`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_cloudfront_distribution                                 |
| ARN               | arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF |
| Region            | global                                                      |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T01:29:14Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key             | Value                                                      |
| ----------------------------- | ---------------------------------------------------------- |
| ARN                           | arn:aws:cloudfront:123456789012:distribution/S8ZTDFP8H8PGF |
| DomainName                    | twzawhe0w7foo.cloudfront.net                               |
| Id                            | S8ZTDFP8H8PGF                                              |
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
  "WebACLId": "arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/1cbd8645-1348-4072-8b2e-633711042db1"
}
```



---

# AWS Resource: `aws_route53_zone` - `2VX36NXN28FIY7F`

## Overview

| Property          | Value                                        |
| ----------------- | -------------------------------------------- |
| Resource Type     | aws_route53_zone                             |
| ARN               | arn:aws:route53:::hostedzone/2VX36NXN28FIY7F |
| Region            | global                                       |
| Account ID        | 123456789012                                 |
| Collected At      | 2026-10-16T01:29:14Z                         |
| Collector Version | 0.1.0                                        |


## Configuration Specifications

| Configuration Key      | Value                       |
| ---------------------- | --------------------------- |
| CallerReference        | storefront                  |
| Id                     | /hostedzone/2VX36NXN28FIY7F |
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
| {'HostedZoneId': 'Z2FDTNDATAQYW2', 'DNSName': 'twzawhe0w7foo.cloudfront.net', 'EvaluateTargetHealth': False}                          | shop.example.com. |                                                                                                                                                    |        | A    |



---

# AWS Resource: `aws_wafv2_web_acl` - `storefront-waf_1cbd8645-1348-4072-8b2e-633711042db1`

## Overview

| Property          | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_wafv2_web_acl                                                                                   |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/1cbd8645-1348-4072-8b2e-633711042db1 |
| Region            | global                                                                                              |
| Account ID        | 123456789012                                                                                        |
| Collected At      | 2026-10-16T01:29:14Z                                                                                |
| Collector Version | 0.1.0                                                                                               |


## Configuration Specifications

| Configuration Key | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/1cbd8645-1348-4072-8b2e-633711042db1 |
| Description       | Edge protection for the storefront                                                                  |
| Id                | 1cbd8645-1348-4072-8b2e-633711042db1                                                                |
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
| Total Duration  | 3.92 hours (235 min)     | 1.01 seconds (0.0003 hrs) | 3.92 hours saved  |
| Efficiency Gain | Baseline (100%)          | +100.0% faster            | 100.0% time saved |
