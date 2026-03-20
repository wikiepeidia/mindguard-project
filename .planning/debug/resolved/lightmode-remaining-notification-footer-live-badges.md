---
status: resolved
trigger: "Investigate issue: lightmode-remaining-notification-footer-live-badges"
created: 2026-03-20T00:00:00Z
updated: 2026-03-20T01:05:00Z
---

## Current Focus

hypothesis: Confirmed. The remaining regression is caused by hardcoded dark utility classes/inline styles in homepage template plus incomplete light overrides for footer/alerts/pixels.
test: User human-verification checkpoint confirmed fixed in real workflow/environment.
expecting: Session can be archived and knowledge base updated without reopening investigation.
next_action: move session file to resolved and append knowledge-base entry

## Symptoms

expected: Notification auto-hides after 2-3s if not manually closed and uses light-mode-compatible colors (dark text on light surface or theme-consistent). Remaining dark backgrounds/text on homepage should be converted to light-mode compatible styles. Footer should look clean and readable in light mode, including brand text 'MindGuard' and links/newsletter controls. Decorative moving blue pixel effect should be tuned for light mode (brighter/pleasant, not muddy).
actual: Some spots still dark mode style in light mode: SĐT/STK/URL controls, LIVE block subtitle area ('Dữ liệu cập nhật theo thời gian thực') appears dark, notification contrast is off (white text), and footer theme is visually poor with over-dark brand text.
errors: none reported.
reproduction: Open homepage in light mode; inspect notification, SĐT/STK/URL controls, LIVE subtitle area, footer branding/links/newsletter, and decorative moving pixel/glow elements.
started: Regression remnants after light mode port; now only small areas remain unfixed.

## Eliminated

## Evidence

- timestamp: 2026-03-20T00:10:00Z
	checked: .planning/debug/knowledge-base.md
	found: Knowledge base has a direct candidate match `light-mode-notification-footer-report-pixel-coverage` with overlapping patterns (footer too dark, notification compatibility, dim pixels).
	implication: Start by testing whether residual selector coverage gaps remain in homepage/footer/light notification styles rather than searching unrelated modules.

- timestamp: 2026-03-20T00:18:00Z
	checked: keyword scan in templates/index.html, static/css/homepage.css, static/css/style.css, static/js/base.js
	found: Homepage template still contains SĐT/STK/URL filter chips and LIVE subtitle text; base.js already contains auto-hide logic for dismissible alerts; style.css still has many footer/alert/live-related blocks.
	implication: The user-reported issue is likely CSS selector/theme mismatch, with JS auto-hide likely already fixed and needing only style consistency validation.

- timestamp: 2026-03-20T00:29:00Z
	checked: full reads of templates/base.html, templates/index.html, static/css/homepage.css, static/css/style.css, static/css/base.css, static/js/base.js
	found: `templates/index.html` still hardcodes dark chips (`bg-dark text-white`) and dark LIVE footer strip (`bg-black bg-opacity-20`); `static/css/homepage.css` does not override those specific badge/filter/suffix zones; `templates/base.html` footer uses `btn-outline-light` and muted links on light background without footer-specific refinements; `static/js/base.js` auto-hide exists but timeout is 5500ms.
	implication: Fix should be primarily CSS + small class updates (not logic rewrite), and notification timing can be tightened to match 2-3s expectation.

- timestamp: 2026-03-20T00:29:00Z
	checked: static/js/base.js
	found: Dismissible alerts auto-close via Bootstrap instance after 5500ms and stop timer on hover.
	implication: To align with reported expectation, reduce timeout to around 2800ms while preserving manual close and hover behavior.

- timestamp: 2026-03-20T00:38:00Z
	checked: templates/index.html, static/css/homepage.css, static/css/style.css, static/css/base.css, static/js/base.js
	found: Replaced hardcoded dark chip classes with semantic classes, replaced LIVE subtitle dark strip with light strip class, added homepage light-mode chip/filter/live-strip styles, refined footer brand/link/newsletter styles, enforced alert light-surface contrast for contextual alert classes, brightened network canvas colors/opacity, and reduced auto-hide delay from 5500ms to 2800ms.
	implication: Targeted regressions should now be fixed with scoped and minimal changes.

- timestamp: 2026-03-20T00:44:00Z
	checked: runtime render via Flask test client for GET /
	found: Status 200 and new markers `hero-token-chip` and `live-subtitle-strip` are present in rendered HTML.
	implication: Template changes are active at runtime.

- timestamp: 2026-03-20T00:45:00Z
	checked: source marker scan on templates/index.html, static/css/homepage.css, static/css/style.css, static/js/base.js
	found: New markers (`hero-token-chip`, `live-subtitle-strip`, `.alert[class*="alert-"]`, `2800`) are present; old targeted markers (`bg-dark bg-opacity-50 text-white`, `bg-black bg-opacity-20 text-center`, `5500`) are absent.
	implication: Intended replacements were applied without leftover targeted tokens.

- timestamp: 2026-03-20T00:46:00Z
	checked: diagnostics for changed files
	found: No errors reported in templates/index.html, static/css/homepage.css, static/css/style.css, static/css/base.css, static/js/base.js.
	implication: Changes are syntactically clean in editor diagnostics.

## Resolution

root_cause: Residual hardcoded dark classes/inline styles in homepage template (chips and LIVE subtitle strip), plus missing footer/flash fine-tuning in light mode and dim network-canvas color values left from earlier dark-leaning defaults.
fix: Updated homepage template/class hooks and light-mode CSS overrides for chips/LIVE strip/filter controls, improved footer visual hierarchy and alert contrast styles, and tuned base canvas + alert auto-hide timing to light-mode expectations.
verification: Self-verified with runtime GET / render marker checks (status 200 + new markers present), source marker checks for new/removed tokens, and no diagnostics errors across all changed files.
files_changed: [templates/index.html, static/css/homepage.css, static/css/style.css, static/css/base.css, static/js/base.js]
