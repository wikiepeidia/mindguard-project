# Milestone v1.5 SMTP Pivot Research Summary

Date: 2026-04-17  
Scope: Replace Resend-specific OTP delivery with a Vercel-compatible SMTP path that does not require a verified custom sending domain.

## 1) Stack additions for v1.5

- Reuse `Flask-Mail` as the generic SMTP transport instead of introducing a new mail library.
- Extend `config.py` with provider-neutral SMTP keys such as `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `SMTP_USE_SSL`, and `SMTP_FROM_EMAIL`.
- Keep `services/otp_email_delivery.py` as the normalized delivery boundary, but add a generic SMTP branch beside the current Resend branch.
- Support Gmail App Password as the immediate operational path; Google requires 2-Step Verification before an app password can be created.
- Keep the auth routes thin and preserve current resend/session/guardrail behavior while swapping the transport.

## 2) Table-stakes feature shortlist

- OTP can be sent through generic SMTP on Vercel without owning a custom sending domain.
- Gmail App Password and generic SMTP providers can be configured entirely via environment variables.
- Register and resend keep the same user-visible OTP flow and fail closed if delivery fails.
- Operators can tell the difference between bad config and transient provider/network failures.
- SMTP-specific unit, route, and production smoke evidence exists before cutover is considered complete.

## 3) Key architecture decisions

- Delivery transport should remain behind `services/otp_email_delivery.py`; routes should not know whether transport is Resend or SMTP.
- `Flask-Mail` should be initialized from standard Flask config before use, rather than hand-rolling raw SMTP handling.
- Gmail App Password is the immediate compatibility path, but the config contract should stay generic enough for Outlook/Brevo/other SMTP providers later.
- The milestone should pivot provider transport only; OTP security, resend policy, abuse limits, and session lifecycle stay unchanged.

## 4) Top pitfalls and mitigations

| Pitfall | Why it is risky here | Mitigation for v1.5 |
|---|---|---|
| Assuming `vercel.app` counts as a sending domain | Resend requires a domain you own, so the current production path remains blocked | Stop planning around Resend domain verification and move to mailbox-based SMTP |
| Gmail app password missing or unsupported | Gmail SMTP will reject login without 2-Step Verification and a valid app password | Treat Gmail setup as explicit operator prerequisite and document it in readiness checks |
| TLS/SSL config mismatch | Port/TLS confusion can produce false "provider down" diagnoses | Keep config explicit (`MAIL_USE_TLS` vs `MAIL_USE_SSL`) and validate before sending |
| Secrets leaking in config or logs | Mail credentials are sensitive and easy to mishandle during debugging | Environment-only secrets, redact logs, fail closed on misconfiguration |
| SMTP cutover regressing OTP behavior | Provider swap could silently break resend/session/lockout flows | Keep auth route contract stable and require focused regression coverage before release |

## 5) Recommended provider strategy

| Stage | Provider choice | Transport | Practical intent |
|---|---|---|---|
| Immediate unblock | Gmail mailbox with App Password | SMTP | Works on Vercel without owning a sending domain |
| Short-term alternative | Generic SMTP account (Outlook/Brevo/etc.) | SMTP | Same adapter contract, different mailbox/provider |
| Future growth | Revisit API provider after domain ownership exists | API or SMTP | Better deliverability and provider features once domain control is solved |

## 6) What to defer out of v1.5

- Resend custom-domain onboarding.
- Multi-provider failover or retry queues.
- Non-OTP transactional email features.
- Broader auth redesign beyond the mail transport pivot.

## Requirements input

Candidate requirement IDs:

- SMTPP-01: Send OTP through generic SMTP on Vercel without requiring a verified custom sending domain.
- SMTPP-02: Normalize SMTP send outcomes and keep config-driven TLS/SSL/auth settings.
- SMTPP-03: Fail closed on sender/credential misconfiguration.
- SMTPC-01: Keep register flow behavior stable under the SMTP transport.
- SMTPC-02: Keep resend flow behavior stable under the SMTP transport.
- SMTPC-03: Preserve resend/session/abuse-guardrail behavior while swapping transports.
- SMTPO-01: Load all SMTP secrets from environment variables only.
- SMTPO-02: Provide operator-facing readiness diagnostics and Gmail/generic SMTP config contract.
- SMTPQ-01: Add SMTP unit coverage.
- SMTPQ-02: Add SMTP route/integration coverage.
- SMTPQ-03: Record production smoke evidence on Vercel.
