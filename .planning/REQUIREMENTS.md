# Requirements: MindGuard v2

**Defined:** 2026-04-14
**Milestone:** v1.4 OTP Email Reliability & QA
**Core Value:** Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.

## v1 Requirements (Milestone v1.4)

### OTP Security (OTPSEC)

- [x] **OTPSEC-01**: User receives a cryptographically random 6-digit OTP for each challenge, with no static fallback values.
- [x] **OTPSEC-02**: OTP is stored and compared as hash (salt/pepper), never persisted or logged in plaintext.
- [x] **OTPSEC-03**: When OTP is re-issued (resend/new challenge), previously active OTP is invalidated.

### OTP Email Delivery (OTPMAIL)

- [ ] **OTPMAIL-01**: User receives OTP email through configured provider in production (primary provider path enabled on Vercel).
- [ ] **OTPMAIL-02**: If OTP email send fails, user receives clear retry guidance and account is not activated.
- [ ] **OTPMAIL-03**: Mail/OTP provider credentials are loaded from environment variables only (no hardcoded secrets).

### OTP Outage Continuity (OTPOUT)

- [ ] **OTPOUT-01**: When primary email provider is unavailable, OTP delivery automatically fails over to configured backup provider without forcing user to restart registration.
- [ ] **OTPOUT-02**: If all delivery providers are unavailable, pending registration is preserved and placed into a retry queue for later resend when email service recovers.
- [ ] **OTPOUT-03**: For prolonged outage beyond retry policy, user can complete registration via a manual admin assist path with auditable handoff and secure verification controls.

### OTP Policy and Verification (OTPPOL)

- [x] **OTPPOL-01**: OTP is rejected after configurable TTL (default 5 minutes).
- [x] **OTPPOL-02**: Wrong OTP attempts are counted and temporary lockout is enforced after threshold.
- [x] **OTPPOL-03**: OTP verify is single-use and replay-safe (successful OTP cannot be reused).

### OTP Resend and Session Flow (OTPRES, OTPSES)

- [ ] **OTPRES-01**: User can request OTP resend from verify flow without re-submitting full registration.
- [ ] **OTPRES-02**: Resend enforces cooldown and resend cap per time window.
- [ ] **OTPSES-01**: Register -> verify session contract is stable on refresh; missing/expired pending state redirects user safely.

### Reliability and Abuse Controls (OTPREL)

- [ ] **OTPREL-01**: `/verify-otp` and resend endpoint are protected with route-level rate limits.
- [ ] **OTPREL-02**: OTP challenge-level throttling (cooldown/attempt lockout) works together with anti-spam telemetry.

### QA Coverage (OTPQA)

- [ ] **OTPQA-01**: Unit tests cover OTP generation, expiry, resend policy, lockout transitions.
- [ ] **OTPQA-02**: Route tests cover register -> OTP send -> verify success/failure branches.
- [ ] **OTPQA-03**: Integration tests mock mail-provider failure, outage recovery resend, and concurrent verify edge cases.

## v2 Requirements (Deferred)

### OTP Reliability and UX Extensions

- **OTPREL-03**: Active-active multi-provider routing and dynamic traffic balancing for OTP delivery at higher scale.
- **OTPOBS-01**: OTP delivery/verify observability dashboard with alert thresholds.
- **OTPUX-01**: Enhanced OTP input UX (split boxes, auto-paste handling, accessibility pass).

### Authentication Expansion

- **OTP2FA-01**: Add optional MFA methods (SMS OTP / authenticator app) after v1.4 stability.

## Out of Scope

| Feature | Reason |
|---------|--------|
| SMS OTP / authenticator MFA | Scope v1.4 focuses on stabilizing email OTP only |
| Full auth architecture refactor | High regression risk; not required to solve OTP reliability now |
| Celery/Redis distributed background queue stack | v1.4 only needs DB-backed retry queue for outage continuity |
| Active-active multi-provider routing with traffic balancing | Primary/backup failover is enough for v1.4 |
| Non-OTP feature expansion (notifications/social/gamification) | Not related to milestone goal |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OTPSEC-01 | Phase 20 | Complete |
| OTPSEC-02 | Phase 20 | Complete |
| OTPSEC-03 | Phase 20 | Complete |
| OTPMAIL-01 | Phase 21 | Pending |
| OTPMAIL-02 | Phase 21 | Pending |
| OTPMAIL-03 | Phase 21 | Pending |
| OTPOUT-01 | Phase 22 | Pending |
| OTPOUT-02 | Phase 22 | Pending |
| OTPOUT-03 | Phase 22 | Pending |
| OTPPOL-01 | Phase 20 | Complete |
| OTPPOL-02 | Phase 20 | Complete |
| OTPPOL-03 | Phase 20 | Complete |
| OTPRES-01 | Phase 23 | Pending |
| OTPRES-02 | Phase 23 | Pending |
| OTPSES-01 | Phase 23 | Pending |
| OTPREL-01 | Phase 24 | Pending |
| OTPREL-02 | Phase 24 | Pending |
| OTPQA-01 | Phase 25 | Pending |
| OTPQA-02 | Phase 25 | Pending |
| OTPQA-03 | Phase 25 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✅

---
*Requirements defined: 2026-04-14*
*Last updated: 2026-04-14 after user feedback added outage continuity requirements and dedicated fallback phase scope*
