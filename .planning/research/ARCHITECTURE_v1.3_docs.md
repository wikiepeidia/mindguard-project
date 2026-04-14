# Architecture Patterns — Documentation Structure for v1.3

**Domain:** Technical documentation & SOP for existing Flask application
**Researched:** 2026-04-14

---

## Documentation Inventory & Current State

### What exists and what's wrong

| Document | Location | State | Problem |
|----------|----------|-------|---------|
| ARCHITECTURE.md | `docs/technical/` | Outdated | Says SQLite, references localhost/ngrok deployment, 4 data flow sections are `[To be filled]`, Design System has placeholder tokens |
| API.md | `docs/technical/` | Empty template | Generic REST template (Bearer tokens, JSON errors) — MindGuard uses session auth + server-rendered HTML, not REST API |
| DATABASE.md | `docs/technical/` | Empty template | Generic PostgreSQL template with `users`/`sessions` tables that don't match actual schema (13+ real models) |
| DECISIONS.md | `docs/technical/` | 1 ADR only | ADR-001 (Flask+SQLite) — missing ADRs for NeonDB migration, Vercel deployment, AI model choices, anti-spam design |
| USER_GUIDE.md | `docs/user/` | Empty template | Generic SaaS template, no MindGuard content |
| SOP_BAO_CAO.md | `documents/SOP/` | Exists, partially outdated | Good structure but references may not match current admin routes/UI |
| HUONG_DAN_BAO_CAO_NGUOI_DUNG.md | `documents/SOP/` | Exists | User-facing report guide, has PLACEHOLDER_HINH tags for screenshots |
| ML_DU_LIEU_GAN_NHAN.md | `documents/SOP/` | Exists | Data labeling plan for future ML, references current schema correctly |
| ML_MODERATION_ROADMAP.md | `documents/SOP/` | Exists | ML roadmap, forward-looking — may not need updates in v1.3 |
| SOP README | `documents/SOP/` | Exists | Index file, needs update if new SOPs are added |

### Key problem: Template mismatch

API.md and DATABASE.md use generic SaaS REST API templates (Bearer tokens, JSON error format, UUID primary keys, `users`/`sessions` tables). MindGuard is **not** a REST API — it's a server-rendered Flask app with:
- Session-cookie authentication (not Bearer tokens)
- HTML responses for most routes (not JSON)
- Integer auto-increment primary keys (not UUIDs)
- 13+ domain-specific models (not generic users/sessions)

**These templates must be rewritten from scratch**, not filled in.

---

## Document Dependency Graph

```
DECISIONS.md ─────────────────────────────────────────────┐
  (context: WHY)                                          │
       │                                                  │
       v                                                  v
DATABASE.md ──────────> ARCHITECTURE.md ──────> SOP_VAN_HANH.md (new)
  (foundation:          (system view:           SOP_QUAN_TRI.md (new)
   WHAT data)            HOW it works)          SOP_BAO_CAO.md (update)
       │                      │
       v                      v
   API.md ◄──────────────────┘
  (contract:
   endpoints + payloads)
       │
       v
   USER_GUIDE.md
  (user-facing:
   HOW to use)
```

### Dependency rules

| Document | Depends on | Reason |
|----------|-----------|--------|
| DECISIONS.md | Nothing (source of truth) | ADRs capture WHY — no external doc dependency |
| DATABASE.md | DECISIONS.md (light) | ADR-NeonDB explains why PostgreSQL; schema comes from `models.py` |
| ARCHITECTURE.md | DECISIONS.md + DATABASE.md | References schema for data flow diagrams; ADRs explain design choices |
| API.md | DATABASE.md + ARCHITECTURE.md | Endpoint docs reference model fields; architecture explains routing pattern |
| SOP_BAO_CAO.md (update) | API.md + ARCHITECTURE.md | SOP references admin endpoints and system behavior |
| SOP_VAN_HANH.md (new) | ARCHITECTURE.md | Deploy/monitoring SOP needs system architecture context |
| SOP_QUAN_TRI.md (new) | API.md + DATABASE.md | Admin workflow SOP references endpoints and data states |
| USER_GUIDE.md | All above | End-user doc synthesizes system capabilities |

