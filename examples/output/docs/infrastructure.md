# Infrastructure Documentation

## Inventory

| Resource Type | Region | Count |
| :--- | :--- | ---: |
| aws_acm_certificate | us-east-1 | 1 |
| aws_cloudfront_distribution | global | 1 |
| aws_cloudwatch_log_group | us-east-1 | 1 |
| aws_db_instance | us-east-1 | 1 |
| aws_dynamodb_table | us-east-1 | 1 |
| aws_iam_role | global | 2 |
| aws_instance | us-east-1 | 1 |
| aws_internet_gateway | us-east-1 | 1 |
| aws_lambda_function | us-east-1 | 1 |
| aws_lb | us-east-1 | 1 |
| aws_lb_listener | us-east-1 | 1 |
| aws_lb_target_group | us-east-1 | 1 |
| aws_nat_gateway | us-east-1 | 1 |
| aws_route53_zone | global | 1 |
| aws_route_table | us-east-1 | 3 |
| aws_s3_bucket | global | 2 |
| aws_security_group | us-east-1 | 3 |
| aws_sfn_state_machine | us-east-1 | 1 |
| aws_subnet | us-east-1 | 3 |
| aws_vpc | us-east-1 | 1 |
| aws_vpc_endpoint | us-east-1 | 1 |
| aws_wafv2_web_acl | global | 1 |

### aws_cloudfront_distribution

- `K4SJFH541UU7J` (global, `arn:aws:cloudfront::123456789012:distribution/K4SJFH541UU7J`) [cite: aws_cloudfront_distribution/global/K4SJFH541UU7J.json#specifications.Id sha256:c8f5b9997e5b]

### aws_cloudwatch_log_group

- `/aws/lambda/order-processor` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor`) [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:fbea7b949378]

### aws_db_instance

- `orders-db` (us-east-1, `arn:aws:rds:us-east-1:123456789012:db:orders-db`) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBInstanceIdentifier sha256:0bbdd86d95b1]

### aws_dynamodb_table

- `orders` (us-east-1, `arn:aws:dynamodb:us-east-1:123456789012:table/orders`) [cite: aws_dynamodb_table/us-east-1/orders.json#specifications.TableName sha256:392c8d77dbb7]

### aws_iam_role

- `order-lambda-role` (global, `arn:aws:iam::123456789012:role/order-lambda-role`) [cite: aws_iam_role/global/order-lambda-role.json#specifications.RoleName sha256:0cc0df19cf76]
- `orders-app-role` (global, `arn:aws:iam::123456789012:role/orders-app-role`) [cite: aws_iam_role/global/orders-app-role.json#specifications.RoleName sha256:80d44983179c]

### aws_instance

- `i-96ebec6d01233d3d7` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7`) [cite: aws_instance/us-east-1/i-96ebec6d01233d3d7.json#specifications.InstanceId sha256:68d87346a89c]

### aws_internet_gateway

- `igw-e27d9033` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-e27d9033`) [cite: aws_internet_gateway/us-east-1/igw-e27d9033.json#specifications.InternetGatewayId sha256:d12085d49a4c]

### aws_lambda_function

- `order-processor` (us-east-1, `arn:aws:lambda:us-east-1:123456789012:function:order-processor`) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:74e5dcbc0443]

### aws_nat_gateway

- `nat-3e17f5a22ce211a96` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-3e17f5a22ce211a96`) [cite: aws_nat_gateway/us-east-1/nat-3e17f5a22ce211a96.json#specifications.NatGatewayId sha256:7c893fcec201]

### aws_route_table

- `rtb-395e2831` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-395e2831`) [cite: aws_route_table/us-east-1/rtb-395e2831.json#specifications.RouteTableId sha256:6a3994757899]
- `rtb-57076453` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-57076453`) [cite: aws_route_table/us-east-1/rtb-57076453.json#specifications.RouteTableId sha256:1c362a7d7cb5]
- `rtb-590d89f0` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590d89f0`) [cite: aws_route_table/us-east-1/rtb-590d89f0.json#specifications.RouteTableId sha256:6e9ca5d72123]

### aws_s3_bucket

- `orders-public-assets` (global, `arn:aws:s3:::orders-public-assets`) [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.Name sha256:dddfb5d26229]
- `storefront-static` (global, `arn:aws:s3:::storefront-static`) [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]

### aws_security_group

- `sg-347a556c97894d9e4` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-347a556c97894d9e4`) [cite: aws_security_group/us-east-1/sg-347a556c97894d9e4.json#specifications.GroupId sha256:6ddb81d2656c]
- `sg-57d34a1b59fbd9d55` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-57d34a1b59fbd9d55`) [cite: aws_security_group/us-east-1/sg-57d34a1b59fbd9d55.json#specifications.GroupId sha256:d938cc83dc91]
- `sg-ceb6d3dc119d60702` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-ceb6d3dc119d60702`) [cite: aws_security_group/us-east-1/sg-ceb6d3dc119d60702.json#specifications.GroupId sha256:b9d22a2ef81d]

### aws_sfn_state_machine

- `order-flow` (us-east-1, `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow`) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.name sha256:1a9ded1385d5]

