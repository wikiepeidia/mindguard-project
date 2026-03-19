# Phase 01: Privacy & Data Governance Foundation - Research

**Researched:** 2026-03-19
**Domain:** Flask privacy-by-default display policy + sensitive data access audit trail
**Confidence:** MEDIUM-HIGH

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

### Quy tac masking du lieu

- So dien thoai: giu 3 so cuoi, phan con lai che bang `*`.
- Identifier khong phai so dien thoai: giu 2 ky tu dau + 2 ky tu cuoi, phan giua che.
- Cac diem bat buoc masking trong Phase 1: index/leaderboard/public search, scammer profile khi khong du quyen, va API public responses.
- Hien chu thich ro rang: "Du lieu da duoc che de bao mat".

### Pham vi hien thi theo vai tro

- Khach chua dang nhap: chi thay du lieu da che o moi noi.
- User da dang nhap (khong admin): van chi thay du lieu da che.
- Admin: duoc xem full-data, nhung moi lan truy cap full-data phai ghi audit log.
- Export admin: mac dinh masked; neu can full thi bat buoc co reason.

### Thiet ke audit log truy cap

- Truong bat buoc: actor (admin id/email), timestamp, action (view/export/update), object bi truy cap, reason khi full-data, IP + user-agent.
- Retention cho Phase 1: 90 ngay.
- Admin UI: bang co filter theo thoi gian, actor, action.
- Canh bao: bat alert khi tan suat truy cap full-data vuot nguong theo actor/IP.

### Claude's Discretion

- Chi tiet UI component cho bang audit (pagination/filter chips/table density).
- Rule cu the cho format mask voi cac edge-case chuoi ngan.
- Cach to chuc service/helper de tai su dung masking logic giua route va template.

### Deferred Ideas (OUT OF SCOPE)

- Anti-spam multi-signal engine, monitor -> soft-enforce logic (Phase 2).
- Light mode token system va UX redesign (Phase 3).
- Quiz 1-question-per-page flow (Phase 4).
- Leaderboard integrity hardening (Phase 5).
</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PRIV-01 | So dien thoai duoc che, chi hien 3 so cuoi o tat ca diem hien thi. | Central masking policy function + route/template/API enforcement map + regression tests per endpoint/view. |
| PRIV-02 | Quy tac masking du lieu nhay cam duoc ap dung nhat quan trong toan he thong. | Single source of truth policy service, no inline masking in templates/routes, serializer layer for JSON/public payloads. |
| PRIV-03 | Admin co nhat ky truy cap du lieu nhay cam de phuc vu kiem toan. | New audit table + mandatory log writes on full-data view/export/update + retention and alert query jobs. |
</phase_requirements>

## Summary

This phase should be implemented as a privacy policy enforcement layer, not as scattered route patches. The current codebase already has `mask_sensitive_data` in `utils/helpers.py`, but it is not aligned with the locked policy (phone must expose only last 3 digits), and several routes/templates expose full identifiers for logged-in non-admin users. Therefore, the highest-leverage move is to centralize masking policy and role-based visibility in one reusable utility/service and route all public/user outputs through it.

For admin governance, this phase needs a durable audit trail with full-data access logging for view/export/update actions, including actor, object, reason, and request metadata (`remote_addr`, `user_agent`). Manual migration scripts are already the project standard and should be preserved. SQLite 3.49.1 in this environment supports modern ALTER TABLE features, but migration design should still be additive and idempotent.

Testing infrastructure is currently ad-hoc (script-style tests, no pytest installed), so planning must include a Wave 0 test bootstrap for this phase. Without this, privacy regressions are likely because masking logic currently appears in routes, templates, and JS assumptions.

**Primary recommendation:** Implement a centralized privacy policy module + audit log service, then refactor route/template/API output paths to consume it, with a manual additive migration for `sensitive_access_logs` and dedicated privacy regression tests.

## Implementation Options

### Option A: Minimal Patch-In-Place (fastest, highest regression risk)

- Modify existing `mask_sensitive_data` and patch each route/template individually.
- Keep audit logging inline in `routes/admin.py` handlers.
- Pros: low immediate code movement.
- Cons: high drift risk, duplicate logic, easy to miss endpoints, difficult to verify PRIV-02.

### Option B: Central Privacy Policy + Audit Service (recommended)

