"""
FinResolve AI — Lightweight Secret Scanner

Scans repository files for accidentally committed secrets, API keys,
private keys, JWT tokens, and credentials.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Known patterns for dangerous credentials
SECRET_PATTERNS = [
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private Key Header"),
    (r"(?:rzp_live_[0-9a-zA-Z]{14,})", "Razorpay Live Key"),
    (r"(?:sk_live_[0-9a-zA-Z]{24,})", "Stripe Live Key"),
    (r"(?:AKIA[0-9A-Z]{16})", "AWS Access Key ID"),
    (r"(?:ghp_[0-9a-zA-Z]{36})", "GitHub Personal Access Token"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "Hardcoded JWT Token"),
    (r'(?i)(?:password|passwd|pwd|secret_key)\s*[:=]\s*["\']([^"\'\n]{8,})["\']', "Hardcoded Password/Secret Assignment"),
]

# Patterns that are explicitly recognized as safe placeholders
SAFE_PLACEHOLDERS = {
    "change_me", "change_me_in_production", "your_password", "placeholder",
    "dummy", "dev-secret-key-change-in-production-only-min-32-chars", "test",
    "password", "secret", "undefined", "none", "<your_key_here>"
}

IGNORED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".gemini", "node_modules"}
IGNORED_EXTENSIONS = {".pyc", ".png", ".jpg", ".webp", ".pdf", ".ico", ".bin"}


def scan_text(text: str, filename: str = "<input>") -> list[dict]:
    """Scan arbitrary text content for secrets."""
    violations = []
    lines = text.splitlines()

    for line_no, line in enumerate(lines, start=1):
        for pattern, label in SECRET_PATTERNS:
            match = re.search(pattern, line)
            if match:
                matched_val = match.group(0)
                # Check for password capture group
                if len(match.groups()) > 0 and match.group(1):
                    val = match.group(1).lower().strip()
                    if val in SAFE_PLACEHOLDERS or any(p in val for p in SAFE_PLACEHOLDERS):
                        continue

                # Ignore comments containing 'Example' or 'example'
                if "# Example:" in line or "# example:" in line:
                    continue

                violations.append({
                    "file": filename,
                    "line": line_no,
                    "type": label,
                    "snippet": line.strip()[:100],
                })
    return violations


def scan_directory(root_dir: Path) -> list[dict]:
    """Recursively scan files in a directory."""
    all_violations = []

    for root, dirs, files in os.walk(root_dir):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            if file == "scan_secrets.py":
                continue
            file_path = Path(root) / file
            if file_path.suffix in IGNORED_EXTENSIONS:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                violations = scan_text(content, str(file_path.relative_to(root_dir)))
                all_violations.extend(violations)
            except Exception as e:
                pass

    return all_violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan codebase for exposed secrets.")
    parser.add_argument("--path", type=str, default=".", help="Root directory to scan")
    parser.add_argument("--test-fixture", action="store_true", help="Run self-test on fake fixture")
    args = parser.parse_args()

    if args.test_fixture:
        test_payload = (
            "AKIAIOSFODNN7EXAMPLE\n"
            "rzp_live_abcdef123456789\n"
            "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgk\n"
        )
        violations = scan_text(test_payload, "<test_fixture>")
        if len(violations) >= 2:
            print("Scanner self-test passed: caught simulated secrets.")
            return 0
        else:
            print("Scanner self-test failed: did not catch simulated secrets.")
            return 1

    root = Path(args.path).resolve()
    print(f"Scanning {root} for accidental secrets...")
    violations = scan_directory(root)

    if violations:
        print(f"\n[!] SECURITY VIOLATION: Found {len(violations)} potential secrets:")
        for v in violations:
            print(f"  - {v['file']}:{v['line']} [{v['type']}]: {v['snippet']}")
        return 1
    else:
        print("[+] Secret scan complete: Zero exposed credentials detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
