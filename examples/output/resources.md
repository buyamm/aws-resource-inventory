# AWS Infrastructure Resource Inventory

**Generated:** 2026-10-15T16:01:58.140875Z  
**Total Resources Discovered:** 30

## Summary by Resource Type

| Resource Type               | Count |
| --------------------------- | ----- |
| aws_acm_certificate         | 1     |
| aws_cloudfront_distribution | 1     |
| aws_cloudwatch_log_group    | 1     |
| aws_db_instance             | 1     |
| aws_dynamodb_table          | 1     |
| aws_iam_role                | 2     |
| aws_instance                | 1     |
| aws_internet_gateway        | 1     |
| aws_lambda_function         | 1     |
| aws_lb                      | 1     |
| aws_lb_listener             | 1     |
| aws_lb_target_group         | 1     |
| aws_nat_gateway             | 1     |
| aws_route53_zone            | 1     |
| aws_route_table             | 3     |
| aws_s3_bucket               | 2     |
| aws_security_group          | 3     |
| aws_sfn_state_machine       | 1     |
| aws_subnet                  | 3     |
| aws_vpc                     | 1     |
| aws_vpc_endpoint            | 1     |
| aws_wafv2_web_acl           | 1     |


## Regional Distribution

| Region    | Resource Count |
| --------- | -------------- |
| global    | 7              |
| us-east-1 | 23             |


## Discovered Resources List

| Resource Type               | Identifier                                          | Region    | ARN                                                                                                            |
| --------------------------- | --------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------- |
| aws_instance                | i-96ebec6d01233d3d7                                 | us-east-1 | arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7                                                |
| aws_vpc                     | vpc-1561eea5                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5                                                            |
| aws_security_group          | sg-57d34a1b59fbd9d55                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-57d34a1b59fbd9d55                                         |
| aws_security_group          | sg-ceb6d3dc119d60702                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-ceb6d3dc119d60702                                         |
| aws_security_group          | sg-347a556c97894d9e4                                | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-347a556c97894d9e4                                         |
| aws_lambda_function         | order-processor                                     | us-east-1 | arn:aws:lambda:us-east-1:123456789012:function:order-processor                                                 |
| aws_db_instance             | orders-db                                           | us-east-1 | arn:aws:rds:us-east-1:123456789012:db:orders-db                                                                |
| aws_cloudwatch_log_group    | aws_lambda_order-processor                          | us-east-1 | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor                                      |
| aws_sfn_state_machine       | order-flow                                          | us-east-1 | arn:aws:states:us-east-1:123456789012:stateMachine:order-flow                                                  |
| aws_dynamodb_table          | orders                                              | us-east-1 | arn:aws:dynamodb:us-east-1:123456789012:table/orders                                                           |
| aws_subnet                  | subnet-86551e9d                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-86551e9d                                                      |
| aws_subnet                  | subnet-dc94c752                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752                                                      |
| aws_subnet                  | subnet-ee0601cc                                     | us-east-1 | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-ee0601cc                                                      |
| aws_route_table             | rtb-57076453                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-57076453                                                    |
| aws_route_table             | rtb-395e2831                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-395e2831                                                    |
| aws_route_table             | rtb-590d89f0                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590d89f0                                                    |
| aws_internet_gateway        | igw-e27d9033                                        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-e27d9033                                               |
| aws_nat_gateway             | nat-3e17f5a22ce211a96                               | us-east-1 | arn:aws:ec2:us-east-1:123456789012:natgateway/nat-3e17f5a22ce211a96                                            |
| aws_vpc_endpoint            | vpce-a3573b69                                       | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-a3573b69                                                  |
| aws_lb                      | app_storefront-alb_50dc6c495c0c9188                 | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188           |
| aws_lb_target_group         | storefront-tg_50dc6c495c0c9188                      | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188                 |
| aws_acm_certificate         | 59f7c298-c41f-48f5-a3db-cb8263d5fcc6                | us-east-1 | arn:aws:acm:us-east-1:123456789012:certificate/59f7c298-c41f-48f5-a3db-cb8263d5fcc6                            |
| aws_lb_listener             | app_storefront-alb_50dc6c495c0c9188_4434430983056   | us-east-1 | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434430983056 |
| aws_s3_bucket               | orders-public-assets                                | global    | arn:aws:s3:::orders-public-assets                                                                              |
| aws_s3_bucket               | storefront-static                                   | global    | arn:aws:s3:::storefront-static                                                                                 |
| aws_iam_role                | order-lambda-role                                   | global    | arn:aws:iam::123456789012:role/order-lambda-role                                                               |
| aws_iam_role                | orders-app-role                                     | global    | arn:aws:iam::123456789012:role/orders-app-role                                                                 |
| aws_cloudfront_distribution | K4SJFH541UU7J                                       | global    | arn:aws:cloudfront::123456789012:distribution/K4SJFH541UU7J                                                    |
| aws_route53_zone            | JX2QH3ZSOFDJU6N                                     | global    | arn:aws:route53:::hostedzone/JX2QH3ZSOFDJU6N                                                                   |
| aws_wafv2_web_acl           | storefront-waf_45c1df2a-6eb9-40fa-a6ea-d3054f42d04c | global    | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/45c1df2a-6eb9-40fa-a6ea-d3054f42d04c            |


