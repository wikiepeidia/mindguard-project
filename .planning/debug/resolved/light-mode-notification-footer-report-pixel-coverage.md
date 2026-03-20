---
status: resolved
trigger: "Investigate issue: light-mode-notification-footer-report-pixel-coverage"
created: 2026-03-20T03:03:28Z
updated: 2026-03-20T03:20:00Z
---

## Current Focus

hypothesis: Local verification indicates regression is fixed; user-side browser validation is required for final confirmation of light-mode visuals and flash auto-hide behavior.
test: Have user validate homepage footer/brand contrast, report disclaimer readability, flash notification visibility/auto-hide, and canvas pixel brightness in real UI.
expecting: User confirms light-mode consistency and notification behavior are correct across target pages.
next_action: Request human verification checkpoint with explicit reproduction steps.

## Symptoms

expected: Light mode should use readable dark text on light surfaces, footer should be visually coherent and not overly black, report scammer privacy/commitment section should be fully light-mode compatible, notifications should be readable and auto-hide behavior should work, and decorative pixel animation should be brighter/visible in light mode. Vietnamese text should keep accents (e.g., 'Email chưa được đăng ký').
actual: White text still appears on light backgrounds in certain locations. Footer theme looks bad and brand text contrast is wrong (Mind too black). Some report scammer section copy block ('Cam kết bảo vệ người tố cáo...') not adapted. Notification area has compatibility issues and may not auto-hide. Residual hardcoded dark colors likely across CSS files.
errors: No explicit console errors provided.
reproduction: Browse light mode pages including homepage, footer area, and report scammer page. Trigger notifications and inspect colors/auto-hide. Search CSS for hardcoded dark text/bg classes and patch for light mode.
started: Regressions appeared after recent light mode migration.

## Eliminated

## Evidence

- timestamp: 2026-03-20T03:03:46Z
	checked: .planning/debug/knowledge-base.md
	found: Knowledge base match on [light mode, text-white, readability, privacy text] with entry `light-mode-ui-inconsistencies-liveboard-vietnamese-accents`.
	implication: Prior regression pattern strongly suggests remaining components were not fully migrated to theme-variable-based styling.

- timestamp: 2026-03-20T03:04:46Z
	checked: static/css/style.css + templates/base.html + static/css/report_scammer.css + static/js/base.js
	found: style.css globally forces dark UI (`footer { background: #020617; }`, `.alert { color: #fff !important; }`, `.btn-close { filter: invert(...) }`, `.dropdown-menu { background: #1e293b !important; }`), which conflicts with light-token system and report disclaimer/flash styles.
	implication: This directly explains white-on-light areas, black footer mismatch, and report commitment block readability issues in light mode.

- timestamp: 2026-03-20T03:04:46Z
	checked: static/js/base.js
	found: No auto-hide behavior exists for flash alerts; notifications only dismiss manually.
	implication: Notification behavior regression includes missing timed dismissal.

- timestamp: 2026-03-20T03:04:46Z
	checked: static/js/base.js + static/css/base.css
	found: Network pixel effect uses low-contrast stroke alpha and canvas opacity (`0.28`) on bright background.
	implication: Decorative moving blue pixels appear too dim in light mode.

- timestamp: 2026-03-20T03:06:13Z
	checked: Flask test client route render (`/`, `/scammer/report`)
	found: Both routes return HTTP 200; markers present: `MindGuard Community Project`, `id="network-canvas"`, `Cam kết bảo vệ người tố cáo`, `report-disclaimer`, `report-warning-note`.
	implication: Core templates render successfully with expected footer/report sections after CSS/JS updates.

- timestamp: 2026-03-20T03:06:13Z
	checked: static/css/style.css + static/css/base.css + static/js/base.js marker scan
	found: Updated markers confirmed for light footer/alert styles, increased canvas opacity, brighter particle colors, and alert auto-hide script path.
	implication: Implemented fixes are present in source and ready for user-environment validation.

## Resolution

root_cause: Legacy global dark-theme overrides in style.css are still active in light mode and override component-level tokenized styles; base.js lacks flash auto-hide and uses low-contrast network canvas rendering.
fix: Replaced high-impact legacy dark global styles in style.css (footer, dropdown, alert, close button filter, form-select options) with light token-based values; increased network-canvas opacity in base.css; updated base.js to use brighter particle/line colors and added auto-hide for dismissible flash alerts.
verification: Local checks passed: (1) Flask route render OK with key HTML markers, (2) source markers confirm auto-hide flash logic and brighter network canvas styles, (3) no diagnostics errors in changed files, and (4) human verification confirmed fixed in real workflow/environment.
files_changed: ["static/css/style.css", "static/css/base.css", "static/js/base.js"]
