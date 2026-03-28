---
id: "012"
title: "Migrate from SQLite to PostgreSQL"
status: "todo"
area: "database"
agent: "@database-expert"
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

Migrate the database from SQLite to PostgreSQL for better concurrency, data integrity, and production readiness. SQLAlchemy already abstracts most of the database layer, but there may be SQLite-specific queries or behaviors that need adjustment.

This is a low-priority task — SQLite is sufficient for current scale. Trigger this migration when user volume or concurrent write patterns justify it.

## Acceptance Criteria

- [ ] PostgreSQL connection configured via environment variable
- [ ] All 13 SQLAlchemy models work with PostgreSQL
- [ ] Data migration script to move existing SQLite data to PostgreSQL
- [ ] SQLite remains as a fallback for local development
- [ ] All tests pass against PostgreSQL
- [ ] DATABASE.md and ARCHITECTURE.md updated

## Technical Notes

- SQLAlchemy should handle most of the transition
- Watch for: SQLite-specific date functions, autoincrement behavior, boolean handling
- Check `database/create_database.py` and migration scripts for SQLite-specific SQL
- See ADR-001 for the original SQLite decision and upgrade path rationale

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