## Detailed Resource Specifications

# AWS Resource: `aws_instance` - `i-96ebec6d01233d3d7`

## Overview

| Property          | Value                                                           |
| ----------------- | --------------------------------------------------------------- |
| Resource Type     | aws_instance                                                    |
| ARN               | arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7 |
| Region            | us-east-1                                                       |
| Account ID        | 123456789012                                                    |
| Collected At      | 2026-10-15T16:01:57Z                                            |
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
| InstanceId            | i-96ebec6d01233d3d7       |
| InstanceType          | t3.micro                  |
| KernelId              | None                      |
| LaunchTime            | 2026-10-15T16:01:56+00:00 |
| Platform              | windows                   |
| PrivateDnsName        | ip-10-0-1-4.ec2.internal  |
| PrivateIpAddress      | 10.0.1.4                  |
| PublicDnsName         | None                      |
| RootDeviceName        | /dev/sda1                 |
| RootDeviceType        | ebs                       |
| SourceDestCheck       | True                      |
| StateTransitionReason |                           |
| SubnetId              | subnet-86551e9d           |
| VirtualizationType    | hvm                       |
| VpcId                 | vpc-1561eea5              |


## Resource Tags

| Tag Key | Tag Value    |
| ------- | ------------ |
| Name    | orders-web-1 |


### Blockdevicemappings

| DeviceName | Ebs                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| /dev/sda1  | {'AttachTime': '2026-10-15T16:01:56+00:00', 'DeleteOnTermination': True, 'Status': 'in-use', 'VolumeId': 'vol-4fd9a55f'} |


### Iaminstanceprofile

```json
{
  "Arn": "arn:aws:iam::123456789012:instance-profile/orders-app-role",
  "Id": "iip-assoc-fd82cc70"
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
| {'AttachTime': '2015-01-01T00:00:00+00:00', 'AttachmentId': 'eni-attach-27fef115', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'} | Primary network interface | [{'GroupId': 'sg-ceb6d3dc119d60702', 'GroupName': 'orders-web-sg'}] | 1b:2b:3c:4d:5e:6f | eni-64dfa24f       | 123456789012 | 10.0.1.4         | [{'Primary': True, 'PrivateIpAddress': '10.0.1.4'}] | True            | in-use | subnet-86551e9d | vpc-1561eea5 |


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
| sg-ceb6d3dc119d60702 | orders-web-sg |


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

# AWS Resource: `aws_vpc` - `vpc-1561eea5`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_vpc                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5 |
| Region            | us-east-1                                           |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-15T16:01:57Z                                |
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
| VpcId              | vpc-1561eea5 |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| Name    | orders-vpc |


### Cidrblockassociationset

| AssociationId           | CidrBlock   | CidrBlockState          |
| ----------------------- | ----------- | ----------------------- |
| vpc-cidr-assoc-1445e8d5 | 10.0.0.0/16 | {'State': 'associated'} |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-57d34a1b59fbd9d55`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-57d34a1b59fbd9d55 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-15T16:01:57Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | default VPC security group |
| GroupId           | sg-57d34a1b59fbd9d55       |
| GroupName         | default                    |
| OwnerId           | 123456789012               |
| VpcId             | vpc-1561eea5               |


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

