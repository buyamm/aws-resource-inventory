# AWS Resource: `aws_route_table` - `rtb-fc59c9b7`

## Overview

| Property          | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| Resource Type     | aws_route_table                                             |
| ARN               | arn:aws:ec2:us-east-1:123456789012:route-table/rtb-fc59c9b7 |
| Region            | us-east-1                                                   |
| Account ID        | 123456789012                                                |
| Collected At      | 2026-10-15T16:40:03Z                                        |
| Collector Version | 0.1.0                                                       |


## Configuration Specifications

| Configuration Key | Value        |
| ----------------- | ------------ |
| OwnerId           | 123456789012 |
| RouteTableId      | rtb-fc59c9b7 |
| VpcId             | vpc-b6ee287f |


### Associations

| AssociationState        | Main | RouteTableAssociationId | RouteTableId |
| ----------------------- | ---- | ----------------------- | ------------ |
| {'State': 'associated'} | True | rtbassoc-0652b6d7       | rtb-fc59c9b7 |


### Routes

| DestinationCidrBlock | GatewayId | Origin           | State  |
| -------------------- | --------- | ---------------- | ------ |
| 10.0.0.0/16          | local     | CreateRouteTable | active |


### Tags

```json
[]
```

