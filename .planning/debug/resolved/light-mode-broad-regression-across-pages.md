---
status: resolved
trigger: "Investigate issue: light-mode-broad-regression-across-pages"
created: 2026-03-20T03:09:41Z
updated: 2026-03-20T03:29:30Z
---

## Current Focus

hypothesis: Applied fix should restore default light utility backgrounds and token-based table text while preserving homepage hero translucency only where needed.
test: Run local smoke checks on core routes and verify no new file-level errors for changed files.
expecting: Key routes render with HTTP 200/302 and changed files show no syntax/lint issues.
next_action: archive resolved session, update knowledge base, and finalize documentation commits.

## Symptoms

expected: All major pages in light mode should have consistent readable contrast (no white text on white/light backgrounds), coherent color tokens, readable flash/alerts/forms/links/buttons, and Vietnamese text with proper accents where applicable.
actual: Recent fixes addressed key pages, but user requested broad regression because certain locations were previously missed during light-mode migration.
errors: No specific runtime errors; likely style/token drift and hardcoded dark values in page-specific CSS/templates.
reproduction: Visit core pages (index, login, register, profile, quiz, leaderboard, chatbot, report/scammer profile). Inspect sections, forms, cards, tables, alerts, footer/header consistency.
started: Ongoing after recent light mode port.

## Eliminated

## Evidence

- timestamp: 2026-03-20T03:10:40Z
	checked: .planning/debug/knowledge-base.md
	found: Matched prior entry light-mode-notification-footer-report-pixel-coverage with overlapping tokens light mode, white text on light background, footer dark override.
	implication: First hypothesis should test recurring global dark overrides in shared styles before page-specific patches.

- timestamp: 2026-03-20T03:11:10Z
	checked: static/css and templates hardcoded color scan
	found: Widespread dark/light hardcoded values remain, especially in static/css/style.css and multiple templates using text-white/bg-black/bg-dark patterns.
	implication: Regression likely broad and selector-driven; high-impact fixes should prioritize shared styles and core routes.

- timestamp: 2026-03-20T03:12:05Z
	checked: templates and route-level CSS for login/register/profile/quiz/leaderboard/chatbot/report/scammer profile
	found: Most page-specific CSS files are tokenized, but static/css/style.css still contains global legacy dark overrides that can nullify Bootstrap light utility surfaces across routes.
	implication: A small global cleanup should deliver cross-page impact with lower risk than broad per-template rewrites.

- timestamp: 2026-03-20T03:12:20Z
	checked: templates/report_scammer.html
	found: Anti-spam warning note text remains unaccented Vietnamese despite requirement for user-facing Vietnamese copy.
	implication: Copy-level regression should be corrected during same pass for consistency requirement.

- timestamp: 2026-03-20T03:13:45Z
	checked: static/css/style.css, templates/report_scammer.html
	found: Removed global .bg-white/.bg-light transparency override, removed forced white table text override block, and restored accented anti-spam warning copy.
	implication: Light mode should now respect Bootstrap/token surfaces across pages with reduced regression risk.

- timestamp: 2026-03-20T03:15:20Z
	checked: local route smoke checks via curl
	found: /, /login, /register, /leaderboard returned 200; /quiz and /chatbot/ returned 302 (auth-gated flow); /scammer/report returned 200.
	implication: Core public pages are reachable; authenticated pages remain reachable through expected redirect behavior.

- timestamp: 2026-03-20T03:15:30Z
	checked: diagnostics on changed files
	found: No errors in static/css/style.css and templates/report_scammer.html.
	implication: No syntax/lint regressions introduced by this fix.

## Resolution

root_cause: Legacy dark-theme compatibility rules in static/css/style.css still globally override light utility classes and table text colors, causing contrast drift across non-home pages that rely on Bootstrap utility backgrounds and tokenized surfaces.
fix: Remove unsafe global overrides and align table defaults with light tokens; restore accented Vietnamese report warning copy.
verification: Automated smoke checks passed for target routes (200/expected 302), file diagnostics show no new errors, and user confirmed fix in real workflow with autonomous verification smoke checks and expected diff.
files_changed: ["static/css/style.css", "templates/report_scammer.html"]
