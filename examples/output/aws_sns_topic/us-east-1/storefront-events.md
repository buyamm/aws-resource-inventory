# AWS Resource: `aws_sns_topic` - `storefront-events`

## Overview

| Property          | Value                                                |
| ----------------- | ---------------------------------------------------- |
| Resource Type     | aws_sns_topic                                        |
| ARN               | arn:aws:sns:us-east-1:123456789012:storefront-events |
| Region            | us-east-1                                            |
| Account ID        | 123456789012                                         |
| Collected At      | 2026-10-16T02:30:23Z                                 |
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
| arn:aws:sqs:us-east-1:123456789012:storefront-orders | 123456789012 | sqs      | arn:aws:sns:us-east-1:123456789012:storefront-events:e21eb8bf-e942-4f1a-9e3c-363645db1129 | arn:aws:sns:us-east-1:123456789012:storefront-events |

