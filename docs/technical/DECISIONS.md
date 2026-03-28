<!--
DOCUMENT METADATA
Owner: @systems-architect
Update trigger: Any significant architectural, technology, or design pattern decision is made
Update scope: Append new ADRs only. Never edit the body of an Accepted ADR.
Read by: All agents. Check this file before proposing changes that may conflict with prior decisions.
-->

# Architecture Decision Records

> This log captures the context and reasoning behind key decisions so they are never lost.
>
> **Rule**: Once an ADR is marked **Accepted**, do not edit its body. If a decision needs to change, write a new ADR that explicitly supersedes the old one. Add `**Status**: Superseded by ADR-XXX` to the old record.
>
> **Agents**: Read the relevant ADRs before proposing architectural changes. A proposal that contradicts an Accepted ADR needs a new ADR — not a silent override.

---

## Decision Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| ADR-001 | Flask + SQLite tech stack selection | Accepted | 2026-03-28 |

---

## ADR-001: Flask + SQLite Tech Stack Selection

**Date**: 2026-03-28
**Status**: Accepted
**Deciders**: Supervisor (team leader) / Developer

### Context

MindGuard is a university group project (USTH GEN14) that needs to serve as a community fraud awareness tool for Vietnamese users. The team has one developer with Python/Flask experience. The project needs to be easy to deploy on any computer (a custom installer exists), support AI integration for chatbot features, and handle user-generated content (scammer reports). Budget is zero -- all services must be free tier.

### Options Considered

1. **Django + PostgreSQL**: Full-featured Python framework -- Pros: built-in admin, ORM, auth. Cons: heavier setup, more complex for a small team, PostgreSQL requires separate installation.
2. **Flask + SQLite**: Lightweight Python micro-framework -- Pros: minimal boilerplate, easy deployment (no DB server needed), developer already familiar, enough for initial scale. Cons: SQLite has write concurrency limits, fewer built-in features than Django.
3. **Node.js (Express) + MongoDB**: JavaScript full-stack -- Pros: large ecosystem, JSON-native. Cons: developer less familiar with JS backend, MongoDB overkill for structured data, deployment complexity.

### Decision

Flask + SQLite chosen because: (1) developer expertise in Python/Flask, (2) SQLite requires zero configuration and is file-based (easy to deploy anywhere via the custom installer), (3) Flask's lightweight nature allows rapid development with a small team, (4) SQLAlchemy ORM provides an upgrade path to PostgreSQL when scale demands it.

### Consequences

- **Positive**: Fast development cycle, easy deployment to any machine, no external database dependency, clear upgrade path to PostgreSQL via SQLAlchemy
- **Negative**: SQLite limits concurrent writes (acceptable for current user scale), Flask requires manual setup of features Django provides built-in (admin dashboard built from scratch)
- **Neutral**: Jinja2 templating means server-side rendering -- no SPA complexity but also no rich client-side interactivity without additional JS

---

<!--
TEMPLATE FOR NEW ADRs — copy this block when adding a new record:

## ADR-[NNN]: [Short Title]

**Date**: YYYY-MM-DD
**Status**: Accepted
**Deciders**: [Human name(s)] / @systems-architect

### Context
[What situation or problem prompted this decision. Include relevant constraints.]

### Options Considered
1. **[Option A]**: [Description] — Pros: [...] Cons: [...]
2. **[Option B]**: [Description] — Pros: [...] Cons: [...]

### Decision
[What was decided and the primary reason why.]

### Consequences
- **Positive**: [What becomes easier or better]
- **Negative**: [Trade-offs or what becomes harder]
- **Neutral**: [What changes but is neither better nor worse]
-->
