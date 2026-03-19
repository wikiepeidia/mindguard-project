# Feature Landscape

**Domain:** Cybersecurity education + anti-scam reporting web platform (brownfield)
**Researched:** 2026-03-19
**Scope focus:** Light mode UX consistency, 1-question-per-page quiz, reporter leaderboard, phone masking, spam rate limits, IP/cookie anti-abuse tracking
**Overall confidence:** MEDIUM

## Table Stakes

Features users expect in 2026 for this scope. Missing these makes the product feel untrustworthy or unfinished.

| Feature | Why Expected in 2026 | Complexity | Dependencies | Notes |
|---------|----------------------|------------|--------------|-------|
| Consistent light-mode visual system across key pages | This milestone explicitly prioritizes light mode UX; users expect consistent readability and interaction patterns across auth, quiz, reporting, and profile flows | Medium | Shared design tokens, base template harmonization, CSS cleanup | Must include contrast/a11y checks to avoid visual regressions |
| Staged quiz flow (1 question per page/screen) with progress indicator | Progressive/staged disclosure is a mature UX standard for reducing cognitive load and error rates in multi-step tasks | Medium | Quiz state persistence, next/prev controls, resume behavior, anti-refresh loss handling | Keep step count visible (progress bar + step text) to improve completion |
| Basic anti-abuse controls on report submission (rate limiting window + cooldown feedback) | Public report forms are abuse targets; throttling is baseline defense-in-depth for bot/spam reduction | Medium | Request fingerprinting, storage for counters, user feedback for limit hits | Should combine account/IP/device signals, not one signal only |
| Privacy-preserving display of sensitive reporter data (phone masking by default) | Privacy-by-default is expected for trust-sensitive reporting systems | Low | Existing reporter data fields, display helper/filter, admin override policy | Masking policy should be deterministic and consistent across all templates/APIs |
| Transparent report pathway and user guidance (what to report, what happens next) | Scam-awareness platforms are expected to include clear avoid/report/recover guidance and reporting clarity | Low | Static content blocks, reporting page copy, FAQ/help links | Improve trust by setting response expectations and safety disclaimers |
| Abuse monitoring telemetry (failed attempts, lockouts, suspicious bursts) | Logging and monitoring are baseline for abuse detection and operational security posture | Medium | Structured logs, basic dashboard counters, alert thresholds | Needed before tuning anti-abuse rules safely |

## Differentiators

Features that are not mandatory for MVP trust, but can make MindGuard distinctly stronger than generic scam-report forms.

| Feature | Value Proposition | Complexity | Dependencies | Notes |
|---------|-------------------|------------|--------------|-------|
| Reporter leaderboard with integrity rules | Gamifies positive reporting behavior and can increase recurring contributions | Medium | Reporter identity strategy, anti-fraud scoring, ranking job, moderation policy | Must include anti-gaming constraints (cooldowns, quality weighting, moderation penalties) |
| Credibility-weighted leaderboard scoring (quality over quantity) | Rewards useful reports instead of raw volume, reducing spam incentives | High | Report verification status, quality signals, score formula versioning | Better long-term than simple count-based ranking |
| Adaptive friction on report flow (step-up CAPTCHA/challenge only when risk rises) | Keeps honest users fast while increasing friction for likely abuse | High | Risk scoring service, IP/cookie/device signals, challenge UX | Start with rules; ML can be deferred |
| Contextual micro-learning during reporting ("why this looks like a scam" hints) | Converts reporting into immediate cybersecurity education, reinforcing platform mission | Medium | Scam taxonomy/content snippets, UI slots in report steps | Strong mission fit and retention benefit |
| Privacy control transparency panel (what is tracked and why) | Increases user trust when using IP/cookie anti-abuse controls | Medium | Policy copy, consent/notice UX, data-retention rules | Must match actual implementation to avoid legal/trust risk |

## Anti-Features

