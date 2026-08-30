"""
FinResolve AI — Security Hardening Unit Tests

Tests authentication, RBAC, secret redaction, audit integrity,
rate limiting, idempotency, security headers, and health endpoints.
"""

import json
import logging
import pytest
from fastapi.testclient import TestClient

from apps.api.config import Settings
from apps.api.main import create_app
from services.audit.logger import AuditLogger
from services.common.logging import RedactingJsonFormatter, redact_sensitive_data
from services.repositories.case_repository import validate_identifier
from services.security.auth import DevBearerAuthProvider, Permission, Role
from services.security.idempotency import InMemoryIdempotencyStore
from services.security.rate_limiter import SlidingWindowRateLimiter
from services.security.rbac import check_permission, get_permissions_for_role


@pytest.fixture
def client():
    settings = Settings(
        app_env="test",
        debug=True,
        auth_enabled=False,
        rate_limit_enabled=True,
        rate_limit_requests_per_minute=5,
    )
    app = create_app(settings)
    return TestClient(app)


class TestAuthenticationAndRBAC:
    """Tests authentication provider and role-based access control."""

    def test_dev_auth_provider_valid_tokens(self):
        provider = DevBearerAuthProvider()
        user_viewer = provider.authenticate_token("Bearer dev-token-viewer")
        assert user_viewer.role == Role.VIEWER
        assert user_viewer.is_authenticated is True
        assert Permission.CASE_VIEW in user_viewer.permissions
        assert Permission.ACTION_APPROVE not in user_viewer.permissions

        user_approver = provider.authenticate_token("Bearer dev-token-approver")
        assert user_approver.role == Role.APPROVER
        assert Permission.ACTION_APPROVE in user_approver.permissions

    def test_dev_auth_provider_invalid_token_raises(self):
        provider = DevBearerAuthProvider()
        with pytest.raises(PermissionError, match="Invalid authentication token"):
            provider.authenticate_token("Bearer invalid-token-xyz")

    def test_rbac_permission_checks(self):
        perms_analyst = get_permissions_for_role(Role.ANALYST)
        assert Permission.EVALUATION_RUN in perms_analyst
        assert Permission.ACTION_APPROVE not in perms_analyst

        perms_admin = get_permissions_for_role(Role.ADMIN)
        assert Permission.ADMIN_ALL in perms_admin


class TestSecretRedactionAndLogging:
    """Tests automatic redaction of sensitive credentials in logs."""

    def test_redact_sensitive_dict(self):
        payload = {
            "username": "finops_user",
            "password": "SuperSecretPassword123!",
            "api_key": "rzp_test_abc123456789012",
            "card_number": "4111111111111111",
            "safe_amount": 50000,
        }
        cleaned = redact_sensitive_data(payload)
        assert cleaned["username"] == "finops_user"
        assert cleaned["password"] == "[REDACTED]"
        assert cleaned["api_key"] == "[REDACTED]"
        assert cleaned["card_number"] == "[REDACTED]"
        assert cleaned["safe_amount"] == 50000

    def test_redacting_json_formatter(self):
        formatter = RedactingJsonFormatter(service_name="test-service")
        record = logging.LogRecord(
            name="finresolve.test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="User logged in with password=SecretPass and bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz.abc",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        data = json.loads(formatted)
        assert data["service"] == "test-service"
        assert "SecretPass" not in data["message"]
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in data["message"]


class TestAuditLogIntegrity:
    """Tests cryptographic SHA-256 chaining and tamper detection."""

    def test_audit_hash_chain_and_verification(self):
        audit = AuditLogger()
        evt1 = audit.record_event(
            actor="usr_01",
            actor_role="ANALYST",
            operation="RECONCILE_CASE",
            result="SUCCESS",
            case_id="CASE-001",
        )
        evt2 = audit.record_event(
            actor="usr_02",
            actor_role="APPROVER",
            operation="PROPOSE_RESOLUTION",
            result="SUCCESS",
            case_id="CASE-001",
        )

        assert evt1.prev_event_hash == "GENESIS"
        assert evt2.prev_event_hash == evt1.event_hash
        assert audit.verify_integrity() is True

    def test_audit_tamper_detection(self):
        audit = AuditLogger()
        audit.record_event(actor="u1", actor_role="ANALYST", operation="OP1", result="SUCCESS")
        audit.record_event(actor="u2", actor_role="APPROVER", operation="OP2", result="SUCCESS")
        
        # Tamper with internal event history
        tampered_event = audit._events[0].model_copy(update={"actor": "MALICIOUS_ACTOR"})
        audit._events[0] = tampered_event

        # Integrity check MUST fail
        assert audit.verify_integrity() is False


class TestIdempotency:
    """Tests idempotency store, replay protection, and payload conflict detection."""

    def test_idempotency_lifecycle(self):
        store = InMemoryIdempotencyStore()
        key = "idemp_test_001"
        payload = {"amount": 5000, "merchant_id": "m_01"}

        # 1. First attempt: NEW
        status, record = store.acquire(key, payload, "ADJUSTMENT")
        assert status == "NEW"

        # 2. While processing: IN_FLIGHT
        status, _ = store.acquire(key, payload, "ADJUSTMENT")
        assert status == "IN_FLIGHT"

        # 3. Complete
        store.complete(key, {"status": "SUCCESS", "adjustment_id": "adj_100"})

        # 4. Subsequent identical attempt: CACHED
        status, cached_rec = store.acquire(key, payload, "ADJUSTMENT")
        assert status == "CACHED"
        assert cached_rec.response_payload["adjustment_id"] == "adj_100"

        # 5. Same key with DIFFERENT payload: CONFLICT
        conflict_payload = {"amount": 9999, "merchant_id": "m_01"}
        status, _ = store.acquire(key, conflict_payload, "ADJUSTMENT")
        assert status == "CONFLICT"


class TestRateLimiter:
    """Tests sliding window rate limiter."""

    def test_rate_limiter_exceed_limit(self):
        limiter = SlidingWindowRateLimiter(requests_per_minute=3)
        key = "client_ip_127.0.0.1"

        assert limiter.is_rate_limited(key)[0] is False
        assert limiter.is_rate_limited(key)[0] is False
        assert limiter.is_rate_limited(key)[0] is False

        # 4th request within 1 minute is rate limited
        is_limited, retry_after = limiter.is_rate_limited(key)
        assert is_limited is True
        assert retry_after > 0


class TestAPIEndpointsAndSecurityHeaders:
    """Tests FastAPI endpoints and HTTP security headers."""

    def test_health_endpoint_and_headers(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        
        # Verify security headers
        assert res.headers["x-content-type-options"] == "nosniff"
        assert res.headers["x-frame-options"] == "DENY"
        assert "x-request-id" in res.headers

    def test_readiness_endpoint(self, client):
        res = client.get("/ready")
        assert res.status_code == 200
        assert res.json()["status"] == "ready"

    def test_metrics_endpoint(self, client):
        res = client.get("/metrics")
        assert res.status_code == 200
        assert "counters" in res.json()

    def test_sanitized_identifier_validation(self):
        # Valid identifiers
        assert validate_identifier("CASE-0001") == "CASE-0001"
        assert validate_identifier("pay_1234_abc") == "pay_1234_abc"

        # Invalid SQL injection / Path traversal payloads
        with pytest.raises(ValueError):
            validate_identifier("CASE-01'; DROP TABLE cases; --")
        with pytest.raises(ValueError):
            validate_identifier("../../../etc/passwd")
