# Remote state in S3; bucket, key and region are given at init time:
#   terraform init \
#     -backend-config="bucket=<state bucket>" \
#     -backend-config="key=default/terraform.tfstate" \
#     -backend-config="region=us-east-1" \
#     -backend-config="use_lockfile=true"   # Terraform >= 1.10
# To try the configuration with local state, add backend_override.tf:
#   terraform { backend "local" {} }

terraform {
  backend "s3" {
    encrypt = true
  }
}
