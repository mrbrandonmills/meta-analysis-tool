"""
Benchmark tests configuration.

This conftest overrides the parent conftest to avoid loading FastAPI dependencies.
Benchmark tests should be standalone and only require pytest.
"""

import pytest

# Benchmark tests are standalone - no fixtures needed from parent conftest
