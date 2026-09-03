"""Data fetchers for Project Volusia.

The canonical ingestion pipeline is ``refresh_v2.py`` (single file, needs only
``requests``). The legacy class-based fetcher modules documented in
BUILD_REPORT.md were never created in this repository, so this package exposes
thin adapter classes that proxy to the ``refresh_v2`` fetcher functions. This
keeps the historical public API importable:

    from volusia_data.fetchers import CensusPEPFetcher, BLSFetcher
"""
from __future__ import annotations

from .. import refresh_v2

_SOURCE_URLS = {
    "Census PEP": "https://www.census.gov/programs-surveys/popest.html",
    "BLS LAUS": "https://www.bls.gov/lau/",
    "BEA Regional": "https://www.bea.gov/data/income-saving/local-area-personal-income",
    "BLS QCEW": "https://www.bls.gov/cew/",
    "NOAA NCEI": "https://www.ncei.noaa.gov/access/services/data/v1",
}


class CensusFetcher:
    """Census fetcher (legacy interface) delegating to refresh_v2."""

    source_url = _SOURCE_URLS["Census PEP"]

    def __init__(self, api_key=None):
        self.api_key = api_key

    def fetch_all(self, year=2024):
        return refresh_v2.fetch_pep()


class CensusPEPFetcher(CensusFetcher):
    """Census Population Estimates Program fetcher (refresh_v2.fetch_pep)."""


class BLSFetcher:
    """BLS LAUS fetcher (legacy interface) delegating to refresh_v2."""

    source_url = _SOURCE_URLS["BLS LAUS"]

    def __init__(self, api_key=None):
        self.api_key = api_key

    def fetch_laus(self):
        return refresh_v2.fetch_bls()


class BEAFetcher:
    """BEA regional fetcher (legacy interface) delegating to refresh_v2."""

    source_url = _SOURCE_URLS["BEA Regional"]

    def __init__(self, api_key=None):
        self.api_key = api_key

    def fetch_cainc1(self):
        return refresh_v2.fetch_bea()


class NOAAFetcher:
    """NOAA NCEI fetcher (legacy interface) delegating to refresh_v2."""

    source_url = _SOURCE_URLS["NOAA NCEI"]

    def __init__(self, api_key=None):
        self.api_key = api_key

    def fetch_daily(self, start_date="2024-01-01", end_date="2024-12-31"):
        return refresh_v2.fetch_noaa()


__all__ = [
    "CensusFetcher",
    "CensusPEPFetcher",
    "BLSFetcher",
    "BEAFetcher",
    "NOAAFetcher",
]
