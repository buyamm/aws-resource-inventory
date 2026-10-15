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

- `storefront-workers` (us-east-1, `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:d7e19156-0c83-434b-b8e0-a1b67c604518:autoScalingGroupName/storefront-workers`) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.AutoScalingGroupName sha256:bfbd9cc6ad6b]

### aws_cloudfront_distribution

- `WUDV5OCSQIBBJ` (global, `arn:aws:cloudfront::123456789012:distribution/WUDV5OCSQIBBJ`) [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.Id sha256:d6bc9a3e5006]

### aws_cloudwatch_log_group

- `/aws/lambda/order-processor` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor`) [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:05c67a5507eb]
- `/ecs/storefront-web` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web`) [cite: aws_cloudwatch_log_group/us-east-1/ecs_storefront-web.json#specifications.logGroupName sha256:56930d54abb4]

### aws_db_instance

- `orders-db` (us-east-1, `arn:aws:rds:us-east-1:123456789012:db:orders-db`) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBInstanceIdentifier sha256:f1c30e919db7]

### aws_dynamodb_table

- `orders` (us-east-1, `arn:aws:dynamodb:us-east-1:123456789012:table/orders`) [cite: aws_dynamodb_table/us-east-1/orders.json#specifications.TableName sha256:970b1c37d7cd]

### aws_ecr_repository

- `storefront-web` (us-east-1, `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web`) [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryName sha256:fc63734dfee5]

### aws_ecs_cluster

- `storefront` (us-east-1, `arn:aws:ecs:us-east-1:123456789012:cluster/storefront`) [cite: aws_ecs_cluster/us-east-1/storefront.json#specifications.clusterName sha256:61c9a1f831d5]

### aws_elasticache_replication_group

- `storefront-cache` (us-east-1, `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache`) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.ReplicationGroupId sha256:fce04d9cfc98]

### aws_iam_role

- `order-lambda-role` (global, `arn:aws:iam::123456789012:role/order-lambda-role`) [cite: aws_iam_role/global/order-lambda-role.json#specifications.RoleName sha256:2a96462513d6]
- `orders-app-role` (global, `arn:aws:iam::123456789012:role/orders-app-role`) [cite: aws_iam_role/global/orders-app-role.json#specifications.RoleName sha256:401f57a8b6cd]
- `storefront-exec-role` (global, `arn:aws:iam::123456789012:role/storefront-exec-role`) [cite: aws_iam_role/global/storefront-exec-role.json#specifications.RoleName sha256:523c0938a79f]
- `storefront-scheduler-role` (global, `arn:aws:iam::123456789012:role/storefront-scheduler-role`) [cite: aws_iam_role/global/storefront-scheduler-role.json#specifications.RoleName sha256:514e8210e0d1]
- `storefront-task-role` (global, `arn:aws:iam::123456789012:role/storefront-task-role`) [cite: aws_iam_role/global/storefront-task-role.json#specifications.RoleName sha256:f5568ce43128]

### aws_instance

- `i-685e30ac4d43a0d83` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-685e30ac4d43a0d83`) [cite: aws_instance/us-east-1/i-685e30ac4d43a0d83.json#specifications.InstanceId sha256:66d0dd1de4db]
- `i-f6333ad6a6250cb6f` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-f6333ad6a6250cb6f`) [cite: aws_instance/us-east-1/i-f6333ad6a6250cb6f.json#specifications.InstanceId sha256:74aadad0fb9c]

### aws_internet_gateway

- `igw-bd38647b` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-bd38647b`) [cite: aws_internet_gateway/us-east-1/igw-bd38647b.json#specifications.InternetGatewayId sha256:e9d575363b22]

### aws_lambda_function

- `order-processor` (us-east-1, `arn:aws:lambda:us-east-1:123456789012:function:order-processor`) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:778b38320819]

### aws_launch_template

- `lt-254efd878ee151eb7` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-254efd878ee151eb7`) [cite: aws_launch_template/us-east-1/lt-254efd878ee151eb7.json#specifications.LaunchTemplateId sha256:f28e5f6524a9]

### aws_nat_gateway

- `nat-8604a604f3c5a3cf0` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8604a604f3c5a3cf0`) [cite: aws_nat_gateway/us-east-1/nat-8604a604f3c5a3cf0.json#specifications.NatGatewayId sha256:1de5f94295c6]

### aws_route_table

- `rtb-52dac71b` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-52dac71b`) [cite: aws_route_table/us-east-1/rtb-52dac71b.json#specifications.RouteTableId sha256:f78440cdfeeb]
- `rtb-590047f7` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590047f7`) [cite: aws_route_table/us-east-1/rtb-590047f7.json#specifications.RouteTableId sha256:ca71d5ad76a0]
- `rtb-fc59c9b7` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-fc59c9b7`) [cite: aws_route_table/us-east-1/rtb-fc59c9b7.json#specifications.RouteTableId sha256:61fc13bad193]

### aws_s3_bucket

- `orders-public-assets` (global, `arn:aws:s3:::orders-public-assets`) [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.Name sha256:dddfb5d26229]
- `storefront-static` (global, `arn:aws:s3:::storefront-static`) [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### aws_security_group

- `sg-67ee3adaaa05cd07e` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-67ee3adaaa05cd07e`) [cite: aws_security_group/us-east-1/sg-67ee3adaaa05cd07e.json#specifications.GroupId sha256:51b1ff075af2]
- `sg-8c9c7f5f96b0d5fb1` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-8c9c7f5f96b0d5fb1`) [cite: aws_security_group/us-east-1/sg-8c9c7f5f96b0d5fb1.json#specifications.GroupId sha256:dd0fe45d87c5]
- `sg-eaaa2c57ac5ecc98e` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-eaaa2c57ac5ecc98e`) [cite: aws_security_group/us-east-1/sg-eaaa2c57ac5ecc98e.json#specifications.GroupId sha256:5b573d31fa2a]
- `sg-fb454a9efcd634f32` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-fb454a9efcd634f32`) [cite: aws_security_group/us-east-1/sg-fb454a9efcd634f32.json#specifications.GroupId sha256:765917c33184]

### aws_sfn_state_machine

- `order-flow` (us-east-1, `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow`) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.name sha256:d0949cba96df]

### aws_subnet

- `subnet-a6e131f6` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6e131f6`) [cite: aws_subnet/us-east-1/subnet-a6e131f6.json#specifications.SubnetId sha256:ef4d3b63ccfb]
- `subnet-b83c8765` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-b83c8765`) [cite: aws_subnet/us-east-1/subnet-b83c8765.json#specifications.SubnetId sha256:36b69891ebf5]
- `subnet-d94916f9` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-d94916f9`) [cite: aws_subnet/us-east-1/subnet-d94916f9.json#specifications.SubnetId sha256:055e57fc7d5b]

### aws_vpc

- `vpc-b6ee287f` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f`) [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]

### aws_vpc_endpoint

- `vpce-073f3c1e` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-073f3c1e`) [cite: aws_vpc_endpoint/us-east-1/vpce-073f3c1e.json#specifications.VpcEndpointId sha256:8c253ca2bb2a]

## Architecture Patterns

### Static site: S3 + CloudFront

CloudFront distribution 'WUDV5OCSQIBBJ' serves content from S3 bucket 'storefront-static'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:d6bc9a3e5006] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

- Participant `arn:aws:cloudfront::123456789012:distribution/WUDV5OCSQIBBJ` [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:d6bc9a3e5006]
- Participant `arn:aws:s3:::storefront-static` [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### Web app: CloudFront + ALB + ECS

CloudFront distribution 'WUDV5OCSQIBBJ' sends requests to load balancer 'app/storefront-alb/50dc6c495c0c9188', whose listener forwards to target group 'storefront-tg/50dc6c495c0c9188' serving ECS service 'storefront/web'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:d6bc9a3e5006] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:5444a4e427e9] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434588500944.json#specifications.LoadBalancerArn sha256:af4469008b88] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434588500944.json#specifications.DefaultActions[0].TargetGroupArn sha256:af4469008b88] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:de1130ac0afe]

- Participant `arn:aws:cloudfront::123456789012:distribution/WUDV5OCSQIBBJ` [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:d6bc9a3e5006]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:5444a4e427e9]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434588500944` [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434588500944.json#specifications.LoadBalancerArn sha256:af4469008b88] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434588500944.json#specifications.DefaultActions[0].TargetGroupArn sha256:af4469008b88]
- Participant `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:de1130ac0afe]

### Compute in VPC

EC2 instance 'i-685e30ac4d43a0d83' runs in VPC 'vpc-b6ee287f'. (confidence 1.00) [cite: aws_instance/us-east-1/i-685e30ac4d43a0d83.json#specifications.VpcId sha256:66d0dd1de4db] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-685e30ac4d43a0d83` [cite: aws_instance/us-east-1/i-685e30ac4d43a0d83.json#specifications.VpcId sha256:66d0dd1de4db]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]

### Compute in VPC

EC2 instance 'i-f6333ad6a6250cb6f' runs in VPC 'vpc-b6ee287f'. (confidence 1.00) [cite: aws_instance/us-east-1/i-f6333ad6a6250cb6f.json#specifications.VpcId sha256:74aadad0fb9c] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-f6333ad6a6250cb6f` [cite: aws_instance/us-east-1/i-f6333ad6a6250cb6f.json#specifications.VpcId sha256:74aadad0fb9c]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]

### Serverless Application

Lambda function 'order-processor' runs with IAM role 'order-lambda-role' and references DynamoDB table(s) 'orders' in its environment variables. (confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:778b38320819] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:778b38320819]

- Participant `arn:aws:lambda:us-east-1:123456789012:function:order-processor` [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:778b38320819] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:778b38320819]

## Interactions

- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:d7e19156-0c83-434b-b8e0-a1b67c604518:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-254efd878ee151eb7` (launch_template, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.LaunchTemplate.LaunchTemplateId sha256:bfbd9cc6ad6b]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:d7e19156-0c83-434b-b8e0-a1b67c604518:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6e131f6` (subnet_placement, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.VPCZoneIdentifier sha256:bfbd9cc6ad6b]
- `arn:aws:cloudfront::123456789012:distribution/WUDV5OCSQIBBJ` → `arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/e910f120-ccdb-46a7-bbb2-4e34585f73b5` (waf_protection, confidence 1.00) [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DistributionConfig.WebACLId sha256:d6bc9a3e5006]
- `arn:aws:cloudfront::123456789012:distribution/WUDV5OCSQIBBJ` → `arn:aws:s3:::storefront-static` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:d6bc9a3e5006] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]
- `arn:aws:cloudfront::123456789012:distribution/WUDV5OCSQIBBJ` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:d6bc9a3e5006] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:5444a4e427e9]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-685e30ac4d43a0d83` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-685e30ac4d43a0d83.json#specifications.VpcId sha256:66d0dd1de4db] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-685e30ac4d43a0d83` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_instance/us-east-1/i-685e30ac4d43a0d83.json#specifications.IamInstanceProfile.Arn sha256:66d0dd1de4db]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-685e30ac4d43a0d83` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-fb454a9efcd634f32` (security_group, confidence 0.90) [cite: aws_instance/us-east-1/i-685e30ac4d43a0d83.json#specifications.SecurityGroups[0].GroupId sha256:66d0dd1de4db]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-685e30ac4d43a0d83` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6e131f6` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-685e30ac4d43a0d83.json#specifications.SubnetId sha256:66d0dd1de4db]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-f6333ad6a6250cb6f` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-f6333ad6a6250cb6f.json#specifications.VpcId sha256:74aadad0fb9c] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-f6333ad6a6250cb6f` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6e131f6` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-f6333ad6a6250cb6f.json#specifications.SubnetId sha256:74aadad0fb9c]
- `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-bd38647b` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_internet_gateway/us-east-1/igw-bd38647b.json#specifications.Attachments[0].VpcId sha256:e9d575363b22]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-254efd878ee151eb7` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-eaaa2c57ac5ecc98e` (security_group, confidence 0.90) [cite: aws_launch_template/us-east-1/lt-254efd878ee151eb7.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:f28e5f6524a9]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-254efd878ee151eb7` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_launch_template/us-east-1/lt-254efd878ee151eb7.json#specifications.LaunchTemplateData.IamInstanceProfile.Name sha256:f28e5f6524a9]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8604a604f3c5a3cf0` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-8604a604f3c5a3cf0.json#specifications.VpcId sha256:1de5f94295c6] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8604a604f3c5a3cf0` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-d94916f9` (subnet_placement, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-8604a604f3c5a3cf0.json#specifications.SubnetId sha256:1de5f94295c6]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-52dac71b` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-52dac71b.json#specifications.VpcId sha256:f78440cdfeeb] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-52dac71b` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6e131f6` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-52dac71b.json#specifications.Associations[0].SubnetId sha256:f78440cdfeeb]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-52dac71b` → `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-073f3c1e` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-52dac71b.json#specifications.Routes[2].GatewayId sha256:f78440cdfeeb]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-52dac71b` → `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-8604a604f3c5a3cf0` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-52dac71b.json#specifications.Routes[1].NatGatewayId sha256:f78440cdfeeb]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590047f7` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590047f7.json#specifications.VpcId sha256:ca71d5ad76a0] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590047f7` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-d94916f9` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590047f7.json#specifications.Associations[0].SubnetId sha256:ca71d5ad76a0]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590047f7` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-b83c8765` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590047f7.json#specifications.Associations[1].SubnetId sha256:ca71d5ad76a0]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590047f7` → `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-bd38647b` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590047f7.json#specifications.Routes[1].GatewayId sha256:ca71d5ad76a0]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-fc59c9b7` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-fc59c9b7.json#specifications.VpcId sha256:61fc13bad193] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-67ee3adaaa05cd07e` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-67ee3adaaa05cd07e.json#specifications.VpcId sha256:51b1ff075af2] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-8c9c7f5f96b0d5fb1` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-8c9c7f5f96b0d5fb1.json#specifications.VpcId sha256:dd0fe45d87c5] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-eaaa2c57ac5ecc98e` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-eaaa2c57ac5ecc98e.json#specifications.VpcId sha256:5b573d31fa2a] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-fb454a9efcd634f32` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-fb454a9efcd634f32.json#specifications.VpcId sha256:765917c33184] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6e131f6` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-a6e131f6.json#specifications.VpcId sha256:ef4d3b63ccfb] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-b83c8765` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-b83c8765.json#specifications.VpcId sha256:36b69891ebf5] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-d94916f9` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-d94916f9.json#specifications.VpcId sha256:055e57fc7d5b] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-073f3c1e` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_vpc_endpoint/us-east-1/vpce-073f3c1e.json#specifications.VpcId sha256:8c253ca2bb2a] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:cluster/storefront` (ecs_cluster, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.clusterArn sha256:de1130ac0afe]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` (task_definition, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.taskDefinition sha256:de1130ac0afe]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` (lb_target, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:de1130ac0afe]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-task-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.taskRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-exec-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.executionRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web` (log_group, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].logConfiguration.options.awslogs-group sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web` (container_image, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].image sha256:065e5bbe2444] [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryUri sha256:fc63734dfee5]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.VpcId sha256:fce04d9cfc98] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-eaaa2c57ac5ecc98e` (security_group, confidence 0.90) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheCluster.SecurityGroups[0].SecurityGroupId sha256:fce04d9cfc98]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-a6e131f6` (subnet_placement, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.Subnets[0].SubnetIdentifier sha256:fce04d9cfc98]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434588500944` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (lb_listener, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434588500944.json#specifications.LoadBalancerArn sha256:af4469008b88]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434588500944` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` (forwards_to, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434588500944.json#specifications.DefaultActions[0].TargetGroupArn sha256:af4469008b88]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434588500944` → `arn:aws:acm:us-east-1:123456789012:certificate/a731cd05-0052-48e0-8889-0431af5b4bbe` (certificate, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434588500944.json#specifications.Certificates[0].CertificateArn sha256:af4469008b88]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.VpcId sha256:5444a4e427e9] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-d94916f9` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[0].SubnetId sha256:5444a4e427e9]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-b83c8765` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[1].SubnetId sha256:5444a4e427e9]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-8c9c7f5f96b0d5fb1` (security_group, confidence 0.90) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.SecurityGroups[0] sha256:5444a4e427e9]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-b6ee287f` (vpc_connection, confidence 1.00) [cite: aws_lb_target_group/us-east-1/storefront-tg_50dc6c495c0c9188.json#specifications.VpcId sha256:e27561dc11b9] [cite: aws_vpc/us-east-1/vpc-b6ee287f.json#specifications.VpcId sha256:a0fdd984f90f]
- `arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report` → `arn:aws:lambda:us-east-1:123456789012:function:order-processor` (event_target, confidence 1.00) [cite: aws_cloudwatch_event_rule/us-east-1/storefront-nightly-report.json#specifications.Targets[0].Arn sha256:aa8d1c0eb104]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:778b38320819]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:dynamodb:us-east-1:123456789012:table/orders` (dynamodb_access, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:778b38320819]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor` (log_group, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:778b38320819] [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:05c67a5507eb]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-fb454a9efcd634f32` (security_group, confidence 0.90) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.VpcSecurityGroups[0].VpcSecurityGroupId sha256:f1c30e919db7]
- `arn:aws:route53:::hostedzone/0QZOTUEJO46KDTZ` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/0QZOTUEJO46KDTZ.json#specifications.ResourceRecordSets[2].AliasTarget.DNSName sha256:8d94606920fa] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:5444a4e427e9]
- `arn:aws:route53:::hostedzone/0QZOTUEJO46KDTZ` → `arn:aws:cloudfront::123456789012:distribution/WUDV5OCSQIBBJ` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/0QZOTUEJO46KDTZ.json#specifications.ResourceRecordSets[3].AliasTarget.DNSName sha256:8d94606920fa] [cite: aws_cloudfront_distribution/global/WUDV5OCSQIBBJ.json#specifications.DomainName sha256:d6bc9a3e5006]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:iam::123456789012:role/storefront-scheduler-role` (iam_role_usage, confidence 0.95) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.RoleArn sha256:046f6025c41b]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (event_target, confidence 1.00) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.Arn sha256:046f6025c41b]
- `arn:aws:sns:us-east-1:123456789012:storefront-events` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (subscription, confidence 1.00) [cite: aws_sns_topic/us-east-1/storefront-events.json#specifications.Subscriptions[0].Endpoint sha256:e534e5a3b8ac]
- `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.roleArn sha256:d0949cba96df]

## Security Findings

- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-8c9c7f5f96b0d5fb1' allows ingress from 0.0.0.0/0 on tcp port 443. [cite: aws_security_group/us-east-1/sg-8c9c7f5f96b0d5fb1.json#specifications.IpPermissions[0].IpRanges[0] sha256:dd0fe45d87c5]
- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-fb454a9efcd634f32' allows ingress from 0.0.0.0/0 on tcp port 22. [cite: aws_security_group/us-east-1/sg-fb454a9efcd634f32.json#specifications.IpPermissions[0].IpRanges[0] sha256:765917c33184]
- [CRITICAL] OVERLY_PERMISSIVE_IAM_POLICY: IAM role 'order-lambda-role' inline policy 'too-broad' allows Action '*' on Resource '*'. [cite: aws_iam_role/global/order-lambda-role.json#specifications.InlinePolicies.too-broad.Statement[0] sha256:2a96462513d6]
- [HIGH] PUBLIC_S3_BUCKET: S3 bucket 'orders-public-assets' ACL grants READ to the AllUsers group. [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.bucket-acl.Grants[1] sha256:dddfb5d26229]
