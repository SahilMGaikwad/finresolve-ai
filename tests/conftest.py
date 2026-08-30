"""
FinResolve AI — Shared Test Fixtures

Provides reusable pytest fixtures for the test suite.
"""

import pytest
from fastapi.testclient import TestClient

from apps.api.config import Settings
from apps.api.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Settings configured for testing."""
    return Settings(
        app_env="testing",
        debug=True,
        log_level="WARNING",
        database_url="postgresql://test:test@localhost:5432/finresolve_test",
        policy_auto_resolve_enabled=False,
        policy_auto_resolve_confidence_threshold=0.95,
        policy_auto_resolve_max_amount=500_000,
    )


@pytest.fixture
def app(test_settings: Settings):
    """Create a FastAPI app instance configured for testing."""
    return create_app(settings=test_settings)


@pytest.fixture
def client(app) -> TestClient:
    """HTTP test client for the FastAPI app."""
    return TestClient(app)