- Add a dedicated privacy policy function set (mask + role visibility + payload transformation).
- Add `SensitiveAccessLog` model + migration + service function `log_sensitive_access(...)`.
- Route all public/user display and API output through policy functions.
- Require `reason` on admin full export.
- Pros: enforceability, testability, lower long-term maintenance.
- Cons: moderate refactor in `routes/main.py`, `routes/api.py`, `routes/admin.py`, and templates.

### Option C: SQL/View-Layer Masking (not recommended for this phase)

- Push masking into SQL projections/views.
- Pros: database-level consistency for selected queries.
- Cons: poor fit for mixed display types and Flask template logic, harder to preserve existing route behavior quickly in brownfield.

## Recommended Approach

Use Option B with phased rollout:

1. Introduce policy + audit primitives (no behavior change yet).
2. Switch public and authenticated non-admin display paths to masked outputs.
3. Add admin-only full-data paths with mandatory audit writes.
4. Add export reason requirement and masked-by-default export.
5. Add audit monitor/retention command and admin table filters.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.0.3 (pinned), 3.1.3 (installed) | Request handling, session role checks, template rendering | Existing framework, all routes already built on blueprints. |
| Flask-SQLAlchemy | 3.1.1 | ORM + session management | Existing extension in `extensions.py`; standard for current codebase pattern. |
| SQLAlchemy | 2.0.47 (installed) | Transaction-safe persistence for audit events | Supports clean session commit/rollback behavior for audit writes. |
| sqlite3 | 3.49.1 (runtime) | Current DB engine | Supports additive ALTER TABLE strategy and reliable local operations. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Werkzeug request API (via Flask) | bundled | `request.remote_addr`, `request.user_agent.string` for audit metadata | Every admin full-data access write. |
| Python `csv` | stdlib | Controlled masked/full export output | Admin export endpoint policy enforcement. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Flask session booleans (`is_admin`) | Flask-Login roles/permissions | Better long-term auth model, but too large for Phase 1 scope. |
| Inline audit writes in routes | SQLAlchemy event listeners | Events can hide behavior and complicate reason capture from UI flows. |
| Script-style unittest only | pytest + fixtures | Better maintainability; requires Wave 0 setup work. |

**Installation (if environment missing runtime deps):**

```bash
pip install -r requirements.txt
```

## Architecture Patterns

### Recommended Project Structure

```text
utils/
  privacy_policy.py        # mask rules + role-based visibility + annotation helper
services/
  sensitive_access_log.py  # audit write/read helper functions
database/
  migrate_sensitive_access_log.py  # additive migration script (manual)
routes/
  main.py                  # apply policy to index/search/profile payloads
  api.py                   # apply policy to public API responses
  admin.py                 # full-data access gates + reason capture + audit writes
templates/
  admin_sensitive_access_logs.html # admin audit table/filter view
```

### Pattern 1: Privacy-By-Default Output Adapter

**What:** Convert model objects to safe display payloads before rendering/JSON.
**When to use:** Any route returning identifier/phone-like fields.
**Example:**

```python
# Source: project pattern + PRIV decisions
def to_display_identifier(raw_identifier: str, report_type: str, is_admin: bool) -> str:
    if is_admin:
        return raw_identifier
    # Phone keeps last 3; non-phone keeps first 2 + last 2.
    if report_type == "general":
        return mask_phone_keep_last3(raw_identifier)
    return mask_identifier_keep_2_2(raw_identifier)
```

### Pattern 2: Explicit Sensitive Access Logging at Intent Points

**What:** Write audit row where full-data is intentionally exposed/exported/updated.
**When to use:** Admin full view actions, full export actions, sensitive updates.
**Example:**

```python
# Source: Flask request API + SQLAlchemy session practices
def log_sensitive_access(db, actor_id, actor_email, action, object_type, object_id, reason=None):
    entry = SensitiveAccessLog(
        actor_id=actor_id,
        actor_email=actor_email,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        reason=reason,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None,
    )
    db.session.add(entry)
    db.session.commit()
```

### Anti-Patterns to Avoid

- **Template-level role branching for raw identifier:** current templates expose full data for logged-in non-admin users; violates locked constraints.
- **Multiple mask rules across files:** causes PRIV-02 drift and silent inconsistencies.
- **Best-effort audit logging (`try/except: pass`) for admin full access:** governance data loss.

