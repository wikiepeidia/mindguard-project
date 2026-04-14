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
| ADR-002 | NeonDB PostgreSQL migration | Accepted | 2026-04-14 |
| ADR-003 | Vercel serverless deployment | Accepted | 2026-04-14 |
| ADR-004 | AI safety strategy | Accepted | 2026-04-14 |
| ADR-005 | DB-backed rate limiting | Accepted | 2026-04-14 |

---

## ADR-001: Flask + SQLite Tech Stack Selection

**Date**: 2026-03-28
**Status**: Accepted
**Note**: Database component partially superseded by ADR-002 (SQLite → NeonDB PostgreSQL)
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

## ADR-002: NeonDB PostgreSQL Migration

**Date**: 2026-04-14
**Status**: Accepted
**Deciders**: Developer / @systems-architect

### Context

MindGuard v1.0 used SQLite as the database (per ADR-001). When deploying to Vercel serverless, SQLite became unviable: Vercel's filesystem is ephemeral — each cold start resets `/tmp`, causing data loss. The team needed a persistent database compatible with serverless architecture. NeonDB offered a free-tier PostgreSQL with connection pooling, and the team already had a NeonDB account.

### Options Considered

1. **SQLite + `/tmp` workaround**: Keep SQLite, copy to/from `/tmp` on each invocation — Pros: no migration needed. Cons: data loss risk on every cold start, complex workaround, unreliable.
2. **NeonDB PostgreSQL**: Serverless PostgreSQL with built-in connection pooling — Pros: free tier (0.5 GB), persistent data, pooler endpoint compatible with serverless, SQLAlchemy already in use. Cons: network latency vs local SQLite, free tier storage limits.
3. **Supabase PostgreSQL**: Alternative managed PostgreSQL — Pros: generous free tier, REST API. Cons: additional complexity, team already had NeonDB account set up.

### Decision

NeonDB PostgreSQL chosen because: (1) free tier sufficient for current scale, (2) same connection string works for local development and production (simplifies config), (3) pooler endpoint with `pool_pre_ping=True` and `sslmode=require` handles serverless connection patterns, (4) SQLAlchemy ORM abstraction meant minimal code changes — models stayed identical.

Configuration: `DATABASE_URL` via environment variable or `.env/postgresql_neondb.json`. Engine options: `pool_pre_ping=True`, `sslmode=require`, pool size tuned for serverless (see `config.py`).

### Consequences

- **Positive**: Zero data loss risk, no env-specific config (same DB for local + production), connection pooling handles serverless cold starts gracefully
- **Negative**: NeonDB free tier limited to 0.5 GB storage, network latency higher than local SQLite (acceptable for current scale), dependency on external service
- **Neutral**: Migration scripts remain manual (in `database/` directory) — no Alembic/flask-migrate per project conventions

---

## ADR-003: Vercel Serverless Deployment

**Date**: 2026-04-14
**Status**: Accepted
**Deciders**: Developer / @systems-architect

### Context

MindGuard needed a deployment platform with zero budget. The app is a Flask server-side rendered application with AI integrations (OpenRouter API calls). Key constraints: free tier needed, Python support required, GitHub integration preferred for CI/CD. The team evaluated platforms that could host Python web apps within these constraints.

### Options Considered

1. **Vercel serverless**: Python serverless functions via `vercel.json` routing — Pros: generous free tier, global CDN, GitHub auto-deploy, edge network. Cons: ephemeral filesystem (no file writes), 10s function timeout on hobby tier, cold start latency.
2. **Railway**: Container-based hosting — Pros: persistent filesystem, no timeout limits, easy setup. Cons: free tier limited to $5/month credit (may run out), no edge CDN.
3. **Render**: Web service hosting — Pros: persistent filesystem, generous free tier for static. Cons: free tier spins down after 15 min inactivity (30s+ cold start), slower recovery than Vercel.

### Decision

Vercel chosen because: (1) free tier generous enough for a student project (100 GB bandwidth, unlimited deploys), (2) GitHub integration provides auto-deploy on push, (3) global edge network improves latency for Vietnamese users, (4) Python supported via serverless functions with `vercel.json` routing.

Adaptations for Vercel constraints:
- **Ephemeral filesystem**: All persistence via NeonDB (ADR-002), no local file writes
- **10s timeout**: AI chatbot timeout set to 8s (see ADR-004) to stay under limit
- **Cold start**: NeonDB pooler with `pool_pre_ping=True` handles connection recovery
- **Session management**: Flask session via secure cookies (no server-side session files)

### Consequences

- **Positive**: Free hosting with CDN, automatic deployments from GitHub, zero DevOps overhead
- **Negative**: 10s function timeout limits long-running operations (AI responses must be fast), no persistent filesystem (evidence file uploads need external storage in future), cold start adds ~2-3s latency on first request
- **Neutral**: `vercel.json` routing config required to map Flask routes to serverless functions

