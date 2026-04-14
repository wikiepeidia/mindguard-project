# Feature Landscape — Documentation Milestone (v1.3)

**Domain:** SOP & Technical Documentation for Flask-based Cybersecurity Education Platform
**Researched:** 2026-04-14
**Confidence:** HIGH (direct codebase inspection + existing document audit)

---

## Context: Current Documentation State

Audit of existing `documents/SOP/` and `docs/technical/` reveals significant gaps between what exists and what v1.3 requires:

| Document | Current State | Gap |
|----------|--------------|-----|
| `SOP_BAO_CAO.md` | ~200 lines, detailed but references pre-PostgreSQL schema, has PLACEHOLDER images, no anti-spam section for NeonDB-backed service | Needs codebase sync: routes changed, anti-spam DB-backed, Vercel deployment context |
| `HUONG_DAN_BAO_CAO_NGUOI_DUNG.md` | Complete user-facing guide | Minor updates only — CAPTCHA flow may have changed |
| `ML_DU_LIEU_GAN_NHAN.md` | Complete | No update needed for v1.3 |
| `ML_MODERATION_ROADMAP.md` | Complete | No update needed for v1.3 |
| `docs/technical/ARCHITECTURE.md` | Partial — mentions SQLite, localhost/ngrok, no Vercel/NeonDB | Major rewrite needed: NeonDB PostgreSQL, Vercel serverless, new services |
| `docs/technical/API.md` | Template stub only — zero real endpoints documented | Full write from scratch required |
| `docs/technical/DATABASE.md` | Template stub only — generic schema example | Full write from scratch, extract from `models.py` |
| `docs/technical/DECISIONS.md` | Only ADR-001 (Flask+SQLite selection) | Missing 3+ ADRs: NeonDB migration, Vercel deployment, AI safety decisions |
| `docs/user/USER_GUIDE.md` | Template stub only | Out of scope for v1.3 (SOP focus), but noted |
| SOP Vận hành hệ thống | Does not exist | Full write from scratch |
| SOP Quản trị viên | Does not exist | Full write from scratch |

---

## Table Stakes

Documentation the team **must** have for handoff and onboarding. Missing any of these = team members cannot operate the system independently.

