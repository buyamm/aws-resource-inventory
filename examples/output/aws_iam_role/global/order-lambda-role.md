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

