# Phase 27: SMTP QA & Production Verification - Context

**Gathered:** 2026-04-17  
**Status:** Ready for execution and closeout  
**Mode:** Autonomous single-phase execution

<domain>
## Phase Boundary

Use a real Gmail mailbox account on the protected Vercel production deployment, prove the OTP SMTP flow works end to end, and close the v1.5 milestone with production evidence.

This phase covers:

- production Vercel env verification for the SMTP sender account
- protected production smoke for `/register` and `/verify-otp/resend`
- production log diagnosis when live smoke uncovers runtime/schema drift
- final evidence capture and milestone tracking updates for `SMTPQ-03`

This phase does not include:

- new provider features or multi-provider failover
- custom sending-domain setup for Resend
- broader auth redesign beyond what the live smoke forces us to fix

</domain>

<decisions>
## Decisions

### Locked Decisions

- **D-01:** Use the real protected Vercel production deployment as the smoke target; do not substitute local-only proof for production evidence.
- **D-02:** Use the configured Gmail App Password mailbox account already loaded into Production env vars as the source of truth.
- **D-03:** Phase 27 is only complete when evidence covers both register reaching `/verify-otp` and resend working after the real cooldown window.
- **D-04:** If production fails, diagnose and repair with Vercel logs plus manual repo migration scripts instead of weakening OTP guardrails.

### the agent's Discretion

- Exact scripting used for protected production smoke, as long as it preserves cookies, CSRF, and deployment protection requirements.
- Whether live blockers are fixed through new migrations, existing migrations, or both, provided the repo contract and production schema end aligned.

</decisions>

<code_context>

## Existing Code Insights

- `services/otp_email_delivery.py` and `routes/auth.py` already support the SMTP path from Phases 25 and 26.
- OTP production verification here is mostly operational, but live smoke can still reveal schema drift in Neon.
- The repo already has manual migration scripts and should keep using them instead of implicit runtime `create_all()` behavior.

</code_context>

<specifics>
## Specific Ideas

- Use `vercel curl` with explicit GET/POST steps, cookie jar reuse, and parsed CSRF tokens because deployment protection blocks anonymous HTTP access.
- If production errors surface, pull the exact trace with `vercel logs` and repair the live schema using idempotent manual migration scripts.
- Capture both the cooldown redirect and the later resend-success redirect so the evidence reflects real OTP guardrail behavior, not just a single happy-path POST.

</specifics>

<deferred>
## Deferred Ideas

- Provider failover or retry queue.
- Broader anti-spam schema cleanup beyond the production blocker required for Phase 27.
- More UX-level production checks outside the OTP cutover scope.

</deferred>
