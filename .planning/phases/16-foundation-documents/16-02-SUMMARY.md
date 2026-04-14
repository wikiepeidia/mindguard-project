---
phase: 16-foundation-documents
plan: 02
status: complete
started: 2026-04-14
completed: 2026-04-14
requirements-completed: [ADR-01, ADR-02, ADR-03, ADR-04]
---

# Plan 16-02 Summary: Architecture Decision Records

## What Was Built

Updated `docs/technical/DECISIONS.md` with 4 new ADRs and an ADR-001 status update:

- **ADR-001**: Added "Partially superseded by ADR-002" note (database component)
- **ADR-002**: NeonDB PostgreSQL migration — why SQLite was replaced, NeonDB chosen
- **ADR-003**: Vercel serverless deployment — constraints and adaptations
- **ADR-004**: AI safety strategy — hard-block, fallback, 8s timeout
- **ADR-005**: DB-backed rate limiting — why @limiter over in-memory/Redis

## ADR Format

All ADRs follow ADR-001 format (Michael Nygard style):
- Context → Options Considered → Decision → Consequences
- Written in English (per D-07, consistent with ADR-001)
- Decision Index table updated with all 5 entries

## Files Modified

| File | Action |
|------|--------|
| `docs/technical/DECISIONS.md` | Updated index + ADR-001 note + 4 new ADRs |

## Deviations

None.
