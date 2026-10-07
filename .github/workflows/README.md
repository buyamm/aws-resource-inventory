# CI/CD Pipeline Documentation

## Overview

This directory contains GitHub Actions workflows that enforce TDD quality gates for the AWS Resource Inventory project.

## Workflows

### TDD Pipeline (`tdd-pipeline.yml`)

The main CI/CD pipeline that runs on every push and pull request. It consists of the following jobs:

#### 1. Type Checking (mypy)
- Runs strict type checking on the `src/` directory
- Ensures type safety across the codebase
- Uses Python 3.11 type hints

#### 2. Linting and Formatting
- **Ruff**: Fast Python linter for code quality
- **Black**: Code formatter to ensure consistent style
- Both must pass for the pipeline to succeed

#### 3. Unit Tests with Coverage Gate (≥80%)
- Runs all unit tests in `tests/unit/`
- Enforces **minimum 80% code coverage** across the entire codebase
- Enforces **100% coverage** for critical modules:
  - `src/parser/` - AWS API response parsing
  - `src/sanitizer/` - Sensitive data sanitization
- Generates coverage reports (HTML, XML, terminal)
- Uploads coverage to Codecov (optional)

#### 4. Property-Based Tests (≥100 iterations)
- Runs property tests using Hypothesis framework
- Minimum **100 iterations per property** (configurable via `HYPOTHESIS_MAX_EXAMPLES`)
- Tests universal properties like:
  - Parse-print round-trip consistency
  - Structure preservation after sanitization
  - IaC generation completeness
- Shows detailed statistics with `--hypothesis-show-statistics`

#### 5. Integration Tests
- Tests component interactions using mocked AWS services (moto)
- Validates:
  - S3, EC2, Lambda spec collection
  - MCP server API contracts
  - Terraform IaC generation
- Uses shorter tracebacks for readability (`--tb=short`)

#### 6. End-to-End Tests
- Validates complete workflows:
  - Discovery → Collection → Output
  - Collection → IaC Generation → Terraform Validation
  - Collection → MCP Server → AI Analysis
- 15-minute timeout per workflow
- Tests real-world usage scenarios

#### 7. Security Scanning
- Runs Bandit security scanner on `src/` directory
- Detects common security issues:
  - Hardcoded credentials
  - SQL injection vulnerabilities
  - Use of insecure functions
- Generates JSON and screen reports
- Does not fail the build (warning only)

#### 8. Test Summary
- Aggregates results from all jobs
- Provides clear pass/fail summary
- Fails if any test job fails

## Triggers

The pipeline runs on:
- **Push** to branches: `main`, `develop`, `feature/**`
- **Pull requests** targeting: `main`, `develop`

## Caching

Dependencies are cached using GitHub Actions cache to speed up builds:
- Cache key: `${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}`
- Cached location: `~/.cache/pip`

## Artifacts

The pipeline uploads the following artifacts:
- **coverage-report**: HTML coverage report from unit tests
- **integration-test-results**: Integration test results
- **e2e-test-results**: End-to-end test results
- **security-scan-results**: Bandit JSON report

## Quality Gates

The pipeline enforces the following gates:

| Gate | Requirement | Job |
|------|-------------|-----|
| Code Coverage | ≥80% overall | unit-tests |
| Parser Coverage | 100% | unit-tests |
| Sanitizer Coverage | 100% | unit-tests |
| Property Test Iterations | ≥100 per property | property-tests |
| Type Checking | No errors | type-check |
| Linting | No violations | lint |
| Formatting | Black compliant | lint |
| Integration Tests | All pass | integration-tests |
| E2E Tests | All pass | e2e-tests |

## Local Validation

Before pushing, you can run the same checks locally:

```bash
# Type checking
mypy src/ --strict --ignore-missing-imports

# Linting
ruff check src/ tests/

# Formatting check
black --check src/ tests/

# Format code
black src/ tests/

# Unit tests with coverage
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Check coverage gate
coverage report --fail-under=80

# Property tests
HYPOTHESIS_MAX_EXAMPLES=100 pytest tests/unit/ -k property -v --hypothesis-show-statistics

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# Security scan
bandit -r src/ -f screen
```

## Configuration

### Hypothesis Configuration
- Minimum examples: 100 (set via `HYPOTHESIS_MAX_EXAMPLES`)
- Seed: 0 (for reproducibility)
- Statistics: Always shown

### Coverage Configuration
- Minimum overall: 80%
- Critical paths: 100% (parser, sanitizer)
- Reports: term-missing, XML, HTML

### Pytest Configuration
See `pyproject.toml` or `pytest.ini` for additional pytest settings.

## Troubleshooting

### Pipeline Failures

1. **Type Check Failed**: Fix type annotations in the reported files
2. **Lint Failed**: Run `ruff check src/ tests/ --fix` to auto-fix
3. **Format Failed**: Run `black src/ tests/` to format
4. **Coverage Below 80%**: Add tests for uncovered code paths
5. **Property Test Failed**: Investigate the failing property and fix the implementation
6. **Integration Test Failed**: Check mocked AWS service configuration
7. **E2E Test Timeout**: Optimize slow operations or increase timeout

### Common Issues

- **Import errors**: Ensure all dependencies are in `requirements.txt`
- **Missing modules**: Check that `__init__.py` files exist
- **Test collection failed**: Verify test file naming (`test_*.py`)
- **Cache issues**: Clear cache by updating requirements files

## Best Practices

1. **Write tests first** (TDD Red-Green-Refactor)
2. **Run tests locally** before pushing
3. **Keep jobs fast** (use caching, parallel execution)
4. **Monitor coverage trends** (aim for increasing coverage)
5. **Review security findings** (even if non-blocking)
6. **Update dependencies regularly** (security patches)

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
