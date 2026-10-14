# AWS Infrastructure Resource Inventory

**Generated:** 2026-10-14T16:28:57.357964Z  
**Total Resources Discovered:** 14

## Summary by Resource Type

| Resource Type            | Count |
| ------------------------ | ----- |
| aws_cloudwatch_log_group | 1     |
| aws_db_instance          | 1     |
| aws_dynamodb_table       | 1     |
| aws_iam_role             | 2     |
| aws_instance             | 1     |
| aws_lambda_function      | 1     |
| aws_s3_bucket            | 1     |
| aws_security_group       | 3     |
| aws_sfn_state_machine    | 1     |
| aws_vpc                  | 2     |


## Regional Distribution

| Region    | Resource Count |
| --------- | -------------- |
| global    | 3              |
| us-east-1 | 11             |


## Discovered Resources List

| Resource Type            | Identifier                 | Region    | ARN                                                                       |
| ------------------------ | -------------------------- | --------- | ------------------------------------------------------------------------- |
| aws_instance             | i-9f9c49245e711cdd9        | us-east-1 | arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9           |
| aws_vpc                  | vpc-ce9c3403               | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-ce9c3403                       |
| aws_vpc                  | vpc-db407a2e               | us-east-1 | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e                       |
| aws_security_group       | sg-285ba61d10f344e74       | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-285ba61d10f344e74    |
| aws_security_group       | sg-cc3138f31141d30f1       | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-cc3138f31141d30f1    |
| aws_security_group       | sg-7c880b8c4789c2216       | us-east-1 | arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216    |
| aws_lambda_function      | order-processor            | us-east-1 | arn:aws:lambda:us-east-1:123456789012:function:order-processor            |
| aws_db_instance          | orders-db                  | us-east-1 | arn:aws:rds:us-east-1:123456789012:db:orders-db                           |
| aws_cloudwatch_log_group | aws_lambda_order-processor | us-east-1 | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| aws_sfn_state_machine    | order-flow                 | us-east-1 | arn:aws:states:us-east-1:123456789012:stateMachine:order-flow             |
| aws_dynamodb_table       | orders                     | us-east-1 | arn:aws:dynamodb:us-east-1:123456789012:table/orders                      |
| aws_s3_bucket            | orders-public-assets       | global    | arn:aws:s3:::orders-public-assets                                         |
| aws_iam_role             | orders-app-role            | global    | arn:aws:iam::123456789012:role/orders-app-role                            |
| aws_iam_role             | order-lambda-role          | global    | arn:aws:iam::123456789012:role/order-lambda-role                          |


## Detailed Resource Specifications

# AWS Resource: `aws_instance` - `i-9f9c49245e711cdd9`

## Overview

| Property          | Value                                                           |
| ----------------- | --------------------------------------------------------------- |
| Resource Type     | aws_instance                                                    |
| ARN               | arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9 |
| Region            | us-east-1                                                       |
| Account ID        | 123456789012                                                    |
| Collected At      | 2026-10-14T16:28:57Z                                            |
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
| InstanceId            | i-9f9c49245e711cdd9       |
| InstanceType          | t3.micro                  |
| KernelId              | None                      |
| LaunchTime            | 2026-10-14T16:28:56+00:00 |
| Platform              | windows                   |
| PrivateDnsName        | ip-10-0-1-4.ec2.internal  |
| PrivateIpAddress      | 10.0.1.4                  |
| PublicDnsName         | None                      |
| RootDeviceName        | /dev/sda1                 |
| RootDeviceType        | ebs                       |
| SourceDestCheck       | True                      |
| StateTransitionReason |                           |
| SubnetId              | subnet-c9c0ff4e           |
| VirtualizationType    | hvm                       |
| VpcId                 | vpc-db407a2e              |


## Resource Tags

| Tag Key | Tag Value    |
| ------- | ------------ |
| Name    | orders-web-1 |


### Blockdevicemappings

| DeviceName | Ebs                                                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| /dev/sda1  | {'AttachTime': '2026-10-14T16:28:56+00:00', 'DeleteOnTermination': True, 'Status': 'in-use', 'VolumeId': 'vol-19553091'} |


### Iaminstanceprofile