| Deliverable | Why Expected | Complexity | Dependencies | Notes |
|-------------|-------------|------------|--------------|-------|
| **SOP Báo cáo lừa đảo (cập nhật)** | Existing `SOP_BAO_CAO.md` references pre-migration schema and routes. Admin following current SOP will hit wrong URLs or misunderstand anti-spam behavior. Core operational document — broken SOP = broken operations. | **MEDIUM** | Requires reading `routes/admin.py`, `routes/scammer.py`, `services/anti_spam.py`, `models.py` to verify all route paths, status fields, and anti-spam integration points. | Update, not rewrite. Key changes: (1) route paths may have shifted, (2) anti-spam now DB-backed with `AntiSpamEvent`/`AntiSpamActorState`, (3) NeonDB context for data export, (4) replace PLACEHOLDER images with actual screenshots or remove placeholders, (5) add Vercel-specific notes (no local file system for exports). |
| **SOP Vận hành hệ thống** | No deployment/ops document exists. Without this, only the original developer can deploy, diagnose, or recover from incidents. Single point of failure for a team project. | **HIGH** | Requires inspecting `vercel.json`, `config.py` env loading, NeonDB connection config, `requirements.txt`, Vercel dashboard setup. Also needs knowledge of Vercel CLI, NeonDB console, and monitoring approach. | Must cover: (1) Vercel deployment workflow (git push → auto-deploy), (2) environment variable management on Vercel, (3) NeonDB connection monitoring and free-tier limits (~100 connections), (4) incident response playbook (502/504 errors, NeonDB connection exhaustion, OpenRouter API down), (5) rollback procedure on Vercel, (6) log access from Vercel dashboard, (7) domain/DNS if applicable. All in Vietnamese. |
| **SOP Quản trị viên** | Admin dashboard exists (`routes/admin.py`) but has zero documentation on how to use it. New admin team members cannot self-onboard. | **MEDIUM** | Requires reading `routes/admin.py` to enumerate all admin pages and actions, `templates/admin/` for UI flow, `services/sensitive_access_log.py` for audit trail, `services/admin_guard.py` for access control. | Must cover: (1) Đăng nhập admin, (2) dashboard overview page, (3) quản lý người dùng, (4) kiểm duyệt báo cáo (link to SOP Báo cáo), (5) xem anti-spam telemetry, (6) xem audit log, (7) quản lý quiz content. Audience: non-technical admin operators. |
| **Database Schema Documentation** | `docs/technical/DATABASE.md` is an empty template. No one can understand the data model without reading `models.py` directly. Blocks onboarding for any developer or data analyst. | **MEDIUM** | Requires reading `models.py` (13 models), any migration scripts in `database/`, and NeonDB connection config. | Must document: (1) all 13 SQLAlchemy models with columns, types, constraints, (2) relationships/foreign keys, (3) indexes, (4) ASCII ERD, (5) NeonDB-specific notes (connection pooling, NullPool config). Write from scratch — current file is a template. |
| **API Reference** | `docs/technical/API.md` is an empty template. Frontend and integration developers have zero reference for endpoint contracts. | **HIGH** | Requires reading all 9 route files (`routes/*.py`) to extract every endpoint: URL, method, auth requirement, request/response format, error codes. | Must document: (1) all blueprint routes grouped by feature (auth, quiz, scammer, chatbot, admin, library, api, main), (2) request parameters/body, (3) response format (HTML vs JSON), (4) authentication requirements (session, admin), (5) anti-spam/rate-limit behavior on protected endpoints. Largest single deliverable by volume. |
| **Architecture Document (cập nhật)** | Existing `ARCHITECTURE.md` says "SQLite" and "localhost + ngrok" — factually wrong for current production. Misleads any new team member. | **MEDIUM** | Requires verifying `config.py` (NeonDB URI), `vercel.json`, `app.py` (blueprint registration), `extensions.py`, all service files. | Key updates: (1) Tech Stack table → NeonDB PostgreSQL + Vercel, (2) Infrastructure section → Vercel serverless + NeonDB, (3) fill in Data Flow diagrams (auth, quiz, report, chatbot — currently "[To be filled]"), (4) add Vercel-specific constraints (10s function timeout, ephemeral instances, read-only filesystem), (5) update component diagram. Partial rewrite, not from scratch. |
| **ADR: NeonDB Migration** | Decision to migrate from SQLite to NeonDB PostgreSQL is not recorded. ADR-001 says "Flask + SQLite" — that decision has been superseded. Without ADR, rationale is lost. | **LOW** | Requires reading PROJECT.md Key Decisions section and v1.1 requirements for context. | ADR-002: Document why NeonDB was chosen over other PostgreSQL options, why same DB for local+production, why NullPool, consequences observed. Supersedes the SQLite portion of ADR-001. |
| **ADR: Vercel Deployment** | Decision to deploy on Vercel serverless (not traditional server) is not recorded. Constrains all future architectural decisions (no background workers, ephemeral filesystem, 10s timeout). | **LOW** | Requires reading `vercel.json` and deployment history context from PROJECT.md. | ADR-003: Document why Vercel over Railway/Render/Fly.io, serverless constraints accepted, consequences for rate limiting (no in-memory), file uploads, cron jobs. |
| **ADR: AI Safety Decisions** | Hard-block on sensitive topics, system prompt language simplification, and fallback strategies are implemented but not recorded. Future developers may remove safety guardrails not understanding why they exist. | **LOW** | Requires reading `utils/chatbot.py` for hard_block_check, system prompt, fallback logic. | ADR-004: Document why hard-block over soft-filter, why specific hotline numbers, why plain-language prompt. Critical for preventing regression of safety measures. |

---

## Differentiators

Documentation that elevates the project from "barely handoffable" to "professionally maintained." Not blockers, but significantly improve team confidence and long-term maintainability.

