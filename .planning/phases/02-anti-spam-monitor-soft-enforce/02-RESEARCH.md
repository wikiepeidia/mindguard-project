# Phase 2: anti-spam-monitor-soft-enforce - Research

**Researched:** 2026-03-20
**Domain:** Flask anti-abuse pipeline for report submission (monitor-first -> soft-enforce)
**Confidence:** HIGH

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

### Nguong va cua so rate-limit

- Cua so kiem soat: 10 phut.
- Nguong kich hoat cooldown: 3 lan gui trong cua so.
- Cooldown mac dinh: 15 phut.
- Scope ap nguong: uu tien theo account (neu da dang nhap).

### Chien luoc da tin hieu rui ro

- Tin hieu uu tien cao nhat: account.
- Khi chua dang nhap: cookie/session la tin hieu chinh, IP la tin hieu phu.
- Co che danh gia rui ro theo 3 muc: low / medium / high.
- Neu account sach nhung IP/cookie xau: tang rui ro nhung chua chuyen sang hard block ngay.

### Claude's Discretion

- Rule chi tiet cho monitor -> soft-enforce transition thresholds theo tung route.
- Noi dung thong diep UX cooldown/chuyen trang thai theo tone nhat quan he thong.
- Cach tinh trong so cu the trong risk score (while preserving locked priorities).
- Chien luoc retention va aggregate telemetry events phu hop SQLite hien tai.

### Deferred Ideas (OUT OF SCOPE)

- Adaptive friction nang cao (ABUS-05) va ML anomaly detection (ABUS-06) de Phase v2.
- Leaderboard integrity hardening thuoc Phase 5.
- UI redesign tong the va design-token rollout thuoc Phase 3.
</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ABUS-01 | He thong ap dung rule tan suat gui to cao theo cua so thoi gian de chan spam. | DB-backed sliding-window counter per actor key (10m window, 3-hit trigger), plus cooldown state persisted and queryable. |
| ABUS-02 | He thong danh gia rui ro dua tren da tin hieu (IP + cookie + account). | Canonical actor fingerprint with account-first priority, session reporter hash, normalized client IP, weighted risk score low/medium/high. |
| ABUS-03 | Trien khai monitor mode truoc, sau do soft-enforce theo nguong duoc cau hinh. | Feature flags in Config for mode switch, telemetry-only monitor path, then gated soft-enforce path with same signals. |
| ABUS-04 | Nguoi dung nhan thong bao cooldown/chuyen trang thai voi ly do ro rang. | Structured decision payload returned to template flash/context with reason code, remaining cooldown minutes, and next allowed time. |
</phase_requirements>

## Summary

Phase 2 should be implemented as a route-integrated anti-abuse decision layer on top of the existing POST flow in `routes/scammer.py`. The current route already has the right insertion point before DB write, already computes reporter anonymity via `hash_reporter_id(session['reporter_id'])`, and already supports friction escalation patterns (Turnstile + math fallback). This means Phase 2 can be delivered without major refactor if we add one anti-abuse service and persistence tables.

For this brownfield Flask app, monitor-first should not rely on in-memory counters only. Monitor decisions and actor signal snapshots must persist in SQLite so thresholds can be tuned from real data and survive process restart. Soft-enforce should reuse existing UX primitives (flash + re-render/redirect) and existing challenge affordances (Turnstile/math) rather than introducing hard blocks.

The strongest implementation path is: add anti-abuse models + service, call it from `routes/scammer.py` pre-write, store every decision event, and switch behavior by config mode (`monitor`, `soft_enforce`). This directly matches ABUS-01..04 and the locked account/cookie/IP priority.

