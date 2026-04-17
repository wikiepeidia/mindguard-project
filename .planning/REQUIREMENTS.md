# Requirements: MindGuard v2

**Defined:** 2026-04-17
**Milestone:** v1.5 Vercel-Compatible OTP Mail Pivot
**Core Value:** Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.

## v1 Requirements (Milestone v1.5)

### SMTP Provider Core (SMTPP)

- [x] **SMTPP-01**: User receives OTP email through a generic SMTP provider path that can run on Vercel without a verified custom sending domain.
- [x] **SMTPP-02**: OTP delivery supports config-driven SMTP auth + TLS/SSL settings and normalizes send outcomes (`sent`, `misconfigured`, `provider_rejected`, `network_error`, `timeout`).
- [x] **SMTPP-03**: If SMTP sender or credentials are invalid, OTP issue/resend fails closed and does not activate or corrupt pending account state.

### Auth Flow Compatibility (SMTPC)

- [x] **SMTPC-01**: Register flow still issues OTP and redirects to verify page successfully when SMTP delivery succeeds.
- [x] **SMTPC-02**: Resend flow uses the same SMTP delivery path and preserves the current challenge/session when send fails.
- [x] **SMTPC-03**: Existing resend cooldown, verify lockout, session continuity, and abuse guardrails remain intact after the provider swap.

### Operations & Vercel Config (SMTPO)

- [x] **SMTPO-01**: SMTP credentials and sender settings are environment-first, with Vercel environment variables as the production source of truth and optional local JSON fallback only for local development.
- [x] **SMTPO-02**: Operators have a clear, tested production config contract for Gmail App Password and generic SMTP providers, including readiness diagnostics that distinguish misconfiguration from transient send failures.

### QA & Cutover (SMTPQ)

- [x] **SMTPQ-01**: Unit tests cover SMTP configuration validation and normalized send-result mapping.
- [x] **SMTPQ-02**: Route/integration tests cover register/resend SMTP success and failure branches without weakening OTP security behavior.
- [x] **SMTPQ-03**: Production cutover evidence proves the SMTP OTP path works on Vercel with a real mailbox account.

## v2 Requirements (Deferred)

### Provider Expansion

- **SMTPX-01**: Add backup-provider failover and retry queue once the primary SMTP cutover is stable.
- **SMTPX-02**: Reintroduce Resend or another API provider only after the team controls a verified sending domain.
- **SMTPX-03**: Add operator dashboard metrics for OTP delivery, bounce, and retry health.

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Buying/verifying a custom sending domain for Resend | This milestone exists specifically because the team cannot depend on domain ownership right now |
| Multi-provider failover or background retry queue | Higher complexity than needed for the immediate provider pivot |
| Non-OTP transactional email expansion | Milestone is limited to unblocking OTP delivery only |
| Full auth architecture refactor | Existing OTP/session/security behavior should stay intact |

## Traceability

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| SMTPP-01 | Phase 25 | Complete |
| SMTPP-02 | Phase 25 | Complete |
| SMTPP-03 | Phase 25 | Complete |
| SMTPO-01 | Phase 25 | Complete |
| SMTPC-01 | Phase 26 | Complete |
| SMTPC-02 | Phase 26 | Complete |
| SMTPC-03 | Phase 26 | Complete |
| SMTPO-02 | Phase 26 | Complete |
| SMTPQ-01 | Phase 25 | Complete |
| SMTPQ-02 | Phase 26 | Complete |
| SMTPQ-03 | Phase 27 | Complete |

**Coverage:**

- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✅

---
*Requirements defined: 2026-04-17*
*Last updated: 2026-04-17 after Phase 27 completed protected Vercel production smoke, schema repairs, and SMTP cutover evidence capture*