| Deliverable | Value Proposition | Complexity | Dependencies | Notes |
|-------------|-------------------|------------|--------------|-------|
| **Runbook: Sự cố thường gặp** | Separate from SOP Vận hành — a quick-reference troubleshooting guide for the 5-10 most common production issues. Reduces incident response time from "read the whole SOP" to "Ctrl+F the error." | **LOW** | Depends on SOP Vận hành being written first. Draws from Vercel logs and known failure modes. | Covers: (1) NeonDB "too many connections", (2) Vercel 504 timeout, (3) OpenRouter API 429/500, (4) Cloudflare Turnstile validation failure, (5) session/cookie issues, (6) deployment failed on Vercel. Each entry: symptom → cause → fix → prevention. |
| **Sơ đồ luồng dữ liệu (Data Flow Diagrams)** | ASCII/Mermaid diagrams for the 4 core flows (auth, quiz, report, chatbot). Currently "[To be filled]" in ARCHITECTURE.md. Visual diagrams dramatically reduce onboarding time vs reading code. | **MEDIUM** | Requires reading route handlers and service calls for each flow end-to-end. Can be part of ARCHITECTURE.md update or standalone. | 4 diagrams: (1) User registration → OTP → session, (2) Quiz start → AI question generation → scoring → leaderboard, (3) Report submission → Turnstile → anti-spam → moderation queue, (4) Chat message → rate limit → AI waterfall → fallback → response. |
| **Bảng tóm tắt Environment Variables** | A single reference table of every env var the app needs, where it's used, and what breaks without it. Currently scattered across `config.py`, `.env/*.json`, and Vercel dashboard. | **LOW** | Requires reading `config.py` JSON loaders and Vercel env var setup. | Columns: Variable name, source (.env JSON / Vercel), required/optional, what breaks if missing, example value. Include: `DATABASE_URL`, `SECRET_KEY`, `ADMIN_PASSWORD`, `REPORT_ENCRYPTION_KEY`, `CLOUDFLARE_SITE_KEY`, `CLOUDFLARE_SECRET_KEY`, OpenRouter keys, Flask-Mail config. |
| **Changelog kỹ thuật v1.0→v1.2** | Consolidated technical changelog covering all 14 phases. `documents/CHANGELOG.md` exists but may not be structured for technical audience. A structured version helps developers understand what changed and why. | **LOW** | Requires reading ROADMAP.md completed phases and git history. | Per-milestone summary: what changed, what was added, what was removed, breaking changes. Focus on schema changes (SQLite→PostgreSQL), new services (anti_spam, leaderboard_integrity), and deployment changes. |
| **ADR: Anti-Spam Architecture** | The multi-signal anti-spam system (IP + cookie + account scoring) is a significant architectural decision not captured in any ADR. Documents the risk scoring algorithm and why rule-based over ML. | **LOW** | Requires reading `services/anti_spam.py` and `models.py` anti-spam models. | ADR-005: Why multi-signal approach, why DB-backed on Vercel, why monitor→soft-enforce→hard-enforce progression, why not Flask-Limiter. |
| **ADR: Privacy & Data Masking** | PII masking strategy (phone numbers showing last 3 digits, reporter hash anonymization) is implemented but not recorded. Important for compliance awareness. | **LOW** | Requires reading `utils/privacy_policy.py` and `utils/encryption.py`. | ADR-006: What data is masked, masking rules, encryption approach, compliance context (Nghị định 13/2023/NĐ-CP). |

---

## Anti-Features

Documentation deliverables to explicitly **NOT** produce in v1.3. Producing these would either waste time, create maintenance burden, or violate milestone constraints.