---

## Optimal Writing Order

### Wave 1: Foundation (no dependencies)

**1. DECISIONS.md** — Add missing ADRs

Source in codebase:
- `config.py` lines 30-37 → ADR-002: NeonDB PostgreSQL migration (DATABASE_URL preference, fallback logic)
- `app.py` lines 22-27 → ADR-003: Vercel serverless deployment (ephemeral filesystem, /tmp for logs)
- `utils/ai_agent.py` → ADR-004: OpenRouter free-tier AI models (fallback strategy, model list)
- `services/anti_spam.py` + `config.py` lines 59-65 → ADR-005: Multi-signal anti-spam (monitor/enforce modes, configurable weights)
- `utils/encryption.py` + `utils/privacy_policy.py` → ADR-006: PII protection strategy

Extraction method: Read each source file, document the decision context (what problem it solved), alternatives that were implicitly rejected (visible from code comments and structure), and consequences (visible from known constraints in current ARCHITECTURE.md).

**2. DATABASE.md** — Document actual schema

Source in codebase:
- `models/models.py` (complete file, ~180 lines) → All 13+ models with columns, types, constraints, relationships

Models to document (in dependency order):
1. `Registration` — core user entity (referenced by 4 other models via ForeignKey)
2. `ScamReport` — educational scam case studies
3. `ScammerReport` — user-submitted scammer reports (core domain entity)
4. `ScammerLeaderboard` — FK → ScammerReport
5. `QuizResult` — quiz scores and certificates
6. `AiQuizQuestion` — AI-generated quiz content
7. `AiChatSession` — FK → Registration; has cascade to AiChatMessage
8. `AiChatMessage` — FK → AiChatSession
9. `ChatSupportMessage` — legacy support chat (string session_id, no FK)
10. `ChatFeedback` — FK → Registration, AiChatSession, AiChatMessage
11. `Subscription` — FK → Registration; scammer tracking subscriptions
12. `SensitiveAccessLog` — FK → Registration; admin audit trail
13. `AntiSpamEvent` — rate limiting events (no FK, uses actor_key)
14. `AntiSpamActorState` — rate limiting actor state (no FK, uses actor_key)

Extraction method: Read `models.py` sequentially. For each model: table name, columns with SQLAlchemy types mapped to PostgreSQL types, constraints (nullable, unique, default, FK), indices (from `index=True` on columns), relationships (from `db.relationship` and `db.ForeignKey`). Generate ASCII ERD from ForeignKey references.

**Critical note:** DATABASE.md template currently uses UUID PKs and `users`/`sessions` tables. Must replace entirely — MindGuard uses Integer auto-increment PKs and `registrations` as the user table.

### Wave 2: System View (depends on Wave 1)

**3. ARCHITECTURE.md** — Update for current reality

Current doc is 80% usable. Specific sections to update:

