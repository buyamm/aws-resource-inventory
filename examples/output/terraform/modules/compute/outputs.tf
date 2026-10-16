output "autoscaling_group_arns" {
  description = "ARNs of the autoscaling groups in this module, keyed by resource name"
  value = {
    workers = aws_autoscaling_group.workers.arn
  }
}

output "cloudwatch_event_rule_arns" {
  description = "ARNs of the cloudwatch event rules in this module, keyed by resource name"
  value = {
    nightly_report = aws_cloudwatch_event_rule.nightly_report.arn
  }
}

output "ecr_repository_arns" {
  description = "ARNs of the ecr repositorys in this module, keyed by resource name"
  value = {
    web = aws_ecr_repository.web.arn
  }
}

output "ecs_cluster_arns" {
  description = "ARNs of the ecs clusters in this module, keyed by resource name"
  value = {
    main = aws_ecs_cluster.main.arn
  }
}

output "ecs_service_ids" {
  description = "IDs of the ecs services in this module, keyed by resource name"
  value = {
    web = aws_ecs_service.web.id
  }
}

output "ecs_task_definition_arns" {
  description = "ARNs of the ecs task definitions in this module, keyed by resource name"
  value = {
    web_1 = aws_ecs_task_definition.web_1.arn
  }
}

output "instance_ids" {
  description = "IDs of the instances in this module, keyed by resource name"
  value = {
    i_b892b745a8c407b02 = aws_instance.i_b892b745a8c407b02.id
    orders_web_1        = aws_instance.orders_web_1.id
  }
}

output "lambda_function_arns" {
  description = "ARNs of the lambda functions in this module, keyed by resource name"
  value = {
    order_processor = aws_lambda_function.order_processor.arn
  }
}

output "launch_template_ids" {
  description = "IDs of the launch templates in this module, keyed by resource name"
  value = {
    worker = aws_launch_template.worker.id
  }
}

output "scheduler_schedule_arns" {
  description = "ARNs of the scheduler schedules in this module, keyed by resource name"
  value = {
    cleanup = aws_scheduler_schedule.cleanup.arn
  }
}

output "sfn_state_machine_arns" {
  description = "ARNs of the sfn state machines in this module, keyed by resource name"
  value = {
    order_flow = aws_sfn_state_machine.order_flow.arn
  }
}
