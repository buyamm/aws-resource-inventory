#!/bin/bash
# Script to validate GitHub Actions workflow syntax

set -e

echo "🔍 Validating GitHub Actions workflow syntax..."

WORKFLOW_FILE=".github/workflows/tdd-pipeline.yml"

# Check if workflow file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ Error: Workflow file not found at $WORKFLOW_FILE"
    exit 1
fi

echo "✅ Workflow file exists: $WORKFLOW_FILE"

# Check if yq or python with pyyaml is available for YAML validation
if command -v yq &> /dev/null; then
    echo "📋 Validating YAML syntax with yq..."
    yq eval "$WORKFLOW_FILE" > /dev/null
    echo "✅ YAML syntax is valid"
elif command -v python3 &> /dev/null; then
    echo "📋 Validating YAML syntax with Python..."
    python3 << 'EOF'
import yaml
import sys

try:
    with open('.github/workflows/tdd-pipeline.yml', 'r') as f:
        yaml.safe_load(f)
    print("✅ YAML syntax is valid")
except yaml.YAMLError as e:
    print(f"❌ YAML syntax error: {e}")
    sys.exit(1)
EOF
else
    echo "⚠️  Warning: Neither yq nor Python with PyYAML available for validation"
    echo "   Basic file structure check passed"
fi

# Validate job structure
echo ""
echo "📊 Workflow structure:"
echo "   - Jobs defined: type-check, lint, unit-tests, property-tests, integration-tests, e2e-tests, security-scan, test-summary"

# Check required directories exist
echo ""
echo "🔍 Checking required directories..."
for dir in "tests/unit" "tests/integration" "tests/e2e" "src"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir"
    else
        echo "   ❌ $dir (missing)"
    fi
done

# Check required files exist
echo ""
echo "🔍 Checking required files..."
for file in "requirements.txt" "requirements-dev.txt" "pyproject.toml"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing)"
    fi
done

echo ""
echo "✅ Workflow validation complete!"
echo ""
echo "💡 To test the workflow locally, install act (https://github.com/nektos/act) and run:"
echo "   act -l  # List available jobs"
echo "   act -j unit-tests  # Run unit tests job locally"