### aws_subnet

- `subnet-86551e9d` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-86551e9d`) [cite: aws_subnet/us-east-1/subnet-86551e9d.json#specifications.SubnetId sha256:83187ba2044f]
- `subnet-dc94c752` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752`) [cite: aws_subnet/us-east-1/subnet-dc94c752.json#specifications.SubnetId sha256:ebcb8ce94d87]
- `subnet-ee0601cc` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-ee0601cc`) [cite: aws_subnet/us-east-1/subnet-ee0601cc.json#specifications.SubnetId sha256:fa9e8b9c4765]

### aws_vpc

- `vpc-1561eea5` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5`) [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]

### aws_vpc_endpoint

- `vpce-a3573b69` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-a3573b69`) [cite: aws_vpc_endpoint/us-east-1/vpce-a3573b69.json#specifications.VpcEndpointId sha256:cc2c20265931]

## Architecture Patterns

### Compute in VPC

EC2 instance 'i-96ebec6d01233d3d7' runs in VPC 'vpc-1561eea5'. (confidence 1.00) [cite: aws_instance/us-east-1/i-96ebec6d01233d3d7.json#specifications.VpcId sha256:68d87346a89c] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7` [cite: aws_instance/us-east-1/i-96ebec6d01233d3d7.json#specifications.VpcId sha256:68d87346a89c]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]

### Serverless Application

Lambda function 'order-processor' runs with IAM role 'order-lambda-role' and references DynamoDB table(s) 'orders' in its environment variables. (confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:74e5dcbc0443] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:74e5dcbc0443]

- Participant `arn:aws:lambda:us-east-1:123456789012:function:order-processor` [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:74e5dcbc0443] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:74e5dcbc0443]

## Interactions