Features to explicitly avoid in this milestone because they create risk, bloat, or misalignment.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Raw phone number exposure in public/admin list views by default | Violates privacy expectations and increases doxxing risk | Default mask all but last 2-3 digits; reveal only for authorized moderation actions |
| Count-only leaderboard without anti-gaming | Encourages spam submissions and degrades data quality | Use quality-weighted points + moderation/verified status gating |
| Hard block based on IP alone | Shared/mobile networks can cause false positives and user lockout | Use multi-signal controls (IP + cookie/device + account + behavior window) |
| Permanent lockout after burst behavior | Punishes legitimate users and increases support burden | Use progressive cooldowns, clear retry timers, and appeal/support path |
| Multi-goal page redesign during this milestone (navigation, IA, branding overhaul together) | Brownfield risk is high; scope explosion can delay security-critical fixes | Limit UX changes to light-mode consistency and quiz/report interaction contracts |
| Heavy bot-management platform dependency before baseline telemetry exists | Premature complexity and vendor lock-in without signal quality | Implement rule-based baseline first; add managed bot tooling after metrics prove need |

## Feature Dependencies

```text
Design token cleanup -> Light-mode consistency
Quiz state contract -> 1-question-per-page flow -> Progress analytics
Report submit telemetry -> Rate limiting rules -> Adaptive friction
Reporter identity normalization -> Masking policy -> Leaderboard integrity
Moderation outcomes -> Quality scoring -> Credibility-weighted leaderboard
```

## Dependency Notes By Target Change

| Target Change | Upstream Dependency | Downstream Effect | Risk if Skipped |
|---------------|---------------------|-------------------|-----------------|
| Light mode UX consistency | Shared style tokens + base template cleanup | Faster UI iteration and fewer per-page CSS hacks | Ongoing UI drift and regression churn |
| 1-question-per-page quiz | Persistent quiz session state | Better completion tracking and lower user drop-off | Lost answers/back navigation bugs |
| Reporter leaderboard | Anti-abuse + moderation signals | Healthy engagement loop | Rapid leaderboard manipulation |
| Phone masking | Unified formatter for template/API output | Privacy consistency across surfaces | Data leakage and trust erosion |
| Spam rate limits | Event counters + cooldown storage | Reduced automated spam load | High false negatives and DB noise |
| IP/cookie anti-abuse tracking | Fingerprinting schema + retention policy | Better abuse detection precision | False positives from single-signal blocking |

## MVP Recommendation (for this subsequent milestone)

Prioritize:

1. Light mode UX consistency (table-stake trust and usability baseline)
2. 1-question-per-page quiz with progress and safe state handling
3. Spam rate limits + IP/cookie-aware anti-abuse baseline
4. Phone masking everywhere reporter data is rendered

Then add:
5. Reporter leaderboard (gated by integrity safeguards)
6. Contextual micro-learning hints in report flow

Defer:

- Full adaptive friction engine with advanced risk scoring: defer until telemetry quality is validated for at least one release cycle.
- Complex ML-based bot classification: defer until rule-based false-positive/false-negative patterns are measured.

## 2026 Classification Summary

- Table-stakes for this scope in 2026: UX consistency, staged quiz flow, privacy-by-default masking, baseline anti-abuse throttling, transparent report guidance.
- Differentiators in 2026: integrity-aware leaderboard, adaptive friction, reporting-as-learning, transparency controls that explain anti-abuse tracking.
- Anti-features in 2026: raw PII display, simplistic engagement mechanics that reward spam, and one-signal blocking policies.

## Confidence Notes

| Area | Confidence | Why |
|------|------------|-----|
| UX staged flow and quiz segmentation | MEDIUM | Strong UX guidance exists; source is older NN/g article but still broadly accepted design practice |
| Rate-limiting / anti-abuse baseline | HIGH | Supported by current OWASP 2026 cheat-sheet guidance and Cloudflare 2026 docs |
| Privacy masking/default minimization | MEDIUM | Supported by OWASP privacy principles; exact masking convention is product-policy dependent |
| Leaderboard gamification guidance | LOW-MEDIUM | Mostly product reasoning + abuse-prevention best practice, limited official prescriptive standard |

## Sources

- OWASP Authentication Cheat Sheet (2026): <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>
- OWASP User Privacy Protection Cheat Sheet (2026): <https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html>
- Cloudflare Learning Center, What is rate limiting? (2026): <https://www.cloudflare.com/learning/bots/what-is-rate-limiting/>
- FTC Consumer Scams hub (2026 updates visible): <https://consumer.ftc.gov/scams>
- Nielsen Norman Group, Progressive Disclosure (classic, still relevant): <https://www.nngroup.com/articles/progressive-disclosure/>

## Research Limits

- The CISA page request returned 403 from the fetch tool.
- FTC extracts are list-level guidance and alerts; not a detailed product spec source.
- No Context7 endpoint is available in this runtime, so confidence is adjusted accordingly.
