# Product Requirements Document

> [!WARNING]
> **READ-ONLY FOR ALL AGENTS**
> This document is the source of truth for what we are building.
> Claude agents must READ this document to understand requirements.
> **Do not edit, rewrite, or "update to reflect current state" without explicit human instruction.**
> When in doubt, leave it unchanged and ask the human.

---

**Version**: 1.0
**Status**: Active
**Last updated by human**: 2026-03-28
**Product owner**: Supervisor (team leader)

---

## 1. Executive Summary

MindGuard is a community-driven fraud awareness platform for Vietnamese users of all ages. It combats the growing problem of online scams by combining interactive education (quizzes about scam types), community-driven scammer reporting (with verification badges and a public leaderboard), and AI-powered chatbot guidance. Inspired by Checkscam.vn, it aims to be a one-stop platform where anyone can learn about fraud, quickly check if someone is a reported scammer, and get real-time advice on suspicious situations.

---

## 2. Problem Statement

### 2.1 Current Situation

Vietnamese citizens face increasing online fraud but lack centralized, accessible tools. While Checkscam.vn exists as a scammer database, users currently rely on word-of-mouth, scattered news articles, and social media posts to learn about scams. Users have no single platform where they can verify a suspicious contact, learn about new scam techniques, and receive real-time guidance all in one place.

### 2.2 The Problem

No single platform combines fraud education, community scammer reporting, and AI-powered guidance. Users can't easily verify if someone is a known scammer, learn about new scam techniques, or get real-time help when facing a suspicious situation. This fragmentation makes it difficult for ordinary citizens to protect themselves effectively.

### 2.3 Why Now

Online fraud in Vietnam continues to grow at an accelerating pace. AI technology (free LLM models via OpenRouter) now makes it possible to provide chatbot assistance at zero cost. Community reporting creates a network effect — the more users report scammers, the more valuable the platform becomes for everyone.

---

## 3. Goals & Success Metrics

### 3.1 Business Goals

- Build a trusted community platform for fraud awareness in Vietnam
- Provide accessible fraud education for all ages and technical levels
- Create a comprehensive scammer database through community reporting
- Demonstrate network effects through organic growth in report count and user engagement

### 3.2 Success Metrics

| Metric | Baseline | Target | How Measured |
|--------|----------|--------|--------------|
| Community scammer reports | 0 | Growing database | Database count |
| Quiz completion rate | 0% | 70%+ | Quiz result records |
| User registrations | 0 | Organic growth | Registration count |
| Chatbot usage | 0 | Regular sessions | Chat session count |

---

## 4. User Personas

### Persona: "Anh Minh" — Concerned Citizen

- **Role**: General Vietnamese internet user (any age)
- **Goals**: Check if a phone number/email/social account belongs to a known scammer before making a transaction
- **Pain points**: No quick way to verify suspicious contacts; scattered information across social media
- **Technical level**: Non-technical to moderate
- **Usage frequency**: Occasional (when encountering suspicious activity)

### Persona: "Chị Lan" — Fraud Victim / Reporter

- **Role**: Someone who has been scammed or witnessed a scam
- **Goals**: Report scammers to warn others; see justice through community verification
- **Pain points**: No centralized reporting system; feels helpless after being scammed
- **Technical level**: Non-technical
- **Usage frequency**: Occasional (to report, then periodic check-ins)

### Persona: "Admin / Moderator"

- **Role**: Platform administrator
- **Goals**: Verify and moderate scammer reports; manage knowledge base articles; maintain platform integrity
- **Pain points**: Manual review of reports; ensuring data quality
- **Technical level**: Moderate to technical
- **Usage frequency**: Daily

---

## 5. Functional Requirements

> Requirements are numbered FR-XXX for unambiguous cross-referencing by agents and in tests.

### 5.1 User Authentication

- **FR-001**: Users must be able to register with name, email, password, and optional profile info (occupation, city)
- **FR-002**: Users must be able to log in with email and password
- **FR-003**: Users must be able to reset their password via email OTP
- **FR-004**: Sessions must expire after 7 days of inactivity

