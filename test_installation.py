"""
Test script to verify all required dependencies are installed correctly.
"""

def test_imports():
    """Test that all required packages can be imported."""
    try:
        # Testing frameworks
        import pytest
        import hypothesis
        from hypothesis import given, strategies as st
        
        # AWS SDK and mocking
        import boto3
        import moto
        
        # Time and HTTP mocking
        import freezegun
        import responses
        
        # Code quality tools
        import black
        import mypy
        import ruff
        
        # Data validation
        import pydantic
        import jsonschema
        
        # CLI utilities
        import click
        
        print("✅ All required dependencies imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