## Migration Notes

1. Additive migration only (manual script in `database/`), no Alembic.
2. New table recommended: `sensitive_access_logs` with columns:
   - `id` PK
   - `actor_id` (nullable int)
   - `actor_email` (nullable str)
   - `action` (`view|export|update`)
   - `object_type` (e.g., `scammer_report`)
   - `object_id` (string to avoid polymorphic FK complexity)
   - `reason` (required for full export, nullable otherwise)
   - `ip_address`
   - `user_agent`
   - `created_at` default UTC timestamp
3. Add indexes:
   - `(created_at)`
   - `(actor_email, created_at)`
   - `(action, created_at)`
4. Keep script idempotent (`inspect()` + conditional CREATE/ALTER behavior).
5. Add retention command/script: delete rows older than 90 days.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Role visibility policy | per-template condition maze | centralized policy helper | Prevents drift and supports testability. |
| Audit request metadata extraction | custom header parser | Flask `request.remote_addr` + `request.user_agent.string` | Standard, stable, already available. |
| DB transaction state machine | manual transaction flags | SQLAlchemy session commit/rollback model | Reduces subtle consistency bugs. |
| Schema rewrite hacks | direct `sqlite_schema` edits | standard ALTER TABLE / additive migration scripts | Safer and maintainable for brownfield DB. |

**Key insight:** Privacy and governance failures in brownfield Flask apps usually come from scattered output logic, not from missing crypto.

## Common Pitfalls

### Pitfall 1: Logged-in Non-Admin Sees Full Identifier

**What goes wrong:** Current condition patterns (`registration_email or is_admin`) expose raw identifiers to any logged-in user.
**Why it happens:** Authenticated state is treated as privileged state.
**How to avoid:** Separate `is_authenticated` from `can_view_sensitive_full`; only admin returns full.
**Warning signs:** Template snippets with `or session.get('registration_email')` around sensitive fields.

### Pitfall 2: API and UI Policy Drift

**What goes wrong:** HTML masked, API still returns raw identifier.
**Why it happens:** No shared serializer/policy layer.
**How to avoid:** Use one output adapter in both `routes/main.py` and `routes/api.py`.
**Warning signs:** `top_match.scammer_info_raw` directly in JSON response.

### Pitfall 3: Audit Coverage Gaps

**What goes wrong:** Some admin full-data flows are not logged (especially exports).
**Why it happens:** Logging added only in one route.
**How to avoid:** Enumerate all sensitive action paths and add tests per action.
**Warning signs:** `send_file` export route with no audit write.

### Pitfall 4: Manual Migration Non-Idempotent

**What goes wrong:** Re-running script fails on existing columns/indexes.
**Why it happens:** Raw ALTER without existence checks.
**How to avoid:** Inspect schema before DDL and commit once.
**Warning signs:** Migration scripts with unconditional DDL and no guard.

## Code Examples

Verified/adapted patterns:

### Mask Rule Helpers

```python
def mask_phone_keep_last3(value: str) -> str:
    if not value:
        return value
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) <= 3:
        return "*" * len(digits)
    return "*" * (len(digits) - 3) + digits[-3:]


def mask_identifier_keep_2_2(value: str) -> str:
    if not value:
        return value
    if len(value) <= 4:
        return value[0] + "*" * (len(value) - 1)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]
```

### Public API Output Guard

