# AWS Resource: `aws_route_table` - `rtb-7bfbfaee`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-7bfbfaee |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-16T01:29:14Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-7bfbfaee |
| VpcId             | vpc-7c4f2f1d |


### Associations

| AssociationState        | Main | RouteTableAssociationId | RouteTableId |
| ----------------------- | ---- | ----------------------- | ------------ |
| {'State': 'associated'} | True | rtbassoc-69e3b0e3       | rtb-7bfbfaee |


### Routes

| DestinationCidrBlock | GatewayId | Origin           | State  |
| -------------------- | --------- | ---------------- | ------ |
| 10.0.0.0/16          | local     | CreateRouteTable | active |


### Tags

```json
[]
```

