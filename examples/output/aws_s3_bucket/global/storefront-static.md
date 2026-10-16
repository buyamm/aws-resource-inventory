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

