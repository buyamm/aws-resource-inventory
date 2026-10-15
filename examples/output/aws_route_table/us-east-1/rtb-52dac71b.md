# AWS Resource: `aws_route_table` - `rtb-52dac71b`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-52dac71b |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-15T16:40:03Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-52dac71b |
| VpcId             | vpc-b6ee287f |


## Resource Tags

| Tag Key | Tag Value          |
| ------- | ------------------ |
| Name    | storefront-private |
| service | storefront         |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-fe53fe54       | rtb-52dac71b | subnet-a6e131f6 |


### Routes

| DestinationCidrBlock | DestinationPrefixListId | GatewayId     | NatGatewayId          | Origin           | State  |
| -------------------- | ----------------------- | ------------- | --------------------- | ---------------- | ------ |
| 10.0.0.0/16          |                         | local         |                       | CreateRouteTable | active |
| 0.0.0.0/0            |                         |               | nat-8604a604f3c5a3cf0 | CreateRoute      | active |
|                      | pl-7c659893             | vpce-073f3c1e |                       | CreateRoute      | active |