**Primary recommendation:** Use a DB-backed anti-abuse service with config-gated monitor -> soft-enforce progression, integrated at POST `/scammer/report` before write and reusing reporter hash/session identity.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.0.3 (current in repo), 3.1.3 (latest verified) | Request lifecycle, route hooks, session access | Existing platform; anti-abuse check naturally fits view pre-write stage. |
| Flask-SQLAlchemy | 3.1.1 (repo) | ORM for telemetry/cooldown tables | Existing persistence layer; avoids split data path. |
| SQLite | app DB at `database/mindguard_v2.db` | Persistent counters/decisions for monitor-first telemetry | Required for monitor observability and restart safety. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Flask-Limiter | 4.1.1 (latest verified, 3.5.1 installed) | Coarse route-level rate gates | Optional safety rail if you need declarative per-route cap while keeping custom risk engine. |
| limits | 5.8.0 (latest verified) | Backend limiter strategies used by Flask-Limiter | Only when Flask-Limiter is enabled. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pure DB custom counters | Flask-Limiter only | Faster to wire, but does not model multi-signal risk scoring or monitor telemetry richness by itself. |
| Flask-Limiter memory storage | Redis-backed limiter storage | Better multi-instance correctness, but out-of-scope infra for this phase and current SQLite architecture. |

**Installation:**

```bash
pip install Flask-Limiter
```

**Version verification:**

```bash
python -m pip index versions Flask-Limiter
python -m pip index versions limits
python -m pip index versions Flask
python -m pip index versions SQLAlchemy
```

Verified today:

- Flask-Limiter latest 4.1.1
- limits latest 5.8.0
- Flask latest 3.1.3
- SQLAlchemy latest 2.0.48

## Architecture Patterns

### Recommended Project Structure

```
services/
  anti_spam.py                # Decision engine + scoring + cooldown calculation
models/
  models.py                   # AntiSpamEvent, AntiSpamActorState models
database/
  migrate_anti_spam_phase2.py # Manual migration script using app.app_context()
routes/
  scammer.py                  # Pre-write anti-abuse check integration point
templates/
  report_scammer.html         # Cooldown/status messages (Vietnamese UX)
tests/
  abuse/
    test_monitor_mode.py
    test_soft_enforce.py
    test_actor_priority.py
```

### Pattern 1: Pre-write Decision Gate in Report Route

**What:** Evaluate anti-abuse decision before report persistence.
**When to use:** Every POST `/scammer/report` submission.
**Example:**

```python
# Source: existing route orchestration pattern in routes/scammer.py + Flask view decorators docs
signals = anti_spam.collect_signals(session, request)  # account -> reporter_hash/cookie -> ip
result = anti_spam.evaluate("scammer.report", signals, now=datetime.utcnow())
anti_spam.record_event(result, signals)

if config.ABUS_MODE == "soft_enforce" and result.should_cooldown:
    flash(result.user_message_vi, "warning")
    return render_template("report_scammer.html", cooldown_until=result.cooldown_until)
```

### Pattern 2: Actor Canonicalization With Locked Priority

**What:** Build one canonical actor key from multi-signal input (account first).
**When to use:** Every anti-abuse decision and aggregate query.
**Example:**

```python
# Priority from locked decisions
if account_id:
    actor_key = f"acct:{account_id}"
elif reporter_hash:
    actor_key = f"cookie:{reporter_hash}"
else:
    actor_key = f"ip:{normalized_ip}"
```

### Pattern 3: Monitor-first Feature Flagging

**What:** Same decision engine in both modes; mode controls enforcement only.
**When to use:** Phase rollout and threshold tuning.
**Example:**

```python
# monitor: always allow write, always log decision
# soft_enforce: block/cooldown only when rule hit
mode = current_app.config.get("ABUS_MODE", "monitor")
if mode == "monitor":
    return Decision(allow=True, monitor_only=True)
```

### Anti-Patterns to Avoid

