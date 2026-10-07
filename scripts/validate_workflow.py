#!/usr/bin/env python3
"""
Script to validate GitHub Actions workflow syntax
"""

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

def validate_workflow():
    """Validate the GitHub Actions workflow file"""
    
    workflow_file = Path(".github/workflows/tdd-pipeline.yml")
    
    print("🔍 Validating GitHub Actions workflow syntax...")
    print()
    
    # Check if file exists
    if not workflow_file.exists():
        print(f"❌ Error: Workflow file not found at {workflow_file}")
        return False
    
    print(f"✅ Workflow file exists: {workflow_file}")
    
    # Validate YAML syntax
    try:
        with open(workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
        print("✅ YAML syntax is valid")
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    
    # Validate structure
    print()
    print("📊 Workflow structure:")
    
    # Check name
    if 'name' in workflow:
        print(f"   ✅ Name: {workflow['name']}")
    else:
        print("   ⚠️  No workflow name defined")
    
    # Check triggers
    if 'on' in workflow:
        triggers = workflow['on']
        print(f"   ✅ Triggers: {list(triggers.keys()) if isinstance(triggers, dict) else triggers}")
    else:
        print("   ❌ No triggers defined")
    
    # Check jobs
    if 'jobs' in workflow:
        jobs = list(workflow['jobs'].keys())
        print(f"   ✅ Jobs ({len(jobs)}):")
        for job in jobs:
            print(f"      - {job}")
    else:
        print("   ❌ No jobs defined")
        return False
    
    # Validate required jobs
    required_jobs = [
        'type-check',
        'lint', 
        'unit-tests',
        'property-tests',
        'integration-tests',
        'e2e-tests',
        'security-scan',
        'test-summary'
    ]
    
    print()
    print("🔍 Checking required jobs...")
    missing_jobs = []
    for job in required_jobs:
        if job in workflow['jobs']:
            print(f"   ✅ {job}")
        else:
            print(f"   ❌ {job} (missing)")
            missing_jobs.append(job)
    
    if missing_jobs:
        print(f"\n❌ Missing required jobs: {', '.join(missing_jobs)}")
        return False
    
    # Check required directories
    print()
    print("🔍 Checking required directories...")
    required_dirs = [
        "tests/unit",
        "tests/integration", 
        "tests/e2e",
        "src"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} (missing)")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️  Warning: Missing directories: {', '.join(missing_dirs)}")
    
    # Check required files
    print()
    print("🔍 Checking required files...")
    required_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml"
    ]
    
    missing_files = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Warning: Missing files: {', '.join(missing_files)}")
    
    # Summary
    print()
    print("=" * 60)
    print("✅ Workflow validation complete!")
    print("=" * 60)
    print()
    print("📋 Summary:")
    print(f"   - Workflow name: {workflow.get('name', 'N/A')}")
    print(f"   - Jobs defined: {len(workflow['jobs'])}")
    print(f"   - Required jobs: All present ✅")
    print()
    print("💡 Tips:")
    print("   - Test locally with act: https://github.com/nektos/act")
    print("   - Use GitHub Actions extension in VS Code for syntax highlighting")
    print("   - Push to a feature branch to test the workflow")
    print()
    
    return True

if __name__ == "__main__":
    success = validate_workflow()
    sys.exit(0 if success else 1)
