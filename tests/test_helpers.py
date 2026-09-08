"""Unit tests for pure helpers that are only indirectly covered elsewhere.

Covers contribution_api validation/privacy helpers and the DB checksum
function, giving these cheap-to-reach code paths explicit unit coverage
and protecting their edge cases.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "Tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from volusia_data import contribution_api as capi  # noqa: E402
from volusia_data import refresh_v2  # noqa: E402


# ------------------------------------------------------------------ sanitize
class TestSanitize:
    def test_strips_control_characters(self):
        out = capi._sanitize("a\x00b\x1fc\x7fd", 100)
        assert out == "abcd"

    def test_truncates_to_max_len(self):
        out = capi._sanitize("x" * 1000, 50)
        assert len(out) == 50

    def test_coerces_non_string(self):
        assert capi._sanitize(12345, 100) == "12345"

    def test_empty(self):
        assert capi._sanitize("", 10) == ""


# ------------------------------------------------------------------ email
class TestValidateEmail:
    def test_valid(self):
        assert capi._validate_email("user@example.com") == "user@example.com"

    def test_empty_returns_empty(self):
        assert capi._validate_email("") == ""

    @pytest.mark.parametrize(
        "bad",
        ["not-an-email", "a@b", "@example.com", "spaces in@example.com", "user@example."],
    )
    def test_invalid_raises(self, bad):
        with pytest.raises(Exception):
            capi._validate_email(bad)

    def test_sanitizes_then_validates(self):
        # Control chars are stripped first, then validated.
        assert capi._validate_email("u\x00ser@example.com") == "user@example.com"


# ------------------------------------------------------------ business days
class TestAddBusinessDays:
    def test_skips_weekend(self):
        # Fri 2026-09-04 + 1 business day = Mon 2026-09-07.
        start = datetime(2026, 9, 4)
        assert capi.add_business_days(start, 1) == datetime(2026, 9, 7)

    def test_crosses_weekend(self):
        # Thu 2026-09-03 + 1 = Fri 2026-09-04 (no weekend).
        assert capi.add_business_days(datetime(2026, 9, 3), 1) == datetime(2026, 9, 4)

    def test_monday_plus_five(self):
        assert capi.add_business_days(datetime(2026, 9, 7), 5) == datetime(2026, 9, 14)

    def test_zero_days_returns_start(self):
        start = datetime(2026, 9, 8)
        assert capi.add_business_days(start, 0) == start


# ---------------------------------------------------------------- rate limit
class TestRateCheck:
    def test_disabled_when_zero(self, monkeypatch):
        monkeypatch.setattr(capi, "_RATE_LIMIT", 0)
        assert capi._rate_check("ip:test") == (True, -1, 0.0)

    def test_first_request_allowed(self, monkeypatch):
        capi._rate_buckets.clear()
        monkeypatch.setattr(capi, "_RATE_LIMIT", 10)
        allowed, remaining, _ = capi._rate_check("ip:unit")
        assert allowed is True
        assert remaining >= 0

    def test_exhaustion_rejects(self, monkeypatch):
        capi._rate_buckets.clear()
        monkeypatch.setattr(capi, "_RATE_LIMIT", 2)
        monkeypatch.setattr(capi, "_RATE_WINDOW", 60)
        assert capi._rate_check("ip:limited")[0] is True
        assert capi._rate_check("ip:limited")[0] is True
        allowed, remaining, retry_after = capi._rate_check("ip:limited")
        assert allowed is False
        assert remaining == 0
        assert retry_after > 0


# ------------------------------------------------------------- checksum (pipeline)
def test_compute_checksum_matches_stored():
    """The checksum stored by the pipeline is reproducible and stable."""
    value, source, vintage = "601107", "Census PEP", "2024"
    expected = refresh_v2.compute_checksum(value, source, vintage)
    assert expected == refresh_v2.compute_checksum(value, source, vintage)
    assert len(expected) == 16  # first 16 hex chars of SHA-256
    assert expected != refresh_v2.compute_checksum("other", source, vintage)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
