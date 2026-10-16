output "acm_certificate_arns" {
  description = "ARNs of the acm certificates in this module, keyed by resource name"
  value = {
    shop_example_com = aws_acm_certificate.shop_example_com.arn
  }
}

output "cloudfront_distribution_ids" {
  description = "IDs of the cloudfront distributions in this module, keyed by resource name"
  value = {
    shop_example_com = aws_cloudfront_distribution.shop_example_com.id
  }
}

output "lb_arns" {
  description = "ARNs of the lbs in this module, keyed by resource name"
  value = {
    alb = aws_lb.alb.arn
  }
}

output "lb_listener_arns" {
  description = "ARNs of the lb listeners in this module, keyed by resource name"
  value = {
    https_443 = aws_lb_listener.https_443.arn
  }
}

output "lb_target_group_arns" {
  description = "ARNs of the lb target groups in this module, keyed by resource name"
  value = {
    tg = aws_lb_target_group.tg.arn
  }
}

output "route53_zone_ids" {
  description = "zone ids of the route53 zones in this module, keyed by resource name"
  value = {
    example_com = aws_route53_zone.example_com.zone_id
  }
}

output "wafv2_web_acl_arns" {
  description = "ARNs of the wafv2 web acls in this module, keyed by resource name"
  value = {
    waf = aws_wafv2_web_acl.waf.arn
  }
}
