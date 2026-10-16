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

