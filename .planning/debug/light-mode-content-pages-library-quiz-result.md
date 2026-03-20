---
status: verifying
trigger: "Investigate issue: light-mode-content-pages-library-quiz-result"
created: 2026-03-20T10:17:35+07:00
updated: 2026-03-20T10:25:20+07:00
---

## Current Focus
<!-- OVERWRITE on each update - reflects NOW -->

hypothesis: Template-local dark utility leftovers were causing the reported light-mode readability inconsistencies.
test: Run marker checks to confirm targeted class cleanup and execute route smoke checks for `/library`, `/library/<id>`, and `/quiz/result` (with login-session simulation).
expecting: No critical dark utility leftovers in the affected text blocks and successful route responses/redirects as designed.
next_action: execute marker and route smoke checks

## Symptoms
<!-- Written during gathering, then IMMUTABLE -->

expected: In light mode, pages /library, /library/<id>, and /quiz/result should use readable contrast with coherent light tokenized surfaces; no white text on light backgrounds; links/cards/meta badges remain readable.
actual: Scan indicates heavy use of text-white and dark utility classes in content templates; likely residual readability issues after broad pass.
errors: No runtime errors provided.
reproduction: Open library listing, article detail, and quiz result in light mode; inspect headings/cards/meta badges/links/body text for contrast issues.
started: Residual after recent light mode migration.

## Eliminated
<!-- APPEND only - prevents re-investigating -->

## Evidence
<!-- APPEND only - facts discovered -->

- timestamp: 2026-03-20T10:19:40+07:00
 checked: .planning/debug/knowledge-base.md
 found: Matched known-pattern candidate `light-mode-broad-regression-across-pages` with overlap on `light mode`, `white text on light background`, and global/dark utility conflicts.
 implication: Prioritize removal of residual dark/white utility usage in templates and avoid broad global overrides.

- timestamp: 2026-03-20T10:19:40+07:00
 checked: templates/library.html, templates/library_detail.html, templates/quiz_result.html
 found: All three templates contain multiple hardcoded dark-oriented classes (`text-white`, `text-white-50`, `alert-dark`, `btn-outline-light`, `bg-dark`) in headings/body/cards/meta.
 implication: Readability regressions in light mode are likely template-level and can be fixed with page-scoped class substitutions.

- timestamp: 2026-03-20T10:22:10+07:00
 checked: routes/library.py and routes/quiz.py
 found: `/quiz/result` is protected by `@login_required`, while `/library` and `/library/<id>` are publicly rendered from ScamReport data.
 implication: Smoke checks must include login session simulation for `/quiz/result` and article-id fallback handling for `/library/<id>`.

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: Residual hardcoded dark text/surface utility classes in content templates (`text-white`, `text-white-50`, `text-slate-*`, `alert-dark`, `bg-dark`) conflicted with light-mode surfaces.
fix: Replaced dark-specific utility classes in `library.html`, `library_detail.html`, and `quiz_result.html` with light-safe semantic classes (`text-body`, `text-muted`, `alert-info`, `bg-light border`) without global CSS overrides.
verification: In progress.
files_changed: [templates/library.html, templates/library_detail.html, templates/quiz_result.html]
