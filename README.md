# AWS Resource Inventory

A Test-Driven Development (TDD) based system for automatically discovering, collecting, and analyzing AWS infrastructure resources.

## Overview

AWS Resource Inventory helps infrastructure engineers document and understand AWS environments that lack Infrastructure as Code (IaC), documentation, or diagrams. The system follows strict TDD methodology with comprehensive test coverage.

## Features

- **Automatic Resource Discovery**: Discover AWS resources across all regions
- **Detailed Specification Collection**: Collect complete configuration for each resource
- **MCP Server Integration**: Safe AI Agent access for infrastructure analysis
- **IaC Generation**: Generate Terraform code from existing infrastructure
- **Visual Diagrams**: Create architecture diagrams using drawio-ai-kit
- **Activity Flow Analysis**: AI-powered analysis of resource relationships
- **Accuracy Verification**: Citation-based approach to prevent AI hallucinations

## Project Structure

```
aws-resource-inventory/
├── src/                    # Source code
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/               # End-to-end tests
│   └── fixtures/          # Test fixtures and sample data
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Requirements

- Python 3.11 or higher
- AWS credentials configured (via environment, AWS CLI, or IAM role)
- Read-only AWS permissions for resource discovery

## Installation

```bash
# Install in development mode
pip install -e ".[dev]"
```

## Development

This project follows Test-Driven Development (TDD) methodology:

1. **RED**: Write a failing test first
2. **GREEN**: Write minimal code to pass the test
3. **REFACTOR**: Improve code quality while keeping tests green

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run property-based tests
pytest -k property --hypothesis-show-statistics

# Run integration tests
pytest tests/integration/

# Run end-to-end tests
pytest tests/e2e/
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check src/ tests/

# Formatting
black src/ tests/
```

## Testing Requirements

- Minimum 80% code coverage across all components
- 100% coverage for critical paths (parsing, credential handling, sanitization)
- Property-based tests must run minimum 100 iterations
- All tests must pass before merging

## License

MIT