| Anti-Feature | Why Suggested | Why Problematic | What to Do Instead |
|--------------|---------------|-----------------|-------------------|
| **English translations of SOPs** | International audience, academic submission | v1.3 constraint: "Tất cả tài liệu viết bằng tiếng Việt." Translation doubles the writing effort and creates sync maintenance burden. Academic submission has its own format. | Defer to post-v1.3. If academic submission needs English, it's a separate deliverable with different audience and format. |
| **Auto-generated API docs (Swagger/OpenAPI)** | Industry standard for API documentation | Flask app uses mostly server-rendered HTML endpoints, not a REST API. Adding Swagger tooling means code changes (decorators, schemas) — violates "docs only, no code changes" constraint. The handful of JSON endpoints don't justify the tooling overhead. | Write API.md manually by reading route files. It's 9 files, not 90. Manual docs are more accurate for a mixed HTML/JSON app. |
| **Full User Guide rewrite** | `docs/user/USER_GUIDE.md` is a template stub | Out of scope for v1.3 — milestone focuses on SOP (operational) and technical docs. User guide requires different audience analysis (end users vs operators) and UI screenshots. | Note as v1.4 deliverable. Existing `HUONG_DAN_BAO_CAO_NGUOI_DUNG.md` covers the most critical user flow already. |
| **Video walkthroughs of admin dashboard** | Visual medium, easier to follow | High production effort, impossible to version control, breaks immediately when UI changes. The app's UI is still stabilizing (v1.2 had significant UI bug fixes). | Write step-by-step SOP with PLACEHOLDER image markers. Add actual screenshots when UI is stable post-Beta. |
| **Automated documentation tests** | Ensure docs stay in sync with code | Requires code changes (docstring enforcement, schema introspection scripts). Violates "no code changes" constraint. Over-engineering for a project with 1 developer. | Add a manual checklist to each doc: "Last verified against codebase: [date]." Review during milestone transitions. |
| **Separate Security Documentation** | Cybersecurity platform should document security posture | At current scale, security details (encryption, masking, auth) belong in ARCHITECTURE.md sections and relevant ADRs. A standalone security doc creates duplication and sync issues. | Cover security in ARCHITECTURE.md (auth section, encryption section) and in ADRs (privacy masking, anti-spam). |
| **ML/AI documentation updates** | AI chatbot is a core feature | ML readiness docs (`ML_DU_LIEU_GAN_NHAN.md`, `ML_MODERATION_ROADMAP.md`) are already complete and scoped for post-v1 phase. AI safety changes are captured in ADR-004. No ML model is in production yet. | Leave existing ML docs as-is. ADR-004 captures v1.2 AI safety decisions. |
| **Deployment automation scripts** | "One-click deploy" documentation | Would require writing new scripts = code changes. Current deploy is `git push` → Vercel auto-deploys. Documenting this in SOP Vận hành is sufficient. | Cover deployment procedure step-by-step in SOP Vận hành. |

---

## Feature Dependencies

```text
[SOP Báo cáo lừa đảo (cập nhật)]
    └──requires reading──> routes/admin.py, routes/scammer.py, services/anti_spam.py, models.py
    └──depends on──> Database Schema Documentation (to reference correct field names)
    └──blocks──> SOP Quản trị viên (references "kiểm duyệt báo cáo" section)

[SOP Vận hành hệ thống]
    └──requires reading──> vercel.json, config.py, NeonDB console knowledge
    └──is independent of──> other SOPs (can be written in parallel)
    └──feeds into──> Runbook: Sự cố thường gặp (differentiator)

[SOP Quản trị viên]
    └──requires reading──> routes/admin.py, templates/admin/*, services/admin_guard.py
    └──depends on──> SOP Báo cáo (cross-references moderation section)
    └──depends on──> Architecture doc (admin needs system context)

[Database Schema Documentation]
    └──requires reading──> models.py (13 models), database/ migration scripts
    └──is independent of──> SOPs (can be written in parallel)
    └──feeds into──> API Reference (response schemas reference DB models)
    └──feeds into──> SOP Báo cáo (field names, status values)

[API Reference]
    └──requires reading──> all 9 route files in routes/
    └──depends on──> Database Schema Documentation (response field references)
    └──is independent of──> SOPs

[Architecture Document (cập nhật)]
    └──requires reading──> config.py, vercel.json, app.py, extensions.py, all services
    └──is independent of──> other deliverables (can be written first)
    └──feeds into──> all SOPs (system context), all ADRs (architectural frame)

[ADRs (NeonDB, Vercel, AI Safety)]
    └──requires reading──> PROJECT.md Key Decisions, relevant source files
    └──depend on──> Architecture doc (provides the frame ADRs reference)
    └──are independent of──> each other (can be written in parallel)
```