```python
def scammer_to_public_payload(report):
    return {
        "identifier": to_display_identifier(
            report.scammer_info_raw,
            report.report_type,
            is_admin=False,
        ),
        "risk_score": report.risk_score or 0,
        "reports_count": report.report_count,
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Inline masking in view/templates | Centralized policy adapter + reusable serializers | Current best practice for privacy-by-default web apps | Lower regression rate, easier audits. |
| Session-auth == full visibility | RBAC policy (`admin` only for full) | Mature governance patterns | Prevents over-exposure for standard users. |
| Unstructured print logs | Structured DB audit trail with filterable metadata | Common compliance baseline | Enables incident forensics and accountability. |

**Deprecated/outdated for this phase:**

- Treating authenticated users as sensitive-data privileged by default.
- Returning raw identifiers in public endpoints.

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking existing admin workflows due to new reason requirement | Medium | Soft rollout: warn + enforce in phase end; add clear UI prompt and validation message. |
| Performance hit from extra audit writes | Low-Medium | Keep row small + indexed + batch cleanup of old rows. |
| Incomplete route coverage of masking | High | Build route inventory and requirement-to-test map before implementation. |
| Data quality issues in old identifiers (short/malformed) | Medium | Define edge-case mask behavior explicitly and test with fixtures. |

## Open Questions

1. **Alert threshold values for excessive full-data access**
   - What we know: must alert by actor/IP when over threshold.
   - What's unclear: exact thresholds and time window.
   - Recommendation: start with config values (e.g., 20/hour actor, 50/hour IP), tune in Phase 1 UAT.

2. **Where to surface alert state in admin UI**
   - What we know: admin table filtering is required.
   - What's unclear: separate dashboard widget vs table badges only.
   - Recommendation: ship table badge + filter in Phase 1; dashboard aggregation can be Phase 1.1 if needed.

3. **API registration gap (`routes/api.py`)**
   - What we know: `api_bp` exists and may not be registered in `app.py`.
   - What's unclear: whether this is intentionally disabled.
   - Recommendation: confirm before planning API privacy test scope; if disabled, still refactor file for future-safe consistency.

## Concrete Planning Guidance

1. **Wave 0 (safety net):** add/repair test harness and privacy fixtures first.
2. **Wave 1 (foundation):** implement policy module + audit model + migration script.
3. **Wave 2 (enforcement):** refactor `routes/main.py`, `routes/api.py`, templates to consume policy adapter.
4. **Wave 3 (governance):** enforce admin reason for full export, add audit list/filter UI and alert query.
5. **Wave 4 (hardening):** retention cleanup script + backfill checks + docs and runbook update.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `unittest` (stdlib) currently; `pytest` not installed |
| Config file | none - see Wave 0 |
| Quick run command | `python -m unittest discover -s tests -p "test_privacy_*.py" -v` |
| Full suite command | `python -m unittest discover -s tests -p "test_*.py" -v` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PRIV-01 | Phone always masked with only last 3 shown on public/user views | unit + integration | `python -m unittest tests/test_privacy_masking.py -v` | ❌ Wave 0 |
| PRIV-02 | Same masking policy across index/search/profile/API | integration | `python -m unittest tests/test_privacy_consistency.py -v` | ❌ Wave 0 |
| PRIV-03 | Admin full-data access creates audit log rows with metadata | integration | `python -m unittest tests/test_sensitive_access_audit.py -v` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python -m unittest tests/test_privacy_masking.py -v`
- **Per wave merge:** `python -m unittest discover -s tests -p "test_privacy_*.py" -v`
- **Phase gate:** Full phase privacy test suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_privacy_masking.py` - covers PRIV-01 edge cases and fixed examples.
- [ ] `tests/test_privacy_consistency.py` - covers PRIV-02 route/API/template parity.
- [ ] `tests/test_sensitive_access_audit.py` - covers PRIV-03 log writes and required fields.
- [ ] `tests/conftest.py` equivalent for unittest fixtures (or lightweight helper module).
- [ ] Runtime deps setup in environment (`pip install -r requirements.txt`) before test execution.

## Sources

### Primary (HIGH confidence)

- SQLite ALTER TABLE reference: <https://www.sqlite.org/lang_altertable.html> (updated 2025-11-13)
- Flask request API (`remote_addr`, `user_agent`): <https://flask.palletsprojects.com/en/stable/api/#flask.Request.remote_addr>
- Flask request context lifecycle: <https://flask.palletsprojects.com/en/stable/reqcontext/>
- SQLAlchemy session/transaction basics: <https://docs.sqlalchemy.org/en/20/orm/session_basics.html>

### Secondary (MEDIUM confidence)

- Project codebase analysis files:
  - `.planning/codebase/ARCHITECTURE.md`
  - `.planning/codebase/CONVENTIONS.md`
  - `.planning/codebase/CONCERNS.md`

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - based on repository pins, installed runtime checks, and official docs.
- Architecture: MEDIUM-HIGH - strongly grounded in existing code patterns; some refactor scope assumptions remain.
- Pitfalls: HIGH - directly observed in current routes/templates/API and confirmed against locked constraints.

**Research date:** 2026-03-19
**Valid until:** 2026-04-18
