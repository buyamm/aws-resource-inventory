# Infrastructure Documentation

## Inventory

| Resource Type | Region | Count |
| :--- | :--- | ---: |
| aws_acm_certificate | us-east-1 | 1 |
| aws_autoscaling_group | us-east-1 | 1 |
| aws_cloudfront_distribution | global | 1 |
| aws_cloudwatch_event_rule | us-east-1 | 1 |
| aws_cloudwatch_log_group | us-east-1 | 2 |
| aws_db_instance | us-east-1 | 1 |
| aws_dynamodb_table | us-east-1 | 1 |
| aws_ecr_repository | us-east-1 | 1 |
| aws_ecs_cluster | us-east-1 | 1 |
| aws_ecs_service | us-east-1 | 1 |
| aws_ecs_task_definition | us-east-1 | 1 |
| aws_elasticache_replication_group | us-east-1 | 1 |
| aws_iam_role | global | 5 |
| aws_instance | us-east-1 | 2 |
| aws_internet_gateway | us-east-1 | 1 |
| aws_lambda_function | us-east-1 | 1 |
| aws_launch_template | us-east-1 | 1 |
| aws_lb | us-east-1 | 1 |
| aws_lb_listener | us-east-1 | 1 |
| aws_lb_target_group | us-east-1 | 1 |
| aws_nat_gateway | us-east-1 | 1 |
| aws_route53_zone | global | 1 |
| aws_route_table | us-east-1 | 3 |
| aws_s3_bucket | global | 2 |
| aws_scheduler_schedule | us-east-1 | 1 |
| aws_security_group | us-east-1 | 4 |
| aws_sfn_state_machine | us-east-1 | 1 |
| aws_sns_topic | us-east-1 | 1 |
| aws_sqs_queue | us-east-1 | 1 |
| aws_subnet | us-east-1 | 3 |
| aws_vpc | us-east-1 | 1 |
| aws_vpc_endpoint | us-east-1 | 1 |
| aws_wafv2_web_acl | global | 1 |

### aws_autoscaling_group

- `storefront-workers` (us-east-1, `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:f970678c-021d-4578-9657-1164773d5b3d:autoScalingGroupName/storefront-workers`) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.AutoScalingGroupName sha256:88dd5b3c73e0]

### aws_cloudfront_distribution

- `RXBBW1AS174FR` (global, `arn:aws:cloudfront::123456789012:distribution/RXBBW1AS174FR`) [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.Id sha256:a5a9f8ee8a1c]

### aws_cloudwatch_log_group

- `/aws/lambda/order-processor` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor`) [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:66f41623e6e1]
- `/ecs/storefront-web` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web`) [cite: aws_cloudwatch_log_group/us-east-1/ecs_storefront-web.json#specifications.logGroupName sha256:0f64bff6e9e0]

### aws_db_instance

- `orders-db` (us-east-1, `arn:aws:rds:us-east-1:123456789012:db:orders-db`) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBInstanceIdentifier sha256:956080851752]

### aws_dynamodb_table

