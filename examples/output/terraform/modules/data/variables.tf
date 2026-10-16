variable "security_group_ids" {
  description = "IDs of the security groups managed by the network module, keyed by resource name"
  type        = map(string)
}
