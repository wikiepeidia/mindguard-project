# Phase 26: Auth Flow SMTP Cutover - Context

**Gathered:** 2026-04-17  
**Status:** Ready for planning and execution  
**Mode:** Autonomous single-phase execution

<domain>
## Phase Boundary

Use the SMTP provider core from Phase 25 in the real register/resend auth flows, then add operator-facing setup/readiness guidance for the free Gmail App Password path.

This phase covers:

- route-level SMTP cutover behavior for `/register` and `/verify-otp/resend`
- fail-closed compatibility for resend/session/challenge state during SMTP failures
- operator-facing diagnostics that distinguish misconfiguration from transient runtime failures
- a concrete free-SMTP setup checklist for this repo

This phase does not include production smoke or final go-live evidence. That stays in Phase 27.

</domain>

<decisions>
## Decisions

### Locked Decisions

- **D-01:** Keep auth routes transport-agnostic; they should keep calling `send_otp_email()` rather than inline SMTP code.
- **D-02:** Use Gmail App Password as the default free operator path documented for this milestone.
- **D-03:** Distinguish `misconfigured` from transient failures (`timeout`, `network_error`) in operator diagnostics without exposing raw config details to end users.
- **D-04:** Preserve existing resend/session/current-challenge behavior from Phases 22 to 24.

### the agent's Discretion

- Whether diagnostics surface through structured logging, helper functions, or both.
- Exact placement and wording of the free SMTP runbook in `TODO.mD`.

</decisions>

<code_context>
## Existing Code Insights

- `routes/auth.py` already routes register/resend through `send_otp_email()` and already fails closed on `ok=False`.
- `services/otp_email_delivery.py` now supports both `resend_api` and `smtp` based on config.
- `tests/test_otp_auth_integration.py` already proves generic resend/session behavior, but not the real SMTP branch selected by config.
- `TODO.mD` was empty and can serve as the operator-facing setup checklist requested by the user.

</code_context>

<specifics>
## Specific Ideas

- Patch `services.otp_email_delivery.mail.send` in route tests so SMTP-path register/resend behavior is exercised without a real network call.
- Log SMTP diagnostics with provider, category, and missing keys when delivery fails.
- Put the free Gmail setup steps directly in `TODO.mD` with exact env vars and failure-category guidance.

</specifics>

<deferred>
## Deferred Ideas

- Production SMTP smoke on Vercel.
- Final release evidence and go-live checklist.
- Backup SMTP providers or multi-provider failover.

</deferred>
