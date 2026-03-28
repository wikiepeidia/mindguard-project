---
id: "011"
title: "Add Python linter and formatter (Ruff)"
status: "todo"
area: "setup"
agent: "@backend-developer"
priority: "low"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: []
blocks: []
blocked_by: []
---

## Description

Add Ruff as the Python linter and formatter for the project. Ruff is fast, covers both linting (replaces Flake8) and formatting (replaces Black), and requires minimal configuration. This improves code consistency and catches common issues early.

## Acceptance Criteria

- [ ] Ruff installed and added to `requirements.txt` (or dev dependencies)
- [ ] `ruff.toml` or `pyproject.toml` configuration created with sensible defaults
- [ ] Existing code passes linting (fix or suppress existing issues)
- [ ] CLAUDE.md updated with linter/formatter info and commands
- [ ] CI pipeline (#010) updated to run linting if available

## Technical Notes

- Ruff config should target Python 3.12
- Start with default rules, suppress any noisy rules for existing code
- Line length: 120 (generous for template-heavy Flask code)

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
