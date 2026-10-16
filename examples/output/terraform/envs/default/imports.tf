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

# aws_vpc/us-east-1/vpc-660d36ef.json
import {
  to = module.network.aws_vpc.orders_vpc
  id = "vpc-660d36ef"
}

# aws_subnet/us-east-1/subnet-4d897e3d.json
import {
  to = module.network.aws_subnet.orders_private_a
  id = "subnet-4d897e3d"
}

# aws_subnet/us-east-1/subnet-2cf4f53a.json
import {
  to = module.network.aws_subnet.public_a
  id = "subnet-2cf4f53a"
}

# aws_subnet/us-east-1/subnet-4db17d3d.json
import {
  to = module.network.aws_subnet.public_b
  id = "subnet-4db17d3d"
}

# aws_route_table/us-east-1/rtb-e28b5541.json
import {
  to = module.network.aws_route_table.private
  id = "rtb-e28b5541"
}

# aws_route_table/us-east-1/rtb-e28b5541.json
import {
  to = module.network.aws_route_table_association.private_subnet_4d897e3d
  id = "subnet-4d897e3d/rtb-e28b5541"
}

# aws_route_table/us-east-1/rtb-bf60be68.json
import {
  to = module.network.aws_route_table.public
  id = "rtb-bf60be68"
}

# aws_route_table/us-east-1/rtb-bf60be68.json
import {
  to = module.network.aws_route_table_association.public_subnet_2cf4f53a
  id = "subnet-2cf4f53a/rtb-bf60be68"
}

# aws_route_table/us-east-1/rtb-bf60be68.json
import {
  to = module.network.aws_route_table_association.public_subnet_4db17d3d
  id = "subnet-4db17d3d/rtb-bf60be68"
}

# aws_route_table/us-east-1/rtb-561c82c8.json
import {
  to = module.network.aws_route_table.rtb_561c82c8
  id = "rtb-561c82c8"
}

# aws_internet_gateway/us-east-1/igw-d045f4ab.json
import {
  to = module.network.aws_internet_gateway.igw
  id = "igw-d045f4ab"
}

# aws_nat_gateway/us-east-1/nat-af9f73b40a8a4af4f.json
import {
  to = module.network.aws_nat_gateway.nat
  id = "nat-af9f73b40a8a4af4f"
}

# aws_vpc_endpoint/us-east-1/vpce-40eb00b6.json
import {
  to = module.network.aws_vpc_endpoint.s3
  id = "vpce-40eb00b6"
}

# aws_security_group/us-east-1/sg-e4a0ee2dde2bb1f50.json
import {
  to = module.network.aws_security_group.alb_sg
  id = "sg-e4a0ee2dde2bb1f50"
}

# aws_security_group/us-east-1/sg-e4a0ee2dde2bb1f50.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.alb_sg_egress_all
  id = "sgr-c8fd2df3255a5027a"
}

# aws_security_group/us-east-1/sg-e4a0ee2dde2bb1f50.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.alb_sg_ingress_tcp_443
  id = "sgr-f9fbc468403bc6198"
}

# aws_security_group/us-east-1/sg-12874fb82c9db66ed.json
import {
  to = module.network.aws_security_group.app
  id = "sg-12874fb82c9db66ed"
}

# aws_security_group/us-east-1/sg-12874fb82c9db66ed.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.app_egress_all
  id = "sgr-b954df3a54b41ff12"
}

# aws_security_group/us-east-1/sg-12874fb82c9db66ed.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.app_ingress_tcp_80
  id = "sgr-d9900cda6419d64e8"
}

# aws_security_group/us-east-1/sg-12874fb82c9db66ed.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.app_ingress_tcp_6379
  id = "sgr-ebb5cd8ffaaf837d6"
}

# aws_security_group/us-east-1/sg-156a39ed25de235cf.json
import {
  to = module.network.aws_security_group.default
  id = "sg-156a39ed25de235cf"
}

# aws_security_group/us-east-1/sg-156a39ed25de235cf.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.default_egress_all
  id = "sgr-9b10765766bf92534"
}

# aws_security_group/us-east-1/sg-2bf145296ea5159ab.json
import {
  to = module.network.aws_security_group.orders_web_sg
  id = "sg-2bf145296ea5159ab"
}

# aws_security_group/us-east-1/sg-2bf145296ea5159ab.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.orders_web_sg_ingress_tcp_5432
  id = "sgr-0b71b21c710e9b06f"
}

# aws_security_group/us-east-1/sg-2bf145296ea5159ab.json
import {
  to = module.network.aws_vpc_security_group_ingress_rule.orders_web_sg_ingress_tcp_22
  id = "sgr-10daa5d732bb0dd4f"
}

# aws_security_group/us-east-1/sg-2bf145296ea5159ab.json
import {
  to = module.network.aws_vpc_security_group_egress_rule.orders_web_sg_egress_all
  id = "sgr-83596752ef1fde5e1"
}

# aws_route53_zone/global/ACA19C6IIUY2GFZ.json
import {
  to = module.edge.aws_route53_zone.example_com
  id = "ACA19C6IIUY2GFZ"
}

# aws_route53_zone/global/ACA19C6IIUY2GFZ.json
import {
  to = module.edge.aws_route53_record.example_com_api_a
  id = "ACA19C6IIUY2GFZ_api.example.com_A"
}

# aws_route53_zone/global/ACA19C6IIUY2GFZ.json
import {
  to = module.edge.aws_route53_record.example_com_shop_a
  id = "ACA19C6IIUY2GFZ_shop.example.com_A"
}

# aws_acm_certificate/us-east-1/a2f4311b-2bbd-4ca0-97e7-018106634454.json
import {
  to = module.edge.aws_acm_certificate.shop_example_com
  id = "arn:aws:acm:us-east-1:123456789012:certificate/a2f4311b-2bbd-4ca0-97e7-018106634454"
}

# aws_wafv2_web_acl/global/storefront-waf_d06f4b4d-1ec6-42a4-81fa-1582637eb32d.json
import {
  to = module.edge.aws_wafv2_web_acl.waf
  id = "d06f4b4d-1ec6-42a4-81fa-1582637eb32d/storefront-waf/CLOUDFRONT"
}

# aws_cloudfront_distribution/global/X5E0C4JHPHC9C.json
import {
  to = module.edge.aws_cloudfront_distribution.shop_example_com
  id = "X5E0C4JHPHC9C"
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

# aws_lb_listener/us-east-1/app_storefront-alb_50dc6c495c0c9188_4434501777232.json
import {
  to = module.edge.aws_lb_listener.https_443
  id = "arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/storefront-alb/50dc6c495c0c9188/4434501777232"
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

# aws_launch_template/us-east-1/lt-bad06a08aee200bf2.json
import {
  to = module.compute.aws_launch_template.worker
  id = "lt-bad06a08aee200bf2"
}

# aws_autoscaling_group/us-east-1/storefront-workers.json
import {
  to = module.compute.aws_autoscaling_group.workers
  id = "storefront-workers"
}

# aws_instance/us-east-1/i-b892b745a8c407b02.json
import {
  to = module.compute.aws_instance.i_b892b745a8c407b02
  id = "i-b892b745a8c407b02"
}

# aws_instance/us-east-1/i-5e2db2f538089c39d.json
import {
  to = module.compute.aws_instance.orders_web_1
  id = "i-5e2db2f538089c39d"
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