- **Hard-block by IP only:** Violates ABUS-02 and creates false positives behind NAT/mobile networks.
- **In-memory-only monitor counters:** Data resets on restart, breaking monitor-first learning.
- **Divergent monitor vs enforce logic:** Creates rollout surprises; keep one decision function.
- **Enforcing after DB write:** Too late for ABUS-01/04; cooldown message should happen before persistence.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Route-level fixed-window parsing | Custom string parser for rate syntax | Flask-Limiter/limits syntax if using decorator limits | Removes parser bugs and gives known semantics. |
| Proxy/IP trust chain parsing | Ad-hoc header parsing everywhere | One normalization helper (single trusted source) | Prevents spoofing and inconsistent actor identity. |
| Audit-like event logging plumbing | Duplicate mini-logger in route | Service pattern similar to `services/sensitive_access_log.py` | Reuses established app pattern and request metadata capture. |

**Key insight:** Hand-rolled anti-abuse policy is unavoidable for multi-signal scoring, but infrastructure primitives (rate syntax, request metadata collection, logging service boundaries) should reuse established tools/patterns.

## Common Pitfalls

### Pitfall 1: Session Fragmentation

**What goes wrong:** Anonymous users rotate sessions/cookies and bypass per-cookie counters.
**Why it happens:** Sole reliance on session key without IP/account corroboration.
**How to avoid:** Always capture all available signals and keep account > cookie > IP priority while storing secondary signals for escalation.
**Warning signs:** Sudden spike of low-confidence events with many unique cookie IDs but same IP/User-Agent pattern.

### Pitfall 2: Wrong Client IP Attribution

**What goes wrong:** All traffic appears from proxy IP or spoofed header value.
**Why it happens:** Blind trust of `X-Forwarded-For` without deployment trust policy.
**How to avoid:** Centralize IP extraction policy and document trusted proxy behavior.
**Warning signs:** Nearly all events share one IP in production or show malformed header chains.

### Pitfall 3: Monitor Data Not Actionable

**What goes wrong:** Events logged but no rollups/threshold visibility, delaying soft-enforce tuning.
**Why it happens:** Storing raw events only, no actor state aggregates.
**How to avoid:** Persist both event log and actor aggregate state (hit_count_window, last_seen, active_cooldown_until).
**Warning signs:** Cannot answer "who would have been blocked" by query.

### Pitfall 4: UX Message Ambiguity

**What goes wrong:** Users see generic failure instead of clear cooldown reason and time.
**Why it happens:** Reusing generic validation flash messages.
**How to avoid:** Define reason codes -> Vietnamese message map with explicit remaining time.
**Warning signs:** Support feedback saying "khong biet vi sao bi chan".

## Code Examples

Verified patterns from official sources and current codebase:

### Flask Decorator/Guard Pattern

```python
# Source: https://flask.palletsprojects.com/en/stable/patterns/viewdecorators/
from functools import wraps
from flask import request

def anti_abuse_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # evaluate anti-abuse state here
        return f(*args, **kwargs)
    return decorated
```

### Flask-Limiter Route Limit (Optional)

```python
# Source: https://flask-limiter.readthedocs.io/en/stable/
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

@scammer_bp.route("/report", methods=["POST"])
@limiter.limit("3 per 10 minute")
def report_scammer():
    ...
```

### SQLite Upsert-style Aggregate Update (if needed)

