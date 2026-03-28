# Content Strategy

> **Owner**: @copywriter-seo
> **Personas**: Defined in `PRD.md` — always read before writing copy
> **Last updated**: 2026-03-28

---

## Overview

MindGuard is a community-driven fraud awareness platform for Vietnamese users of all ages. It combines interactive fraud education (quizzes), community-powered scammer reporting with public verification badges, and an AI chatbot that gives real-time fraud prevention guidance. All content must reinforce the core promise: that protecting yourself from fraud is possible, accessible, and better when we do it together.

**Primary value proposition**: One free platform where Vietnamese users can learn about scams, check if someone is a known scammer, and get AI-powered fraud prevention advice — no registration required to look up a scammer.

**Canonical brand statement**: "Bảo vệ cộng đồng khỏi lừa đảo" (Protecting the community from fraud)

---

## Brand Voice & Tone

### Voice (constant across all content)

| Dimension | Setting | Description |
|-----------|---------|-------------|
| Formality | Conversational | Accessible to all ages and technical levels in Vietnam; reads like a trusted friend, not a government notice |
| Energy | Medium | Encouraging without being alarming — fraud is a serious topic but users must never feel overwhelmed or judged |
| Personality | Human | Warm, community-oriented; we are in this together, not a faceless authority telling people what to do |
| Authority | Peer | We share knowledge as equals; MindGuard is the friend who happens to know more about scams, not a lecturer |

### Tone by Context

| Context | Tone | Example |
|---------|------|---------|
| Marketing headlines | Confident, community-focused, benefit-led | "Cùng nhau chống lừa đảo" (Together against fraud) |
| Error messages | Calm, direct, helpful — explain what happened and what to do next | "Có lỗi xảy ra. Vui lòng thử lại sau." (An error occurred. Please try again later.) |
| Success confirmations | Warm, encouraging, forward-looking | "Báo cáo đã được gửi thành công! Cảm ơn bạn đã bảo vệ cộng đồng." |
| Onboarding | Encouraging, step-by-step, zero jargon | "Chào mừng bạn đến MindGuard! Hãy bắt đầu với một bài quiz nhanh." |
| Quiz results | [TBD — to be filled by @copywriter-seo when quiz result pages are written] | — |
| Empty states | [TBD — to be filled by @copywriter-seo when empty state copy is written] | — |

### Voice Rules

- Always lead with the outcome for the user, not the feature we built ("Biết ngay ai đang lừa đảo" before "We built a scammer database")
- Use "bạn" (you) throughout — never refer to users in the third person ("người dùng") in UI copy
- Fraud is a community problem; use "chúng ta" (we/us together) in headlines and community-facing copy to reinforce shared ownership
- Specific numbers build trust; vague claims destroy it — "hàng nghìn báo cáo" (thousands of reports) is weaker than the actual count; always use real numbers where available
- Never shame a user who was scammed — Chị Lan's persona is the reference point; all copy related to reporting must be empowering, not pitying
- In bilingual contexts (Vietnamese UI, English docs), Vietnamese is always primary; English is developer/admin-facing only

### Forbidden Phrases

- "Hàng đầu" / "tốt nhất" / "số 1" (best/leading/number 1) — unverifiable superlatives that erode trust
- "Dễ dàng" / "đơn giản" (easy/simple) — patronising if the user finds it hard; show the simplicity, don't claim it
- "Chúng tôi rất vui khi thông báo" (We are excited to announce) — the user does not care about our excitement
- "Lưu ý rằng" / "Quan trọng là" (Please note that / It is important that) — padding that softens the message
- Any claim without a specific number or proof point: "nhiều người dùng" (many users), "nhanh hơn đáng kể" (significantly faster)
- "Liền mạch" / "trực quan" (seamless/intuitive) — if the experience is good, users will feel it; claiming it reads as defensive

---

## Target Personas

> Personas are defined in `PRD.md`. This section captures only the copy-relevant summary for each.

### "Anh Minh" — Concerned Citizen

**Job-to-be-done**: Quickly check whether a phone number, email address, or social media account belongs to a known scammer before making a transaction or responding to a contact.

**Biggest objection**: "Cơ sở dữ liệu này có đáng tin không? Có bao nhiêu kẻ lừa đảo thực sự được liệt kê?" (Is this database reliable? How many scammers are actually listed?)

**Language to use**: Plain everyday Vietnamese; no technical jargon; familiar terms like "số điện thoại lạ" (strange phone number), "kiểm tra nhanh" (quick check), "an toàn" (safe). Avoid legal or formal register.

**Tone for this persona**: Reassuring and action-oriented. Give Anh Minh confidence that the lookup takes seconds and that the database is community-verified. Do not overwhelm with caveats.

**Primary CTA for this persona**: "Kiểm tra ngay" (Check now)

---

### "Chị Lan" — Fraud Victim / Reporter

**Job-to-be-done**: Report a scammer to warn the rest of the community and feel that concrete action is being taken — that her report has a visible impact.

**Biggest objection**: "Danh tính của tôi có được bảo vệ không? Báo cáo của tôi có thực sự được xem xét không?" (Will my identity be protected? Will my report actually matter?)

**Language to use**: Empathetic and validating Vietnamese. Acknowledge that being scammed is not her fault. Use "cộng đồng" (community), "bảo vệ người khác" (protect others), "cùng nhau" (together). Avoid clinical or bureaucratic language around the reporting process.

**Tone for this persona**: Supportive and empowering. Chị Lan needs to feel that submitting a report is an act of strength — she is protecting others — not an admission of weakness. The anonymisation feature is a trust signal and must be mentioned early.

**Primary CTA for this persona**: "Báo cáo lừa đảo" (Report fraud)

