# One import block per generated resource (Terraform >= 1.5):
# `terraform plan` lists them, `terraform apply` records them in state
# without changing the resources when the plan has no other changes.

# aws_iam_role/global/storefront-exec-role.json
import {
  to = module.iam.aws_iam_role.exec_role
  id = "storefront-exec-role"
}

# aws_iam_role/global/storefront-exec-role.json
import {
  to = module.iam.aws_iam_role_policy_attachment.exec_role_amazonecstaskexecutionrolepolicy
  id = "storefront-exec-role/arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# aws_iam_role/global/order-lambda-role.json
import {
  to = module.iam.aws_iam_role.order_lambda_role
  id = "order-lambda-role"
}

# aws_iam_role/global/order-lambda-role.json
import {
  to = module.iam.aws_iam_role_policy.order_lambda_role_too_broad
  id = "order-lambda-role:too-broad"
}

# aws_iam_role/global/orders-app-role.json
import {
  to = module.iam.aws_iam_role.orders_app_role
  id = "orders-app-role"
}

# aws_iam_role/global/storefront-scheduler-role.json
import {
  to = module.iam.aws_iam_role.scheduler_role
  id = "storefront-scheduler-role"
}

# aws_iam_role/global/storefront-task-role.json
import {
  to = module.iam.aws_iam_role.task_role
  id = "storefront-task-role"
}

# aws_cloudwatch_log_group/us-east-1/aws_lambda_order-processor.json
import {
  to = module.observability.aws_cloudwatch_log_group.aws_lambda_order_processor
  id = "/aws/lambda/order-processor"
}

# aws_cloudwatch_log_group/us-east-1/ecs_storefront-web.json
import {
  to = module.observability.aws_cloudwatch_log_group.ecs_storefront_web
  id = "/ecs/storefront-web"
}

# aws_vpc/us-east-1/vpc-040f0f81.json
import {
  to = module.network.aws_vpc.orders_vpc
  id = "vpc-040f0f81"
}

# aws_subnet/us-east-1/subnet-7f177dcb.json
import {
  to = module.network.aws_subnet.orders_private_a
  id = "subnet-7f177dcb"
}

# aws_subnet/us-east-1/subnet-084ef767.json
import {
  to = module.network.aws_subnet.public_a
  id = "subnet-084ef767"
}

# aws_subnet/us-east-1/subnet-a6f66dc7.json
import {
  to = module.network.aws_subnet.public_b
  id = "subnet-a6f66dc7"
}

# aws_route_table/us-east-1/rtb-ee1782b8.json
import {
  to = module.network.aws_route_table.private
  id = "rtb-ee1782b8"
}

# aws_route_table/us-east-1/rtb-ee1782b8.json
import {
  to = module.network.aws_route_table_association.private_subnet_7f177dcb
  id = "subnet-7f177dcb/rtb-ee1782b8"
}

# aws_route_table/us-east-1/rtb-47bf1246.json
import {
  to = module.network.aws_route_table.public
  id = "rtb-47bf1246"
}

# aws_route_table/us-east-1/rtb-47bf1246.json
import {
  to = module.network.aws_route_table_association.public_subnet_084ef767
  id = "subnet-084ef767/rtb-47bf1246"
}

# aws_route_table/us-east-1/rtb-47bf1246.json
import {
  to = module.network.aws_route_table_association.public_subnet_a6f66dc7
  id = "subnet-a6f66dc7/rtb-47bf1246"
}

# aws_route_table/us-east-1/rtb-8fc56d9e.json
import {
  to = module.network.aws_route_table.rtb_8fc56d9e
  id = "rtb-8fc56d9e"
}

# aws_internet_gateway/us-east-1/igw-c94e6ba3.json
import {
  to = module.network.aws_internet_gateway.igw
  id = "igw-c94e6ba3"
}

# aws_nat_gateway/us-east-1/nat-8af9c7bd4aed62d36.json
import {
  to = module.network.aws_nat_gateway.nat
  id = "nat-8af9c7bd4aed62d36"
}

# aws_vpc_endpoint/us-east-1/vpce-170a3c5e.json
import {
  to = module.network.aws_vpc_endpoint.s3
  id = "vpce-170a3c5e"
}

# aws_security_group/us-east-1/sg-e351ba83453fe3b63.json
import {
  to = module.network.aws_security_group.alb_sg
  id = "sg-e351ba83453fe3b63"
}

# aws_security_group/us-east-1/sg-e351ba83453fe3b63.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.alb_sg_ingress_tcp_443
  id = "sgr-3c10a568e478102e8"
}

