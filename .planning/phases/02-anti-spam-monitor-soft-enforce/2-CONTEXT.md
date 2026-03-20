# Phase 2: Anti-Spam Monitor & Soft Enforce - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase nay trien khai ABUS-01, ABUS-02, ABUS-03, ABUS-04 theo huong monitor truoc va soft-enforce sau tren luong gui to cao. Muc tieu la giam spam/gian lan ma khong gay false-positive qua muc, dong thoi cung cap thong diep cooldown/chuyen trang thai ro rang cho nguoi dung.

</domain>

<decisions>
## Implementation Decisions

### Nguong va cua so rate-limit
- Cua so kiem soat: 10 phut.
- Nguong kich hoat cooldown: 3 lan gui trong cua so.
- Cooldown mac dinh: 15 phut.
- Scope áp nguong: uu tien theo account (neu da dang nhap).

### Chien luoc da tin hieu rui ro
- Tín hiệu uu tien cao nhat: account.
- Khi chua dang nhap: cookie/session la tin hieu chinh, IP la tin hieu phu.
- Co che danh gia rui ro theo 3 muc: low / medium / high.
- Neu account sach nhung IP/cookie xau: tang rui ro nhung chua chuyen sang hard block ngay.

### Claude's Discretion
- Rule chi tiet cho monitor -> soft-enforce transition thresholds theo tung route.
- Noi dung thong diep UX cooldown/chuyen trang thai theo tone nhat quan he thong.
- Cach tinh trong so cu the trong risk score (while preserving locked priorities).
- Chien luoc retention va aggregate telemetry events phu hop SQLite hien tai.

</decisions>

<specifics>
## Specific Ideas

- Uu tien han che false-positive thay vi chan gat ngay.
- Co che anti-spam phai de nhin, de ly giai, khong gay kho cho user hop le.
- Van giu huong monitor-first de co du telemetry truoc khi soft-enforce manh hon.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product and phase scope
- `.planning/PROJECT.md` - Product priorities and constraints.
- `.planning/REQUIREMENTS.md` - ABUS-01, ABUS-02, ABUS-03, ABUS-04.
- `.planning/ROADMAP.md` - Phase 2 goal and success criteria.
- `.planning/STATE.md` - Current progress and session continuity.
- `.planning/phases/01-privacy-data-governance-foundation/1-CONTEXT.md` - Prior governance decisions that Phase 2 must preserve.

### Existing anti-abuse touchpoints
- `routes/scammer.py` - Main report submission flow and current reporter/session handling.
- `routes/auth.py` - Existing captcha/turnstile fallback pattern reusable for anti-abuse escalation.
- `utils/encryption.py` - Existing reporter hashing utility (`hash_reporter_id`).
- `utils/helpers.py` - Current shared helper patterns for route-level guards.
- `models/models.py` - Current schema constraints and existing fields usable for anti-spam linking.
- `templates/report_scammer.html` - User-facing report flow where cooldown/challenge messages are surfaced.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `hash_reporter_id(...)` trong `utils/encryption.py` da ton tai, co the dung lam actor signal bo sung.
- Session-based reporter identity (`session['reporter_id']`) da duoc tao trong `routes/scammer.py`.
- Turnstile + math fallback pattern da san o `routes/auth.py` va `routes/scammer.py`, phu hop cho step-up challenge.

### Established Patterns
- Route handlers dang la noi orchestration chinh cho validation/captcha/db write.
- Du an uu tien fallback behavior thay vi hard-fail khi external check gap loi.
- Manual migration script la pattern bat buoc khi them bang/cot phuc vu anti-spam telemetry.

### Integration Points
- Diem enforce chinh: `POST /scammer/report` trong `routes/scammer.py`.
- Diem message UX: `templates/report_scammer.html` + flash/response context.
- Diem theo doi admin: mo rong tiep tu admin governance page/route pattern vua co o Phase 1.

</code_context>

<deferred>
## Deferred Ideas

- Adaptive friction nang cao (ABUS-05) va ML anomaly detection (ABUS-06) de Phase v2.
- Leaderboard integrity hardening thuoc Phase 5.
- UI redesign tong the va design-token rollout thuoc Phase 3.

</deferred>

---
*Phase: 02-anti-spam-monitor-soft-enforce*
*Context gathered: 2026-03-20*