# AWS Resource: `aws_security_group` - `sg-ceb6d3dc119d60702`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-ceb6d3dc119d60702 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-15T16:01:57Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Web tier             |
| GroupId           | sg-ceb6d3dc119d60702 |
| GroupName         | orders-web-sg        |
| OwnerId           | 123456789012         |
| VpcId             | vpc-1561eea5         |


### Ippermissions

| FromPort | IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | ToPort | UserIdGroupPairs |
| -------- | ---------- | ------------------------- | ---------- | ------------- | ------ | ---------------- |
| 22       | tcp        | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | 22     | []               |


### Ippermissionsegress

| IpProtocol | IpRanges                  | Ipv6Ranges | PrefixListIds | UserIdGroupPairs |
| ---------- | ------------------------- | ---------- | ------------- | ---------------- |
| -1         | [{'CidrIp': '0.0.0.0/0'}] | []         | []            | []               |


### Tags

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-347a556c97894d9e4`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-347a556c97894d9e4 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-15T16:01:57Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Public HTTPS         |
| GroupId           | sg-347a556c97894d9e4 |
| GroupName         | storefront-alb-sg    |
| OwnerId           | 123456789012         |
| VpcId             | vpc-1561eea5         |


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

# AWS Resource: `aws_lambda_function` - `order-processor`

## Overview

| Property          | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| Resource Type     | aws_lambda_function                                            |
| ARN               | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| Region            | us-east-1                                                      |
| Account ID        | 123456789012                                                   |
| Collected At      | 2026-10-15T16:01:57Z                                           |
| Collector Version | 0.1.0                                                          |


## Configuration Specifications

| Configuration Key | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| CodeSha256        | waOhCdKJrCL2WZOuy/VNi88bTRKaUrp+2whtIFlUFf8=                   |
| CodeSize          | 164                                                            |
| Description       |                                                                |
| FunctionArn       | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| FunctionName      | order-processor                                                |
| Handler           | handler.handler                                                |
| LastModified      | 2026-10-15T16:01:56.987439000Z                                 |
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
| Collected At      | 2026-10-15T16:01:58Z                            |
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
| InstanceCreateTime               | 2026-10-15T16:01:57.045000+00:00                |
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
| active | sg-ceb6d3dc119d60702 |



---

# AWS Resource: `aws_cloudwatch_log_group` - `aws_lambda_order-processor`

## Overview

| Property          | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| Resource Type     | aws_cloudwatch_log_group                                                  |
| ARN               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| Region            | us-east-1                                                                 |
| Account ID        | 123456789012                                                              |
| Collected At      | 2026-10-15T16:01:57Z                                                      |
| Collector Version | 0.1.0                                                                     |


## Configuration Specifications

| Configuration Key | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| arn               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| creationTime      | 1792080116997                                                             |
| logGroupName      | /aws/lambda/order-processor                                               |
| metricFilterCount | 0                                                                         |
| retentionInDays   | 14                                                                        |
| storedBytes       | 0                                                                         |


## Resource Tags

| Tag Key | Tag Value |
| ------- | --------- |
| team    | orders    |



---

# AWS Resource: `aws_sfn_state_machine` - `order-flow`

## Overview

| Property          | Value                                                         |
| ----------------- | ------------------------------------------------------------- |
| Resource Type     | aws_sfn_state_machine                                         |
| ARN               | arn:aws:states:us-east-1:123456789012:stateMachine:order-flow |
| Region            | us-east-1                                                     |
| Account ID        | 123456789012                                                  |
| Collected At      | 2026-10-15T16:01:57Z                                          |
| Collector Version | 0.1.0                                                         |


## Configuration Specifications

| Configuration Key | Value                                                                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| creationDate      | 2026-10-15T16:01:57.031000+00:00                                                                                                                           |
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
| Collected At      | 2026-10-15T16:01:58Z                                 |
| Collector Version | 0.1.0                                                |


## Configuration Specifications

| Configuration Key | Value                                                |
| ----------------- | ---------------------------------------------------- |
| CreationDateTime  | 2026-10-15T23:01:56.977657+07:00                     |
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

# AWS Resource: `aws_subnet` - `subnet-86551e9d`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-86551e9d |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-15T16:01:58Z                                      |
| Collector Version | 0.1.0                                                     |


## Configuration Specifications

| Configuration Key           | Value                                                     |
| --------------------------- | --------------------------------------------------------- |
| AssignIpv6AddressOnCreation | False                                                     |
| AvailabilityZone            | us-east-1a                                                |
| AvailabilityZoneId          | use1-az6                                                  |
| AvailableIpAddressCount     | 250                                                       |
| CidrBlock                   | 10.0.1.0/24                                               |
| DefaultForAz                | False                                                     |
| Ipv6Native                  | False                                                     |
| MapPublicIpOnLaunch         | False                                                     |
| OwnerId                     | 123456789012                                              |
| State                       | available                                                 |
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-86551e9d |
| SubnetId                    | subnet-86551e9d                                           |
| VpcId                       | vpc-1561eea5                                              |


## Resource Tags

| Tag Key | Tag Value        |
| ------- | ---------------- |
| Name    | orders-private-a |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_subnet` - `subnet-dc94c752`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752 |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-15T16:01:58Z                                      |
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
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752 |
| SubnetId                    | subnet-dc94c752                                           |
| VpcId                       | vpc-1561eea5                                              |


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