---

## ADR-004: AI Safety Strategy

**Date**: 2026-04-14
**Status**: Accepted
**Deciders**: Developer / Supervisor

### Context

MindGuard's AI chatbot uses OpenRouter API (models: DeepSeek, Gemini, Llama) to provide fraud prevention guidance in Vietnamese. Risks identified: (1) models may respond to sensitive topics (politics, religion, self-harm) outside the fraud domain, (2) AI responses may be uncertain or incorrect for high-stakes fraud situations, (3) long API response times could exceed Vercel's 10s function timeout.

### Options Considered

1. **No guardrails**: Let the model respond freely — Pros: simplest implementation. Cons: risk of harmful/inappropriate responses, no timeout protection.
2. **Prompt-only safety**: System prompt instructs model to refuse sensitive topics — Pros: easy to implement. Cons: prompt injection possible, no hard guarantees, no timeout protection.
3. **Multi-layer safety (hard-block + fallback + timeout)**: Keyword-based pre-filter blocks sensitive topics before API call, structured fallback when AI is uncertain, strict timeout — Pros: defense in depth, Vercel-compliant. Cons: some legitimate queries may be blocked by keyword filter, maintenance of block list needed.

### Decision

Multi-layer safety strategy implemented in `utils/chatbot.py`:

1. **Hard-block list** (`_SENSITIVE_KEYWORDS`): Pre-filters messages containing sensitive topics (politics, religion, self-harm keywords). Returns a static safe response with hotline information (Công an: 113) — no API call made.
2. **Timeout 8s**: `urllib.request.urlopen(req, timeout=8)` — stays under Vercel's 10s function kill limit with 2s margin for network overhead.
3. **Fallback response** (`get_fallback_response()`): When AI is unavailable or uncertain, returns safety-focused advice (cảnh báo OTP, hướng dẫn liên hệ cơ quan chức năng).
4. **System prompt**: Constrains model to fraud prevention domain, uses plain Vietnamese (not technical jargon), per AISF-03.

### Consequences

- **Positive**: User safety protected, Vercel timeout compliant, graceful degradation when AI unavailable
- **Negative**: Keyword-based blocking may catch legitimate queries about fraud involving sensitive platforms, hard-coded block list requires manual maintenance
- **Neutral**: Dual chatbot paths: `utils/chatbot.py` (support flow) and `utils/ai_agent.py` (advanced AI agent) — both share safety patterns

---

## ADR-005: DB-backed Rate Limiting

**Date**: 2026-04-14
**Status**: Accepted
**Deciders**: Developer (teammate implementation)

### Context

MindGuard's chatbot endpoints (`/chatbot/api`, `/chatbot/support`, `/chatbot/send`) call OpenRouter API on every request. OpenRouter free tier has limited credits — without rate limiting, a single user or bot could drain the API budget. Vercel serverless functions are stateless — each invocation has its own memory space with no shared state between invocations, making in-memory counters ineffective.

### Options Considered

1. **In-memory counter (e.g., `dict` or `collections.Counter`)**: Track request counts in process memory — Pros: zero latency, no external dependency. Cons: Vercel serverless = each invocation is a new process, counter resets every cold start, completely ineffective.
2. **Redis-backed (e.g., Upstash Redis)**: External fast key-value store — Pros: designed for rate limiting, sub-ms latency. Cons: additional service to manage, another free tier to monitor, increased deployment complexity.
3. **DB-backed via Flask-Limiter (`@limiter`)**: Store rate limit counters in the existing NeonDB PostgreSQL — Pros: uses existing infrastructure, no new service, Flask-Limiter handles the logic. Cons: slightly higher latency than Redis (~5-10ms per check), additional DB writes.

### Decision

DB-backed rate limiting via Flask-Limiter (`@limiter`) decorator chosen because: (1) reuses existing NeonDB connection — no additional infrastructure, (2) Flask-Limiter provides declarative syntax (`@limiter.limit("20/minute;3/second")`), (3) acceptable latency for current scale.

Applied limits:
- `/chatbot/api` (AI chat): `20/minute; 3/second`
- `/chatbot/support` (support chat): `10/minute; 2/second`
- `/chatbot/send` (send message): `10/minute`
- `/auth/login` (POST): `10/minute; 3/second`
- `/auth/register` (POST): `5/minute`
- `/admin/login` (POST): `5/minute; 1/second`
- `/api/*` (general API): `30/minute; 5/second`

### Consequences

- **Positive**: No extra infrastructure cost, protects API budget, declarative and easy to adjust per-endpoint
- **Negative**: Each rate limit check involves a DB query (~5-10ms overhead), slightly increases NeonDB usage
- **Neutral**: Rate limit state persists across cold starts (DB-backed), which is correctly the behavior we want for serverless

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
