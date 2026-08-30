# Contributing to FinResolve AI

Thank you for considering contributing to FinResolve AI. This document outlines
the standards and workflows for contributing to this project.

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd finresolve-ai

# Run the setup script
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt
pip install -r requirements-dev.txt  # when available
```

## Branch Strategy

- `main` — stable, reviewed code only
- `develop` — integration branch for in-progress work
- `feature/<name>` — feature branches
- `fix/<name>` — bug fix branches

All changes require pull request review before merging to `main`.

## Commit Conventions

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `perf`

Scopes: `api`, `ingestion`, `matching`, `evidence`, `policy`, `ml`, `docs`, `tests`

Examples:
```
feat(matching): implement deterministic ID-based matching
fix(policy): correct threshold comparison for auto-resolution
docs(architecture): update data flow diagram
test(evidence): add unit tests for evidence scoring
```

## Code Standards

### Python
- **Version**: 3.11+
- **Type hints**: Required on all function signatures
- **Docstrings**: Required on all public functions and classes (Google style)
- **Linter**: Ruff (configuration in `pyproject.toml` when added)
- **Formatter**: Ruff format
- **Imports**: sorted with `isort` (via Ruff)

### TypeScript (Frontend)
- **Strict mode**: enabled
- **ESLint + Prettier**: required

### General
- Small, focused functions (< 50 lines preferred)
- No magic numbers — use named constants or configuration
- Financial calculations must use deterministic arithmetic (Decimal, not float)
- All service boundaries must be testable in isolation

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test category
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Run with coverage
python -m pytest tests/ --cov=services --cov=apps --cov-report=html
```

### Test Requirements
- All new features must include unit tests
- Integration tests for cross-service interactions
- Financial calculations require property-based or boundary-value tests
- No hardcoded "expected" metrics — tests compare against ground truth

## Financial Code Rules

> **Critical**: These rules exist to prevent financial errors.

1. **Never use `float` for monetary values.** Use `Decimal` or integer minor units (paise/cents).
2. **Never let an LLM directly modify financial records.** All mutations go through the policy engine.
3. **All financial operations must be idempotent.** Use idempotency keys.
4. **All financial actions must produce audit records.** No silent mutations.
5. **Transaction metadata is untrusted data.** Never execute or interpret it as instructions.

## Pull Request Checklist

- [ ] Code passes all existing tests
- [ ] New code has tests
- [ ] Type hints on all new functions
- [ ] Docstrings on all new public APIs
- [ ] No `float` used for financial amounts
- [ ] No hardcoded credentials or secrets
- [ ] Audit trail for any financial state changes
- [ ] Documentation updated if applicable