# AWS Resource: `aws_subnet` - `subnet-ee0601cc`

## Overview

| Property          | Value                                                     |
| ----------------- | --------------------------------------------------------- |
| Resource Type     | aws_subnet                                                |
| ARN               | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-ee0601cc |
| Region            | us-east-1                                                 |
| Account ID        | 123456789012                                              |
| Collected At      | 2026-10-15T16:01:58Z                                      |
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
| SubnetArn                   | arn:aws:ec2:us-east-1:123456789012:subnet/subnet-ee0601cc |
| SubnetId                    | subnet-ee0601cc                                           |
| VpcId                       | vpc-1561eea5                                              |


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

# AWS Resource: `aws_route_table` - `rtb-57076453`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-57076453 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-15T16:01:58Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-57076453 |
| VpcId             | vpc-1561eea5 |


### Associations

| AssociationState        | Main | RouteTableAssociationId | RouteTableId |
| ----------------------- | ---- | ----------------------- | ------------ |
| {'State': 'associated'} | True | rtbassoc-063aebf2       | rtb-57076453 |


### Routes

| DestinationCidrBlock | GatewayId | Origin           | State  |
| -------------------- | --------- | ---------------- | ------ |
| 10.0.0.0/16          | local     | CreateRouteTable | active |


### Tags

```json
[]
```



---

# AWS Resource: `aws_route_table` - `rtb-395e2831`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-395e2831 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-15T16:01:58Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-395e2831 |
| VpcId             | vpc-1561eea5 |


## Resource Tags

| Tag Key | Tag Value         |
| ------- | ----------------- |
| Name    | storefront-public |
| service | storefront        |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-4ed8ef43       | rtb-395e2831 | subnet-dc94c752 |
| {'State': 'associated'} | False | rtbassoc-e27cd101       | rtb-395e2831 | subnet-ee0601cc |


### Routes

| DestinationCidrBlock | GatewayId    | Origin           | State  |
| -------------------- | ------------ | ---------------- | ------ |
| 10.0.0.0/16          | local        | CreateRouteTable | active |
| 0.0.0.0/0            | igw-e27d9033 | CreateRoute      | active |



---

# AWS Resource: `aws_route_table` - `rtb-590d89f0`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590d89f0 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-15T16:01:58Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-590d89f0 |
| VpcId             | vpc-1561eea5 |


## Resource Tags

| Tag Key | Tag Value          |
| ------- | ------------------ |
| Name    | storefront-private |
| service | storefront         |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-497b00d3       | rtb-590d89f0 | subnet-86551e9d |


### Routes

| DestinationCidrBlock | DestinationPrefixListId | GatewayId     | NatGatewayId          | Origin           | State  |
| -------------------- | ----------------------- | ------------- | --------------------- | ---------------- | ------ |
| 10.0.0.0/16          |                         | local         |                       | CreateRouteTable | active |
| 0.0.0.0/0            |                         |               | nat-3e17f5a22ce211a96 | CreateRoute      | active |
|                      | pl-cc234682             | vpce-a3573b69 |                       | CreateRoute      | active |



