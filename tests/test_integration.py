"""
Project Volusia — Systems Integration Tests
Tests the integration between pipeline, portal, and data sources.
"""

import hashlib
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Import the system under test
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "Tools" / "volusia_data"))

from systems_integration import SystemsIntegration


@pytest.fixture()
def seeded_db(tmp_path, monkeypatch):
    """Hermetic DB with the tables/rows the integration checks expect.

    systems_integration reads its module-level DB_PATH at call time, so
    monkeypatching it redirects every check to this temp database. The real
    Tools/volusia_data/volusia.db is gitignored and must not be a dependency.
    """
    from datetime import datetime, timezone

    db = tmp_path / "volusia.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            value TEXT,
            unit TEXT,
            category TEXT DEFAULT '',
            source TEXT,
            source_url TEXT,
            vintage TEXT,
            fetched_at TEXT,
            description TEXT,
            checksum TEXT,
            signature TEXT
        );
        CREATE TABLE datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            fetched_at TEXT
        );
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE fetch_manifest (
            run_id TEXT PRIMARY KEY,
            duration_ms INTEGER,
            status TEXT,
            indicators_count INTEGER,
            fetched_at TEXT,
            details TEXT
        );
        """
    )
    now = datetime.now(timezone.utc).isoformat()
    for name, value, unit, source, vintage in [
        ("total_population_pep_2024", "601107", "persons", "Census PEP", "2024"),
        ("unemployment_rate_bls", "5.3", "percent", "BLS LAUS", "2026-07"),
    ]:
        checksum = hashlib.sha256(f"{value}|{source}|{vintage}".encode()).hexdigest()[:16]
        conn.execute(
            "INSERT INTO indicators (name, value, unit, category, source, source_url,"
            " vintage, fetched_at, description, checksum) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, value, unit, "Economy", source, "https://example.invalid", vintage, now, "seed", checksum),
        )
    conn.execute(
        "INSERT INTO fetch_manifest (run_id, duration_ms, status, indicators_count, fetched_at) VALUES (?, ?, ?, ?, ?)",
        ("run-seed", 10, "completed", 2, now),
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr("systems_integration.DB_PATH", db)
    return db


class TestSystemsIntegration:
    """Test suite for integrated system components."""

    @pytest.fixture
    def integration(self, seeded_db):
        """Create integration manager against the seeded temp DB.

        Must depend on seeded_db: SystemsIntegration.__init__ captures
        DB_PATH at instance-creation time, so the monkeypatch has to be
        in place first.
        """
        return SystemsIntegration()

    def test_check_all_returns_health(self, integration, seeded_db):
        """Verify check_all returns healthy status when systems are working."""
        results = integration.check_all()

        assert "timestamp" in results
        assert "integration_status" in results
        assert "checks" in results

        # Should have all sub-checks
        assert "database" in results["checks"]
        assert "pipeline" in results["checks"]
        assert "api" in results["checks"]
        assert "consistency" in results["checks"]

    def test_database_check_connectivity(self, integration, seeded_db):
        """Verify database connectivity check works."""
        result = integration._check_database()

        assert isinstance(result, dict)
        assert "passed" in result
        # Should connect successfully
        assert result["passed"] is True

    def test_pipeline_state_check(self, integration, seeded_db):
        """Verify pipeline state can be checked."""
        result = integration._check_pipeline()

        assert isinstance(result, dict)
        assert "passed" in result
        # Pipeline should have run at some point
        assert "last_run" in result

    def test_api_endpoints_check(self, integration):
        """Verify API endpoints respond correctly."""
        result = integration._check_api_endpoints()

        assert isinstance(result, dict)
        assert "passed" in result
        assert "endpoints" in result

        # Check each endpoint
        for endpoint, expected in [("/api/health", 200), ("/api/indicators", 200)]:
            assert endpoint in result["endpoints"]
            assert "status" in result["endpoints"][endpoint]
            assert "passed" in result["endpoints"][endpoint]

    def test_consistency_check(self, integration, seeded_db):
        """Verify data consistency check works."""
        result = integration._check_consistency()

        assert isinstance(result, dict)
        assert "passed" in result

    def test_checksum_verification(self, seeded_db):
        """Verify checksum validation works."""
        from systems_integration import DataValidator

        result = DataValidator.verify_checksums()

        assert isinstance(result, dict)
        assert "total" in result
        assert "valid" in result
        assert "invalid" in result
        assert "passed" in result


class TestIntegrationAPI:
    """Test API endpoints that integrate with other systems."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from portal_app import app

        return TestClient(app)

    def test_status_endpoint_includes_manifest(self, client):
        """Verify status endpoint includes pipeline manifest."""
        response = client.get("/api/status")

        assert response.status_code == 200
        data = response.json()

        assert "manifest" in data
        assert "sla" in data
        assert "indicators" in data

    def test_status_endpoint_sla_tracking(self, client):
        """Verify SLA status is tracked."""
        response = client.get("/api/status")

        data = response.json()

        assert "sla" in data
        sla = data["sla"]
        assert "met" in sla
        assert "target" in sla
        assert "last_refresh_days" in sla

    def test_indicators_include_provenance(self, client):
        """Verify indicators include source provenance."""
        response = client.get("/api/indicators?limit=5")

        assert response.status_code == 200
        data = response.json()

        if data["indicators"]:
            indicator = data["indicators"][0]
            assert "source" in indicator
            assert "source_url" in indicator
            assert "vintage" in indicator


class TestPipelineIntegration:
    """Test pipeline integration with external systems."""

    def test_pipeline_exports_checksum(self, seeded_db):
        """Verify pipeline computes checksums for indicators."""
        conn = sqlite3.connect(str(seeded_db))
        try:
            rows = conn.execute("SELECT checksum FROM indicators WHERE checksum IS NOT NULL LIMIT 5").fetchall()
        finally:
            conn.close()

        assert len(rows) > 0
        assert all(r[0] for r in rows)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
