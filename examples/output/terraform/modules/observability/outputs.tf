output "cloudwatch_log_group_arns" {
  description = "ARNs of the cloudwatch log groups in this module, keyed by resource name"
  value = {
    aws_lambda_order_processor = aws_cloudwatch_log_group.aws_lambda_order_processor.arn
    ecs_storefront_web         = aws_cloudwatch_log_group.ecs_storefront_web.arn
  }
}