### 5.2 Quiz System

- **FR-010**: Users must be able to take fraud awareness quizzes with multiple-choice questions
- **FR-011**: System must support both static question bank and AI-generated questions (via OpenRouter)
- **FR-012**: Quiz results must be saved with score, and a certificate code generated for passing scores (75%+)
- **FR-013**: Quiz flow must use single-question-per-page with session persistence

### 5.3 Scammer Reporting

- **FR-020**: Users must be able to submit scammer reports with name, contact info (phone/email/social), evidence, and scam type
- **FR-021**: Reporter identity must be anonymized (hash-based, showing only first 8 characters)
- **FR-022**: Scammer profiles must display aggregated reports, verification status, and danger level
- **FR-023**: A public leaderboard must rank scammers by report count and danger level
- **FR-024**: Verification status must progress: Unverified → Verified → Confirmed based on report count and admin review

### 5.4 AI Chatbot

- **FR-030**: Users must be able to chat with an AI assistant specialized in fraud prevention
- **FR-031**: Chat sessions must be persistent per user with full message history
- **FR-032**: System must use OpenRouter API with free LLM models (Mistral, Qwen, Llama)
- **FR-033**: Chatbot must have a system prompt focused on Vietnamese fraud prevention guidance

### 5.5 Knowledge Base

- **FR-040**: Admins must be able to create, edit, and publish articles about scam types and prevention
- **FR-041**: Users must be able to browse and search articles by category
- **FR-042**: Articles must be read-only for regular users

### 5.6 Admin Dashboard

- **FR-050**: Admins must have a moderation interface to approve/reject/flag scammer reports
- **FR-051**: Admins must be able to view platform statistics (users, reports, articles)
- **FR-052**: Admins must be able to view sensitive access logs and audit trails
- **FR-053**: Admins must be able to manage the reporter honor roll

### 5.7 Anti-Spam & Security

- **FR-060**: System must implement rate limiting by account, cookie, and IP with configurable weights
- **FR-061**: Cloudflare Turnstile CAPTCHA must protect forms from bots
- **FR-062**: Sensitive data (phone, email, ID numbers) must be masked in display
- **FR-063**: Audit logging must track all admin and sensitive operations

---

## 6. Non-Functional Requirements

### Performance

- Page load < 3s on standard connection
- API responses < 500ms

### Security

- All passwords hashed with Werkzeug
- Sensitive data encrypted
- OWASP Top 10 mitigations implemented
- Cloudflare Turnstile on forms

### Scalability

- SQLite sufficient for current scale
- PostgreSQL migration planned for growth

### Accessibility

- Vietnamese language primary
- Mobile-responsive design

### Browser / Platform Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile-responsive down to 375px

### Reliability

- SQLite database with backup scripts

---

## 7. Out of Scope (v1.0)

The following will **not** be built in the initial version. This list prevents scope creep and helps agents avoid building features that aren't required yet.

- ML/DL model for automatic scam classification — deferred until sufficient training data collected (planned for v2)
- PostgreSQL migration — planned for when user scale requires it
- Partner/sponsor logo section — low priority, cosmetic feature
- Multi-language support — Vietnamese only for v1
- Mobile native app — web-only for v1
- Payment processing — platform is free
- Real-time notifications/push — not needed for v1

---

## 8. Open Questions

> These are unresolved decisions that require human input before implementation can proceed.

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Which ML framework for future scam classification model? | Supervisor | Open |
| 2 | When to migrate from SQLite to PostgreSQL? | Developer | Open |
| 3 | Production deployment target (VPS, cloud platform)? | Supervisor | Open |
| 4 | What specific UI/UX quirks need fixing? (needs audit) | Developer | Open |

---

## 9. Revision History

> Human entries only. Agents do not modify this section.

| Date | Author | Change Description |
|------|--------|--------------------|
| 2026-03-28 | Developer | Initial PRD based on existing v1 implementation |
