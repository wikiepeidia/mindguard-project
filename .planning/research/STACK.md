# Technology Stack Recommendation (2026)

**Project:** MindGuard v2 (brownfield Flask monolith)  
**Scope:** UX light-mode overhaul, per-question quiz flow, reporter leaderboard, privacy masking, anti-spam / anti-fraud controls  
**Researched:** 2026-03-19

## Executive Recommendation

Giữ **Flask monolith + Jinja + Bootstrap** làm trục chính. Khong doi sang microservices, khong doi framework frontend.  
Huong toi uu cho scope nay la:

1. **Nang cap in-place** tren Flask 3.x va Flask-SQLAlchemy 3.x.
2. **Them Redis** lam tang bo nho chia se cho rate limit, anti-spam counters, lock nhe, queue nhe.
3. **Giu SQLite cho mốc nay** neu traffic vua/nhỏ, nhung chuan bi migration path sang PostgreSQL khi leaderboard/report growth tang nhanh.
4. **Chong gian lan theo pipeline** (Turnstile + rate limit + dedupe + risk scoring + moderation queue), thay vi chi 1 lop CAPTCHA.

## Current vs Recommended

| Layer | Current repo | Recommended 2026 (compatible upgrade) | Why |
|---|---|---|---|
| Web framework | Flask 3.0.3 | Flask 3.1.x line | Ban stable docs hien tai da o 3.1.x, giu compatibility cao |
| ORM | Flask-SQLAlchemy 3.1.1 | Flask-SQLAlchemy 3.1.x + SQLAlchemy 2.0 style incrementally | Dung huong docs official, khong can rewrite model |
| DB | SQLite file | SQLite + schema/index tuning ngay; add migration path to PostgreSQL | Scope hien tai co leaderboard/rate events de phat sinh lock neu tang tai |
| Bot defense | Turnstile co ban | Turnstile + Flask-Limiter + Redis-backed counters + risk rules | Lop phong thu nhieu tang, can theo route va actor fingerprint |
| Background jobs | chua ro worker layer | RQ + Redis (lightweight) | Phu hop monolith, de tach tac vu nhe (score recompute, denormalize leaderboard) |
| Frontend | Bootstrap 5.3.0 + custom CSS/JS | Bootstrap 5.3.x + design tokens (CSS vars) + progressive enhancement JS | Dat muc tieu light-mode overhaul nhanh, khong can SPA migration |
| Security headers | thiet lap thu cong/chua ro day du | Header middleware tu code app (khuyen nghi custom) | Tranh phu thuoc extension cu, kiem soat ro CSP/nonce cho Jinja |

## Recommended Stack (Concrete)

### 1. Core App (keep monolith)

- `Flask` (3.1.x line)
- `Flask-SQLAlchemy` (3.1.x line)
- `Werkzeug` (3.1.x line)
- `Jinja2` (theo Flask dependency)

**Implementation note:**
- Khong can doi sang FastAPI/ASGI cho scope nay.
- Thuc hien update theo tung dependency batch nho, co regression test route auth/quiz/report.

### 2. Data + Persistence

- **Now (milestone nay):** SQLite van chay duoc, nhung bat buoc them index va constraints cho report/leaderboard.
- **Soon (phase tiep theo neu growth):** PostgreSQL 16+ cho write concurrency va analytics query.

**SQLite hardening checklist (ap dung ngay):**
- Bat `PRAGMA foreign_keys=ON` tren moi connection.
- Can nhac transaction mode non-legacy (Python 3.12+ `autocommit=False` at connect level) de tranh edge-case transactional DDL.
- Tao unique/index phuc vu:
  - report dedupe keys
  - leaderboard aggregates (reporter_id, created_at)
  - risk event lookup (ip_hash, device_hash, window bucket)
- Dung `ON CONFLICT DO UPDATE/DO NOTHING` cho counter/upsert cases.

### 3. Anti-Spam / Anti-Fraud

- `Flask-Limiter` (4.1.1 theo docs stable) + storage `redis://...`
- `redis` Python client (latest stable line)
- Cloudflare Turnstile (giu va nang cap server-side verification pipeline)

**Rate-limit key design (important):**
- Khong chi `remote_addr`.
- Dung composite key: `normalized_ip + session_id + device_cookie_hash + route_scope`.
- Neu deploy sau reverse proxy, bat buoc `ProxyFix` dung so hop proxy de tranh spoof `X-Forwarded-For`.

**Risk scoring inputs:**
- velocity (so report / 5m, 1h)
- duplicate content ratio
- fingerprint churn (1 cookie -> nhieu account, 1 IP -> nhieu account)
- Turnstile fail ratio

### 4. Background Jobs (lightweight)

- `rq` + Redis worker

**Use for:**
- recompute leaderboard denormalized table
- async dedupe similarity scoring
- delayed moderation escalation

**Why RQ over Celery here:**
- Scope vua/nhỏ, monolith-first, RQ setup don gian hon va du dung.

### 5. Privacy and Data Protection

- Keep existing `utils/encryption.py` direction, bo sung:
  - deterministic keyed hash (HMAC-SHA256) cho truong phuc vu dedupe/tracking
  - encrypted-at-rest cho raw sensitive payload (neu van luu)
- `phonenumbers` for E.164 normalization truoc khi mask/hash

