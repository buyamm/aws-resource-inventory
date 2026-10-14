# Activity Flow & Architecture Analysis

**Resources analyzed:** 14  
**Relationships identified:** 11  
**Architecture patterns:** 2  
**Security findings:** 3

## Architecture Patterns

### Compute in VPC (confidence 1.00)
EC2 instance 'i-9f9c49245e711cdd9' runs in VPC 'vpc-db407a2e'. [cite: aws_instance/us-east-1/i-9f9c49245e711cdd9.json#specifications.VpcId sha256:80dddd3538c3] [cite: aws_vpc/us-east-1/vpc-db407a2e.json#specifications.VpcId sha256:bc584957dd47]

### Serverless Application (confidence 0.95)
Lambda function 'order-processor' runs with IAM role 'order-lambda-role' and references DynamoDB table(s) 'orders' in its environment variables. [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Role sha256:9e210849e20b] [cite: aws_lambda_function/us-east-1/order-processor.json#specifications.Environment.Variables.TABLE_NAME sha256:9e210849e20b]

## Relationships

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

### [HIGH] UNRESTRICTED_SECURITY_GROUP_ACCESS
Security group 'sg-7c880b8c4789c2216' allows ingress from 0.0.0.0/0 on tcp port 22. [cite: aws_security_group/us-east-1/sg-7c880b8c4789c2216.json#specifications.IpPermissions[0].IpRanges[0] sha256:50964fd4d7da]

### [CRITICAL] OVERLY_PERMISSIVE_IAM_POLICY
IAM role 'order-lambda-role' inline policy 'too-broad' allows Action '*' on Resource '*'. [cite: aws_iam_role/global/order-lambda-role.json#specifications.InlinePolicies.too-broad.Statement[0] sha256:3fc73fabd37b]

### [HIGH] PUBLIC_S3_BUCKET
S3 bucket 'orders-public-assets' ACL grants READ to the AllUsers group. [cite: aws_s3_bucket/global/orders-public-assets.json#specifications.bucket-acl.Grants[1] sha256:dddfb5d26229]

## Patterns Not Detectable

- API Gateway + Lambda + DynamoDB: API Gateway is not a Supported_Resource_Type; the pattern cannot be detected from collected data.
- EC2 + Load Balancer: Elastic Load Balancing is not a Supported_Resource_Type; the pattern cannot be detected from collected data.
- S3 + CloudFront: CloudFront is not a Supported_Resource_Type; the pattern cannot be detected from collected data.

## Evidence Citations

| Resource ARN | Spec File | Property Path | Source Checksum | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9` | `aws_instance/us-east-1/i-9f9c49245e711cdd9.json` | `specifications.VpcId` | `80dddd3538c3` | `"vpc-db407a2e"` |
| `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-db407a2e` | `aws_vpc/us-east-1/vpc-db407a2e.json` | `specifications.VpcId` | `bc584957dd47` | `"vpc-db407a2e"` |
| `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9` | `aws_instance/us-east-1/i-9f9c49245e711cdd9.json` | `specifications.IamInstanceProfile.Arn` | `80dddd3538c3` | `"arn:aws:iam::123456789012:instance-profile/orders-app-role"` |
| `arn:aws:ec2:us-east-1:123456789012:instance/i-9f9c49245e711cdd9` | `aws_instance/us-east-1/i-9f9c49245e711cdd9.json` | `specifications.SecurityGroups[0].GroupId` | `80dddd3538c3` | `"sg-7c880b8c4789c2216"` |
| `arn:aws:ec2:us-east-1:123456789012:security-group/sg-285ba61d10f344e74` | `aws_security_group/us-east-1/sg-285ba61d10f344e74.json` | `specifications.VpcId` | `d504cc1c5642` | `"vpc-ce9c3403"` |
| `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-ce9c3403` | `aws_vpc/us-east-1/vpc-ce9c3403.json` | `specifications.VpcId` | `154336ecf044` | `"vpc-ce9c3403"` |
| `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216` | `aws_security_group/us-east-1/sg-7c880b8c4789c2216.json` | `specifications.VpcId` | `50964fd4d7da` | `"vpc-db407a2e"` |
| `arn:aws:ec2:us-east-1:123456789012:security-group/sg-cc3138f31141d30f1` | `aws_security_group/us-east-1/sg-cc3138f31141d30f1.json` | `specifications.VpcId` | `ad1446f62b03` | `"vpc-db407a2e"` |
| `arn:aws:lambda:us-east-1:123456789012:function:order-processor` | `aws_lambda_function/us-east-1/order-processor.json` | `specifications.Role` | `9e210849e20b` | `"arn:aws:iam::123456789012:role/order-lambda-role"` |
| `arn:aws:lambda:us-east-1:123456789012:function:order-processor` | `aws_lambda_function/us-east-1/order-processor.json` | `specifications.Environment.Variables.TABLE_NAME` | `9e210849e20b` | `"orders"` |
| `arn:aws:lambda:us-east-1:123456789012:function:order-processor` | `aws_lambda_function/us-east-1/order-processor.json` | `specifications.FunctionName` | `9e210849e20b` | `"order-processor"` |
| `arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/order-processor` | `aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json` | `specifications.logGroupName` | `9bb64f241ebc` | `"/aws/lambda/order-processor"` |
| `arn:aws:rds:us-east-1:123456789012:db:orders-db` | `aws_db_instance/us-east-1/orders-db.json` | `specifications.VpcSecurityGroups[0].VpcSecurityGroupId` | `8560c33d1770` | `"sg-7c880b8c4789c2216"` |
| `arn:aws:states:us-east-1:123456789012:stateMachine:order-flow` | `aws_sfn_state_machine/us-east-1/order-flow.json` | `specifications.roleArn` | `50b7ff5b4ac2` | `"arn:aws:iam::123456789012:role/order-lambda-role"` |
| `arn:aws:ec2:us-east-1:123456789012:security-group/sg-7c880b8c4789c2216` | `aws_security_group/us-east-1/sg-7c880b8c4789c2216.json` | `specifications.IpPermissions[0].IpRanges[0]` | `50964fd4d7da` | `{"CidrIp": "0.0.0.0/0"}` |
| `arn:aws:iam::123456789012:role/order-lambda-role` | `aws_iam_role/global/order-lambda-role.json` | `specifications.InlinePolicies.too-broad.Statement[0]` | `3fc73fabd37b` | `{"Action": "*", "Effect": "Allow", "Resource": "*"}` |
| `arn:aws:s3:::orders-public-assets` | `aws_s3_bucket/global/orders-public-assets.json` | `specifications.bucket-acl.Grants[1]` | `dddfb5d26229` | `{"Grantee": {"Type": "Group", "URI": "http://acs.amazonaws.com/groups/global/AllUsers"}, "Permission": "READ"}` |
