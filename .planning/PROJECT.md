# MindGuard Web App Improvement Milestone

## What This Is

MindGuard is a Flask-based cybersecurity education and scam-reporting platform for Vietnamese users. The existing system already supports account flows, quiz learning, scam report intake, AI chatbot interactions, and admin moderation. This milestone focuses on improving user experience, UI quality, and reliability across those existing capabilities.

## Core Value

Users can quickly and confidently learn, report, and get guidance about scam risks through a reliable and easy-to-use web experience.

## Requirements

### Validated

- ✓ User can register, verify identity flow, and log in via session-based authentication — existing
- ✓ User can take quizzes and receive score/result experiences — existing
- ✓ User can submit scammer reports with validation and evidence upload support — existing
- ✓ User can interact with AI-assisted chatbot responses through OpenRouter-backed integration with fallback behavior — existing
- ✓ Admin can access moderation/dashboard capabilities for reports and management workflows — existing
- ✓ App persists operational data using Flask-SQLAlchemy on SQLite with manual migration scripts — existing

### Active

- [ ] Improve quiz experience quality (content quality, flow clarity, score feedback, and usability)
- [ ] Improve scam reporting UX and validation robustness for more accurate submissions
- [ ] Improve chatbot reliability and UX using current API-based OpenRouter integration (no local model hosting)
- [ ] Improve database schema consistency and migration safety for current and upcoming features
- [ ] Improve admin dashboard workflows and moderation visibility
- [ ] Strengthen security hardening (auth/session safety, CAPTCHA reliability, abuse resistance)
- [ ] Improve overall UI/UX consistency, accessibility, responsiveness, and navigation

### Out of Scope

- Hosting or training a real local AI model — current milestone intentionally uses API-based AI for simplicity and delivery speed
- Replacing Flask + SQLite architecture — constrained to incremental improvements on current stack

## Context

- The codebase is already in production-style modular Flask blueprint architecture with existing routes for auth, quiz, scam reporting, chatbot, and admin features.
- There is an up-to-date codebase map under `.planning/codebase/` documenting stack, architecture, conventions, testing, and concerns.
- The milestone is brownfield improvement work, not greenfield build-from-scratch.
- Primary user-facing language remains Vietnamese, while implementation code/documentation may remain English-focused for maintainability.

## Constraints

- **Tech stack**: Keep Flask + SQLite architecture — avoid disruptive rewrites and preserve compatibility with current implementation.
- **Database migration**: Manual migration scripts only — aligns with existing project DB workflow and tooling.
- **Language**: Vietnamese for user-facing text — maintains product consistency for target audience.
- **Delivery timeline**: Quick iterative improvements — prioritize high-impact UX/reliability changes over broad re-architecture.
- **AI approach**: API-based model integration only — maintain simplicity, cost control, and current OpenRouter-based path.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat this as brownfield optimization milestone | Existing capabilities already implemented and in use | — Pending |
| Prioritize UX/UI and reliability across existing modules | Core requested outcome is improved user experience | — Pending |
| Keep OpenRouter API approach instead of local model hosting | Faster delivery and lower operational complexity | — Pending |
| Keep Flask + SQLite with manual migrations | Matches current architecture and team workflow | — Pending |

---
*Last updated: 2026-03-19 after initialization*