| Section | Current state | Action | Source |
|---------|--------------|--------|--------|
| Overview paragraph | Says "SQLite provides persistence" | Replace with NeonDB PostgreSQL | `config.py` |
| Tech Stack table | Lists SQLite, localhost+ngrok hosting | Update DB row, add Vercel row | `config.py`, `app.py` |
| ASCII diagram | Missing Vercel/NeonDB in External Services | Add NeonDB and Vercel | — |
| Data Flow: Auth | `[To be filled]` | Document from `routes/auth.py` (login→OTP→session→profile) | `routes/auth.py` (7 routes) |
| Data Flow: Quiz | `[To be filled]` | Document from `routes/quiz.py` (start→AI gen→step→finalize→result→cert) | `routes/quiz.py` (5 routes) |
| Data Flow: Report | `[To be filled]` | Document from `routes/scammer.py` (report→turnstile→antispam→save→admin queue) | `routes/scammer.py` + `services/anti_spam.py` |
| Data Flow: Chatbot | `[To be filled]` | Document from `routes/chatbot.py` (session→send→OpenRouter→save→render) | `routes/chatbot.py` (7 routes) |
| Design System | All placeholder values | Fill from actual CSS/Bootstrap usage or mark as N/A | `static/css/`, `templates/base.html` |
| Infrastructure | Says "TBD", "localhost + ngrok" | Update: Vercel production, NeonDB, ngrok for dev | Vercel config, `app.py` |
| Performance | References SQLite in-process | Update for network-based PostgreSQL latency | — |
| Known Constraints | SQLite items outdated | Remove SQLite debt, add Vercel-specific constraints (cold starts, read-only FS, 10s timeout) | — |
| Security Architecture | Correct but incomplete | Add CSRF protection (`extensions.py`), rate limiter, security headers (`app.py` lines 51-58) | `app.py`, `extensions.py` |

Extraction method: For data flows, trace request path through route handler code. Each route file is self-contained — read the handler function, note middleware checks (session, turnstile, anti-spam), database operations, external API calls, and response type.

### Wave 3: Contract (depends on Wave 2)

**4. API.md** — Document all endpoints

MindGuard has **42 routes** across 8 blueprints. Most return HTML. Only `routes/api.py` and a few AJAX endpoints return JSON.

**Template must be redesigned.** Current template assumes REST API. Recommended structure:

```
# API & Route Reference

## Overview
- Most routes return server-rendered HTML
- JSON endpoints are internal (consumed by frontend JS)
- Authentication via Flask session cookie

## Blueprint: auth (/auth/*)
  - GET/POST /login
  - GET/POST /register
  - ...

## Blueprint: api (/api/*)   ← JSON endpoints
  - GET /check?q=...
  - GET /stats

## Blueprint: chatbot (/chatbot/*)
  - POST /send          ← JSON (AJAX)
  - POST /api           ← JSON (AJAX)
  - ...
```

Source in codebase (route count per blueprint):
- `routes/auth.py` — 7 routes (login, register, verify-otp, onboarding, complete-onboarding, profile, profile/edit, logout)
- `routes/admin.py` — 10 routes (login, dashboard, logout, unsuspend, create-admin, delete-user, edit-user, scammer-reports, approve-report, reject-report, export-dataset, sensitive-access-logs)
- `routes/chatbot.py` — 7 routes (index, new, send, api, rename, support, feedback)
- `routes/quiz.py` — 5 routes (quiz, step, finalize, result, certificate)
- `routes/scammer.py` — 2 routes (report, follow)
- `routes/main.py` — 4 routes (home, leaderboard, api/search, scammer detail)
- `routes/library.py` — 2 routes (library index, article detail)
- `routes/api.py` — 2 routes (check, stats)

Extraction method: For each route, read the handler to document: HTTP method, URL pattern, authentication requirement (session check at top of handler), request parameters (form data, query params, JSON body), response type (render_template = HTML, jsonify = JSON), side effects (DB writes, external API calls).

**Key distinction to document:** Which endpoints are HTML pages vs JSON APIs. The JSON endpoints are: `/api/check`, `/api/stats`, `/api/search`, `/chatbot/send`, `/chatbot/api`, `/chatbot/rename`, `/chatbot/support`, `/chatbot/feedback`, `/scammer/follow`.

### Wave 4: Operations (depends on Waves 2-3)

**5. SOP_BAO_CAO.md** — Update existing

Current SOP references correct endpoints but may need:
- Verification against current `routes/admin.py` route signatures
- Screenshots update (PLACEHOLDER_HINH tags already exist)
- Anti-spam section (new since original SOP was written)

Source: Compare SOP endpoints against `routes/admin.py` route decorators.

