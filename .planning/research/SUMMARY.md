# Project Research Summary

**Project:** MindGuard v2
**Domain:** Cybersecurity education and scam-reporting web platform (brownfield Flask monolith)
**Researched:** 2026-03-19
**Confidence:** MEDIUM-HIGH

## Executive Summary

MindGuard v2 is best built as an incremental hardening and UX modernization of the current Flask monolith, not a replatform. The combined research consistently supports keeping Flask + Jinja + Bootstrap and delivering improvements in additive slices: anti-spam policy services, privacy-safe data handling, and phased UI upgrades. This aligns with current architecture boundaries and minimizes regression risk on critical auth, quiz, and reporting routes.

For this cycle, the strongest approach is to prioritize trust foundations first: shared light-mode design consistency, per-question quiz flow with durable server-side state, and multi-signal anti-abuse controls (not IP-only blocking). The research shows these are table-stakes for 2026 user expectations on scam-report platforms and directly support the active requirements in PROJECT.md.

The largest risks are false-positive abuse controls, privacy leakage from sensitive fields, and big-bang UX changes. Mitigation should follow monitor-then-enforce rollout, additive database migrations with rollback hygiene, and feature-flagged UI migration measured by funnel telemetry.

## Key Findings

### Recommended Stack Direction

Keep the current monolith and upgrade in place rather than adopting microservices or SPA architecture. Add Redis-backed anti-abuse capabilities and lightweight background processing while preserving existing route and template contracts.

**Core technologies:**

- Flask 3.1.x: request lifecycle and blueprint composition, stable documented path from current 3.0.x baseline.
- Flask-SQLAlchemy 3.1.x (SQLAlchemy 2.0 style incrementally): keeps model compatibility while enabling cleaner query/migration hygiene.
- SQLite (current phase) with strict migration/index hardening: fastest delivery for v1; prepare PostgreSQL path when concurrency grows.
- Flask-Limiter with Redis backend: production-grade rate limiting and abuse throttling.
- Redis + RQ: shared counters and lightweight async jobs (leaderboard reconcile, abuse event processing).
- Privacy utilities (hashing/masking normalization + phonenumbers): consistent PII minimization and deterministic masking.
- Bootstrap 5.3.x + CSS design tokens: lowest-risk way to deliver light-mode consistency across pages.

### Feature Direction

The feature research separates baseline trust expectations from engagement enhancements. For v1 planning, table-stakes should ship first, differentiators should be gated by anti-gaming safeguards, and anti-features should be explicitly blocked.

**Table-stakes:**

- Light-mode UX consistency across auth, quiz, reporting, and profile flows.
- 1-question-per-page quiz with visible progress and safe state persistence.
- Baseline anti-abuse controls on report submission (rate limiting + clear cooldown feedback).
- Privacy-by-default masking of sensitive reporter fields (phone visible only as masked form).
- Transparent guidance for reporting flow and expected outcomes.
- Abuse telemetry for monitoring false positives/false negatives.

**Differentiators:**

- Reporter leaderboard with integrity controls.
- Credibility-weighted scoring (quality over raw quantity).
- Adaptive friction (step-up challenge based on risk, not blanket friction).
- Contextual micro-learning inside reporting flow.
- Privacy transparency panel explaining tracked signals and retention intent.

**Anti-features (avoid in v1):**

- Raw phone display in public/admin-by-default views.
- Count-only leaderboard without quality or moderation gates.
- Hard blocking using only a single signal (IP or cookie alone).
- Permanent lockouts for burst behavior without recovery path.
- Big-bang redesign spanning IA/navigation/branding together.
- Heavy bot-vendor dependency before baseline telemetry exists.

### Architecture Build Order

The architecture research strongly supports additive integration seams around existing routes (`auth`, `scammer`, `quiz`) and monitor-first policy rollout.

**Build order:**

1. Security and data-governance foundation: migration hygiene, CSRF/rate-limit guardrails, audit logging, abuse event schema.
2. Anti-spam monitor mode: add service layer + policy engine + telemetry repository with no hard blocks yet.
3. Soft enforcement on report flow: challenge/block thresholds only for clearly abusive patterns; validate false-positive rate.
4. Auth flow reuse: apply same anti-abuse service to login/register with route-specific thresholds.
5. UI design system foundation: shared light-mode tokens and base layout consistency.
6. Page UX modernization: per-question quiz flow and report UX improvements under feature flags.
7. Operations tuning and scale readiness: tighten thresholds, move expensive tasks to queue, prep PostgreSQL path if needed.

### Critical Pitfalls

