output "iam_role_arns" {
  description = "ARNs of the iam roles of module iam, keyed by resource name"
  value       = module.iam.iam_role_arns
}

output "cloudwatch_log_group_arns" {
  description = "ARNs of the cloudwatch log groups of module observability, keyed by resource name"
  value       = module.observability.cloudwatch_log_group_arns
}

output "internet_gateway_ids" {
  description = "IDs of the internet gateways of module network, keyed by resource name"
  value       = module.network.internet_gateway_ids
}

output "nat_gateway_ids" {
  description = "IDs of the nat gateways of module network, keyed by resource name"
  value       = module.network.nat_gateway_ids
}

output "route_table_ids" {
  description = "IDs of the route tables of module network, keyed by resource name"
  value       = module.network.route_table_ids
}

output "security_group_ids" {
  description = "IDs of the security groups of module network, keyed by resource name"
  value       = module.network.security_group_ids
}

output "subnet_ids" {
  description = "IDs of the subnets of module network, keyed by resource name"
  value       = module.network.subnet_ids
}

output "vpc_endpoint_ids" {
  description = "IDs of the vpc endpoints of module network, keyed by resource name"
  value       = module.network.vpc_endpoint_ids
}

output "vpc_ids" {
  description = "IDs of the vpcs of module network, keyed by resource name"
  value       = module.network.vpc_ids
}

output "acm_certificate_arns" {
  description = "ARNs of the acm certificates of module edge, keyed by resource name"
  value       = module.edge.acm_certificate_arns
}

output "cloudfront_distribution_ids" {
  description = "IDs of the cloudfront distributions of module edge, keyed by resource name"
  value       = module.edge.cloudfront_distribution_ids
}

output "lb_arns" {
  description = "ARNs of the lbs of module edge, keyed by resource name"
  value       = module.edge.lb_arns
}

output "lb_listener_arns" {
  description = "ARNs of the lb listeners of module edge, keyed by resource name"
  value       = module.edge.lb_listener_arns
}

output "lb_target_group_arns" {
  description = "ARNs of the lb target groups of module edge, keyed by resource name"
  value       = module.edge.lb_target_group_arns
}

output "route53_zone_ids" {
  description = "zone ids of the route53 zones of module edge, keyed by resource name"
  value       = module.edge.route53_zone_ids
}

output "wafv2_web_acl_arns" {
  description = "ARNs of the wafv2 web acls of module edge, keyed by resource name"
  value       = module.edge.wafv2_web_acl_arns
}

output "db_instance_arns" {
  description = "ARNs of the db instances of module data, keyed by resource name"
  value       = module.data.db_instance_arns
}

output "dynamodb_table_arns" {
  description = "ARNs of the dynamodb tables of module data, keyed by resource name"
  value       = module.data.dynamodb_table_arns
}

output "elasticache_replication_group_arns" {
  description = "ARNs of the elasticache replication groups of module data, keyed by resource name"
  value       = module.data.elasticache_replication_group_arns
}

output "s3_bucket_ids" {
  description = "IDs of the s3 buckets of module data, keyed by resource name"
  value       = module.data.s3_bucket_ids
}

output "sns_topic_arns" {
  description = "ARNs of the sns topics of module data, keyed by resource name"
  value       = module.data.sns_topic_arns
}

output "sqs_queue_arns" {
  description = "ARNs of the sqs queues of module data, keyed by resource name"
  value       = module.data.sqs_queue_arns
}

output "autoscaling_group_arns" {
  description = "ARNs of the autoscaling groups of module compute, keyed by resource name"
  value       = module.compute.autoscaling_group_arns
}

output "cloudwatch_event_rule_arns" {
  description = "ARNs of the cloudwatch event rules of module compute, keyed by resource name"
  value       = module.compute.cloudwatch_event_rule_arns
}

output "ecr_repository_arns" {
  description = "ARNs of the ecr repositorys of module compute, keyed by resource name"
  value       = module.compute.ecr_repository_arns
}

output "ecs_cluster_arns" {
  description = "ARNs of the ecs clusters of module compute, keyed by resource name"
  value       = module.compute.ecs_cluster_arns
}

output "ecs_service_ids" {
  description = "IDs of the ecs services of module compute, keyed by resource name"
  value       = module.compute.ecs_service_ids
}

output "ecs_task_definition_arns" {
  description = "ARNs of the ecs task definitions of module compute, keyed by resource name"
  value       = module.compute.ecs_task_definition_arns
}

output "instance_ids" {
  description = "IDs of the instances of module compute, keyed by resource name"
  value       = module.compute.instance_ids
}

output "lambda_function_arns" {
  description = "ARNs of the lambda functions of module compute, keyed by resource name"
  value       = module.compute.lambda_function_arns
}

output "launch_template_ids" {
  description = "IDs of the launch templates of module compute, keyed by resource name"
  value       = module.compute.launch_template_ids
}

output "scheduler_schedule_arns" {
  description = "ARNs of the scheduler schedules of module compute, keyed by resource name"
  value       = module.compute.scheduler_schedule_arns
}

output "sfn_state_machine_arns" {
  description = "ARNs of the sfn state machines of module compute, keyed by resource name"
  value       = module.compute.sfn_state_machine_arns
}
