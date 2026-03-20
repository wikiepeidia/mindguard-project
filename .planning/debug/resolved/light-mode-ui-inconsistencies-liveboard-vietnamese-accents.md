---
status: resolved
trigger: "Investigate issue: light-mode-ui-inconsistencies-liveboard-vietnamese-accents"
created: 2026-03-20T00:00:00Z
updated: 2026-03-20T00:35:00Z
---

## Current Focus

hypothesis: Confirmed and patched. Homepage now uses light-mode aligned contrast overrides, LIVE phone filter maps correctly, and privacy banner copy is accented.
test: Render homepage through Flask test client and verify presence of patched LIVE filter and accented notice text; manual browser check remains for visual confirmation.
expecting: Route stays healthy (HTTP 200), expected DOM/script literals are present, and visual/readability issues are resolved in real UI.
next_action: Request human verification on real browser light-mode rendering and LIVE board interactions.

## Symptoms

expected: In light mode, all homepage text should be readable with strong contrast; color system should be consistent and intentional; key sections ('Lá chắn số bảo vệ bạn', 'Công cụ hỗ trợ toàn diện', cards for 'Tố cáo ẩn danh', 'Chatbot AI 24/7', 'Kiến thức phòng vệ', and 'Cách hoạt động') should have balanced colors; footer/link labels should be visually correct; LIVE board should function; Vietnamese copy should keep full accents everywhere.
actual: Many inconsistent colors and poor readability. Some text is white on light background (example around 'Lá chắn số bảo vệ bạn'). Section colors are described as very bad in 'Công cụ hỗ trợ toàn diện'. Copy blocks listed by user indicate typography/color quality issues. LIVE board doesn't work. Some Vietnamese content appears without accents.
errors: No concrete stack trace provided for UI issue. Need inspect templates/CSS/JS for theme token usage, hardcoded colors, and encoding/text literals; inspect LIVE board data/render path.
reproduction: Open homepage in light mode, inspect hero + feature/tool sections + process section + footer links; verify LIVE board behavior; compare displayed Vietnamese strings against intended accented copy.
started: Reported in current state after prior changes; likely regressions from recent light mode rollout.

## Eliminated

## Evidence

- timestamp: 2026-03-20T00:05:00Z
	checked: .planning/debug/knowledge-base.md
	found: No reliable known-pattern match for this issue; existing entry concerns homepage DB crash from missing table.
	implication: Continue normal investigation; do not anchor on prior homepage crash pattern.

- timestamp: 2026-03-20T00:09:00Z
	checked: text search across templates/static assets
	found: Reported problematic strings and LIVE controls are in templates/index.html; relevant behavior code is in static/css/homepage.css and static/js/homepage.js.
	implication: Core issue is localized to homepage template/style/script stack and homepage data route.

- timestamp: 2026-03-20T00:14:00Z
	checked: templates/index.html, static/css/homepage.css, static/js/homepage.js, routes/main.py
	found: Homepage uses many hardcoded dark-theme classes (`text-white`, `text-light`, `text-slate-*`) and dark card/background styling in sections that now render on light canvas; LIVE phone filter button calls `filterLive(..., 'general')` while button declares `data-filter='phone'` and data typically uses phone/bank/website categories.
	implication: UI contrast regressions are caused by dark-only styling surviving light rollout; LIVE board behavior regression is at least partly a front-end filter mapping bug.

- timestamp: 2026-03-20T00:22:00Z
	checked: patched files (templates/index.html, static/css/homepage.css, static/js/homepage.js, utils/privacy_policy.py)
	found: Added section-scoped light-mode contrast styles, corrected SĐT filter from `general` to `phone`, and restored accented privacy copy string.
	implication: Code-level root causes are directly addressed with minimal file scope.

- timestamp: 2026-03-20T00:23:00Z
	checked: Flask test client GET /
	found: Response status 200; output contains `id="liveScammerList"`, `filterLive(this, 'phone')`, and accented `Dữ liệu đã được che để bảo mật`.
	implication: Homepage route remains functional and key rendered markers for the fixes are present.

## Resolution

root_cause: Homepage light-mode rollout left dark-theme text/background styling in `index.html` and `homepage.css` (causing low contrast), LIVE SĐT filter had incorrect key mapping (`general` vs `phone`), and privacy banner copy source in `utils/privacy_policy.py` used unaccented Vietnamese text.
fix: Updated homepage styles to light-mode-safe contrast with section-scoped overrides; fixed LIVE phone filter mapping in both template trigger and JS logic; corrected privacy note literal with full Vietnamese accents.
verification: Self-check passed via Flask test client (`GET /` => 200) and rendered HTML contains corrected LIVE filter invocation and accented privacy notice.
files_changed: [templates/index.html, static/css/homepage.css, static/js/homepage.js, utils/privacy_policy.py]
