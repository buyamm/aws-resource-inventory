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

