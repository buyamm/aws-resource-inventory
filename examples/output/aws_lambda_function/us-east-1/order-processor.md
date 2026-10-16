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