---

# AWS Resource: `aws_internet_gateway` - `igw-e27d9033`

## Overview

| Property          | Value                                                            |
| ----------------- | ---------------------------------------------------------------- |
| Resource Type     | aws_internet_gateway                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-e27d9033 |
| Region            | us-east-1                                                        |
| Account ID        | 123456789012                                                     |
| Collected At      | 2026-10-15T16:01:58Z                                             |
| Collector Version | 0.1.0                                                            |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| InternetGatewayId | igw-e27d9033 |
| OwnerId           | 123456789012 |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-igw |
| service | storefront     |


### Attachments

| State     | VpcId        |
| --------- | ------------ |
| available | vpc-1561eea5 |



---

# AWS Resource: `aws_nat_gateway` - `nat-3e17f5a22ce211a96`

## Overview

| Property          | Value                                                               |
| ----------------- | ------------------------------------------------------------------- |
| Resource Type     | aws_nat_gateway                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:natgateway/nat-3e17f5a22ce211a96 |
| Region            | us-east-1                                                           |
| Account ID        | 123456789012                                                        |
| Collected At      | 2026-10-15T16:01:58Z                                                |
| Collector Version | 0.1.0                                                               |


## Configuration Specifications

| Configuration Key | Value                            |
| ----------------- | -------------------------------- |
| ConnectivityType  | None                             |
| CreateTime        | 2026-10-15T16:01:57.149000+00:00 |
| NatGatewayId      | nat-3e17f5a22ce211a96            |
| State             | available                        |
| SubnetId          | subnet-dc94c752                  |
| VpcId             | vpc-1561eea5                     |


## Resource Tags

| Tag Key | Tag Value      |
| ------- | -------------- |
| Name    | storefront-nat |
| service | storefront     |


### Natgatewayaddresses

| AllocationId      | AssociationId     | NetworkInterfaceId | PrivateIp      | PublicIp        |
| ----------------- | ----------------- | ------------------ | -------------- | --------------- |
| eipalloc-df1cdc26 | eipassoc-19f138f8 | eni-8085a8fe       | 10.166.137.104 | 127.223.174.226 |



---

# AWS Resource: `aws_vpc_endpoint` - `vpce-a3573b69`

## Overview

| Property          | Value                                                         |
| ----------------- | ------------------------------------------------------------- |
| Resource Type     | aws_vpc_endpoint                                              |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-a3573b69 |
| Region            | us-east-1                                                     |
| Account ID        | 123456789012                                                  |
| Collected At      | 2026-10-15T16:01:58Z                                          |
| Collector Version | 0.1.0                                                         |


## Configuration Specifications

| Configuration Key | Value                                                                                                           |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| CreationTimestamp | 2026-10-15T16:01:57+00:00                                                                                       |
| OwnerId           | 123456789012                                                                                                    |
| PolicyDocument    | {"Version": "2008-10-17", "Statement": [{"Effect": "Allow", "Principal": "*", "Action": "*", "Resource": "*"}]} |
| PrivateDnsEnabled | True                                                                                                            |
| ServiceName       | com.amazonaws.us-east-1.s3                                                                                      |
| State             | available                                                                                                       |
| VpcEndpointId     | vpce-a3573b69                                                                                                   |
| VpcEndpointType   | Gateway                                                                                                         |
| VpcId             | vpc-1561eea5                                                                                                    |


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
  "rtb-590d89f0"
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
| Collected At      | 2026-10-15T16:01:58Z                                                                                 |
| Collector Version | 0.1.0                                                                                                |


## Configuration Specifications

| Configuration Key     | Value                                                                                                |
| --------------------- | ---------------------------------------------------------------------------------------------------- |
| CanonicalHostedZoneId | Z2P70J7EXAMPLE                                                                                       |
| CreatedTime           | 2026-10-15T16:01:57.250000+00:00                                                                     |
| DNSName               | storefront-alb-1.us-east-1.elb.amazonaws.com                                                         |
| IpAddressType         | ipv4                                                                                                 |
| LoadBalancerArn       | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188 |
| LoadBalancerName      | storefront-alb                                                                                       |
| Scheme                | internet-facing                                                                                      |
| Type                  | application                                                                                          |
| VpcId                 | vpc-1561eea5                                                                                         |


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
| subnet-dc94c752 | us-east-1a |
| subnet-ee0601cc | us-east-1b |


