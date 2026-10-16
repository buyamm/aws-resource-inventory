output "iam_role_arns" {
  description = "ARNs of the iam roles in this module, keyed by resource name"
  value = {
    exec_role         = aws_iam_role.exec_role.arn
    order_lambda_role = aws_iam_role.order_lambda_role.arn
    orders_app_role   = aws_iam_role.orders_app_role.arn
    scheduler_role    = aws_iam_role.scheduler_role.arn
    task_role         = aws_iam_role.task_role.arn
  }
}
