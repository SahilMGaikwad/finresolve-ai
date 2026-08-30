"""
FinResolve AI — Health Endpoint Tests

Tests for the /health endpoint to verify:
- Correct HTTP status code
- Required response fields
- Response value correctness
"""

import pytest


@pytest.mark.unit
class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_has_required_fields(self, client):
        """Health response must contain all required fields."""
        response = client.get("/health")
        data = response.json()

        required_fields = {"status", "version", "environment", "phase", "timestamp"}
        assert required_fields.issubset(data.keys()), (
            f"Missing fields: {required_fields - data.keys()}"
        )

    def test_health_status_is_ok(self, client):
        """Health status must be 'ok' when the service is running."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_version_is_set(self, client):
        """Health response must include a non-empty version string."""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_health_environment_is_testing(self, client):
        """In test configuration, environment should be 'testing'."""
        response = client.get("/health")
        data = response.json()
        assert data["environment"] == "testing"

    def test_health_phase_is_one(self, client):
        """Current phase should be '1'."""
        response = client.get("/health")
        data = response.json()
        assert data["phase"] == "1"

    def test_health_timestamp_is_iso_format(self, client):
        """Timestamp must be a valid ISO 8601 string."""
        from datetime import datetime

        response = client.get("/health")
        data = response.json()

        # Should not raise ValueError
        parsed = datetime.fromisoformat(data["timestamp"])
        assert parsed is not None