### Listeners

| AlpnPolicy | Certificates                                                                                                | DefaultActions                                                                                                                            | ListenerArn                                                                                                    | LoadBalancerArn                                                                                      | Port | Protocol | SslPolicy                 |
| ---------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---- | -------- | ------------------------- |
| []         | [{'CertificateArn': 'arn:aws:acm:us-east-1:123456789012:certificate/59f7c298-c41f-48f5-a3db-cb8263d5fcc6'}] | [{'Type': 'forward', 'TargetGroupArn': 'arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188'}] | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434430983056 | arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188 | 443  | HTTPS    | ELBSecurityPolicy-2016-08 |


### Securitygroups

```json
[
  "sg-347a556c97894d9e4"
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
| Collected At      | 2026-10-15T16:01:58Z                                                                           |
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
| VpcId                      | vpc-1561eea5                                                                                   |


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

# AWS Resource: `aws_acm_certificate` - `59f7c298-c41f-48f5-a3db-cb8263d5fcc6`

## Overview

| Property          | Value                                                                               |
| ----------------- | ----------------------------------------------------------------------------------- |
| Resource Type     | aws_acm_certificate                                                                 |
| ARN               | arn:aws:acm:us-east-1:123456789012:certificate/59f7c298-c41f-48f5-a3db-cb8263d5fcc6 |
| Region            | us-east-1                                                                           |
| Account ID        | 123456789012                                                                        |
| Collected At      | 2026-10-15T16:01:58Z                                                                |
| Collector Version | 0.1.0                                                                               |


## Configuration Specifications

| Configuration Key  | Value                                                                               |
| ------------------ | ----------------------------------------------------------------------------------- |
| CertificateArn     | arn:aws:acm:us-east-1:123456789012:certificate/59f7c298-c41f-48f5-a3db-cb8263d5fcc6 |
| CreatedAt          | 2026-10-15T16:01:57.207985+07:00                                                    |
| DomainName         | shop.example.com                                                                    |
| IssuedAt           | 2026-10-15T16:01:57.207985+07:00                                                    |
| Issuer             | Amazon                                                                              |
| KeyAlgorithm       | RSA_2048                                                                            |
| NotAfter           | 2027-10-15T16:01:57+07:00                                                           |
| NotBefore          | 2026-10-15T16:01:57+07:00                                                           |
| RenewalEligibility | INELIGIBLE                                                                          |
| Serial             | 67421154526262129659220035070403335987261677817                                     |
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

# AWS Resource: `aws_lb_listener` - `app_storefront-alb_50dc6c495c0c9188_4434430983056`

## Overview

| Property          | Value                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_lb_listener                                                                                                |
| ARN               | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434430983056 |
| Region            | us-east-1                                                                                                      |
| Account ID        | 123456789012                                                                                                   |
| Collected At      | 2026-10-15T16:01:58Z                                                                                           |
| Collector Version | 0.1.0                                                                                                          |


## Configuration Specifications

| Configuration Key | Value                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| ListenerArn       | arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434430983056 |
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
| arn:aws:acm:us-east-1:123456789012:certificate/59f7c298-c41f-48f5-a3db-cb8263d5fcc6 |


### Defaultactions

| TargetGroupArn                                                                                 | Type    |
| ---------------------------------------------------------------------------------------------- | ------- |
| arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188 | forward |


### Tags

```json
[]
```



---

# AWS Resource: `aws_s3_bucket` - `orders-public-assets`

## Overview

| Property          | Value                             |
| ----------------- | --------------------------------- |
| Resource Type     | aws_s3_bucket                     |
| ARN               | arn:aws:s3:::orders-public-assets |
| Region            | global                            |
| Account ID        | 123456789012                      |
| Collected At      | 2026-10-15T16:01:58Z              |
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
| Collected At      | 2026-10-15T16:01:58Z           |
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
| Collected At      | 2026-10-15T16:01:58Z                             |
| Collector Version | 0.1.0                                            |


## Configuration Specifications

| Configuration Key  | Value                                            |
| ------------------ | ------------------------------------------------ |
| Arn                | arn:aws:iam::123456789012:role/order-lambda-role |
| CreateDate         | 2026-10-15T16:01:56.952000+00:00                 |
| Description        | Execution role for order-processor               |
| MaxSessionDuration | 3600                                             |
| Path               | /                                                |
| RoleId             | AROARZPUZDIKI6U4TOXCB                            |
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

# AWS Resource: `aws_iam_role` - `orders-app-role`

## Overview

| Property          | Value                                          |
| ----------------- | ---------------------------------------------- |
| Resource Type     | aws_iam_role                                   |
| ARN               | arn:aws:iam::123456789012:role/orders-app-role |
| Region            | global                                         |
| Account ID        | 123456789012                                   |
| Collected At      | 2026-10-15T16:01:58Z                           |
| Collector Version | 0.1.0                                          |


## Configuration Specifications

| Configuration Key  | Value                                          |
| ------------------ | ---------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/orders-app-role |
| CreateDate         | 2026-10-15T16:01:56.945000+00:00               |
| MaxSessionDuration | 3600                                           |
| Path               | /                                              |
| RoleId             | AROARZPUZDIKPSYQ3UTIG                          |
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

# AWS Resource: `aws_cloudfront_distribution` - `K4SJFH541UU7J`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_cloudfront_distribution                                 |
| ARN               | arn:aws:cloudfront::123456789012:distribution/K4SJFH541UU7J |
| Region            | global                                                      |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-15T16:01:58Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key             | Value                                                      |
| ----------------------------- | ---------------------------------------------------------- |
| ARN                           | arn:aws:cloudfront:123456789012:distribution/K4SJFH541UU7J |
| DomainName                    | v7hl68ilxwkby.cloudfront.net                               |
| Id                            | K4SJFH541UU7J                                              |
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
  "WebACLId": "arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/45c1df2a-6eb9-40fa-a6ea-d3054f42d04c"
}
```