**6. SOP_VAN_HANH.md** — New: System Operations SOP

Content to extract from codebase:
- Vercel deployment: `app.py` lines 22-27 (VERCEL env check), `vercel.json` if exists
- Config management: `config.py` JSON loader pattern for `.env/*.json`
- Logging: `app.py` lines 28-36 (access logging setup)
- Database: NeonDB connection via `DATABASE_URL`
- Extensions: `extensions.py` (rate limiter default: 200/min)

**7. SOP_QUAN_TRI.md** — New: Admin Operations SOP

Content to extract from codebase:
- Admin auth: `routes/admin.py` login handler + `session.get('is_admin')` checks
- User management: create-admin, edit-user, delete-user, unsuspend routes
- Report moderation: scammer-reports, approve-report, reject-report
- Data export: export-dataset route
- Audit logs: sensitive-access-logs route
- `services/admin_guard.py` — admin protection logic

### Wave 5: User-facing (depends on everything)

**8. USER_GUIDE.md** — Write from scratch

Must be Vietnamese. Source: all route handlers mapped in API.md + UI from templates.

---

## Integration Points Between Documents

### Cross-references to maintain

| From | To | Reference type |
|------|----|---------------|
| ARCHITECTURE.md "Data Flow" sections | DATABASE.md model names | Model references in flow diagrams |
| ARCHITECTURE.md "Tech Stack" table | DECISIONS.md ADR IDs | "See ADR-002" for decision rationale |
| API.md endpoint request/response | DATABASE.md column definitions | Field names and types in payloads |
| API.md authentication section | ARCHITECTURE.md "Security Architecture" | Link to auth design explanation |
| SOP_BAO_CAO.md step-by-step | API.md admin endpoints | Endpoint URLs and expected behavior |
| SOP_QUAN_TRI.md | API.md + DATABASE.md | Admin routes + data states (pending/approved/rejected) |
| SOP_VAN_HANH.md | ARCHITECTURE.md Infrastructure | Deploy target, monitoring, config |
| USER_GUIDE.md | All SOPs | Simplified version of operational docs |
| DECISIONS.md ADRs | ARCHITECTURE.md Known Constraints | ADR consequences appear as constraints |

### Consistency rules

1. **Model names** must match `models.py` `__tablename__` exactly (e.g., `scammer_reports` not `scammer_report`)
2. **Route URLs** must match `@bp.route()` decorators exactly (verify with grep)
3. **Config keys** must match `config.py` class attributes exactly
4. **Status values** must match model defaults (e.g., `'pending'`, `'unverified'` — single-quoted lowercase strings)

---

## Content Extraction Strategy Per Document

### Automated extraction possible

| Document | Extractable from code | Method |
|----------|----------------------|--------|
| DATABASE.md schema tables | `models.py` model definitions | Parse Column types, constraints, FKs |
| API.md route list | `@bp.route()` decorators | grep across `routes/*.py` |
| API.md auth requirements | `session.get()` checks in handlers | grep for session checks |
| ARCHITECTURE.md component diagram | `app.py` blueprint registrations | Read import + register_blueprint calls |

### Requires manual analysis

| Document | Content | Why manual |
|----------|---------|-----------|
| DECISIONS.md ADR context | "Why was this chosen?" | Requires understanding implicit decisions from code structure |
| ARCHITECTURE.md data flows | Request lifecycle | Requires reading handler logic and tracing calls |
| SOP documents | Step-by-step procedures | Requires understanding user intent, not just code |
| USER_GUIDE.md | User-facing instructions | Requires UX perspective, Vietnamese localization |

---

## Patterns to Follow

### Pattern 1: Source-linked documentation

Every fact in a doc should trace back to a source file. Use markdown comments to track provenance:

```markdown
<!-- Source: models/models.py:ScammerReport -->
### scammer_reports
| Column | Type | ... |
```

