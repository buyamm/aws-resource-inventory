variable "iam_role_arns" {
  description = "ARNs of the iam roles managed by the iam module, keyed by resource name"
  type        = map(string)
}

variable "lb_target_group_arns" {
  description = "ARNs of the lb target groups managed by the edge module, keyed by resource name"
  type        = map(string)
}

variable "security_group_ids" {
  description = "IDs of the security groups managed by the network module, keyed by resource name"
  type        = map(string)
}

variable "sqs_queue_arns" {
  description = "ARNs of the sqs queues managed by the data module, keyed by resource name"
  type        = map(string)
}

variable "subnet_ids" {
  description = "IDs of the subnets managed by the network module, keyed by resource name"
  type        = map(string)
}