```json
{
  "Arn": "arn:aws:iam::123456789012:instance-profile/orders-app-role",
  "Id": "iip-assoc-98e5e1a0"
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
| {'AttachTime': '2015-01-01T00:00:00+00:00', 'AttachmentId': 'eni-attach-3b59f78e', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'} | Primary network interface | [{'GroupId': 'sg-7c880b8c4789c2216', 'GroupName': 'orders-web-sg'}] | 1b:2b:3c:4d:5e:6f | eni-65f758fc       | 123456789012 | 10.0.1.4         | [{'Primary': True, 'PrivateIpAddress': '10.0.1.4'}] | True            | in-use | subnet-c9c0ff4e | vpc-db407a2e |


### Placement

```json
{
  "AvailabilityZone": "us-east-1b",
  "GroupName": "",
  "Tenancy": "default"
}
```


### Securitygroups

| GroupId              | GroupName     |
| -------------------- | ------------- |
| sg-7c880b8c4789c2216 | orders-web-sg |


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

# AWS Resource: `aws_vpc` - `vpc-ce9c3403`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_vpc                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-ce9c3403 |
| Region            | us-east-1                                           |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-14T16:28:57Z                                |
| Collector Version | 0.1.0                                               |


## Configuration Specifications

| Configuration Key  | Value         |
| ------------------ | ------------- |
| CidrBlock          | 172.31.0.0/16 |
| DhcpOptionsId      | default       |
| EnableDnsHostnames | True          |
| EnableDnsSupport   | True          |
| InstanceTenancy    | default       |
| IsDefault          | True          |
| OwnerId            | 123456789012  |
| State              | available     |
| VpcId              | vpc-ce9c3403  |


### Cidrblockassociationset

| AssociationId           | CidrBlock     | CidrBlockState          |
| ----------------------- | ------------- | ----------------------- |
| vpc-cidr-assoc-93acd175 | 172.31.0.0/16 | {'State': 'associated'} |


### Ipv6Cidrblockassociationset

```json
[]
```


### Tags

```json
[]
```



---

# AWS Resource: `aws_vpc` - `vpc-db407a2e`

## Overview

| Property          | Value                                               |
| ----------------- | --------------------------------------------------- |
| Resource Type     | aws_vpc                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e |
| Region            | us-east-1                                           |
| Account ID        | 123456789012                                        |
| Collected At      | 2026-10-14T16:28:57Z                                |
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
| VpcId              | vpc-db407a2e |


## Resource Tags

| Tag Key | Tag Value  |
| ------- | ---------- |
| Name    | orders-vpc |


### Cidrblockassociationset

| AssociationId           | CidrBlock   | CidrBlockState          |
| ----------------------- | ----------- | ----------------------- |
| vpc-cidr-assoc-c8c24dbe | 10.0.0.0/16 | {'State': 'associated'} |


### Ipv6Cidrblockassociationset

```json
[]
```



---

# AWS Resource: `aws_security_group` - `sg-285ba61d10f344e74`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-285ba61d10f344e74 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-14T16:28:57Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | default VPC security group |
| GroupId           | sg-285ba61d10f344e74       |
| GroupName         | default                    |
| OwnerId           | 123456789012               |
| VpcId             | vpc-ce9c3403               |


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

# AWS Resource: `aws_security_group` - `sg-cc3138f31141d30f1`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-cc3138f31141d30f1 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-14T16:28:57Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                      |
| ----------------- | -------------------------- |
| Description       | default VPC security group |
| GroupId           | sg-cc3138f31141d30f1       |
| GroupName         | default                    |
| OwnerId           | 123456789012               |
| VpcId             | vpc-db407a2e               |


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

# AWS Resource: `aws_security_group` - `sg-7c880b8c4789c2216`

## Overview

| Property          | Value                                                                  |
| ----------------- | ---------------------------------------------------------------------- |
| Resource Type     | aws_security_group                                                     |
| ARN               | arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216 |
| Region            | us-east-1                                                              |
| Account ID        | 123456789012                                                           |
| Collected At      | 2026-10-14T16:28:57Z                                                   |
| Collector Version | 0.1.0                                                                  |


## Configuration Specifications

| Configuration Key | Value                |
| ----------------- | -------------------- |
| Description       | Web tier             |
| GroupId           | sg-7c880b8c4789c2216 |
| GroupName         | orders-web-sg        |
| OwnerId           | 123456789012         |
| VpcId             | vpc-db407a2e         |


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

# AWS Resource: `aws_lambda_function` - `order-processor`

## Overview

| Property          | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| Resource Type     | aws_lambda_function                                            |
| ARN               | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| Region            | us-east-1                                                      |
| Account ID        | 123456789012                                                   |
| Collected At      | 2026-10-14T16:28:57Z                                           |
| Collector Version | 0.1.0                                                          |


## Configuration Specifications

| Configuration Key | Value                                                          |
| ----------------- | -------------------------------------------------------------- |
| CodeSha256        | BDtH4Huf9CMc3iLRdqn8DhDGsQxETljhj6P7Pox3VMw=                   |
| CodeSize          | 164                                                            |
| Description       |                                                                |
| FunctionArn       | arn:aws:lambda:us-east-1:123456789012:function:order-processor |
| FunctionName      | order-processor                                                |
| Handler           | handler.handler                                                |
| LastModified      | 2026-10-14T16:28:56.804755000Z                                 |
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
| Collected At      | 2026-10-14T16:28:57Z                            |
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
| InstanceCreateTime               | 2026-10-14T16:28:56.860000+00:00                |
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
| active | sg-7c880b8c4789c2216 |



---

# AWS Resource: `aws_cloudwatch_log_group` - `aws_lambda_order-processor`

## Overview

| Property          | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| Resource Type     | aws_cloudwatch_log_group                                                  |
| ARN               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| Region            | us-east-1                                                                 |
| Account ID        | 123456789012                                                              |
| Collected At      | 2026-10-14T16:28:57Z                                                      |
| Collector Version | 0.1.0                                                                     |


## Configuration Specifications

| Configuration Key | Value                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| arn               | arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor |
| creationTime      | 1791995336813                                                             |
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
| Collected At      | 2026-10-14T16:28:57Z                                          |
| Collector Version | 0.1.0                                                         |


## Configuration Specifications

| Configuration Key | Value                                                                                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| creationDate      | 2026-10-14T16:28:56.847000+00:00                                                                                                                           |
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
| Collected At      | 2026-10-14T16:28:57Z                                 |
| Collector Version | 0.1.0                                                |


## Configuration Specifications

| Configuration Key | Value                                                |
| ----------------- | ---------------------------------------------------- |
| CreationDateTime  | 2026-10-14T23:28:56.796319+07:00                     |
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

# AWS Resource: `aws_s3_bucket` - `orders-public-assets`

## Overview

| Property          | Value                             |
| ----------------- | --------------------------------- |
| Resource Type     | aws_s3_bucket                     |
| ARN               | arn:aws:s3:::orders-public-assets |
| Region            | global                            |
| Account ID        | 123456789012                      |
| Collected At      | 2026-10-14T16:28:57Z              |
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

# AWS Resource: `aws_iam_role` - `orders-app-role`

## Overview

| Property          | Value                                          |
| ----------------- | ---------------------------------------------- |
| Resource Type     | aws_iam_role                                   |
| ARN               | arn:aws:iam::123456789012:role/orders-app-role |
| Region            | global                                         |
| Account ID        | 123456789012                                   |
| Collected At      | 2026-10-14T16:28:57Z                           |
| Collector Version | 0.1.0                                          |


## Configuration Specifications

| Configuration Key  | Value                                          |
| ------------------ | ---------------------------------------------- |
| Arn                | arn:aws:iam::123456789012:role/orders-app-role |
| CreateDate         | 2026-10-14T16:28:56.764000+00:00               |
| MaxSessionDuration | 3600                                           |
| Path               | /                                              |
| RoleId             | AROARZPUZDIKAHS2OASY6                          |
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

# AWS Resource: `aws_iam_role` - `order-lambda-role`

## Overview

| Property          | Value                                            |
| ----------------- | ------------------------------------------------ |
| Resource Type     | aws_iam_role                                     |
| ARN               | arn:aws:iam::123456789012:role/order-lambda-role |
| Region            | global                                           |
| Account ID        | 123456789012                                     |
| Collected At      | 2026-10-14T16:28:57Z                             |
| Collector Version | 0.1.0                                            |


## Configuration Specifications

| Configuration Key  | Value                                            |
| ------------------ | ------------------------------------------------ |
| Arn                | arn:aws:iam::123456789012:role/order-lambda-role |
| CreateDate         | 2026-10-14T16:28:56.771000+00:00                 |
| Description        | Execution role for order-processor               |
| MaxSessionDuration | 3600                                             |
| Path               | /                                                |
| RoleId             | AROARZPUZDIKEXHFBBBZI                            |
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

## Performance & Time Savings Summary Report

> [!NOTE]
> Based on industry baseline calculation of 5 minutes per resource for manual documentation.

| Metric          | Manual Effort (Baseline) | Automated Collection      | Savings           |
| --------------- | ------------------------ | ------------------------- | ----------------- |
| Baseline Rate   | 5 minutes / resource     | N/A                       | -                 |
| Total Resources | 14                       | 14                        | -                 |
| Total Duration  | 1.17 hours (70 min)      | 0.31 seconds (0.0001 hrs) | 1.17 hours saved  |
| Efficiency Gain | Baseline (100%)          | +100.0% faster            | 100.0% time saved |