- `orders` (us-east-1, `arn:aws:dynamodb:us-east-1:123456789012:table/orders`) [cite: aws_dynamodb_table/us-east-1/orders.json#specifications.TableName sha256:6ae58e81cad0]

### aws_ecr_repository

- `storefront-web` (us-east-1, `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web`) [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryName sha256:347bd12b24d7]

### aws_ecs_cluster

- `storefront` (us-east-1, `arn:aws:ecs:us-east-1:123456789012:cluster/storefront`) [cite: aws_ecs_cluster/us-east-1/storefront.json#specifications.clusterName sha256:61c9a1f831d5]

### aws_elasticache_replication_group

- `storefront-cache` (us-east-1, `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache`) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.ReplicationGroupId sha256:4502dd58cb69]

### aws_iam_role

- `order-lambda-role` (global, `arn:aws:iam::123456789012:role/order-lambda-role`) [cite: aws_iam_role/global/order-lambda-role.json#specifications.RoleName sha256:16a064def9c7]
- `orders-app-role` (global, `arn:aws:iam::123456789012:role/orders-app-role`) [cite: aws_iam_role/global/orders-app-role.json#specifications.RoleName sha256:e77d86df14c5]
- `storefront-exec-role` (global, `arn:aws:iam::123456789012:role/storefront-exec-role`) [cite: aws_iam_role/global/storefront-exec-role.json#specifications.RoleName sha256:96d6123b330c]
- `storefront-scheduler-role` (global, `arn:aws:iam::123456789012:role/storefront-scheduler-role`) [cite: aws_iam_role/global/storefront-scheduler-role.json#specifications.RoleName sha256:70e7c582d877]
- `storefront-task-role` (global, `arn:aws:iam::123456789012:role/storefront-task-role`) [cite: aws_iam_role/global/storefront-task-role.json#specifications.RoleName sha256:2079893d8c15]

### aws_instance

- `i-3bd88a7f905f64de6` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-3bd88a7f905f64de6`) [cite: aws_instance/us-east-1/i-3bd88a7f905f64de6.json#specifications.InstanceId sha256:08c01bd994fa]
- `i-565d781fe501611ba` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-565d781fe501611ba`) [cite: aws_instance/us-east-1/i-565d781fe501611ba.json#specifications.InstanceId sha256:7074ada6b498]

### aws_internet_gateway

- `igw-c94e6ba3` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-c94e6ba3`) [cite: aws_internet_gateway/us-east-1/igw-c94e6ba3.json#specifications.InternetGatewayId sha256:54d61c0dabbd]

### aws_lambda_function

- `order-processor` (us-east-1, `arn:aws:lambda:us-east-1:123456789012:function:order-processor`) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:111200847901]

### aws_launch_template

- `lt-4fe346ea9a7834369` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-4fe346ea9a7834369`) [cite: aws_launch_template/us-east-1/lt-4fe346ea9a7834369.json#specifications.LaunchTemplateId sha256:3e1f0e6ad542]

### aws_nat_gateway

- `nat-8af9c7bd4aed62d36` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8af9c7bd4aed62d36`) [cite: aws_nat_gateway/us-east-1/nat-8af9c7bd4aed62d36.json#specifications.NatGatewayId sha256:dc4655b2e459]

### aws_route_table

- `rtb-47bf1246` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-47bf1246`) [cite: aws_route_table/us-east-1/rtb-47bf1246.json#specifications.RouteTableId sha256:bf816db5ab26]
- `rtb-8fc56d9e` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-8fc56d9e`) [cite: aws_route_table/us-east-1/rtb-8fc56d9e.json#specifications.RouteTableId sha256:886ca34ef236]
- `rtb-ee1782b8` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-ee1782b8`) [cite: aws_route_table/us-east-1/rtb-ee1782b8.json#specifications.RouteTableId sha256:4c74a02a2ae5]

### aws_s3_bucket

- `orders-public-assets` (global, `arn:aws:s3:::orders-public-assets`) [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.Name sha256:dddfb5d26229]
- `storefront-static` (global, `arn:aws:s3:::storefront-static`) [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### aws_security_group

- `sg-1f2b0a4eff89696aa` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-1f2b0a4eff89696aa`) [cite: aws_security_group/us-east-1/sg-1f2b0a4eff89696aa.json#specifications.GroupId sha256:5ec6f2a2572b]
- `sg-80de5126f2f05dbc9` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-80de5126f2f05dbc9`) [cite: aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json#specifications.GroupId sha256:13802e1cad84]
- `sg-b7692d5b41942a421` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-b7692d5b41942a421`) [cite: aws_security_group/us-east-1/sg-b7692d5b41942a421.json#specifications.GroupId sha256:56656818c7d0]
- `sg-e351ba83453fe3b63` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-e351ba83453fe3b63`) [cite: aws_security_group/us-east-1/sg-e351ba83453fe3b63.json#specifications.GroupId sha256:4cfb8b0a5012]

### aws_sfn_state_machine

- `order-flow` (us-east-1, `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow`) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.name sha256:6b33a7a6d63d]

### aws_subnet

- `subnet-084ef767` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-084ef767`) [cite: aws_subnet/us-east-1/subnet-084ef767.json#specifications.SubnetId sha256:89d848f67957]
- `subnet-7f177dcb` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb`) [cite: aws_subnet/us-east-1/subnet-7f177dcb.json#specifications.SubnetId sha256:ddeb2de748bc]
- `subnet-a6f66dc7` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6f66dc7`) [cite: aws_subnet/us-east-1/subnet-a6f66dc7.json#specifications.SubnetId sha256:c6238e897232]

### aws_vpc

- `vpc-040f0f81` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81`) [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]

### aws_vpc_endpoint

- `vpce-170a3c5e` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-170a3c5e`) [cite: aws_vpc_endpoint/us-east-1/vpce-170a3c5e.json#specifications.VpcEndpointId sha256:952fd2be4e05]

## Architecture Patterns

### Static site: S3 + CloudFront

CloudFront distribution 'RXBBW1AS174FR' serves content from S3 bucket 'storefront-static'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:a5a9f8ee8a1c] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

- Participant `arn:aws:cloudfront::123456789012:distribution/RXBBW1AS174FR` [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:a5a9f8ee8a1c]
- Participant `arn:aws:s3:::storefront-static` [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### Web app: CloudFront + ALB + ECS

CloudFront distribution 'RXBBW1AS174FR' sends requests to load balancer 'app/storefront-alb/50dc6c495c0c9188', whose listener forwards to target group 'storefront-tg/50dc6c495c0c9188' serving ECS service 'storefront/web'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:a5a9f8ee8a1c] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:1deb17f620e7] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json#specifications.LoadBalancerArn sha256:1e97becf234b] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json#specifications.DefaultActions[0].TargetGroupArn sha256:1e97becf234b] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:3a61aef7f966]

- Participant `arn:aws:cloudfront::123456789012:distribution/RXBBW1AS174FR` [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:a5a9f8ee8a1c]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:1deb17f620e7]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434489454224` [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json#specifications.LoadBalancerArn sha256:1e97becf234b] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json#specifications.DefaultActions[0].TargetGroupArn sha256:1e97becf234b]
- Participant `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:3a61aef7f966]

### Compute in VPC

EC2 instance 'i-3bd88a7f905f64de6' runs in VPC 'vpc-040f0f81'. (confidence 1.00) [cite: aws_instance/us-east-1/i-3bd88a7f905f64de6.json#specifications.VpcId sha256:08c01bd994fa] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-3bd88a7f905f64de6` [cite: aws_instance/us-east-1/i-3bd88a7f905f64de6.json#specifications.VpcId sha256:08c01bd994fa]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]

### Compute in VPC

EC2 instance 'i-565d781fe501611ba' runs in VPC 'vpc-040f0f81'. (confidence 1.00) [cite: aws_instance/us-east-1/i-565d781fe501611ba.json#specifications.VpcId sha256:7074ada6b498] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-565d781fe501611ba` [cite: aws_instance/us-east-1/i-565d781fe501611ba.json#specifications.VpcId sha256:7074ada6b498]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]

### Serverless Application

Lambda function 'order-processor' runs with IAM role 'order-lambda-role' and references DynamoDB table(s) 'orders' in its environment variables. (confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:111200847901] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:111200847901]

- Participant `arn:aws:lambda:us-east-1:123456789012:function:order-processor` [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:111200847901] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:111200847901]

## Interactions

- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:f970678c-021d-4578-9657-1164773d5b3d:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-4fe346ea9a7834369` (launch_template, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.LaunchTemplate.LaunchTemplateId sha256:88dd5b3c73e0]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:f970678c-021d-4578-9657-1164773d5b3d:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` (subnet_placement, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.VPCZoneIdentifier sha256:88dd5b3c73e0]
- `arn:aws:cloudfront::123456789012:distribution/RXBBW1AS174FR` → `arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/b5e7fc2f-fa34-44a4-8362-0cb65c2450a9` (waf_protection, confidence 1.00) [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DistributionConfig.WebACLId sha256:a5a9f8ee8a1c]
- `arn:aws:cloudfront::123456789012:distribution/RXBBW1AS174FR` → `arn:aws:s3:::storefront-static` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:a5a9f8ee8a1c] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]
- `arn:aws:cloudfront::123456789012:distribution/RXBBW1AS174FR` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:a5a9f8ee8a1c] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:1deb17f620e7]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-3bd88a7f905f64de6` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-3bd88a7f905f64de6.json#specifications.VpcId sha256:08c01bd994fa] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-3bd88a7f905f64de6` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-3bd88a7f905f64de6.json#specifications.SubnetId sha256:08c01bd994fa]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-565d781fe501611ba` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-565d781fe501611ba.json#specifications.VpcId sha256:7074ada6b498] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-565d781fe501611ba` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_instance/us-east-1/i-565d781fe501611ba.json#specifications.IamInstanceProfile.Arn sha256:7074ada6b498]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-565d781fe501611ba` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-80de5126f2f05dbc9` (security_group, confidence 0.90) [cite: aws_instance/us-east-1/i-565d781fe501611ba.json#specifications.SecurityGroups[0].GroupId sha256:7074ada6b498]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-565d781fe501611ba` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-565d781fe501611ba.json#specifications.SubnetId sha256:7074ada6b498]
- `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-c94e6ba3` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_internet_gateway/us-east-1/igw-c94e6ba3.json#specifications.Attachments[0].VpcId sha256:54d61c0dabbd]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-4fe346ea9a7834369` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-b7692d5b41942a421` (security_group, confidence 0.90) [cite: aws_launch_template/us-east-1/lt-4fe346ea9a7834369.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:3e1f0e6ad542]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-4fe346ea9a7834369` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_launch_template/us-east-1/lt-4fe346ea9a7834369.json#specifications.LaunchTemplateData.IamInstanceProfile.Name sha256:3e1f0e6ad542]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8af9c7bd4aed62d36` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-8af9c7bd4aed62d36.json#specifications.VpcId sha256:dc4655b2e459] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8af9c7bd4aed62d36` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-084ef767` (subnet_placement, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-8af9c7bd4aed62d36.json#specifications.SubnetId sha256:dc4655b2e459]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-47bf1246` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-47bf1246.json#specifications.VpcId sha256:bf816db5ab26] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-47bf1246` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-084ef767` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-47bf1246.json#specifications.Associations[0].SubnetId sha256:bf816db5ab26]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-47bf1246` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6f66dc7` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-47bf1246.json#specifications.Associations[1].SubnetId sha256:bf816db5ab26]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-47bf1246` → `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-c94e6ba3` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-47bf1246.json#specifications.Routes[1].GatewayId sha256:bf816db5ab26]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-8fc56d9e` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-8fc56d9e.json#specifications.VpcId sha256:886ca34ef236] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-ee1782b8` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-ee1782b8.json#specifications.VpcId sha256:4c74a02a2ae5] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-ee1782b8` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-ee1782b8.json#specifications.Associations[0].SubnetId sha256:4c74a02a2ae5]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-ee1782b8` → `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-170a3c5e` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-ee1782b8.json#specifications.Routes[2].GatewayId sha256:4c74a02a2ae5]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-ee1782b8` → `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8af9c7bd4aed62d36` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-ee1782b8.json#specifications.Routes[1].NatGatewayId sha256:4c74a02a2ae5]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-1f2b0a4eff89696aa` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-1f2b0a4eff89696aa.json#specifications.VpcId sha256:5ec6f2a2572b] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-80de5126f2f05dbc9` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json#specifications.VpcId sha256:13802e1cad84] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-b7692d5b41942a421` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-b7692d5b41942a421.json#specifications.VpcId sha256:56656818c7d0] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-e351ba83453fe3b63` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-e351ba83453fe3b63.json#specifications.VpcId sha256:4cfb8b0a5012] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-084ef767` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-084ef767.json#specifications.VpcId sha256:89d848f67957] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-7f177dcb.json#specifications.VpcId sha256:ddeb2de748bc] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6f66dc7` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-a6f66dc7.json#specifications.VpcId sha256:c6238e897232] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-170a3c5e` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_vpc_endpoint/us-east-1/vpce-170a3c5e.json#specifications.VpcId sha256:952fd2be4e05] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:cluster/storefront` (ecs_cluster, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.clusterArn sha256:3a61aef7f966]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` (task_definition, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.taskDefinition sha256:3a61aef7f966]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` (subnet_placement, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.subnets[0] sha256:3a61aef7f966]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-b7692d5b41942a421` (security_group, confidence 0.90) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:3a61aef7f966]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` (lb_target, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:3a61aef7f966]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-task-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.taskRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-exec-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.executionRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web` (log_group, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].logConfiguration.options.awslogs-group sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web` (container_image, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].image sha256:065e5bbe2444] [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryUri sha256:347bd12b24d7]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.VpcId sha256:4502dd58cb69] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-b7692d5b41942a421` (security_group, confidence 0.90) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheCluster.SecurityGroups[0].SecurityGroupId sha256:4502dd58cb69]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` (subnet_placement, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.Subnets[0].SubnetIdentifier sha256:4502dd58cb69]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434489454224` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (lb_listener, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json#specifications.LoadBalancerArn sha256:1e97becf234b]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434489454224` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` (forwards_to, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json#specifications.DefaultActions[0].TargetGroupArn sha256:1e97becf234b]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434489454224` → `arn:aws:acm:us-east-1:123456789012:certificate/1492cb3f-a6df-47d4-892f-f87748ae6367` (certificate, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json#specifications.Certificates[0].CertificateArn sha256:1e97becf234b]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.VpcId sha256:1deb17f620e7] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-084ef767` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[0].SubnetId sha256:1deb17f620e7]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6f66dc7` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[1].SubnetId sha256:1deb17f620e7]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-e351ba83453fe3b63` (security_group, confidence 0.90) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.SecurityGroups[0] sha256:1deb17f620e7]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_lb_target_group/us-east-1/storefront-tg_50dc6c495c0c9188.json#specifications.VpcId sha256:d7e36f938705] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report` → `arn:aws:lambda:us-east-1:123456789012:function:order-processor` (event_target, confidence 1.00) [cite: aws_cloudwatch_event_rule/us-east-1/storefront-nightly-report.json#specifications.Targets[0].Arn sha256:aa8d1c0eb104]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:111200847901]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:dynamodb:us-east-1:123456789012:table/orders` (dynamodb_access, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:111200847901]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor` (log_group, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:111200847901] [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:66f41623e6e1]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-040f0f81` (vpc_connection, confidence 1.00) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBSubnetGroup.VpcId sha256:956080851752] [cite: aws_vpc/us-east-1/vpc-040f0f81.json#specifications.VpcId sha256:896e201646a5]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-80de5126f2f05dbc9` (security_group, confidence 0.90) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.VpcSecurityGroups[0].VpcSecurityGroupId sha256:956080851752]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-7f177dcb` (subnet_placement, confidence 1.00) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBSubnetGroup.Subnets[0].SubnetIdentifier sha256:956080851752]
- `arn:aws:route53:::hostedzone/F2D50YHDFNN6736` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/F2D50YHDFNN6736.json#specifications.ResourceRecordSets[2].AliasTarget.DNSName sha256:e188f475b957] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:1deb17f620e7]
- `arn:aws:route53:::hostedzone/F2D50YHDFNN6736` → `arn:aws:cloudfront::123456789012:distribution/RXBBW1AS174FR` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/F2D50YHDFNN6736.json#specifications.ResourceRecordSets[3].AliasTarget.DNSName sha256:e188f475b957] [cite: aws_cloudfront_distribution/global/RXBBW1AS174FR.json#specifications.DomainName sha256:a5a9f8ee8a1c]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:iam::123456789012:role/storefront-scheduler-role` (iam_role_usage, confidence 0.95) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.RoleArn sha256:68ad746a5225]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (event_target, confidence 1.00) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.Arn sha256:68ad746a5225]
- `arn:aws:sns:us-east-1:123456789012:storefront-events` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (subscription, confidence 1.00) [cite: aws_sns_topic/us-east-1/storefront-events.json#specifications.Subscriptions[0].Endpoint sha256:85c46fac3728]
- `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.roleArn sha256:6b33a7a6d63d]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:f970678c-021d-4578-9657-1164773d5b3d:autoScalingGroupName/storefront-workers` → `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-b7692d5b41942a421.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:56656818c7d0] [cite: aws_launch_template/us-east-1/lt-4fe346ea9a7834369.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:3e1f0e6ad542]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-b7692d5b41942a421.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:56656818c7d0] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:3a61aef7f966]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:f970678c-021d-4578-9657-1164773d5b3d:autoScalingGroupName/storefront-workers` → `arn:aws:rds:us-east-1:123456789012:db:orders-db` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:13802e1cad84] [cite: aws_launch_template/us-east-1/lt-4fe346ea9a7834369.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:3e1f0e6ad542]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:rds:us-east-1:123456789012:db:orders-db` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:13802e1cad84] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:3a61aef7f966]

## Security Findings

- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-80de5126f2f05dbc9' allows ingress from 0.0.0.0/0 on tcp port 22. [cite: aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json#specifications.IpPermissions[0].IpRanges[0] sha256:13802e1cad84]
- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-e351ba83453fe3b63' allows ingress from 0.0.0.0/0 on tcp port 443. [cite: aws_security_group/us-east-1/sg-e351ba83453fe3b63.json#specifications.IpPermissions[0].IpRanges[0] sha256:4cfb8b0a5012]
- [CRITICAL] OVERLY_PERMISSIVE_IAM_POLICY: IAM role 'order-lambda-role' inline policy 'too-broad' allows Action '*' on Resource '*'. [cite: aws_iam_role/global/order-lambda-role.json#specifications.InlinePolicies.too-broad.Statement[0] sha256:16a064def9c7]
- [HIGH] PUBLIC_S3_BUCKET: S3 bucket 'orders-public-assets' ACL grants READ to the AllUsers group. [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.bucket-acl.Grants[1] sha256:dddfb5d26229]
