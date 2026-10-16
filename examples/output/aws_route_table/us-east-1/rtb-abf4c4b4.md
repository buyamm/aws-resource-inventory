# AWS Resource: `aws_route_table` - `rtb-abf4c4b4`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T01:29:14Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-abf4c4b4 |
| VpcId             | vpc-7c4f2f1d |


## Resource Tags

| Tag Key | Tag Value          |
| ------- | ------------------ |
| Name    | storefront-private |
| service | storefront         |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-85544a58       | rtb-abf4c4b4 | subnet-30a75c4f |


### Routes

| DestinationCidrBlock | DestinationPrefixListId | GatewayId     | NatGatewayId          | Origin           | State  |
| -------------------- | ----------------------- | ------------- | --------------------- | ---------------- | ------ |
| 10.0.0.0/16          |                         | local         |                       | CreateRouteTable | active |
| 0.0.0.0/0            |                         |               | nat-60d1a0cf8c8f398eb | CreateRoute      | active |
|                      | pl-c6e0eb33             | vpce-55746589 |                       | CreateRoute      | active |