This enables future verification: if code changes, you can grep for the source comment and update the doc.

### Pattern 2: Two-audience API docs

Since MindGuard has both HTML pages and JSON endpoints, split API.md into two sections:
1. **Page Routes** — for developers understanding navigation flow (URL, method, auth, template rendered)
2. **JSON API** — for frontend JS developers (URL, method, request format, response format, error codes)

### Pattern 3: Vietnamese-first with English anchors

All docs in Vietnamese per project convention. But use English for:
- Code identifiers (`ScammerReport`, `status`, `pending`)
- Technical terms where Vietnamese equivalent is ambiguous
- Section anchors (for cross-doc linking)

### Pattern 4: ADR numbering convention

Current: ADR-001. New ADRs should follow:
- ADR-002: NeonDB PostgreSQL migration
- ADR-003: Vercel serverless deployment
- ADR-004: OpenRouter AI model selection
- ADR-005: Multi-signal anti-spam design
- ADR-006: PII protection strategy

Each ADR uses the existing template in DECISIONS.md (Context → Options → Decision → Consequences).

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Filling templates blindly
**What:** Trying to populate the existing API.md/DATABASE.md templates as-is
**Why bad:** Templates assume REST API + UUID PKs + users/sessions — fundamentally wrong for MindGuard
**Instead:** Rewrite templates to match MindGuard's actual patterns (session auth, HTML responses, integer PKs, 13 domain models)

### Anti-Pattern 2: Documenting aspirational state
**What:** Writing docs for what the system *should* be rather than what it *is*
**Why bad:** Misleads onboarding developers; creates trust gap
**Instead:** Document actual current state. Use "Known Constraints" or "Future Work" sections for aspirational items.

### Anti-Pattern 3: Duplicating code in docs
**What:** Copy-pasting entire model definitions or route handlers into docs
**Why bad:** Docs go stale immediately on next code change
**Instead:** Document the contract (what columns exist, types, constraints) not the implementation (SQLAlchemy syntax). Link to source files.

### Anti-Pattern 4: One giant doc
**What:** Putting everything in ARCHITECTURE.md
**Why bad:** Becomes unmaintainable; nobody reads 2000-line docs
**Instead:** ARCHITECTURE.md is the system overview. Detailed schema → DATABASE.md. Endpoint contracts → API.md. Why decisions → DECISIONS.md.

---

## Scalability Considerations

| Concern | Now (v1.3 scope) | At v2.0 (more features) | At team scale (5+ devs) |
|---------|-------------------|------------------------|------------------------|
| Doc discovery | 7 files, flat in `docs/` | Add index/README per folder | Consider doc site (MkDocs/Sphinx) |
| Doc freshness | Manual updates per milestone | Add "last verified" dates | CI check: warn if doc older than 30 days |
| Cross-references | Markdown links between docs | Same, but more links | Automated link checker |
| SOP versioning | Date in header | Version number + changelog | Formal review/approval workflow |

---

## Sources

- `models/models.py` — 13+ SQLAlchemy models (direct read, HIGH confidence)
- `routes/*.py` — 42 routes across 8 blueprints (grep verified, HIGH confidence)
- `config.py` — NeonDB PostgreSQL config, anti-spam settings (direct read, HIGH confidence)
- `app.py` — Blueprint registration, Vercel adaptations, security headers (direct read, HIGH confidence)
- `extensions.py` — Flask extensions: SQLAlchemy, Mail, Limiter, CSRF (direct read, HIGH confidence)
- `services/*.py` — 5 service modules including admin_guard (file search, HIGH confidence)
- `utils/*.py` — 8 utility modules (file search, HIGH confidence)
- `documents/SOP/*.md` — 4 existing SOP documents + README (direct read, HIGH confidence)
- `docs/technical/*.md` — 4 existing technical docs (direct read, HIGH confidence)
- `.planning/PROJECT.md` — v1.3 milestone definition (direct read, HIGH confidence)
