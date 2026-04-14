# Requirements: MindGuard v2

**Defined:** 2026-04-14
**Milestone:** v1.4 OTP Email Reliability & QA
**Core Value:** Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.

## v1 Requirements (Milestone v1.4)

### OTP Security (OTPSEC)

- [ ] **OTPSEC-01**: User receives a cryptographically random 6-digit OTP for each challenge, with no static fallback values.
- [ ] **OTPSEC-02**: OTP is stored and compared as hash (salt/pepper), never persisted or logged in plaintext.
- [ ] **OTPSEC-03**: When OTP is re-issued (resend/new challenge), previously active OTP is invalidated.

### OTP Email Delivery (OTPMAIL)

- [ ] **OTPMAIL-01**: User receives OTP email through configured provider in production (primary provider path enabled on Vercel).
- [ ] **OTPMAIL-02**: If OTP email send fails, user receives clear retry guidance and account is not activated.
- [ ] **OTPMAIL-03**: Mail/OTP provider credentials are loaded from environment variables only (no hardcoded secrets).

### OTP Policy and Verification (OTPPOL)

- [ ] **OTPPOL-01**: OTP is rejected after configurable TTL (default 5 minutes).
- [ ] **OTPPOL-02**: Wrong OTP attempts are counted and temporary lockout is enforced after threshold.
- [ ] **OTPPOL-03**: OTP verify is single-use and replay-safe (successful OTP cannot be reused).

### OTP Resend and Session Flow (OTPRES, OTPSES)

- [ ] **OTPRES-01**: User can request OTP resend from verify flow without re-submitting full registration.
- [ ] **OTPRES-02**: Resend enforces cooldown and resend cap per time window.
- [ ] **OTPSES-01**: Register -> verify session contract is stable on refresh; missing/expired pending state redirects user safely.

### Reliability and Abuse Controls (OTPREL)

- [ ] **OTPREL-01**: `/verify-otp` and resend endpoint are protected with route-level rate limits.
- [ ] **OTPREL-02**: OTP challenge-level throttling (cooldown/attempt lockout) works together with anti-spam telemetry.

### QA Coverage (OTPQA)

- [ ] **OTPQA-01**: Unit tests cover OTP generation, expiry, resend policy, and lockout transitions.
- [ ] **OTPQA-02**: Route tests cover register -> OTP send -> verify success/failure branches.
- [ ] **OTPQA-03**: Integration tests mock mail-provider failure and concurrent verify edge cases.

## v2 Requirements (Deferred)

### OTP Reliability and UX Extensions

- **OTPREL-03**: Multi-provider failover policy for OTP email (automatic provider fallback).
- **OTPOBS-01**: OTP delivery/verify observability dashboard with alert thresholds.
- **OTPUX-01**: Enhanced OTP input UX (split boxes, auto-paste handling, accessibility pass).

### Authentication Expansion

- **OTP2FA-01**: Add optional MFA methods (SMS OTP / authenticator app) after v1.4 stability.

## Out of Scope

| Feature | Reason |
|---------|--------|
| SMS OTP / authenticator MFA | Scope v1.4 focuses on stabilizing email OTP only |
| Full auth architecture refactor | High regression risk; not required to solve OTP reliability now |
| Celery/Redis background queue for OTP | Added infra complexity not justified for current milestone |
| Active-active multi-provider routing | Premature optimization for current usage stage |
| Non-OTP feature expansion (notifications/social/gamification) | Not related to milestone goal |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OTPSEC-01 | Unassigned | Pending |
| OTPSEC-02 | Unassigned | Pending |
| OTPSEC-03 | Unassigned | Pending |
| OTPMAIL-01 | Unassigned | Pending |
| OTPMAIL-02 | Unassigned | Pending |
| OTPMAIL-03 | Unassigned | Pending |
| OTPPOL-01 | Unassigned | Pending |
| OTPPOL-02 | Unassigned | Pending |
| OTPPOL-03 | Unassigned | Pending |
| OTPRES-01 | Unassigned | Pending |
| OTPRES-02 | Unassigned | Pending |
| OTPSES-01 | Unassigned | Pending |
| OTPREL-01 | Unassigned | Pending |
| OTPREL-02 | Unassigned | Pending |
| OTPQA-01 | Unassigned | Pending |
| OTPQA-02 | Unassigned | Pending |
| OTPQA-03 | Unassigned | Pending |

**Coverage:**
- v1 requirements: 17 total
- Mapped to phases: 0
- Unmapped: 17 ⚠️

---
*Requirements defined: 2026-04-14*
*Last updated: 2026-04-14 after v1.4 requirement scoping from research output*
