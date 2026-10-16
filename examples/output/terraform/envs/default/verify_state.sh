#!/usr/bin/env bash
# Verify that the generated Terraform matches the actual AWS resources (Requirements 7.5, 7.6).
# Success: the plan has no changes, or only imports whose configuration already matches.
# Exit codes: 0 = no changes, 2 = changes detected, 1 = error.
set -uo pipefail
cd "$(dirname "$0")"

if [ ! -d ".terraform" ]; then
  terraform init -input=false || exit 1
fi

terraform plan -detailed-exitcode -no-color -input=false -out=verify.tfplan > plan_output.txt 2>&1
PLAN_EXIT=$?
cat plan_output.txt

case $PLAN_EXIT in
  0) echo "SUCCESS: zero changes - Terraform configuration matches AWS."; exit 0 ;;
  2)
    if terraform show -json verify.tfplan | python3 -c 'import json, sys
changes = json.load(sys.stdin).get("resource_changes", [])
sys.exit(0 if all(c["change"]["actions"] == ["no-op"] for c in changes) else 1)'; then
      echo "SUCCESS: zero changes - only imports pending (terraform apply records them)."
      exit 0
    fi
    echo "CHANGES DETECTED: review plan_output.txt."; exit 2 ;;
  *) echo "ERROR: terraform plan failed."; exit 1 ;;
esac
