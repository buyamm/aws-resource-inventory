# AWS Resource: `aws_route53_zone` - `F2D50YHDFNN6736`

## Overview

| Property          | Value                                        |
| ----------------- | -------------------------------------------- |
| Resource Type     | aws_route53_zone                             |
| ARN               | arn:aws:route53:::hostedzone/F2D50YHDFNN6736 |
| Region            | global                                       |
| Account ID        | 123456789012                                 |
| Collected At      | 2026-10-16T02:30:23Z                         |
| Collector Version | 0.1.0                                        |


## Configuration Specifications

| Configuration Key      | Value                       |
| ---------------------- | --------------------------- |
| CallerReference        | storefront                  |
| Id                     | /hostedzone/F2D50YHDFNN6736 |
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
| {'HostedZoneId': 'Z2FDTNDATAQYW2', 'DNSName': 'egydycao61es5.cloudfront.net', 'EvaluateTargetHealth': False}                          | shop.example.com. |                                                                                                                                                    |        | A    |