### Suggested Write Order (based on dependencies)

```
Wave 1 (parallel — no dependencies):
  ├── Architecture Document (cập nhật)
  ├── Database Schema Documentation
  └── SOP Vận hành hệ thống

Wave 2 (depends on Wave 1):
  ├── API Reference (needs DB schema)
  ├── SOP Báo cáo lừa đảo (needs DB schema)
  └── ADRs ×3 (needs Architecture context)

Wave 3 (depends on Wave 2):
  └── SOP Quản trị viên (needs SOP Báo cáo + Architecture)

Wave 4 (differentiators, if time permits):
  ├── Runbook: Sự cố thường gặp
  ├── Bảng tóm tắt Environment Variables
  └── Additional ADRs (Anti-Spam, Privacy)
```

---

## MVP Recommendation

Prioritize in this order:

1. **Architecture Document** — Foundation for everything else. Currently misleading (says SQLite). Must be corrected first.
2. **Database Schema Documentation** — Referenced by API docs and SOPs. Write from `models.py`, mechanical work.
3. **SOP Vận hành hệ thống** — Highest operational risk: only 1 person can currently deploy/debug.
4. **API Reference** — Largest volume but most mechanical: read routes, document endpoints.
5. **SOP Báo cáo lừa đảo (cập nhật)** — Existing doc is 80% correct, needs sync with NeonDB/Vercel reality.
6. **SOP Quản trị viên** — Depends on items above, but critical for admin onboarding.
7. **ADRs ×3** — Short documents, high value per word. Record decisions before memory fades.

**Defer to post-v1.3:** User Guide rewrite, English translations, differentiator ADRs (anti-spam, privacy), video content.

---

## Complexity Summary

| Deliverable | Complexity | Effort | Type |
|-------------|-----------|--------|------|
| Architecture Document (cập nhật) | MEDIUM | Partial rewrite — update 60% of existing content | Table Stakes |
| Database Schema Documentation | MEDIUM | Write from scratch — extract from 13 models | Table Stakes |
| SOP Vận hành hệ thống | HIGH | Write from scratch — requires Vercel/NeonDB operational knowledge | Table Stakes |
| API Reference | HIGH | Write from scratch — 9 route files to audit | Table Stakes |
| SOP Báo cáo lừa đảo (cập nhật) | MEDIUM | Update existing — verify routes, add anti-spam context | Table Stakes |
| SOP Quản trị viên | MEDIUM | Write from scratch — enumerate admin pages and workflows | Table Stakes |
| ADR: NeonDB Migration | LOW | Short document — decision + rationale + consequences | Table Stakes |
| ADR: Vercel Deployment | LOW | Short document — decision + constraints accepted | Table Stakes |
| ADR: AI Safety | LOW | Short document — safety guardrails rationale | Table Stakes |
| Runbook: Sự cố thường gặp | LOW | Quick-reference format, 5-10 entries | Differentiator |
| Data Flow Diagrams | MEDIUM | 4 end-to-end flow diagrams, requires trace through code | Differentiator |
| Environment Variables Table | LOW | Extract from config.py, single reference table | Differentiator |
| Changelog kỹ thuật | LOW | Consolidate from ROADMAP.md and git history | Differentiator |
| ADR: Anti-Spam Architecture | LOW | Short document | Differentiator |
| ADR: Privacy & Data Masking | LOW | Short document | Differentiator |

---

## Sources

- Direct codebase inspection: `models.py`, `routes/*.py`, `services/*.py`, `config.py`, `vercel.json`
- Existing documentation audit: `documents/SOP/`, `docs/technical/`, `docs/user/`
- Project state: `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`
- All confidence: **HIGH** — based on direct file reads, not external research
