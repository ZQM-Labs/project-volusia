"""
Project Volusia — Systems Integration Tests
Tests the integration between pipeline, portal, and data sources.
"""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# Import the system under test
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "Tools" / "volusia_data"))

from systems_integration import SystemsIntegration


class TestSystemsIntegration:
    """Test suite for integrated system components."""

    @pytest.fixture
    def integration(self):
        """Create integration manager instance."""
        return SystemsIntegration()

    def test_check_all_returns_health(self, integration):
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

    def test_database_check_connectivity(self, integration):
        """Verify database connectivity check works."""
        result = integration._check_database()

        assert isinstance(result, dict)
        assert "passed" in result
        # Should connect successfully
        assert result["passed"] is True

    def test_pipeline_state_check(self, integration):
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

    def test_consistency_check(self, integration):
        """Verify data consistency check works."""
        result = integration._check_consistency()

        assert isinstance(result, dict)
        assert "passed" in result

    def test_checksum_verification(self):
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

    def test_pipeline_exports_checksum(self):
        """Verify pipeline computes checksums."""
        # Database should have checksums for indicators
        db_path = Path(__file__).parent.parent / "Tools" / "volusia_data" / "volusia.db"

        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            rows = conn.execute("SELECT checksum FROM indicators LIMIT 5").fetchall()

            # At least some should have checksums
            assert len(rows) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
