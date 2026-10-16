variable "default_tags" {
  description = "Tags every taggable resource of this environment carries (provider default_tags)"
  type        = map(string)
  default     = {}
}
