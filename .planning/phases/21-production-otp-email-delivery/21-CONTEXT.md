# Phase 21: Production OTP Email Delivery - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Kich hoat gui OTP email that tren production cho luong dang ky/xac minh tai khoan, va xu ly ro rang khi gui OTP that bai.

Pham vi phase nay chi bao gom OTPMAIL-01, OTPMAIL-02, OTPMAIL-03:
- Gui OTP that qua provider da cau hinh.
- Neu gui that bai thi khong kich hoat tai khoan va thong bao huong dan thu lai ro rang.
- Tat ca credentials mail/OTP phai nap tu environment variables, khong hardcode secrets.

Khong mo rong sang resend UX/cooldown, outage fallback, abuse guardrails, hoac OTP QA full gate o phase nay.

</domain>

<decisions>
## Implementation Decisions

### Provider va Kenh Gui Mail
- **D-01:** Su dung Resend API lam provider chinh cho Phase 21.
- **D-02:** Tao service gui OTP qua HTTP API (Resend) va de route auth chi goi qua service; khong goi truc tiep provider trong route.

### Failure Handling (OTPMAIL-02)
- **D-03:** Dang ky chi duoc xem la hoan tat khi email OTP gui thanh cong. Neu gui that bai, khong tao tai khoan active, khong dat `registration_email` vao session dang nhap.
- **D-04:** Neu gui OTP that bai, hien thong bao tieng Viet ro rang cho nguoi dung (thu lai sau it phut / kiem tra cau hinh mail), khong lo chi tiet nhay cam tu provider.
- **D-05:** Chinh sach retry cho gui OTP: toi da 1 lan retry trong cung request (tong cong 2 lan gui), moi lan gui timeout ngan (mac dinh 5 giay) de phu hop serverless.

### Runtime Config va Secrets (OTPMAIL-03)
- **D-06:** Mail credentials phai lay tu environment variables tren runtime production: `EMAIL_PROVIDER`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`.
- **D-07:** Khong su dung credentials hardcoded hoac fallback plaintext trong code. Neu thieu bien moi truong bat buoc, he thong fail closed cho OTP send va tra thong bao huong dan ro rang.

### Noi dung Email OTP
- **D-08:** Email OTP toi thieu phai co: ma OTP, thong tin hieu luc ngan (TTL), va canh bao an toan "khong chia se OTP".
- **D-09:** Ban plain-text la bat buoc; HTML la tuy chon (the agent co the bo sung neu khong lam phuc tap hoa phase).

### the agent's Discretion
- Dat ten subject email cu the va dinh dang noi dung chi tiet (mien la giu dung D-08).
- Lua chon muc logging chi tiet (chi log challenge/provider status, khong log OTP plaintext).
- Vi tri dat service file gui mail (`services/` hoac `utils/`) mien nhat quan pattern codebase.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope va Requirement Nguon
- `.planning/ROADMAP.md` — Scope, goal, success criteria cua Phase 21.
- `.planning/REQUIREMENTS.md` — Requirement IDs OTPMAIL-01/02/03 va traceability milestone.
- `.planning/PROJECT.md` — Constraints production (Vercel + env-only secrets + khong hardcode).

### Existing OTP/Auth Flow
- `routes/auth.py` — Register/verify flow, `issue_otp_challenge`, va TODO send OTP email.
- `templates/verify_otp.html` — Verify UX hien tai va thong diep nguoi dung.
- `utils/otp_security.py` — OTP challenge/verify policy da duoc hardening o Phase 20.

### Mail Integration Hien Co
- `extensions.py` — `mail = Mail()` da ton tai (co the giu lai cho fallback tuong lai, khong la duong chinh cua phase nay).
- `app.py` — startup wiring hien co de doi chieu integration points.
- `config.py` — Noi dat env config key cho OTP va bo sung `EMAIL_PROVIDER`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`.
- `.env/RESEND.json` — Local secret artifact (khong dung lam source of truth production).

### Research Notes Lien Quan
- `.planning/research/FEATURES.md` — Feature table stakes cho OTPMAIL.
- `.planning/research/PITFALLS.md` — Pitfall OTP-P5 (mail delivery chua wired production).
- `.planning/research/STACK.md` — Env contract va stack constraints cho OTP delivery.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `extensions.py` + `app.py`: Co san integration layer de dat fallback SMTP neu can o phase sau.
- `routes/auth.py`: Register flow da issue challenge va luu `pending_otp_challenge_id`, chi con thieu step gui email OTP that.
- `utils/otp_security.py`: Da co challenge lifecycle (TTL/attempt/lockout/single-use) nen Phase 21 tap trung vao delivery.
- `requests`: da duoc su dung san trong auth routes, co the tai su dung cho Resend API client.

### Established Patterns
- Blueprint auth dang xu ly toan bo register/verify flow trong `routes/auth.py`.
- Session contract da co key `pending_registration`, `pending_otp_challenge_id`, `pending_verification_email`.
- Flash messages tieng Viet la pattern UX thong nhat cho auth flow.

### Integration Points
- Diem chen gui mail: ngay sau `issue_otp_challenge(...)` trong register flow.
- Diem fail handling: register POST branch truoc redirect den verify page.
- Diem config: bo sung `EMAIL_PROVIDER`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL` vao `Config`.

</code_context>

<specifics>
## Specific Ideas

- Uu tien huong di nhanh va on dinh cho production: Resend API (transactional email) de giam rui ro SMTP quota/relay drift.
- Message toi nguoi dung khi send fail phai de hieu va co hanh dong tiep theo, nhung khong lo stack trace/provider internals.
- Cac log van hanh nen gan challenge id va email da mask (neu can), tuyet doi khong ghi OTP plaintext.

</specifics>

<deferred>
## Deferred Ideas

- Failover da provider (primary/backup auto-switch) va outage queue processing.
- Resend OTP cooldown/countdown UX va resend endpoint contract.
- OTP abuse guardrails (route-level + challenge-level throttling phoi hop anti-spam telemetry).
- OTP QA reliability gate toan dien (integration matrix + concurrent verify stress).

Nhung noi dung tren de danh cho cac phase tiep theo trong roadmap.

</deferred>

---

*Phase: 21-production-otp-email-delivery*
*Context gathered: 2026-04-15*