**Masking policy for phone (requested):**
- Chi hien thi `*** *** XYZ` (3 so cuoi)
- Luu 2 cot logic:
  - `phone_masked` (display-safe)
  - `phone_hash` (dedupe/search, keyed)
- Khong log raw phone vao app logs

### 6. Frontend for Light-Mode Overhaul

- Keep Bootstrap 5.3.x
- Design system nhe bang CSS custom properties:
  - `--bg-default`, `--surface`, `--text-primary`, `--accent`, `--danger`
- Tach style theo page (`quiz.css`, `report.css`) nhu repo da co, khong nhung inline CSS/JS vao template.

**For per-question quiz flow:**
- Server-rendered multi-step route (`/quiz/<attempt_id>/<step>`)
- Session + DB state (attempt table) de support refresh/back safely
- Optional progressive enhancement JS cho transition, nhung logic chot diem o server

### 7. Observability and Abuse Ops

- Structured logging JSON (stdlib logging + formatter)
- Bao gom event types:
  - `report_submitted`
  - `report_rate_limited`
  - `report_risk_scored`
  - `report_auto_quarantined`
- Ban dau co the ghi file + DB event table; chua can ELK ngay.

## Explicit Cautions (Do / Do Not)

### Do

- Do them anti-spam theo **nhieu lop**: Turnstile + limiter + risk rules + moderation queue.
- Do apply `ProxyFix` dung cau hinh khi sau proxy, neu khong rate limit key se sai.
- Do giu migration script thu cong trong `database/` de dong bo convention repo hien tai.
- Do tao test cho abuse paths (burst submit, duplicate payload, IP rotation pattern).

### Do Not

- Do not dua he thong sang microservices o milestone nay.
- Do not dua vao memory limiter trong production (docs Flask-Limiter ghi ro memory storage chi cho dev/test).
- Do not dung extension security da lau khong cap nhat lam cot song (vd `flask-talisman` release cu 2019). Neu can headers, uu tien tu cau hinh middleware/response hook trong app.
- Do not luu PII raw vao leaderboard table.

## Upgrade/Additions List (Practical)

### Upgrade (existing)

- Flask: `3.0.3 -> 3.1.x`
- Werkzeug: `3.0.3 -> 3.1.x`
- requests: update to current stable patch line

### Add (new)

- `Flask-Limiter[redis]`
- `redis`
- `rq`
- `phonenumbers`
- `python-json-logger` (or equivalent) for structured logs

### Optional (phase 2)

- `psycopg[binary]` (khi bat dau PostgreSQL)
- `alembic` only if team doi chuan migration process; neu khong tiep tuc migration scripts thu cong theo convention hien tai

## Implementation Approach by Target Scope

1. **Light-mode UX overhaul**
- Introduce design token file trong `static/css/base.css`.
- Refactor page CSS de dong nhat contrast, spacing, typography.
- Keep Bootstrap utility-first approach de giam rewrite.

2. **Per-question quiz flow**
- Add `quiz_attempts` + `quiz_attempt_answers` tables.
- Track progress theo question index; autosave moi submit.
- Lock final scoring server-side sau question cuoi.

3. **Leaderboard for reporters**
- Add denormalized aggregate table (daily/weekly/all-time).
- Update via transactional write + async reconcile job (RQ).
- Chi hien thi identity da mask.

4. **Privacy masking**
- Normalize -> hash/encrypt -> mask pipeline khi ingest report.
- Expose chi masked fields o template/API.

5. **Anti-spam / anti-fraud controls**
- Route-level rate limits:
  - `/scammer/report` strict
  - auth routes medium
  - read routes lenient
- Risk scoring + threshold:
  - low -> accept
  - medium -> accept + queue review
  - high -> quarantine + require stronger challenge

## Confidence + Evidence

| Area | Confidence | Notes |
|---|---|---|
| Flask/Flask-SQLAlchemy upgrade direction | HIGH | Official Pallets stable docs/changelog lines |
| SQLite hardening details | HIGH | SQLAlchemy 2.0 SQLite dialect docs (2026 build) |
| Rate limiting stack | HIGH | Flask-Limiter official docs incl. Redis backend warning for memory storage |
| Turnstile integration direction | HIGH | Official Cloudflare Turnstile docs (updated Mar 2026) |
| RQ recommendation vs Celery for this scope | MEDIUM | Official RQ docs + monolith complexity fit |
| Flask security-header extension choice | MEDIUM | `flask-talisman` repo aging signal (release old), de-risk by custom headers |

## Sources

- Flask docs (stable): https://flask.palletsprojects.com/
- Flask deploy behind proxy: https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/
- Flask-SQLAlchemy docs: https://flask-sqlalchemy.readthedocs.io/en/stable/
- SQLAlchemy SQLite dialect (2.0 docs): https://docs.sqlalchemy.org/en/20/dialects/sqlite.html
- Alembic docs (context only): https://alembic.sqlalchemy.org/en/latest/
- Flask-Limiter docs: https://flask-limiter.readthedocs.io/en/stable/
- Cloudflare Turnstile docs: https://developers.cloudflare.com/turnstile/
- RQ docs: https://python-rq.org/
- Flask-WTF docs (CSRF option): https://flask-wtf.readthedocs.io/en/1.2.x/
- Flask-Talisman repository status check: https://github.com/GoogleCloudPlatform/flask-talisman
