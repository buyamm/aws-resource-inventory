output "internet_gateway_ids" {
  description = "IDs of the internet gateways in this module, keyed by resource name"
  value = {
    igw = aws_internet_gateway.igw.id
  }
}

output "nat_gateway_ids" {
  description = "IDs of the nat gateways in this module, keyed by resource name"
  value = {
    nat = aws_nat_gateway.nat.id
  }
}

output "route_table_ids" {
  description = "IDs of the route tables in this module, keyed by resource name"
  value = {
    private      = aws_route_table.private.id
    public       = aws_route_table.public.id
    rtb_561c82c8 = aws_route_table.rtb_561c82c8.id
  }
}

output "security_group_ids" {
  description = "IDs of the security groups in this module, keyed by resource name"
  value = {
    alb_sg        = aws_security_group.alb_sg.id
    app           = aws_security_group.app.id
    default       = aws_security_group.default.id
    orders_web_sg = aws_security_group.orders_web_sg.id
  }
}

output "subnet_ids" {
  description = "IDs of the subnets in this module, keyed by resource name"
  value = {
    orders_private_a = aws_subnet.orders_private_a.id
    public_a         = aws_subnet.public_a.id
    public_b         = aws_subnet.public_b.id
  }
}

output "vpc_endpoint_ids" {
  description = "IDs of the vpc endpoints in this module, keyed by resource name"
  value = {
    s3 = aws_vpc_endpoint.s3.id
  }
}

output "vpc_ids" {
  description = "IDs of the vpcs in this module, keyed by resource name"
  value = {
    orders_vpc = aws_vpc.orders_vpc.id
  }
}