---

## Keyword Strategy

### Domain & Canonical URL

- **Primary domain**: [TBD — not yet deployed to production; to be confirmed when production deployment target is decided (see PRD Open Question #3)]
- **Canonical protocol + www preference**: [TBD — to be set once primary domain is confirmed; will be recorded here and applied consistently across all pages]

> **Note**: Full SEO keyword strategy is deferred until production deployment is ready. All keyword targets below are placeholders. Run keyword research with real tools (Ahrefs, Google Search Console, or similar) before targeting any keyword.

### Primary Keyword Targets

| Keyword | Intent | Mapped Page | Monthly Volume | Difficulty | Status | Date Added |
|---------|--------|-------------|---------------|------------|--------|------------|
| kiểm tra lừa đảo (check fraud) | Transactional | [TBD — scammer lookup page] | [TBD — verify] | [TBD — verify] | Not started | 2026-03-28 |
| báo cáo lừa đảo (report fraud) | Transactional | [TBD — report submission page] | [TBD — verify] | [TBD — verify] | Not started | 2026-03-28 |
| cách nhận biết lừa đảo (how to identify fraud) | Informational | [TBD — knowledge base / quiz entry] | [TBD — verify] | [TBD — verify] | Not started | 2026-03-28 |
| danh sách kẻ lừa đảo (scammer list) | Commercial investigation | [TBD — public scammer leaderboard] | [TBD — verify] | [TBD — verify] | Not started | 2026-03-28 |
| chatbot tư vấn lừa đảo (fraud prevention chatbot) | Informational | [TBD — chatbot page] | [TBD — verify] | [TBD — verify] | Not started | 2026-03-28 |

### Secondary Keywords (supporting, per page)

| Page | Secondary Keywords |
|------|--------------------|
| [TBD — all pages pending deployment and keyword research] | [TBD — verify] |

### Content Clusters

| Pillar Page | Cluster Pages | Status |
|-------------|---------------|--------|
| [TBD — fraud awareness hub / knowledge base] | [TBD — individual scam-type articles] | Planned |

### Keywords to Avoid / Not Target

| Keyword | Reason |
|---------|--------|
| checkscam (brand name) | Competitor brand name; navigational intent belongs to Checkscam.vn — targeting it creates a poor user experience and is unlikely to convert |
| [TBD — add as research is done] | — |

---

## Page Copy Library

> To be filled by @copywriter-seo as pages are written. Each entry must pass the On-Page SEO Checklist before being recorded here.

---

### Homepage

> [To be filled by @copywriter-seo when homepage copy is written.]

---

### Scammer Lookup Page

> [To be filled by @copywriter-seo when scammer lookup page copy is written.]

---

### Report Submission Page

> [To be filled by @copywriter-seo when report submission page copy is written.]

---

### Quiz Pages

> [To be filled by @copywriter-seo when quiz copy is written.]

---

### Chatbot Page

> [To be filled by @copywriter-seo when chatbot page copy is written.]

---

### Knowledge Base

> [To be filled by @copywriter-seo when knowledge base copy is written.]

---

## CTA Library

> To be filled by @copywriter-seo as pages are written. All CTAs in active use must be logged here before implementation.

| CTA Text | Page / Context | Level | Notes | Date Added |
|----------|---------------|-------|-------|------------|
| Kiểm tra ngay (Check now) | Scammer lookup / homepage hero | Primary | Primary CTA for Anh Minh persona; action-oriented, low commitment | 2026-03-28 |
| Báo cáo lừa đảo (Report fraud) | Report submission / homepage | Primary | Primary CTA for Chị Lan persona; empowering framing | 2026-03-28 |

---

## Technical SEO Decisions

> To be filled by @copywriter-seo as pages are written. Implementation of all meta tags, structured data, and canonical URLs is delegated to @frontend-developer with the exact spec from this section.

### Meta Tag Defaults

Applied to all pages unless a page-level override exists in the Page Copy Library above.

| Tag | Default value | Notes |
|-----|--------------|-------|
| robots | `index, follow` | Override to `noindex, nofollow` for: /admin, /admin/*, /thank-you, /404, /500 |
| og:image | [TBD — 1200×630px default social image to be created] | Override per page when a unique image exists |
| twitter:card | `summary_large_image` | |
| lang | `vi` | Vietnamese is the primary language for all user-facing pages |

### Structured Data in Use

| Schema type | Applied to | Implementation status |
|-------------|------------|----------------------|
| Organization | Homepage | Pending — spec to be written by @copywriter-seo, implemented by @frontend-developer |
| WebSite | Homepage | Pending |
| FAQPage | Knowledge base articles with FAQ sections | Pending |
| BreadcrumbList | All pages except homepage | Pending |

### Redirect Map

| From | To | Type | Reason |
|------|-----|------|--------|
| [TBD — to be populated when URL structure is finalised and any legacy slugs are identified] | — | — | — |

### Hreflang Configuration

Not applicable for v1.0. MindGuard is Vietnamese-only in this version. Multi-language support is explicitly out of scope per PRD Section 7. Revisit when internationalisation is planned.

---

## Content Calendar

> To be filled by @copywriter-seo as content is planned and produced.

| Publish date | Title / Topic | Type | Primary keyword | Status | Owner |
|-------------|--------------|------|----------------|--------|-------|
| [TBD] | [TBD — first knowledge base article on common scam types in Vietnam] | Knowledge base article | [TBD — verify] | Planned | @copywriter-seo |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-28 | Initial content strategy — brand voice, tone matrix, personas, CTA library seeds, and keyword framework defined for MindGuard v1.0. SEO keyword research deferred until production deployment is confirmed. |
