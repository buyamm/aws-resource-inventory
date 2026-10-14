#!/usr/bin/env bash
# Verify that the generated Terraform matches the actual AWS resources (Requirements 7.5, 7.6).
# Exit codes: 0 = no changes, 2 = changes detected, 1 = error.
set -uo pipefail

if [ ! -d ".terraform" ]; then
  terraform init -input=false || exit 1
fi

terraform plan -detailed-exitcode -no-color -input=false > plan_output.txt 2>&1
PLAN_EXIT=$?
cat plan_output.txt

case $PLAN_EXIT in
  0) echo "SUCCESS: zero changes - Terraform configuration matches AWS."; exit 0 ;;
  2) echo "CHANGES DETECTED: review plan_output.txt."; exit 2 ;;
  *) echo "ERROR: terraform plan failed."; exit 1 ;;
esac
