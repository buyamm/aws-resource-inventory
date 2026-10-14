# Infrastructure Documentation

## Inventory

| Resource Type | Region | Count |
| :--- | :--- | ---: |
| aws_cloudwatch_log_group | us-east-1 | 1 |
| aws_db_instance | us-east-1 | 1 |
| aws_dynamodb_table | us-east-1 | 1 |
| aws_iam_role | global | 2 |
| aws_instance | us-east-1 | 1 |
| aws_lambda_function | us-east-1 | 1 |
| aws_s3_bucket | global | 1 |
| aws_security_group | us-east-1 | 3 |
| aws_sfn_state_machine | us-east-1 | 1 |
| aws_vpc | us-east-1 | 2 |

### aws_cloudwatch_log_group

- `/aws/lambda/order-processor` (us-east-1, `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor`) [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:9bb64f241ebc]

### aws_db_instance

- `orders-db` (us-east-1, `arn:aws:rds:us-east-1:123456789012:db:orders-db`) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.DBInstanceIdentifier sha256:8560c33d1770]

### aws_dynamodb_table

- `orders` (us-east-1, `arn:aws:dynamodb:us-east-1:123456789012:table/orders`) [cite: aws_dynamodb_table/us-east-1/orders.json#specifications.TableName sha256:00bfd6d2f678]

### aws_iam_role

- `order-lambda-role` (global, `arn:aws:iam::123456789012:role/order-lambda-role`) [cite: aws_iam_role/global/order-lambda-role.json#specifications.RoleName sha256:3fc73fabd37b]
- `orders-app-role` (global, `arn:aws:iam::123456789012:role/orders-app-role`) [cite: aws_iam_role/global/orders-app-role.json#specifications.RoleName sha256:e98756e4d820]

### aws_instance

- `i-9f9c49245e711cdd9` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9`) [cite: aws_instance/us-east-1/i-9f9c49245e711cdd9.json#specifications.InstanceId sha256:80dddd3538c3]

### aws_lambda_function

- `order-processor` (us-east-1, `arn:aws:lambda:us-east-1:123456789012:function:order-processor`) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:9e210849e20b]

### aws_s3_bucket

- `orders-public-assets` (global, `arn:aws:s3:::orders-public-assets`) [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.Name sha256:dddfb5d26229]

### aws_security_group

- `sg-285ba61d10f344e74` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-285ba61d10f344e74`) [cite: aws_security_group/us-east-1/sg-285ba61d10f344e74.json#specifications.GroupId sha256:d504cc1c5642]
- `sg-7c880b8c4789c2216` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216`) [cite: aws_security_group/us-east-1/sg-7c880b8c4789c2216.json#specifications.GroupId sha256:50964fd4d7da]
- `sg-cc3138f31141d30f1` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:security-group/sg-cc3138f31141d30f1`) [cite: aws_security_group/us-east-1/sg-cc3138f31141d30f1.json#specifications.GroupId sha256:ad1446f62b03]

### aws_sfn_state_machine

- `order-flow` (us-east-1, `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow`) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.name sha256:50b7ff5b4ac2]

### aws_vpc

- `vpc-ce9c3403` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-ce9c3403`) [cite: aws_vpc/us-east-1/vpc-ce9c3403.json#specifications.VpcId sha256:154336ecf044]
- `vpc-db407a2e` (us-east-1, `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e`) [cite: aws_vpc/us-east-1/vpc-db407a2e.json#specifications.VpcId sha256:bc584957dd47]

## Architecture Patterns

### Compute in VPC

EC2 instance 'i-9f9c49245e711cdd9' runs in VPC 'vpc-db407a2e'. (confidence 1.00) [cite: aws_instance/us-east-1/i-9f9c49245e711cdd9.json#specifications.VpcId sha256:80dddd3538c3] [cite: aws_vpc/us-east-1/vpc-db407a2e.json#specifications.VpcId sha256:bc584957dd47]

- Participant `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9` [cite: aws_instance/us-east-1/i-9f9c49245e711cdd9.json#specifications.VpcId sha256:80dddd3538c3]
- Participant `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e` [cite: aws_vpc/us-east-1/vpc-db407a2e.json#specifications.VpcId sha256:bc584957dd47]

### Serverless Application

Lambda function 'order-processor' runs with IAM role 'order-lambda-role' and references DynamoDB table(s) 'orders' in its environment variables. (confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:9e210849e20b] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:9e210849e20b]

- Participant `arn:aws:lambda:us-east-1:123456789012:function:order-processor` [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:9e210849e20b] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:9e210849e20b]

## Interactions

- `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e` (vpc_connection, confidence 1.00) [cite: aws_instance/us-east-1/i-9f9c49245e711cdd9.json#specifications.VpcId sha256:80dddd3538c3] [cite: aws_vpc/us-east-1/vpc-db407a2e.json#specifications.VpcId sha256:bc584957dd47]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9` → `arn:aws:iam::123456789012:role/orders-app-role` (iam_role_usage, confidence 0.95) [cite: aws_instance/us-east-1/i-9f9c49245e711cdd9.json#specifications.IamInstanceProfile.Arn sha256:80dddd3538c3]
- `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216` (security_group, confidence 0.90) [cite: aws_instance/us-east-1/i-9f9c49245e711cdd9.json#specifications.SecurityGroups[0].GroupId sha256:80dddd3538c3]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-285ba61d10f344e74` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-ce9c3403` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-285ba61d10f344e74.json#specifications.VpcId sha256:d504cc1c5642] [cite: aws_vpc/us-east-1/vpc-ce9c3403.json#specifications.VpcId sha256:154336ecf044]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-7c880b8c4789c2216.json#specifications.VpcId sha256:50964fd4d7da] [cite: aws_vpc/us-east-1/vpc-db407a2e.json#specifications.VpcId sha256:bc584957dd47]
- `arn:aws:ec2:us-east-1:123456789012:security-group/sg-cc3138f31141d30f1` → `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e` (vpc_connection, confidence 1.00) [cite: aws_security_group/us-east-1/sg-cc3138f31141d30f1.json#specifications.VpcId sha256:ad1446f62b03] [cite: aws_vpc/us-east-1/vpc-db407a2e.json#specifications.VpcId sha256:bc584957dd47]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:9e210849e20b]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:dynamodb:us-east-1:123456789012:table/orders` (dynamodb_access, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:9e210849e20b]
- `arn:aws:lambda:us-east-1:123456789012:function:order-processor` → `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor` (log_group, confidence 1.00) [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.FunctionName sha256:9e210849e20b] [cite: aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json#specifications.logGroupName sha256:9bb64f241ebc]
- `arn:aws:rds:us-east-1:123456789012:db:orders-db` → `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216` (security_group, confidence 0.90) [cite: aws_db_instance/us-east-1/orders-db.json#specifications.VpcSecurityGroups[0].VpcSecurityGroupId sha256:8560c33d1770]
- `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow` → `arn:aws:iam::123456789012:role/order-lambda-role` (iam_role_usage, confidence 0.95) [cite: aws_sfn_state_machine/us-east-1/order-flow.json#specifications.roleArn sha256:50b7ff5b4ac2]

## Security Findings

- [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS: Security group 'sg-7c880b8c4789c2216' allows ingress from 0.0.0.0/0 on tcp port 22. [cite: aws_security_group/us-east-1/sg-7c880b8c4789c2216.json#specifications.IpPermissions[0].IpRanges[0] sha256:50964fd4d7da]
- [CRITICAL] OVERLY_PERMISSIVE_IAM_POLICY: IAM role 'order-lambda-role' inline policy 'too-broad' allows Action '*' on Resource '*'. [cite: aws_iam_role/global/order-lambda-role.json#specifications.InlinePolicies.too-broad.Statement[0] sha256:3fc73fabd37b]
- [HIGH] PUBLIC_S3_BUCKET: S3 bucket 'orders-public-assets' ACL grants READ to the AllUsers group. [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.bucket-acl.Grants[1] sha256:dddfb5d26229]