---

# AWS Resource: `aws_route53_zone` - `JX2QH3ZSOFDJU6N`

## Overview

| Property          | Value                                        |
| ----------------- | -------------------------------------------- |
| Resource Type     | aws_route53_zone                             |
| ARN               | arn:aws:route53:::hostedzone/JX2QH3ZSOFDJU6N |
| Region            | global                                       |
| Account ID        | 123456789012                                 |
| Collected At      | 2026-10-15T16:01:58Z                         |
| Collector Version | 0.1.0                                        |


## Configuration Specifications

| Configuration Key      | Value                       |
| ---------------------- | --------------------------- |
| CallerReference        | storefront                  |
| Id                     | /hostedzone/JX2QH3ZSOFDJU6N |
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
| {'HostedZoneId': 'Z2FDTNDATAQYW2', 'DNSName': 'v7hl68ilxwkby.cloudfront.net', 'EvaluateTargetHealth': False}                          | shop.example.com. |                                                                                                                                                    |        | A    |



---

# AWS Resource: `aws_wafv2_web_acl` - `storefront-waf_45c1df2a-6eb9-40fa-a6ea-d3054f42d04c`

## Overview

| Property          | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_wafv2_web_acl                                                                                   |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/45c1df2a-6eb9-40fa-a6ea-d3054f42d04c |
| Region            | global                                                                                              |
| Account ID        | 123456789012                                                                                        |
| Collected At      | 2026-10-15T16:01:58Z                                                                                |
| Collector Version | 0.1.0                                                                                               |


## Configuration Specifications

| Configuration Key | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/45c1df2a-6eb9-40fa-a6ea-d3054f42d04c |
| Description       | Edge protection for the storefront                                                                  |
| Id                | 45c1df2a-6eb9-40fa-a6ea-d3054f42d04c                                                                |
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
| Total Resources | 30                       | 30                        | -                 |
| Total Duration  | 2.50 hours (150 min)     | 0.69 seconds (0.0002 hrs) | 2.50 hours saved  |
| Efficiency Gain | Baseline (100%)          | +100.0% faster            | 100.0% time saved |