# aws_security_group/us-east-1/sg-e351ba83453fe3b63.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.alb_sg_egress_all
  id = "sgr-ce21b8989ffd93f76"
}

# aws_security_group/us-east-1/sg-b7692d5b41942a421.json
import {
  to = module.network.aws_security_group.app
  id = "sg-b7692d5b41942a421"
}

# aws_security_group/us-east-1/sg-b7692d5b41942a421.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.app_ingress_tcp_6379
  id = "sgr-9d0c8cdd25bf9e25b"
}

# aws_security_group/us-east-1/sg-b7692d5b41942a421.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.app_ingress_tcp_80
  id = "sgr-fe3ba9b2082dd23dc"
}

# aws_security_group/us-east-1/sg-b7692d5b41942a421.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.app_egress_all
  id = "sgr-ffb44cdf38aa3f177"
}

# aws_security_group/us-east-1/sg-1f2b0a4eff89696aa.json
import {
  to = module.network.aws_security_group.default
  id = "sg-1f2b0a4eff89696aa"
}

# aws_security_group/us-east-1/sg-1f2b0a4eff89696aa.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.default_egress_all
  id = "sgr-3d9b8032b1879d361"
}

# aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json
import {
  to = module.network.aws_security_group.orders_web_sg
  id = "sg-80de5126f2f05dbc9"
}

# aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.orders_web_sg_egress_all
  id = "sgr-13098ef73a78053d3"
}

# aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.orders_web_sg_ingress_tcp_22
  id = "sgr-73f5c51533480388a"
}

# aws_security_group/us-east-1/sg-80de5126f2f05dbc9.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.orders_web_sg_ingress_tcp_5432
  id = "sgr-b30ff45d4d07224fb"
}

# aws_route53_zone/global/F2D50YHDFNN6736.json
import {
  to = module.edge.aws_route53_zone.example_com
  id = "F2D50YHDFNN6736"
}

# aws_route53_zone/global/F2D50YHDFNN6736.json
import {
  to = module.edge.aws_route53_record.example_com_api_a
  id = "F2D50YHDFNN6736_api.example.com_A"
}

# aws_route53_zone/global/F2D50YHDFNN6736.json
import {
  to = module.edge.aws_route53_record.example_com_shop_a
  id = "F2D50YHDFNN6736_shop.example.com_A"
}

# aws_acm_certificate/us-east-1/1492cb3f-a6df-47d4-892f-f87748ae6367.json
import {
  to = module.edge.aws_acm_certificate.shop_example_com
  id = "arn:aws:acm:us-east-1:123456789012:certificate/1492cb3f-a6df-47d4-892f-f87748ae6367"
}

# aws_wafv2_web_acl/global/storefront-waf_b5e7fc2f-fa34-44a4-8362-0cb65c2450a9.json
import {
  to = module.edge.aws_wafv2_web_acl.waf
  id = "b5e7fc2f-fa34-44a4-8362-0cb65c2450a9/storefront-waf/CLOUDFRONT"
}

# aws_cloudfront_distribution/global/RXBBW1AS174FR.json
import {
  to = module.edge.aws_cloudfront_distribution.shop_example_com
  id = "RXBBW1AS174FR"
}

# aws_lb/us-east-1/app_storefront-alb_50dc6c495c0c9188.json
import {
  to = module.edge.aws_lb.alb
  id = "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/storefront-alb/50dc6c495c0c9188"
}

# aws_lb_target_group/us-east-1/storefront-tg_50dc6c495c0c9188.json
import {
  to = module.edge.aws_lb_target_group.tg
  id = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/storefront-tg/50dc6c495c0c9188"
}

# aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434489454224.json
import {
  to = module.edge.aws_lb_listener.https_443
  id = "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434489454224"
}

# aws_s3_bucket/global/orders-public-assets.json
import {
  to = module.data.aws_s3_bucket.orders_public_assets
  id = "orders-public-assets"
}

# aws_s3_bucket/global/orders-public-assets.json
import {
  to = module.data.aws_s3_bucket_versioning.orders_public_assets
  id = "orders-public-assets"
}

# aws_s3_bucket/global/storefront-static.json
import {
  to = module.data.aws_s3_bucket.static
  id = "storefront-static"
}

# aws_dynamodb_table/us-east-1/orders.json
import {
  to = module.data.aws_dynamodb_table.orders
  id = "orders"
}

# aws_db_instance/us-east-1/orders-db.json
import {
  to = module.data.aws_db_instance.orders_db
  id = "orders-db"
}

# aws_elasticache_replication_group/us-east-1/storefront-cache.json
import {
  to = module.data.aws_elasticache_replication_group.cache
  id = "storefront-cache"
}

# aws_sqs_queue/us-east-1/storefront-orders.json
import {
  to = module.data.aws_sqs_queue.orders
  id = "https://sqs.us-east-1.amazonaws.com/123456789012/storefront-orders"
}

# aws_sns_topic/us-east-1/storefront-events.json
import {
  to = module.data.aws_sns_topic.events
  id = "arn:aws:sns:us-east-1:123456789012:storefront-events"
}

# aws_ecr_repository/us-east-1/storefront-web.json
import {
  to = module.compute.aws_ecr_repository.web
  id = "storefront-web"
}

# aws_launch_template/us-east-1/lt-4fe346ea9a7834369.json
import {
  to = module.compute.aws_launch_template.worker
  id = "lt-4fe346ea9a7834369"
}

# aws_autoscaling_group/us-east-1/storefront-workers.json
import {
  to = module.compute.aws_autoscaling_group.workers
  id = "storefront-workers"
}

# aws_instance/us-east-1/i-3bd88a7f905f64de6.json
import {
  to = module.compute.aws_instance.i_3bd88a7f905f64de6
  id = "i-3bd88a7f905f64de6"
}

# aws_instance/us-east-1/i-565d781fe501611ba.json
import {
  to = module.compute.aws_instance.orders_web_1
  id = "i-565d781fe501611ba"
}

# aws_ecs_cluster/us-east-1/storefront.json
import {
  to = module.compute.aws_ecs_cluster.main
  id = "storefront"
}

# aws_ecs_task_definition/us-east-1/storefront-web_1.json
import {
  to = module.compute.aws_ecs_task_definition.web_1
  id = "arn:aws:ecs:us-east-1:123456789012:task-definition/storefront-web:1"
}

# aws_ecs_service/us-east-1/storefront_web.json
import {
  to = module.compute.aws_ecs_service.web
  id = "storefront/web"
}

# aws_lambda_function/us-east-1/order-processor.json
import {
  to = module.compute.aws_lambda_function.order_processor
  id = "order-processor"
}

# aws_sfn_state_machine/us-east-1/order-flow.json
import {
  to = module.compute.aws_sfn_state_machine.order_flow
  id = "arn:aws:states:us-east-1:123456789012:stateMachine:order-flow"
}

# aws_cloudwatch_event_rule/us-east-1/storefront-nightly-report.json
import {
  to = module.compute.aws_cloudwatch_event_rule.nightly_report
  id = "storefront-nightly-report"
}

# aws_cloudwatch_event_rule/us-east-1/storefront-nightly-report.json
import {
  to = module.compute.aws_cloudwatch_event_target.nightly_report_order_processor
  id = "storefront-nightly-report/order-processor"
}

# aws_scheduler_schedule/us-east-1/default_storefront-cleanup.json
import {
  to = module.compute.aws_scheduler_schedule.cleanup
  id = "default/storefront-cleanup"
}