1. Single-signal abuse blocking (IP/cookie only): use multi-signal risk scoring and graduated actions.
2. Privacy boundary gaps in anti-fraud telemetry: enforce masking, data classification, retention/role boundaries.
3. Missing guardrails on state-changing endpoints: require CSRF, rate limits, dedupe/idempotency windows.
4. Embedding anti-spam logic directly in route handlers: move to service/policy layers for testability and safer iteration.
5. Hard-fail behavior when upstream challenge services degrade: use timeouts, fallback policy, and queue where realtime is unnecessary.
6. Big-bang UX rollout: use feature flags and funnel metrics (completion, drop-off, per-step time).
7. No moderation audit trail: log actor, reason codes, and timeline for sensitive actions.
8. Unrepeatable DB migration changes: enforce standalone migration scripts in `database/` with verification and rollback plans.

## Implications for Roadmap

Suggested phase structure for requirements and roadmap generation:

### Phase 1: Foundations (Security, Data, Observability)

**Rationale:** De-risks every later feature and blocks high-severity governance failures early.
**Delivers:** Migration hygiene, abuse tables, CSRF/rate-limit baseline, moderation audit trail, privacy masking utilities.
**Addresses:** Table-stakes for privacy and abuse monitoring.
**Avoids:** Pitfalls 2, 3, 7, 8.

### Phase 2: Anti-Spam Engine (Monitor -> Soft Enforce)

**Rationale:** Needs telemetry before strict blocking to prevent user lockouts.
**Delivers:** Anti-spam service + rule engine + route guard wrappers on report flow, threshold configs, reason-coded decisions.
**Addresses:** Table-stakes for anti-abuse and cooldown feedback.
**Avoids:** Pitfalls 1, 4, 5.

### Phase 3: UX System and Quiz Flow Modernization

**Rationale:** Build shared token system before page-level redesign to avoid inconsistent UI drift.
**Delivers:** Light-mode design token foundation, one-question-per-page quiz with progress + resilient state, mobile-first regression checks.
**Addresses:** Table-stakes for UX consistency and staged quiz flow.
**Avoids:** Pitfall 6.

### Phase 4: Leaderboard Integrity and Engagement

**Rationale:** Leaderboard should only launch after anti-gaming and moderation signals exist.
**Delivers:** Reporter leaderboard, quality-weighted scoring, integrity rules, reconciliation job.
**Addresses:** Differentiators (leaderboard and credibility scoring).
**Avoids:** Count-only gaming anti-feature.

### Phase 5: Tuning, Reliability, and Scale Preparation

**Rationale:** Consolidates metrics-driven tuning after initial rollout behavior is observed.
**Delivers:** Threshold tuning, false-positive reduction, queue hardening, optional PostgreSQL migration plan trigger criteria.
**Addresses:** Reliability and sustainability goals.
**Avoids:** Overfitting and premature replatforming.

### Recommendations for v1 Scope

Include in v1:

- Light-mode consistency and quiz flow redesign (1 question/page) with telemetry.
- Privacy-safe reporter masking everywhere rendered.
- Multi-signal anti-abuse baseline with monitor-first rollout and soft enforcement.
- Foundation for moderation auditability.

Gate or defer beyond core v1:

- Advanced adaptive friction engine beyond rules-based thresholds.
- ML-driven bot classification.
- Broad platform redesign outside targeted UX flows.
- Major architectural replatform.

### Research Flags

Phases likely needing deeper research during planning:

- Phase 2: threshold calibration and false-positive management strategy under real traffic.
- Phase 4: quality-weighted leaderboard formula and abuse-resistance economics.
- Phase 5: PostgreSQL migration trigger criteria and cutover strategy.

Phases with established patterns (lower research burden):

- Phase 1: CSRF/rate limiting/audit logging/migration hygiene in Flask monoliths.
- Phase 3: design tokens + progressive disclosure quiz UX patterns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Based on official Flask, SQLAlchemy, Flask-Limiter, Cloudflare references and codebase fit. |
| Features | MEDIUM | Strong baseline from OWASP/industry guidance; leaderboard mechanics need product tuning. |
| Architecture | HIGH | Directly grounded in current blueprint/route structure and additive integration strategy. |
| Pitfalls | HIGH | High agreement between codebase concerns and domain failure modes. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- Abuse thresholds are not research-resolvable without production-like telemetry; must tune via staged rollout.
- Leaderboard scoring governance (quality signals, moderation weighting) needs explicit product policy before launch.
- Privacy notice wording and retention windows require policy decisions aligned with implementation.
- Trigger points for SQLite -> PostgreSQL migration should be defined as measurable SLO/SLI thresholds.

## Sources

### Primary (HIGH confidence)

- `.planning/research/STACK.md`
- `.planning/research/FEATURES.md`
- `.planning/research/ARCHITECTURE.md`
- `.planning/research/PITFALLS.md`
- `.planning/PROJECT.md`

### Secondary (MEDIUM confidence)

- Flask official docs and deployment guidance
- Flask-SQLAlchemy and SQLAlchemy SQLite dialect docs
- Flask-Limiter docs
- Cloudflare Turnstile docs
- OWASP authentication/privacy cheat sheets

---
*Research completed: 2026-03-19*
*Ready for roadmap: yes*
