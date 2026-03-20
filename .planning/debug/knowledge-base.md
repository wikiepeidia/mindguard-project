# GSD Debug Knowledge Base

Resolved debug sessions. Used by `gsd-debugger` to surface known-pattern hypotheses at the start of new investigations.

---

## light-mode-notification-footer-report-pixel-coverage — Light-mode footer, flash, and report disclaimer visual regression

- **Date:** 2026-03-20
- **Error patterns:** light mode, footer too dark, white text on light background, report disclaimer not adapted, notification compatibility, missing auto-hide, dim network pixels
- **Root cause:** Legacy global dark-theme overrides in style.css stayed active during light mode and overrode tokenized component styling; base.js also lacked flash auto-hide and used low-contrast network-canvas colors.
- **Fix:** Replaced dark global footer/dropdown/alert/select option styles with token-based light-friendly styles, increased network-canvas visibility, and added timed auto-hide for dismissible alerts.
- **Files changed:** static/css/style.css, static/css/base.css, static/js/base.js

---

## missing-scammer-reports-table-homepage — Homepage GET / crashed with missing scammer_reports table

- **Date:** 2026-03-20
- **Error patterns:** HTTP 500, GET /, sqlalchemy.exc.OperationalError, no such table, scammer_reports, homepage crash
- **Root cause:** `db.create_all()` was only executed in the `__main__` block, so import-based startup paths (including `flask run`) skipped schema initialization and homepage query to `scammer_reports` crashed.
- **Fix:** Run `db.create_all()` during app initialization (not only in `__main__`) so both `flask run` and `python app.py` have required tables.
- **Files changed:** app.py

---

## light-mode-ui-inconsistencies-liveboard-vietnamese-accents — Homepage light-mode contrast and LIVE board filter mismatch

- **Date:** 2026-03-20
- **Error patterns:** light mode, poor readability, text-white on light background, LIVE board not working, filterLive general phone mismatch, missing Vietnamese accents, privacy text unaccented
- **Root cause:** Light-mode rollout left dark-theme text/background classes in homepage template/styles, LIVE phone filter used wrong key mapping (`general` instead of `phone`), and privacy notice source text was unaccented.
- **Fix:** Added section-scoped light-mode contrast overrides, corrected LIVE filter mapping in template/JS, and restored accented privacy copy in the source helper.
- **Files changed:** templates/index.html, static/css/homepage.css, static/js/homepage.js, utils/privacy_policy.py

---

## light-mode-broad-regression-across-pages — Broad light-mode contrast drift across shared utility surfaces

- **Date:** 2026-03-20
- **Error patterns:** light mode, broad regression, contrast drift, hardcoded dark values, global override, white text on light background, bootstrap utility surfaces, anti-spam copy accents
- **Root cause:** Legacy dark-theme compatibility rules in static/css/style.css globally overrode light utility classes and table text colors, causing cross-page contrast issues beyond homepage.
- **Fix:** Removed unsafe global light-surface transparency override and forced white table text block; restored accented Vietnamese anti-spam warning copy in report template.
- **Files changed:** static/css/style.css, templates/report_scammer.html

---

## lightmode-remaining-notification-footer-live-badges — Remaining homepage light-mode chips, LIVE strip, footer, and notification timing regressions

- **Date:** 2026-03-20
- **Error patterns:** light mode, remaining dark styles, SĐT STK URL controls, LIVE subtitle strip dark, footer too dark, notification contrast, notification auto-hide 2-3s, dim moving blue effect
- **Root cause:** Residual hardcoded dark classes/inline styles in homepage template (chips and LIVE subtitle strip), plus missing footer/flash fine-tuning in light mode and dim network-canvas color values left from earlier dark-leaning defaults.
- **Fix:** Updated homepage template/class hooks and light-mode CSS overrides for chips/LIVE strip/filter controls, improved footer visual hierarchy and alert contrast styles, and tuned base canvas + alert auto-hide timing to light-mode expectations.
- **Files changed:** templates/index.html, static/css/homepage.css, static/css/style.css, static/css/base.css, static/js/base.js

---
