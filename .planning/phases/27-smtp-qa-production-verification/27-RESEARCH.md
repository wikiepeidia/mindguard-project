# Phase 27: SMTP QA & Production Verification - Research

**Date:** 2026-04-17  
**Discovery Level:** Level 0  
**Status:** Applied

## Why Level 0

Phase 27 does not introduce a new dependency or a new provider. The work is live verification of the existing SMTP cutover, plus fixing production schema drift that the smoke uncovers.

## Findings

### Protected Vercel smoke must be done with authenticated requests

- The production aliases are deployment-protected, so anonymous `curl` or `requests` calls return the Vercel auth page.
- `vercel curl` works, but POST flows should be executed stepwise without `--location` on form posts because redirect replay can break CSRF-protected endpoints.

### Live production uncovered two schema drifts

- `POST /register` initially failed because the Neon production database did not yet have the `otp_challenges` table.
- After creating `otp_challenges`, `POST /verify-otp/resend` still failed because OTP abuse actor IDs (`otp:<sha256>`) exceeded the existing `VARCHAR(64)` width of `anti_spam_* .account_id` columns.

### The correct root fix is schema-width alignment, not actor-ID truncation

- OTP actor IDs are intentionally namespaced and should stay stable.
- Widening `anti_spam_events.account_id` and `anti_spam_actor_states.account_id` to `VARCHAR(128)` keeps the current anti-spam design intact and matches future-proofed actor shapes.

## Applied Approach

1. Pull the exact production error traces from `vercel logs`.
2. Run `database/migrate_otp_challenges.py` against the Production database sourced from `vercel env pull`.
3. Widen anti-spam `account_id` columns at the repo contract and migration level, then run the new migration against Production.
4. Re-run the protected production smoke until register, cooldown redirect, and resend success all behave as expected.

## Risks Left Intentionally Out of Scope

- Reading the live mailbox inbox contents or verifying the OTP code itself.
- Broader anti-spam schema refactors beyond the `account_id` width bug that broke resend.
- Replacing deployment protection or Cloudflare Turnstile behavior.