- `arn:aws:cloudfront::123456789012:distribution/K4SJFH541UU7J` → `arn:aws:wafv2:global:123456789012:global/webacl/storefront-waf/45c1df2a-6eb9-40fa-a6ea-d3054f42d04c` (waf_protection, confidence 1.00) [cite: aws_cloudfront_distribution/global/K4SJFH541UU7J.json#specifications.DistributionConfig.WebACLId sha256:c8f5b9997e5b]
- `arn:aws:cloudfront::123456789012:distribution/K4SJFH541UU7J` → `arn:aws:s3:::storefront-static` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/K4SJFH541UU7J.json#specifications.DistributionConfig.Origins.Items[0].DomainName sha256:c8f5b9997e5b] [cite: aws_s3_bucket/global/storefront-static.json#specifications.Name sha256:85655120f74e]
- `arn:aws:cloudfront::123456789012:distribution/K4SJFH541UU7J` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (cdn_origin, confidence 1.00) [cite: aws_cloudfront_distribution/global/K4SJFH541UU7J.json#specifications.DistributionConfig.Origins.Items[1].DomainName sha256:c8f5b9997e5b] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:f87889f960fd]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-96ebec6d01233d3d7.json#specifications.VpcId sha256:68d87346a89c] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_instance/us-east-1/i-96ebec6d01233d3d7.json#specifications.IamInstanceProfile.Arn sha256:68d87346a89c]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-ceb6d3dc119d60702` (security_group, confidence 0.90) [cite: aws_instance/us-east-1/i-96ebec6d01233d3d7.json#specifications.SecurityGroups[0].GroupId sha256:68d87346a89c]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-96ebec6d01233d3d7` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-86551e9d` (subnet_placement, confidence 1.00) [cite: aws_instance/us-east-1/i-96ebec6d01233d3d7.json#specifications.SubnetId sha256:68d87346a89c]
- `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-e27d9033` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_internet_gateway/us-east-1/igw-e27d9033.json#specifications.Attachments[0].VpcId sha256:d12085d49a4c]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-3e17f5a22ce211a96` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-3e17f5a22ce211a96.json#specifications.VpcId sha256:7c893fcec201] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-3e17f5a22ce211a96` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752` (subnet_placement, confidence 1.00) [cite: aws_nat_gateway/us-east-1/nat-3e17f5a22ce211a96.json#specifications.SubnetId sha256:7c893fcec201]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-395e2831` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-395e2831.json#specifications.VpcId sha256:6a3994757899] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-395e2831` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-395e2831.json#specifications.Associations[0].SubnetId sha256:6a3994757899]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-395e2831` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-ee0601cc` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-395e2831.json#specifications.Associations[1].SubnetId sha256:6a3994757899]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-395e2831` → `arn:aws:ec2:us-east-1:123456789012:internet-gateway/igw-e27d9033` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-395e2831.json#specifications.Routes[1].GatewayId sha256:6a3994757899]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-57076453` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-57076453.json#specifications.VpcId sha256:1c362a7d7cb5] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590d89f0` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590d89f0.json#specifications.VpcId sha256:6e9ca5d72123] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590d89f0` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-86551e9d` (route_table_association, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590d89f0.json#specifications.Associations[0].SubnetId sha256:6e9ca5d72123]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590d89f0` → `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-a3573b69` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590d89f0.json#specifications.Routes[2].GatewayId sha256:6e9ca5d72123]
- `arn:aws:ec2:us-east-1:123456789012:route-table/rtb-590d89f0` → `arn:aws:ec2:us-east-1:123456789012:natgateway/nat-3e17f5a22ce211a96` (route_target, confidence 1.00) [cite: aws_route_table/us-east-1/rtb-590d89f0.json#specifications.Routes[1].NatGatewayId sha256:6e9ca5d72123]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-347a556c97894d9e4` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-347a556c97894d9e4.json#specifications.VpcId sha256:6ddb81d2656c] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-57d34a1b59fbd9d55` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-57d34a1b59fbd9d55.json#specifications.VpcId sha256:d938cc83dc91] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-ceb6d3dc119d60702` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-ceb6d3dc119d60702.json#specifications.VpcId sha256:b9d22a2ef81d] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-86551e9d` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-86551e9d.json#specifications.VpcId sha256:83187ba2044f] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-dc94c752.json#specifications.VpcId sha256:ebcb8ce94d87] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-ee0601cc` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_subnet/us-east-1/subnet-ee0601cc.json#specifications.VpcId sha256:fa9e8b9c4765] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:ec2:us-east-1:123456789012:vpc-endpoint/vpce-a3573b69` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_vpc_endpoint/us-east-1/vpce-a3573b69.json#specifications.VpcId sha256:cc2c20265931] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434430983056` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (lb_listener, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434430983056.json#specifications.LoadBalancerArn sha256:9755e4d60e68]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434430983056` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` (forwards_to, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434430983056.json#specifications.DefaultActions[0].TargetGroupArn sha256:9755e4d60e68]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434430983056` → `arn:aws:acm:us-east-1:123456789012:certificate/59f7c298-c41f-48f5-a3db-cb8263d5fcc6` (certificate, confidence 1.00) [cite: aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434430983056.json#specifications.Certificates[0].CertificateArn sha256:9755e4d60e68]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.VpcId sha256:f87889f960fd] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-dc94c752` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[0].SubnetId sha256:f87889f960fd]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:subnet/subnet-ee0601cc` (subnet_placement, confidence 1.00) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.AvailabilityZones[1].SubnetId sha256:f87889f960fd]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-347a556c97894d9e4` (security_group, confidence 0.90) [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.SecurityGroups[0] sha256:f87889f960fd]
- `arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-1561eea5` (vpc_connection, confidence 1.00) [cite: aws_lb_target_group/us-east-1/storefront-tg_50dc6c495c0c9188.json#specifications.VpcId sha256:b9e0fb318bff] [cite: aws_vpc/us-east-1/vpc-1561eea5.json#specifications.VpcId sha256:507efbbe6597]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:74e5dcbc0443]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:dynamodb:us-east-1:123456789012:table/orders` (dynamodb_access, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:74e5dcbc0443]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor` (log_group, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:74e5dcbc0443] [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:fbea7b949378]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-ceb6d3dc119d60702` (security_group, confidence 0.90) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.VpcSecurityGroups[0].VpcSecurityGroupId sha256:0bbdd86d95b1]
- `arn:aws:route53:::hostedzone/JX2QH3ZSOFDJU6N` → `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/JX2QH3ZSOFDJU6N.json#specifications.ResourceRecordSets[2].AliasTarget.DNSName sha256:eca921de2aec] [cite: aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json#specifications.DNSName sha256:f87889f960fd]
- `arn:aws:route53:::hostedzone/JX2QH3ZSOFDJU6N` → `arn:aws:cloudfront::123456789012:distribution/K4SJFH541UU7J` (dns_alias, confidence 1.00) [cite: aws_route53_zone/global/JX2QH3ZSOFDJU6N.json#specifications.ResourceRecordSets[3].AliasTarget.DNSName sha256:eca921de2aec] [cite: aws_cloudfront_distribution/global/K4SJFH541UU7J.json#specifications.DomainName sha256:c8f5b9997e5b]
- `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.roleArn sha256:1a9ded1385d5]

## Security Findings

- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-347a556c97894d9e4' allows ingress from 0.0.0.0/0 on tcp port 443. [cite: aws_security_group/us-east-1/sg-347a556c97894d9e4.json#specifications.IpPermissions[0].IpRanges[0] sha256:6ddb81d2656c]
- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-ceb6d3dc119d60702' allows ingress from 0.0.0.0/0 on tcp port 22. [cite: aws_security_group/us-east-1/sg-ceb6d3dc119d60702.json#specifications.IpPermissions[0].IpRanges[0] sha256:b9d22a2ef81d]
- [CRITICAL] OVERLY_PERMISSIVE_IAM_POLICY: IAM role 'order-lambda-role' inline policy 'too-broad' allows Action '*' on Resource '*'. [cite: aws_iam_role/global/order-lambda-role.json#specifications.InlinePolicies.too-broad.Statement[0] sha256:0cc0df19cf76]
- [HIGH] PUBLIC_S3_BUCKET: S3 bucket 'orders-public-assets' ACL grants READ to the AllUsers group. [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.bucket-acl.Grants[1] sha256:dddfb5d26229]
