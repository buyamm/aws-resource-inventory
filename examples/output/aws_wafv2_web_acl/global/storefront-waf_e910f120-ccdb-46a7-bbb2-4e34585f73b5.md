# AWS Resource: `aws_wafv2_web_acl` - `storefront-waf_e910f120-ccdb-46a7-bbb2-4e34585f73b5`

## Overview

| Property          | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| Resource Type     | aws_wafv2_web_acl                                                                                   |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/e910f120-ccdb-46a7-bbb2-4e34585f73b5 |
| Region            | global                                                                                              |
| Account ID        | 123456789012                                                                                        |
| Collected At      | 2026-10-15T16:40:03Z                                                                                |
| Collector Version | 0.1.0                                                                                               |


## Configuration Specifications

| Configuration Key | Value                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| ARN               | arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/e910f120-ccdb-46a7-bbb2-4e34585f73b5 |
| Description       | Edge protection for the storefront                                                                  |
| Id                | e910f120-ccdb-46a7-bbb2-4e34585f73b5                                                                |
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

