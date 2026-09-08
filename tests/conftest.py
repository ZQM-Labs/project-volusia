"""Shared test fixtures for Project Volusia test suite.

This module provides:
- Automatic rate limit state cleanup to prevent cross-test pollution
- Shared sys.path setup for importing from Tools/
"""

import sys
from pathlib import Path

import pytest

# Add Tools/ to sys.path so tests can import volusia_data
TOOLS = Path(__file__).resolve().parent.parent / "Tools"
sys.path.insert(0, str(TOOLS))

from volusia_data import contribution_api as capi  # noqa: E402


@pytest.fixture(autouse=True)
def _clear_rate_limit_state():
    """Clear rate limit buckets before and after each test.

    The contribution_api uses a module-level dict (_rate_buckets) to track
    rate limits. Without cleanup, tests that make many requests can exhaust
    the rate budget and cause subsequent tests to fail with 429 errors.

    This fixture ensures each test starts with a clean rate limit state.
    """
    capi._rate_buckets.clear()
    yield
    capi._rate_buckets.clear()
