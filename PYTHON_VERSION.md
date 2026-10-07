# Python Version Notice

## Current Configuration

This project is currently configured to work with **Python 3.9** due to system constraints.

## Design Specification

The original design document specifies **Python 3.11+** for optimal compatibility with:
- Latest AWS SDK features
- Advanced type hints
- Property-based testing libraries

## Migration Path

When Python 3.11+ becomes available:

1. Update `requirements.txt`:
   - Change `boto3>=1.28.0,<1.43.0` to `boto3>=1.34.0`
   - Change `pydantic>=1.10.0,<2.0.0` to `pydantic>=2.5.0`

2. Update `requirements-dev.txt`:
   - Change `mypy>=0.991` to `mypy>=1.4.1`
   - Change `boto3-stubs[essential]>=1.28.0,<1.43.0` to `boto3-stubs[essential]>=1.34.0`
   - Change `sphinx>=5.3.0` to `sphinx>=7.1.0`
   - Change `sphinx-rtd-theme>=1.2.0` to `sphinx-rtd-theme>=1.3.0`

3. Recreate virtual environment:
   ```bash
   rm -rf venv
   python3.11 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

## Current Compatibility

All dependencies have been tested and are compatible with Python 3.9.6.
The TDD workflow and testing frameworks work correctly with this version.
