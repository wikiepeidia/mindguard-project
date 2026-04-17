---
phase: 27-smtp-qa-production-verification
plan: 02
subsystem: otp-production-validation
tags: [otp, smtp, vercel, production, evidence]

requires:
  - phase: 27-smtp-qa-production-verification
    provides: Production schema aligned with the live OTP and anti-spam paths
provides:
  - Protected production smoke evidence for register and resend
  - Milestone tracking updates marking v1.5 complete
  - Repo memory notes for future protected Vercel smoke and migration work
affects: []

tech-stack:
  added: []
  patterns: [Protected Vercel smoke via stepwise vercel curl, production evidence capture, milestone closeout]

key-files:
  created: [.planning/phases/27-smtp-qa-production-verification/27-VALIDATION.md]
  modified: [.planning/PROJECT.md, .planning/REQUIREMENTS.md, .planning/ROADMAP.md, .planning/STATE.md, memories/repo/planning.md]

key-decisions:
  - "Protected Vercel smoke is recorded with explicit GET/POST steps instead of redirect-following POSTs."
  - "Phase 27 evidence includes both the cooldown redirect and the later resend-success redirect so the live guardrail behavior stays visible."

patterns-established:
  - "For this repo, production smoke against protected deployments should use `vercel curl` with manual redirect control and cookie reuse."
  - "Milestone closeout should record schema blockers uncovered during production smoke, not just the final green state."

requirements-completed: [SMTPQ-03]

duration: 35min
completed: 2026-04-17
---

# Phase 27 Plan 02 Summary

Captured the final Vercel production evidence for SMTP OTP and closed out the v1.5 milestone.

## Accomplishments

- Verified Production envs were set to `EMAIL_PROVIDER=smtp` with the Gmail mailbox sender path.
- Confirmed the protected production register flow redirects to `/verify-otp` for a real Gmail plus-alias on the configured mailbox.
- Confirmed immediate resend returns the expected cooldown redirect instead of crashing.
- Reused the same live verify session after cooldown and confirmed resend succeeds with a `302` back to `/verify-otp` plus the success notice.
- Updated milestone tracking so `SMTPQ-03` and Phase 27 are complete.
- Added repo memory capturing the operational lessons from this protected production smoke.

## Task Commits

Pending final closeout commit.

## Verification

- Protected production smoke on `mindguard-five.vercel.app` via `vercel curl` with cookie reuse, CSRF parsing, and browser-style GET/POST steps.
- `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -q`

## Self-Check: PASSED
