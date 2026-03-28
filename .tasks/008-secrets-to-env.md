---
id: "008"
title: "Move hardcoded secrets to environment variables"
status: "todo"
area: "backend"
agent: "@backend-developer"
priority: "normal"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: ["FR-060"]
blocks: ["013"]
blocked_by: []
---

## Description

Several secrets are currently hardcoded in `config.py` including the Flask SECRET_KEY and admin credentials. These must be moved to environment variables or the existing `.env/` JSON config system before any production deployment. This is a security requirement and blocks production readiness.

## Acceptance Criteria

- [ ] Flask SECRET_KEY loaded from environment variable or `.env/` config
- [ ] Admin credentials loaded from environment variable or `.env/` config
- [ ] `config.py` uses `os.environ.get()` with sensible defaults for development
- [ ] Documentation updated with required environment variables
- [ ] Application still starts correctly with default dev values

## Technical Notes

- Current secrets in `config.py`: `SECRET_KEY = "dev-secret-key-mindguard-2025-secure"`, admin username/password
- The `.env/` directory already uses JSON files for API keys — follow the same pattern or switch to standard `.env` file
- Update `README.md` environment variables table after changes
- See ADR-001 for deployment context

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
