output "db_instance_arns" {
  description = "ARNs of the db instances in this module, keyed by resource name"
  value = {
    orders_db = aws_db_instance.orders_db.arn
  }
}

output "dynamodb_table_arns" {
  description = "ARNs of the dynamodb tables in this module, keyed by resource name"
  value = {
    orders = aws_dynamodb_table.orders.arn
  }
}

output "elasticache_replication_group_arns" {
  description = "ARNs of the elasticache replication groups in this module, keyed by resource name"
  value = {
    cache = aws_elasticache_replication_group.cache.arn
  }
}

output "s3_bucket_ids" {
  description = "IDs of the s3 buckets in this module, keyed by resource name"
  value = {
    orders_public_assets = aws_s3_bucket.orders_public_assets.id
    static               = aws_s3_bucket.static.id
  }
}

output "sns_topic_arns" {
  description = "ARNs of the sns topics in this module, keyed by resource name"
  value = {
    events = aws_sns_topic.events.arn
  }
}

output "sqs_queue_arns" {
  description = "ARNs of the sqs queues in this module, keyed by resource name"
  value = {
    orders = aws_sqs_queue.orders.arn
  }
}
