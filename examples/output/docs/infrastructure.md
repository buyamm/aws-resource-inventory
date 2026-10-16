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

- `storefront-workers` (us-east-1, `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers`) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.AutoScalingGroupName sha256:87fb01cb7c84]

### aws_cloudfront_distribution

- `S8ZTDFP8H8PGF` (global, `arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF`) [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.Id sha256:c6faf9435f2e]

### aws_cloudwatch_log_group

- `/aws/lambda/order-processor` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor`) [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:7ef2cb8e5187]
- `/ecs/storefront-web` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web`) [cite: aws_cloudwatch_log_group/us-east-1/ecs_storefront-web.json#specifications.logGroupName sha256:704c87cea18a]

### aws_db_instance

- `orders-db` (us-east-1, `arn:aws:rds:us-east-1:123456789012:db:orders-db`) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBInstanceIdentifier sha256:5d2f824784a5]

### aws_dynamodb_table

- `orders` (us-east-1, `arn:aws:dynamodb:us-east-1:123456789012:table/orders`) [cite: aws_dynamodb_table/us-east-1/orders.json#specifications.TableName sha256:f634ec584f03]

### aws_ecr_repository

- `storefront-web` (us-east-1, `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web`) [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryName sha256:08e36d49656a]

### aws_ecs_cluster

- `storefront` (us-east-1, `arn:aws:ecs:us-east-1:123456789012:cluster/storefront`) [cite: aws_ecs_cluster/us-east-1/storefront.json#specifications.clusterName sha256:61c9a1f831d5]

### aws_elasticache_replication_group

- `storefront-cache` (us-east-1, `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache`) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.ReplicationGroupId sha256:dceb3e6ddf31]

### aws_iam_role

- `order-lambda-role` (global, `arn:aws:iam::123456789012:role/order-lambda-role`) [cite: aws_iam_role/global/order-lambda-role.json#specifications.RoleName sha256:e0d055cab5a4]
- `orders-app-role` (global, `arn:aws:iam::123456789012:role/orders-app-role`) [cite: aws_iam_role/global/orders-app-role.json#specifications.RoleName sha256:96023be30a50]
- `storefront-exec-role` (global, `arn:aws:iam::123456789012:role/storefront-exec-role`) [cite: aws_iam_role/global/storefront-exec-role.json#specifications.RoleName sha256:6a37e7a4d724]
- `storefront-scheduler-role` (global, `arn:aws:iam::123456789012:role/storefront-scheduler-role`) [cite: aws_iam_role/global/storefront-scheduler-role.json#specifications.RoleName sha256:4c40999d21e5]
- `storefront-task-role` (global, `arn:aws:iam::123456789012:role/storefront-task-role`) [cite: aws_iam_role/global/storefront-task-role.json#specifications.RoleName sha256:b346f49fc97a]

### aws_instance

- `i-47f9de669501b27af` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af`) [cite: aws_instance/us-east-1/i-47f9de669501b27af.json#specifications.InstanceId sha256:fbcc065e03e4]
- `i-7c15a7e2df90fa017` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-7c15a7e2df90fa017`) [cite: aws_instance/us-east-1/i-7c15a7e2df90fa017.json#specifications.InstanceId sha256:428742aee241]

### aws_internet_gateway

- `igw-dbc38f85` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-dbc38f85`) [cite: aws_internet_gateway/us-east-1/igw-dbc38f85.json#specifications.InternetGatewayId sha256:4e2e70e39655]

### aws_lambda_function

- `order-processor` (us-east-1, `arn:aws:lambda:us-east-1:123456789012:function:order-processor`) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:e3708fbacdd8]

### aws_launch_template

- `lt-c743f2f076e986059` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-c743f2f076e986059`) [cite: aws_launch_template/us-east-1/lt-c743f2f076e986059.json#specifications.LaunchTemplateId sha256:a66bfdae6500]

### aws_nat_gateway

- `nat-60d1a0cf8c8f398eb` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-60d1a0cf8c8f398eb`) [cite: aws_nat_gateway/us-east-1/nat-60d1a0cf8c8f398eb.json#specifications.NatGatewayId sha256:efe9dd603272]

### aws_route_table

- `rtb-260c9780` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-260c9780`) [cite: aws_route_table/us-east-1/rtb-260c9780.json#specifications.RouteTableId sha256:6cdd0de72826]
- `rtb-7bfbfaee` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-7bfbfaee`) [cite: aws_route_table/us-east-1/rtb-7bfbfaee.json#specifications.RouteTableId sha256:967e385ed49f]
- `rtb-abf4c4b4` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4`) [cite: aws_route_table/us-east-1/rtb-abf4c4b4.json#specifications.RouteTableId sha256:043f29c6024d]

### aws_s3_bucket

- `orders-public-assets` (global, `arn:aws:s3:::orders-public-assets`) [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.Name sha256:dddfb5d26229]
- `storefront-static` (global, `arn:aws:s3:::storefront-static`) [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### aws_security_group

- `sg-2edfb301c8a045aa8` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2edfb301c8a045aa8`) [cite: aws_security_group/us-east-1/sg-2edfb301c8a045aa8.json#specifications.GroupId sha256:eca72d6b0d89]
- `sg-71a3ac0ec6bbd92b7` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-71a3ac0ec6bbd92b7`) [cite: aws_security_group/us-east-1/sg-71a3ac0ec6bbd92b7.json#specifications.GroupId sha256:4bfe76169da1]
- `sg-7c3a665620cbf02dc` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c3a665620cbf02dc`) [cite: aws_security_group/us-east-1/sg-7c3a665620cbf02dc.json#specifications.GroupId sha256:c1f701f34c06]
- `sg-c6ec367b2a800f7fe` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-c6ec367b2a800f7fe`) [cite: aws_security_group/us-east-1/sg-c6ec367b2a800f7fe.json#specifications.GroupId sha256:9f22b0082430]

### aws_sfn_state_machine

- `order-flow` (us-east-1, `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow`) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.name sha256:5247039d16b1]

### aws_subnet

- `subnet-30a75c4f` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f`) [cite: aws_subnet/us-east-1/subnet-30a75c4f.json#specifications.SubnetId sha256:18d71c4e5e35]
- `subnet-9134f3a5` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-9134f3a5`) [cite: aws_subnet/us-east-1/subnet-9134f3a5.json#specifications.SubnetId sha256:6beb7e1ec70b]
- `subnet-91c2dcc6` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6`) [cite: aws_subnet/us-east-1/subnet-91c2dcc6.json#specifications.SubnetId sha256:717465d35156]

### aws_vpc

- `vpc-7c4f2f1d` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d`) [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]

### aws_vpc_endpoint

- `vpce-55746589` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-55746589`) [cite: aws_vpc_endpoint/us-east-1/vpce-55746589.json#specifications.VpcEndpointId sha256:cb2bd7f40f66]

## Architecture Patterns

### Static site: S3 + CloudFront

CloudFront distribution 'S8ZTDFP8H8PGF' serves content from S3 bucket 'storefront-static'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:c6faf9435f2e] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

- Participant `arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF` [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:c6faf9435f2e]
- Participant `arn:aws:s3:::storefront-static` [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### Web app: CloudFront + ALB + ECS

CloudFront distribution 'S8ZTDFP8H8PGF' sends requests to load balancer 'app/storefront-alb/50dc6c495c0c9188', whose listener forwards to target group 'storefront-tg/50dc6c495c0c9188' serving ECS service 'storefront/web'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:c6faf9435f2e] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:e091403e0d78] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434536313232.json#specifications.LoadBalancerArn sha256:c911f1a7d5b6] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434536313232.json#specifications.DefaultActions[0].TargetGroupArn sha256:c911f1a7d5b6] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:781293bfbc6b]

- Participant `arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF` [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:c6faf9435f2e]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:e091403e0d78]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232` [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434536313232.json#specifications.LoadBalancerArn sha256:c911f1a7d5b6] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434536313232.json#specifications.DefaultActions[0].TargetGroupArn sha256:c911f1a7d5b6]
- Participant `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:781293bfbc6b]

### Compute in VPC

EC2 instance 'i-47f9de669501b27af' runs in VPC 'vpc-7c4f2f1d'. (confidence 1.00) [cite: aws_instance/us-east-1/i-47f9de669501b27af.json#specifications.VpcId sha256:fbcc065e03e4] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af` [cite: aws_instance/us-east-1/i-47f9de669501b27af.json#specifications.VpcId sha256:fbcc065e03e4]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]

### Compute in VPC

EC2 instance 'i-7c15a7e2df90fa017' runs in VPC 'vpc-7c4f2f1d'. (confidence 1.00) [cite: aws_instance/us-east-1/i-7c15a7e2df90fa017.json#specifications.VpcId sha256:428742aee241] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-7c15a7e2df90fa017` [cite: aws_instance/us-east-1/i-7c15a7e2df90fa017.json#specifications.VpcId sha256:428742aee241]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]

### Serverless Application

Lambda function 'order-processor' runs with IAM role 'order-lambda-role' and references DynamoDB table(s) 'orders' in its environment variables. (confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:e3708fbacdd8] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:e3708fbacdd8]

- Participant `arn:aws:lambda:us-east-1:123456789012:function:order-processor` [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:e3708fbacdd8] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:e3708fbacdd8]

## Interactions

- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-c743f2f076e986059` (launch_template, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.LaunchTemplate.LaunchTemplateId sha256:87fb01cb7c84]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` (subnet_placement, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.VPCZoneIdentifier sha256:87fb01cb7c84]
- `arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF` → `arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/1cbd8645-1348-4072-8b2e-633711042db1` (waf_protection, confidence 1.00) [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DistributionConfig.WebACLId sha256:c6faf9435f2e]
- `arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF` → `arn:aws:s3:::storefront-static` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:c6faf9435f2e] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]
- `arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:c6faf9435f2e] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:e091403e0d78]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-47f9de669501b27af.json#specifications.VpcId sha256:fbcc065e03e4] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_instance/us-east-1/i-47f9de669501b27af.json#specifications.IamInstanceProfile.Arn sha256:fbcc065e03e4]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2edfb301c8a045aa8` (security_group, confidence 0.90) [cite: aws_instance/us-east-1/i-47f9de669501b27af.json#specifications.SecurityGroups[0].GroupId sha256:fbcc065e03e4]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-47f9de669501b27af` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-47f9de669501b27af.json#specifications.SubnetId sha256:fbcc065e03e4]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-7c15a7e2df90fa017` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-7c15a7e2df90fa017.json#specifications.VpcId sha256:428742aee241] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-7c15a7e2df90fa017` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-7c15a7e2df90fa017.json#specifications.SubnetId sha256:428742aee241]
- `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-dbc38f85` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_internet_gateway/us-east-1/igw-dbc38f85.json#specifications.Attachments[0].VpcId sha256:4e2e70e39655]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-c743f2f076e986059` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c3a665620cbf02dc` (security_group, confidence 0.90) [cite: aws_launch_template/us-east-1/lt-c743f2f076e986059.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:a66bfdae6500]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-c743f2f076e986059` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_launch_template/us-east-1/lt-c743f2f076e986059.json#specifications.LaunchTemplateData.IamInstanceProfile.Name sha256:a66bfdae6500]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-60d1a0cf8c8f398eb` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-60d1a0cf8c8f398eb.json#specifications.VpcId sha256:efe9dd603272] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-60d1a0cf8c8f398eb` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6` (subnet_placement, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-60d1a0cf8c8f398eb.json#specifications.SubnetId sha256:efe9dd603272]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-260c9780` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-260c9780.json#specifications.VpcId sha256:6cdd0de72826] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-260c9780` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-260c9780.json#specifications.Associations[0].SubnetId sha256:6cdd0de72826]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-260c9780` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-9134f3a5` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-260c9780.json#specifications.Associations[1].SubnetId sha256:6cdd0de72826]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-260c9780` → `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-dbc38f85` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-260c9780.json#specifications.Routes[1].GatewayId sha256:6cdd0de72826]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-7bfbfaee` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-7bfbfaee.json#specifications.VpcId sha256:967e385ed49f] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-abf4c4b4.json#specifications.VpcId sha256:043f29c6024d] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-abf4c4b4.json#specifications.Associations[0].SubnetId sha256:043f29c6024d]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4` → `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-55746589` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-abf4c4b4.json#specifications.Routes[2].GatewayId sha256:043f29c6024d]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-abf4c4b4` → `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-60d1a0cf8c8f398eb` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-abf4c4b4.json#specifications.Routes[1].NatGatewayId sha256:043f29c6024d]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2edfb301c8a045aa8` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-2edfb301c8a045aa8.json#specifications.VpcId sha256:eca72d6b0d89] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-71a3ac0ec6bbd92b7` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-71a3ac0ec6bbd92b7.json#specifications.VpcId sha256:4bfe76169da1] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c3a665620cbf02dc` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-7c3a665620cbf02dc.json#specifications.VpcId sha256:c1f701f34c06] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-c6ec367b2a800f7fe` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-c6ec367b2a800f7fe.json#specifications.VpcId sha256:9f22b0082430] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-30a75c4f.json#specifications.VpcId sha256:18d71c4e5e35] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-9134f3a5` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-9134f3a5.json#specifications.VpcId sha256:6beb7e1ec70b] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-91c2dcc6.json#specifications.VpcId sha256:717465d35156] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-55746589` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_vpc_endpoint/us-east-1/vpce-55746589.json#specifications.VpcId sha256:cb2bd7f40f66] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:cluster/storefront` (ecs_cluster, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.clusterArn sha256:781293bfbc6b]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` (task_definition, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.taskDefinition sha256:781293bfbc6b]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` (subnet_placement, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.subnets[0] sha256:781293bfbc6b]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c3a665620cbf02dc` (security_group, confidence 0.90) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:781293bfbc6b]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` (lb_target, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:781293bfbc6b]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-task-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.taskRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-exec-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.executionRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web` (log_group, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].logConfiguration.options.awslogs-group sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web` (container_image, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].image sha256:065e5bbe2444] [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryUri sha256:08e36d49656a]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.VpcId sha256:dceb3e6ddf31] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c3a665620cbf02dc` (security_group, confidence 0.90) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheCluster.SecurityGroups[0].SecurityGroupId sha256:dceb3e6ddf31]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` (subnet_placement, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.Subnets[0].SubnetIdentifier sha256:dceb3e6ddf31]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (lb_listener, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434536313232.json#specifications.LoadBalancerArn sha256:c911f1a7d5b6]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` (forwards_to, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434536313232.json#specifications.DefaultActions[0].TargetGroupArn sha256:c911f1a7d5b6]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434536313232` → `arn:aws:acm:us-east-1:123456789012:certificate/8f72f034-ca75-4120-acc5-f35a9fd3885d` (certificate, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434536313232.json#specifications.Certificates[0].CertificateArn sha256:c911f1a7d5b6]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.VpcId sha256:e091403e0d78] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-91c2dcc6` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[0].SubnetId sha256:e091403e0d78]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-9134f3a5` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[1].SubnetId sha256:e091403e0d78]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-c6ec367b2a800f7fe` (security_group, confidence 0.90) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.SecurityGroups[0] sha256:e091403e0d78]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_lb_target_group/us-east-1/storefront-tg_50dc6c495c0c9188.json#specifications.VpcId sha256:1d5a1a06333a] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report` → `arn:aws:lambda:us-east-1:123456789012:function:order-processor` (event_target, confidence 1.00) [cite: aws_cloudwatch_event_rule/us-east-1/storefront-nightly-report.json#specifications.Targets[0].Arn sha256:aa8d1c0eb104]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:e3708fbacdd8]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:dynamodb:us-east-1:123456789012:table/orders` (dynamodb_access, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:e3708fbacdd8]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor` (log_group, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:e3708fbacdd8] [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:7ef2cb8e5187]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-7c4f2f1d` (vpc_connection, confidence 1.00) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBSubnetGroup.VpcId sha256:5d2f824784a5] [cite: aws_vpc/us-east-1/vpc-7c4f2f1d.json#specifications.VpcId sha256:99dd7be024c1]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2edfb301c8a045aa8` (security_group, confidence 0.90) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.VpcSecurityGroups[0].VpcSecurityGroupId sha256:5d2f824784a5]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-30a75c4f` (subnet_placement, confidence 1.00) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBSubnetGroup.Subnets[0].SubnetIdentifier sha256:5d2f824784a5]
- `arn:aws:route53:::hostedzone/2VX36NXN28FIY7F` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/2VX36NXN28FIY7F.json#specifications.ResourceRecordSets[2].AliasTarget.DNSName sha256:b0d7adcdc0f5] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:e091403e0d78]
- `arn:aws:route53:::hostedzone/2VX36NXN28FIY7F` → `arn:aws:cloudfront::123456789012:distribution/S8ZTDFP8H8PGF` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/2VX36NXN28FIY7F.json#specifications.ResourceRecordSets[3].AliasTarget.DNSName sha256:b0d7adcdc0f5] [cite: aws_cloudfront_distribution/global/S8ZTDFP8H8PGF.json#specifications.DomainName sha256:c6faf9435f2e]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:iam::123456789012:role/storefront-scheduler-role` (iam_role_usage, confidence 0.95) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.RoleArn sha256:4b67acc17da9]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (event_target, confidence 1.00) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.Arn sha256:4b67acc17da9]
- `arn:aws:sns:us-east-1:123456789012:storefront-events` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (subscription, confidence 1.00) [cite: aws_sns_topic/us-east-1/storefront-events.json#specifications.Subscriptions[0].Endpoint sha256:03c98dd2f797]
- `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.roleArn sha256:5247039d16b1]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers` → `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-7c3a665620cbf02dc.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:c1f701f34c06] [cite: aws_launch_template/us-east-1/lt-c743f2f076e986059.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:a66bfdae6500]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-7c3a665620cbf02dc.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:c1f701f34c06] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:781293bfbc6b]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:9bbe6615-958a-43a1-81c1-b9c0e0c23918:autoScalingGroupName/storefront-workers` → `arn:aws:rds:us-east-1:123456789012:db:orders-db` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-2edfb301c8a045aa8.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:eca72d6b0d89] [cite: aws_launch_template/us-east-1/lt-c743f2f076e986059.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:a66bfdae6500]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:rds:us-east-1:123456789012:db:orders-db` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-2edfb301c8a045aa8.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:eca72d6b0d89] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:781293bfbc6b]

## Security Findings

- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-2edfb301c8a045aa8' allows ingress from 0.0.0.0/0 on tcp port 22. [cite: aws_security_group/us-east-1/sg-2edfb301c8a045aa8.json#specifications.IpPermissions[0].IpRanges[0] sha256:eca72d6b0d89]
- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-c6ec367b2a800f7fe' allows ingress from 0.0.0.0/0 on tcp port 443. [cite: aws_security_group/us-east-1/sg-c6ec367b2a800f7fe.json#specifications.IpPermissions[0].IpRanges[0] sha256:9f22b0082430]
- [CRITICAL] OVERLY_PERMISSIVE_IAM_POLICY: IAM role 'order-lambda-role' inline policy 'too-broad' allows Action '*' on Resource '*'. [cite: aws_iam_role/global/order-lambda-role.json#specifications.InlinePolicies.too-broad.Statement[0] sha256:e0d055cab5a4]
- [HIGH] PUBLIC_S3_BUCKET: S3 bucket 'orders-public-assets' ACL grants READ to the AllUsers group. [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.bucket-acl.Grants[1] sha256:dddfb5d26229]