```python
# Source: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
from sqlalchemy.dialects.sqlite import insert

stmt = insert(AntiSpamActorState).values(actor_key=actor_key, hit_count=1)
stmt = stmt.on_conflict_do_update(
    index_elements=["actor_key"],
    set_={"hit_count": AntiSpamActorState.hit_count + 1}
)
db.session.execute(stmt)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-signal IP blocking | Multi-signal + progressive friction | Widely standardized by anti-abuse systems in recent years | Lower false-positive risk and better explainability. |
| Immediate hard-block | Monitor-first then soft-enforce | Modern rollout practice for risk systems | Safer production rollout and threshold tuning from telemetry. |
| In-memory counters only | Persistent telemetry + aggregate state | Standard for auditable abuse controls | Enables post-hoc analysis and deterministic cooldown behavior. |

**Deprecated/outdated:**

- IP-only trust decisions: high collateral damage in shared networks.
- Non-persistent monitor telemetry: not enough for phase transition decisions.

## Open Questions

1. **Trusted proxy topology for production IP extraction**
   - What we know: current code uses `request.remote_addr` in most places and one `X-Forwarded-For` fallback in sensitive access logging.
   - What's unclear: deployment trust boundary (direct app vs reverse proxy chain).
   - Recommendation: lock one extraction policy in Phase 2 plan and validate in staging before tuning IP weights.

2. **Operational toggle owner for monitor -> soft_enforce**
   - What we know: config-driven flags fit existing pattern in `config.py`.
   - What's unclear: who/when flips mode in release process.
   - Recommendation: define explicit checklist gate tied to telemetry thresholds.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | unittest (stdlib) + Flask test client |
| Config file | none - discover-based runner |
| Quick run command | `python -m unittest discover -s tests/privacy -p "test_*.py" -v` |
| Full suite command | `python -m unittest discover -s tests -p "test*.py" -v` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ABUS-01 | 10-minute window, 3-hit trigger sets cooldown | unit/service + route integration | `python -m unittest tests.abuse.test_soft_enforce.TestSoftEnforce.test_trigger_cooldown_after_3_hits -v` | ❌ Wave 0 |
| ABUS-02 | Risk score from account+cookie+IP with locked priority | unit/service | `python -m unittest tests.abuse.test_actor_priority.TestActorPriority.test_account_priority_over_cookie_ip -v` | ❌ Wave 0 |
| ABUS-03 | Monitor mode logs only; soft_enforce applies cooldown | integration | `python -m unittest tests.abuse.test_monitor_mode.TestMonitorMode.test_monitor_allows_but_logs -v` | ❌ Wave 0 |
| ABUS-04 | Cooldown/status UX message includes reason and remaining time | route/template integration | `python -m unittest tests.abuse.test_soft_enforce.TestSoftEnforce.test_user_receives_clear_cooldown_message -v` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python -m unittest discover -s tests/abuse -p "test_*.py" -v`
- **Per wave merge:** `python -m unittest discover -s tests -p "test*.py" -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/abuse/test_monitor_mode.py` - monitor-only decision behavior (ABUS-03)
- [ ] `tests/abuse/test_soft_enforce.py` - cooldown triggering and UX reason payload (ABUS-01, ABUS-04)
- [ ] `tests/abuse/test_actor_priority.py` - account/cookie/IP precedence and score tiering (ABUS-02)
- [ ] `tests/abuse/__init__.py` - package discovery consistency

## Sources

### Primary (HIGH confidence)

- Repository code and context files:
  - `routes/scammer.py`, `utils/encryption.py`, `services/sensitive_access_log.py`, `models/models.py`, `templates/report_scammer.html`
  - `.planning/phases/02-anti-spam-monitor-soft-enforce/2-CONTEXT.md`
  - `.planning/REQUIREMENTS.md`
- Flask-Limiter docs (stable): <https://flask-limiter.readthedocs.io/en/stable/>
- Flask official docs (view decorators): <https://flask.palletsprojects.com/en/stable/patterns/viewdecorators/>
- SQLAlchemy SQLite dialect docs (2.0): <https://docs.sqlalchemy.org/en/20/dialects/sqlite.html>

### Secondary (MEDIUM confidence)

- limits docs (stable): <https://limits.readthedocs.io/en/stable/>

### Tertiary (LOW confidence)

- None

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - validated against current repo and official docs; versions checked via pip index.
- Architecture: HIGH - directly mapped to existing `routes/scammer.py` orchestration and phase constraints.
- Pitfalls: MEDIUM-HIGH - confirmed by current code patterns, with one deployment-specific uncertainty (proxy trust).

**Research date:** 2026-03-20
**Valid until:** 2026-04-19
