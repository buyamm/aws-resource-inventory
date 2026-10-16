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

- `storefront-workers` (us-east-1, `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers`) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.AutoScalingGroupName sha256:fd2c18a309b4]

### aws_cloudfront_distribution

- `X5E0C4JHPHC9C` (global, `arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C`) [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.Id sha256:e6d402a3ad31]

### aws_cloudwatch_log_group

- `/aws/lambda/order-processor` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor`) [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:4b618454ba18]
- `/ecs/storefront-web` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web`) [cite: aws_cloudwatch_log_group/us-east-1/ecs_storefront-web.json#specifications.logGroupName sha256:15bdd0e893f6]

### aws_db_instance

- `orders-db` (us-east-1, `arn:aws:rds:us-east-1:123456789012:db:orders-db`) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBInstanceIdentifier sha256:3a7f9a2e57b9]

### aws_dynamodb_table

- `orders` (us-east-1, `arn:aws:dynamodb:us-east-1:123456789012:table/orders`) [cite: aws_dynamodb_table/us-east-1/orders.json#specifications.TableName sha256:783d8ea656ca]

### aws_ecr_repository

- `storefront-web` (us-east-1, `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web`) [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryName sha256:e40c758b70ea]

### aws_ecs_cluster

- `storefront` (us-east-1, `arn:aws:ecs:us-east-1:123456789012:cluster/storefront`) [cite: aws_ecs_cluster/us-east-1/storefront.json#specifications.clusterName sha256:61c9a1f831d5]

### aws_elasticache_replication_group

- `storefront-cache` (us-east-1, `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache`) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.ReplicationGroupId sha256:f25524b567e0]

### aws_iam_role

- `order-lambda-role` (global, `arn:aws:iam::123456789012:role/order-lambda-role`) [cite: aws_iam_role/global/order-lambda-role.json#specifications.RoleName sha256:f25f33238ee8]
- `orders-app-role` (global, `arn:aws:iam::123456789012:role/orders-app-role`) [cite: aws_iam_role/global/orders-app-role.json#specifications.RoleName sha256:54dd4e14e527]
- `storefront-exec-role` (global, `arn:aws:iam::123456789012:role/storefront-exec-role`) [cite: aws_iam_role/global/storefront-exec-role.json#specifications.RoleName sha256:ff5bcc902f3b]
- `storefront-scheduler-role` (global, `arn:aws:iam::123456789012:role/storefront-scheduler-role`) [cite: aws_iam_role/global/storefront-scheduler-role.json#specifications.RoleName sha256:4cc0970c767c]
- `storefront-task-role` (global, `arn:aws:iam::123456789012:role/storefront-task-role`) [cite: aws_iam_role/global/storefront-task-role.json#specifications.RoleName sha256:020747f16984]

### aws_instance

- `i-5e2db2f538089c39d` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d`) [cite: aws_instance/us-east-1/i-5e2db2f538089c39d.json#specifications.InstanceId sha256:ab7e8ab380c6]
- `i-b892b745a8c407b02` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-b892b745a8c407b02`) [cite: aws_instance/us-east-1/i-b892b745a8c407b02.json#specifications.InstanceId sha256:8c9c8d150f7e]

### aws_internet_gateway

- `igw-d045f4ab` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-d045f4ab`) [cite: aws_internet_gateway/us-east-1/igw-d045f4ab.json#specifications.InternetGatewayId sha256:0c5c02b6bade]

### aws_lambda_function

- `order-processor` (us-east-1, `arn:aws:lambda:us-east-1:123456789012:function:order-processor`) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:1585d9f4ac9b]

### aws_launch_template

- `lt-bad06a08aee200bf2` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-bad06a08aee200bf2`) [cite: aws_launch_template/us-east-1/lt-bad06a08aee200bf2.json#specifications.LaunchTemplateId sha256:3a695fbf8e2c]

### aws_nat_gateway

- `nat-af9f73b40a8a4af4f` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-af9f73b40a8a4af4f`) [cite: aws_nat_gateway/us-east-1/nat-af9f73b40a8a4af4f.json#specifications.NatGatewayId sha256:6f199aad56d6]

### aws_route_table

- `rtb-561c82c8` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-561c82c8`) [cite: aws_route_table/us-east-1/rtb-561c82c8.json#specifications.RouteTableId sha256:e6fe77b0d2c4]
- `rtb-bf60be68` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68`) [cite: aws_route_table/us-east-1/rtb-bf60be68.json#specifications.RouteTableId sha256:f934a81ed305]
- `rtb-e28b5541` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-e28b5541`) [cite: aws_route_table/us-east-1/rtb-e28b5541.json#specifications.RouteTableId sha256:9b49f828df8f]

### aws_s3_bucket

- `orders-public-assets` (global, `arn:aws:s3:::orders-public-assets`) [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.Name sha256:dddfb5d26229]
- `storefront-static` (global, `arn:aws:s3:::storefront-static`) [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### aws_security_group

- `sg-12874fb82c9db66ed` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-12874fb82c9db66ed`) [cite: aws_security_group/us-east-1/sg-12874fb82c9db66ed.json#specifications.GroupId sha256:3adac5c9a964]
- `sg-156a39ed25de235cf` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-156a39ed25de235cf`) [cite: aws_security_group/us-east-1/sg-156a39ed25de235cf.json#specifications.GroupId sha256:4327b5c87e5f]
- `sg-2bf145296ea5159ab` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2bf145296ea5159ab`) [cite: aws_security_group/us-east-1/sg-2bf145296ea5159ab.json#specifications.GroupId sha256:e5bbe17547b7]
- `sg-e4a0ee2dde2bb1f50` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-e4a0ee2dde2bb1f50`) [cite: aws_security_group/us-east-1/sg-e4a0ee2dde2bb1f50.json#specifications.GroupId sha256:d0bb4c047521]

### aws_sfn_state_machine

- `order-flow` (us-east-1, `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow`) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.name sha256:e25ed9c8e0ec]

### aws_subnet

- `subnet-2cf4f53a` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a`) [cite: aws_subnet/us-east-1/subnet-2cf4f53a.json#specifications.SubnetId sha256:0424b687ec9e]
- `subnet-4d897e3d` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d`) [cite: aws_subnet/us-east-1/subnet-4d897e3d.json#specifications.SubnetId sha256:5513632573df]
- `subnet-4db17d3d` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4db17d3d`) [cite: aws_subnet/us-east-1/subnet-4db17d3d.json#specifications.SubnetId sha256:81d089619867]

### aws_vpc

- `vpc-660d36ef` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef`) [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]

### aws_vpc_endpoint

- `vpce-40eb00b6` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-40eb00b6`) [cite: aws_vpc_endpoint/us-east-1/vpce-40eb00b6.json#specifications.VpcEndpointId sha256:601e718ae79d]

## Architecture Patterns

### Static site: S3 + CloudFront

CloudFront distribution 'X5E0C4JHPHC9C' serves content from S3 bucket 'storefront-static'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:e6d402a3ad31] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

- Participant `arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C` [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:e6d402a3ad31]
- Participant `arn:aws:s3:::storefront-static` [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### Web app: CloudFront + ALB + ECS

CloudFront distribution 'X5E0C4JHPHC9C' sends requests to load balancer 'app/storefront-alb/50dc6c495c0c9188', whose listener forwards to target group 'storefront-tg/50dc6c495c0c9188' serving ECS service 'storefront/web'. (confidence 1.00) [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:e6d402a3ad31] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:a39ecd1e87ec] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json#specifications.LoadBalancerArn sha256:88f506359555] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json#specifications.DefaultActions[0].TargetGroupArn sha256:88f506359555] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:741478c1710f]

- Participant `arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C` [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:e6d402a3ad31]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:a39ecd1e87ec]
- Participant `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232` [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json#specifications.LoadBalancerArn sha256:88f506359555] [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json#specifications.DefaultActions[0].TargetGroupArn sha256:88f506359555]
- Participant `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:741478c1710f]

### Compute in VPC

EC2 instance 'i-5e2db2f538089c39d' runs in VPC 'vpc-660d36ef'. (confidence 1.00) [cite: aws_instance/us-east-1/i-5e2db2f538089c39d.json#specifications.VpcId sha256:ab7e8ab380c6] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d` [cite: aws_instance/us-east-1/i-5e2db2f538089c39d.json#specifications.VpcId sha256:ab7e8ab380c6]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]

### Compute in VPC

EC2 instance 'i-b892b745a8c407b02' runs in VPC 'vpc-660d36ef'. (confidence 1.00) [cite: aws_instance/us-east-1/i-b892b745a8c407b02.json#specifications.VpcId sha256:8c9c8d150f7e] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-b892b745a8c407b02` [cite: aws_instance/us-east-1/i-b892b745a8c407b02.json#specifications.VpcId sha256:8c9c8d150f7e]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]

### Serverless Application

Lambda function 'order-processor' runs with IAM role 'order-lambda-role' and references DynamoDB table(s) 'orders' in its environment variables. (confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:1585d9f4ac9b] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:1585d9f4ac9b]

- Participant `arn:aws:lambda:us-east-1:123456789012:function:order-processor` [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:1585d9f4ac9b] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:1585d9f4ac9b]

## Interactions

- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-bad06a08aee200bf2` (launch_template, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.LaunchTemplate.LaunchTemplateId sha256:fd2c18a309b4]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` (subnet_placement, confidence 1.00) [cite: aws_autoscaling_group/us-east-1/storefront-workers.json#specifications.VPCZoneIdentifier sha256:fd2c18a309b4]
- `arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C` → `arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/d06f4b4d-1ec6-42a4-81fa-1582637eb32d` (waf_protection, confidence 1.00) [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DistributionConfig.WebACLId sha256:e6d402a3ad31]
- `arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C` → `arn:aws:s3:::storefront-static` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:e6d402a3ad31] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]
- `arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:e6d402a3ad31] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:a39ecd1e87ec]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-5e2db2f538089c39d.json#specifications.VpcId sha256:ab7e8ab380c6] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_instance/us-east-1/i-5e2db2f538089c39d.json#specifications.IamInstanceProfile.Arn sha256:ab7e8ab380c6]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2bf145296ea5159ab` (security_group, confidence 0.90) [cite: aws_instance/us-east-1/i-5e2db2f538089c39d.json#specifications.SecurityGroups[0].GroupId sha256:ab7e8ab380c6]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-5e2db2f538089c39d` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-5e2db2f538089c39d.json#specifications.SubnetId sha256:ab7e8ab380c6]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-b892b745a8c407b02` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-b892b745a8c407b02.json#specifications.VpcId sha256:8c9c8d150f7e] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-b892b745a8c407b02` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-b892b745a8c407b02.json#specifications.SubnetId sha256:8c9c8d150f7e]
- `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-d045f4ab` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_internet_gateway/us-east-1/igw-d045f4ab.json#specifications.Attachments[0].VpcId sha256:0c5c02b6bade]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-bad06a08aee200bf2` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-12874fb82c9db66ed` (security_group, confidence 0.90) [cite: aws_launch_template/us-east-1/lt-bad06a08aee200bf2.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:3a695fbf8e2c]
- `arn:aws:ec2:us-east-1:123456789012:launch-template/lt-bad06a08aee200bf2` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_launch_template/us-east-1/lt-bad06a08aee200bf2.json#specifications.LaunchTemplateData.IamInstanceProfile.Name sha256:3a695fbf8e2c]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-af9f73b40a8a4af4f` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-af9f73b40a8a4af4f.json#specifications.VpcId sha256:6f199aad56d6] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-af9f73b40a8a4af4f` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a` (subnet_placement, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-af9f73b40a8a4af4f.json#specifications.SubnetId sha256:6f199aad56d6]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-561c82c8` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-561c82c8.json#specifications.VpcId sha256:e6fe77b0d2c4] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-bf60be68.json#specifications.VpcId sha256:f934a81ed305] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-bf60be68.json#specifications.Associations[0].SubnetId sha256:f934a81ed305]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4db17d3d` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-bf60be68.json#specifications.Associations[1].SubnetId sha256:f934a81ed305]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-bf60be68` → `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-d045f4ab` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-bf60be68.json#specifications.Routes[1].GatewayId sha256:f934a81ed305]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-e28b5541` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-e28b5541.json#specifications.VpcId sha256:9b49f828df8f] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-e28b5541` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-e28b5541.json#specifications.Associations[0].SubnetId sha256:9b49f828df8f]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-e28b5541` → `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-40eb00b6` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-e28b5541.json#specifications.Routes[2].GatewayId sha256:9b49f828df8f]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-e28b5541` → `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-af9f73b40a8a4af4f` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-e28b5541.json#specifications.Routes[1].NatGatewayId sha256:9b49f828df8f]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-12874fb82c9db66ed` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-12874fb82c9db66ed.json#specifications.VpcId sha256:3adac5c9a964] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-156a39ed25de235cf` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-156a39ed25de235cf.json#specifications.VpcId sha256:4327b5c87e5f] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2bf145296ea5159ab` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-2bf145296ea5159ab.json#specifications.VpcId sha256:e5bbe17547b7] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-e4a0ee2dde2bb1f50` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-e4a0ee2dde2bb1f50.json#specifications.VpcId sha256:d0bb4c047521] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-2cf4f53a.json#specifications.VpcId sha256:0424b687ec9e] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-4d897e3d.json#specifications.VpcId sha256:5513632573df] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4db17d3d` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-4db17d3d.json#specifications.VpcId sha256:81d089619867] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-40eb00b6` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_vpc_endpoint/us-east-1/vpce-40eb00b6.json#specifications.VpcId sha256:601e718ae79d] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:cluster/storefront` (ecs_cluster, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.clusterArn sha256:741478c1710f]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` (task_definition, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.taskDefinition sha256:741478c1710f]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` (subnet_placement, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.subnets[0] sha256:741478c1710f]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-12874fb82c9db66ed` (security_group, confidence 0.90) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:741478c1710f]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` (lb_target, confidence 1.00) [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.loadBalancers[0].targetGroupArn sha256:741478c1710f]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-task-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.taskRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:iam::123456789012:role/storefront-exec-role` (iam_role_usage, confidence 0.95) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.executionRoleArn sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/storefront-web` (log_group, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].logConfiguration.options.awslogs-group sha256:065e5bbe2444]
- `arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1` → `arn:aws:ecr:us-east-1:123456789012:repository/storefront-web` (container_image, confidence 1.00) [cite: aws_ecs_task_definition/us-east-1/storefront-web_1.json#specifications.containerDefinitions[0].image sha256:065e5bbe2444] [cite: aws_ecr_repository/us-east-1/storefront-web.json#specifications.repositoryUri sha256:e40c758b70ea]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.VpcId sha256:f25524b567e0] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-12874fb82c9db66ed` (security_group, confidence 0.90) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheCluster.SecurityGroups[0].SecurityGroupId sha256:f25524b567e0]
- `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` (subnet_placement, confidence 1.00) [cite: aws_elasticache_replication_group/us-east-1/storefront-cache.json#specifications.CacheSubnetGroup.Subnets[0].SubnetIdentifier sha256:f25524b567e0]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (lb_listener, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json#specifications.LoadBalancerArn sha256:88f506359555]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` (forwards_to, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json#specifications.DefaultActions[0].TargetGroupArn sha256:88f506359555]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232` → `arn:aws:acm:us-east-1:123456789012:certificate/a2f4311b-2bbd-4ca0-97e7-018106634454` (certificate, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json#specifications.Certificates[0].CertificateArn sha256:88f506359555]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.VpcId sha256:a39ecd1e87ec] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-2cf4f53a` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[0].SubnetId sha256:a39ecd1e87ec]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4db17d3d` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[1].SubnetId sha256:a39ecd1e87ec]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-e4a0ee2dde2bb1f50` (security_group, confidence 0.90) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.SecurityGroups[0] sha256:a39ecd1e87ec]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_lb_target_group/us-east-1/storefront-tg_50dc6c495c0c9188.json#specifications.VpcId sha256:d0ab3e3ccd50] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:events:us-east-1:123456789012:rule/storefront-nightly-report` → `arn:aws:lambda:us-east-1:123456789012:function:order-processor` (event_target, confidence 1.00) [cite: aws_cloudwatch_event_rule/us-east-1/storefront-nightly-report.json#specifications.Targets[0].Arn sha256:aa8d1c0eb104]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:1585d9f4ac9b]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:dynamodb:us-east-1:123456789012:table/orders` (dynamodb_access, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:1585d9f4ac9b]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor` (log_group, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:1585d9f4ac9b] [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:4b618454ba18]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-660d36ef` (vpc_connection, confidence 1.00) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBSubnetGroup.VpcId sha256:3a7f9a2e57b9] [cite: aws_vpc/us-east-1/vpc-660d36ef.json#specifications.VpcId sha256:c2274cdfeb0c]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-2bf145296ea5159ab` (security_group, confidence 0.90) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.VpcSecurityGroups[0].VpcSecurityGroupId sha256:3a7f9a2e57b9]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-4d897e3d` (subnet_placement, confidence 1.00) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBSubnetGroup.Subnets[0].SubnetIdentifier sha256:3a7f9a2e57b9]
- `arn:aws:route53:::hostedzone/ACA19C6IIUY2GFZ` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/ACA19C6IIUY2GFZ.json#specifications.ResourceRecordSets[2].AliasTarget.DNSName sha256:d82368da4fb5] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:a39ecd1e87ec]
- `arn:aws:route53:::hostedzone/ACA19C6IIUY2GFZ` → `arn:aws:cloudfront::123456789012:distribution/X5E0C4JHPHC9C` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/ACA19C6IIUY2GFZ.json#specifications.ResourceRecordSets[3].AliasTarget.DNSName sha256:d82368da4fb5] [cite: aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json#specifications.DomainName sha256:e6d402a3ad31]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:iam::123456789012:role/storefront-scheduler-role` (iam_role_usage, confidence 0.95) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.RoleArn sha256:26ebd196e9a7]
- `arn:aws:scheduler:us-east-1:123456789012:schedule/default/storefront-cleanup` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (event_target, confidence 1.00) [cite: aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json#specifications.Target.Arn sha256:26ebd196e9a7]
- `arn:aws:sns:us-east-1:123456789012:storefront-events` → `arn:aws:sqs:us-east-1:123456789012:storefront-orders` (subscription, confidence 1.00) [cite: aws_sns_topic/us-east-1/storefront-events.json#specifications.Subscriptions[0].Endpoint sha256:548601ead8c0]
- `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.roleArn sha256:e25ed9c8e0ec]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers` → `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-12874fb82c9db66ed.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:3adac5c9a964] [cite: aws_launch_template/us-east-1/lt-bad06a08aee200bf2.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:3a695fbf8e2c]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:elasticache:us-east-1:123456789012:replicationgroup:storefront-cache` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-12874fb82c9db66ed.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:3adac5c9a964] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:741478c1710f]
- `arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup:fddff19a-c8c9-4401-9bef-23ac1c8a6198:autoScalingGroupName/storefront-workers` → `arn:aws:rds:us-east-1:123456789012:db:orders-db` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-2bf145296ea5159ab.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:e5bbe17547b7] [cite: aws_launch_template/us-east-1/lt-bad06a08aee200bf2.json#specifications.LaunchTemplateData.SecurityGroupIds[0] sha256:3a695fbf8e2c]
- `arn:aws:ecs:us-east-1:123456789012:service/storefront/web` → `arn:aws:rds:us-east-1:123456789012:db:orders-db` (network_access, confidence 0.90) [cite: aws_security_group/us-east-1/sg-2bf145296ea5159ab.json#specifications.IpPermissions[1].UserIdGroupPairs[0].GroupId sha256:e5bbe17547b7] [cite: aws_ecs_service/us-east-1/storefront_web.json#specifications.networkConfiguration.awsvpcConfiguration.securityGroups[0] sha256:741478c1710f]

## Security Findings

- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-2bf145296ea5159ab' allows ingress from 0.0.0.0/0 on tcp port 22. [cite: aws_security_group/us-east-1/sg-2bf145296ea5159ab.json#specifications.IpPermissions[0].IpRanges[0] sha256:e5bbe17547b7]
- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-e4a0ee2dde2bb1f50' allows ingress from 0.0.0.0/0 on tcp port 443. [cite: aws_security_group/us-east-1/sg-e4a0ee2dde2bb1f50.json#specifications.IpPermissions[0].IpRanges[0] sha256:d0bb4c047521]
- [CRITICAL] OVERLY_PERMISSIVE_IAM_POLICY: IAM role 'order-lambda-role' inline policy 'too-broad' allows Action '*' on Resource '*'. [cite: aws_iam_role/global/order-lambda-role.json#specifications.InlinePolicies.too-broad.Statement[0] sha256:f25f33238ee8]
- [HIGH] PUBLIC_S3_BUCKET: S3 bucket 'orders-public-assets' ACL grants READ to the AllUsers group. [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.bucket-acl.Grants[1] sha256:dddfb5d26229]
