# AWS Resource: `aws_route_table` - `rtb-bf60be68`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T02:05:49Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-bf60be68 |
| VpcId             | vpc-660d36ef |


## Resource Tags

| Tag Key | Tag Value         |
| ------- | ----------------- |
| Name    | storefront-public |
| service | storefront        |


### Associations

| AssociationState        | Main  | RouteTableAssociationId | RouteTableId | SubnetId        |
| ----------------------- | ----- | ----------------------- | ------------ | --------------- |
| {'State': 'associated'} | False | rtbassoc-16e988c5       | rtb-bf60be68 | subnet-2cf4f53a |
| {'State': 'associated'} | False | rtbassoc-ab796c06       | rtb-bf60be68 | subnet-4db17d3d |


### Routes

| DestinationCidrBlock | GatewayId    | Origin           | State  |
| -------------------- | ------------ | ---------------- | ------ |
| 10.0.0.0/16          | local        | CreateRouteTable | active |
| 0.0.0.0/0            | igw-d045f4ab | CreateRoute      | active |

