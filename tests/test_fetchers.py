#!/usr/bin/env python3
"""
Project Volusia — Fetcher CLI Tests
Tests for the standalone fetcher tools.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

import pytest

# Add Tools dir to path
TOOLS = Path(__file__).resolve().parent.parent / "Tools"
sys.path.insert(0, str(TOOLS))

from volusia_data.fetchers import fetch_census_pep
from volusia_data.fetchers import fetch_noaa
from volusia_data.fetchers import fetch_qcew


def test_census_pep_fetch():
    """Test Census PEP fetcher returns data."""
    result = fetch_census_pep.fetch_pep()
    assert result is not None
    assert len(result) >= 3  # At least 2022, 2023, 2024
    for entry in result:
        assert "year" in entry
        assert "population" in entry
        assert entry["population"] > 500000  # Volusia > 500k


def test_noaa_fetch():
    """Test NOAA NCEI fetcher returns data."""
    result = fetch_noaa.fetch_noaa()
    assert result is not None
    assert "avg_tmax" in result
    assert "avg_tmin" in result
    assert "total_prcp" in result
    assert result["days_counted"] > 300  # Most of the year


def test_qcew_fetch():
    """Test BLS QCEW fetcher returns data."""
    result = fetch_qcew.fetch_qcew()
    assert result is not None
    assert "establishments" in result
    assert "employment" in result
    assert "avg_weekly_wage" in result
    assert int(result["establishments"]) > 10000


def test_census_pep_no_key_needed():
    """Verify Census PEP works without API key."""
    old_key = os.environ.get("CENSUS_API_KEY")
    os.environ.pop("CENSUS_API_KEY", None)
    try:
        result = fetch_census_pep.fetch_pep()
        assert result is not None
    finally:
        if old_key:
            os.environ["CENSUS_API_KEY"] = old_key


def test_noaa_no_key_needed():
    """Verify NOAA works without API key."""
    result = fetch_noaa.fetch_noaa()
    assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
