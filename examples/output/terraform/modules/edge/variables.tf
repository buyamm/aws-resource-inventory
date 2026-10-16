variable "security_group_ids" {
  description = "IDs of the security groups managed by the network module, keyed by resource name"
  type        = map(string)
}

variable "subnet_ids" {
  description = "IDs of the subnets managed by the network module, keyed by resource name"
  type        = map(string)
}

variable "vpc_ids" {
  description = "IDs of the vpcs managed by the network module, keyed by resource name"
  type        = map(string)
}
