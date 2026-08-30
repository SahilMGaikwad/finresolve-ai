"""
FinResolve AI — Structured Logging & Secret Redaction

JSON log formatter that automatically redacts credentials, tokens, and sensitive fields.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

# Sensitive keys whose values must always be redacted
SENSITIVE_KEYS = {
    "password", "passwd", "secret", "secret_key", "api_key", "token",
    "access_token", "refresh_token", "auth", "authorization", "bearer",
    "private_key", "credit_card", "card_number", "cvv", "pan", "aadhaar",
}

# Regex to catch inline bearer tokens / keys / password assignments
INLINE_SECRET_REGEX = re.compile(
    r"(?i)(bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+|AKIA[0-9A-Z]{16}|rzp_live_[0-9a-zA-Z]{14,}|(?:password|passwd|secret|api_key|token)\s*=\s*[^\s,;]+)"
)


def redact_sensitive_data(data: Any) -> Any:
    """Recursively scrub sensitive keys and tokens from dict/list structures."""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                cleaned[k] = "[REDACTED]"
            else:
                cleaned[k] = redact_sensitive_data(v)
        return cleaned
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        return INLINE_SECRET_REGEX.sub("[REDACTED_SECRET]", data)
    return data


class RedactingJsonFormatter(logging.Formatter):
    """
    Formats log records into structured JSON, redacting any sensitive data.
    """

    def __init__(self, service_name: str = "finresolve-ai"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": self.service_name,
            "message": redact_sensitive_data(record.getMessage()),
        }

        # Include request context if present
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "case_id"):
            log_obj["case_id"] = record.case_id

        # Include exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Include structured extra fields if provided
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log_obj["context"] = redact_sensitive_data(record.extra_fields)

        return json.dumps(log_obj, default=str)
