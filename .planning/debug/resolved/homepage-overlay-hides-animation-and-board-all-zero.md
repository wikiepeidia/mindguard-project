---
status: resolved
trigger: "Investigate issue: homepage-overlay-hides-animation-and-board-all-zero"
created: 2026-03-20T10:55:48+07:00
updated: 2026-03-20T11:10:30+07:00
---

## Current Focus
<!-- OVERWRITE on each update - reflects NOW -->

hypothesis: Layering and homepage fallback fixes address rendering issues, and data emptiness was due to local database content state.
test: Human verification confirmed visual behavior and seeded local DB using `PYTHONPATH=. python database/test/seed_data.py` to validate non-zero homepage data paths.
expecting: Homepage renders network canvas immediately and board/stats show non-zero values after seed.
next_action: Session resolved and ready for archive.

## Symptoms
<!-- Written during gathering, then IMMUTABLE -->

expected: Animation/decorative network should be visible immediately on first paint at top of homepage without requiring scroll. Theme remains consistent. Live board and stats should show actual data from DB as before, not all zeros.
actual: User must scroll down near section Công cụ hỗ trợ toàn diện before animation becomes visible. Homepage board shows all metrics as 0 and no meaningful entries.
errors: no explicit console/traceback reported.
reproduction: open homepage directly, observe hidden animation at top and board/leaderboard values all zero.
started: likely started after recent light mode fixes/plans.

## Eliminated
<!-- APPEND only - prevents re-investigating -->

## Evidence
<!-- APPEND only - facts discovered -->

- timestamp: 2026-03-20T10:56:20+07:00
	checked: .planning/debug/knowledge-base.md
	found: Knowledge base match on [light mode, homepage, LIVE board, dim network effect] with previous root cause in lightmode-remaining-notification-footer-live-badges.
	implication: Prior regression class is plausible; test template/CSS/JS and data wiring first before broader hypotheses.

- timestamp: 2026-03-20T10:58:02+07:00
	checked: routes/main.py::index, templates/index.html, static/css/homepage.css, static/js/homepage.js
	found: Homepage board renders only `top_scammers` from `ScammerLeaderboard.join(ScammerReport).filter(status='approved')`; if leaderboard rows are absent, board becomes empty regardless of raw reports. Homepage CSS is light-mode opaque and may obscure a shared animated background layer from base layout.
	implication: Need to verify whether leaderboard table is empty/out-of-sync and whether shared animated layer is behind opaque hero backgrounds/z-index.

- timestamp: 2026-03-20T10:59:01+07:00
	checked: templates/base.html, static/css/base.css, static/js/base.js
	found: Animated network is `canvas#network-canvas` with `position: fixed` and `z-index: -1`; homepage sections use opaque/near-opaque backgrounds, so canvas can sit behind page paint and appear hidden at top.
	implication: Raising canvas stacking level (while keeping interaction disabled) is a direct candidate fix for animation hidden-until-scroll symptom.

- timestamp: 2026-03-20T11:02:22+07:00
	checked: config.py and app-context DB queries on ScamReport/Registration/ScammerReport/ScammerLeaderboard
	found: Active database URI points to `database/mindguard_v2.db`; all homepage-relevant tables currently return 0 rows, and `top_scammers` source query depends on `ScammerLeaderboard JOIN ScammerReport(status='approved')`.
	implication: Zero metrics are currently true for this DB state, and homepage board is fragile to leaderboard-sync gaps; backend path needs fallback robustness.

- timestamp: 2026-03-20T11:04:20+07:00
	checked: routes/main.py and static/css/base.css patches
	found: Homepage now uses `visible_scammer_count` fallback plus `approved_report_fallback` when leaderboard rows are missing; network canvas moved to `z-index: 0` with non-canvas body children layered above.
	implication: Fix targets both hidden animation on first paint and board fragility from leaderboard-only sourcing.

- timestamp: 2026-03-20T11:04:48+07:00
	checked: runtime checks via Flask test client and app-context DB counts
	found: `GET /` returns 200 with expected homepage markers; DB counts still all zero in current local database.
	implication: Render/query path is healthy post-fix, while zero metrics remain expected until data is present.

- timestamp: 2026-03-20T11:10:30+07:00
	checked: human verification + local seed command result
	found: User confirmed layering fix in browser, then seeded local DB (`PYTHONPATH=. python database/test/seed_data.py`) and validated non-zero counts (`scammer_reports=10`, `leaderboard=10`, `articles=3`), homepage no longer shows all-zero/empty-safe state.
	implication: Root causes are confirmed fixed end-to-end in real workflow and data state.

## Resolution
<!-- OVERWRITE as understanding evolves -->

root_cause: Canvas background layer is stacked behind light-mode page paints, and homepage board/stats logic is overly strict about approved leaderboard data without a direct-report fallback path.
fix: Raised network canvas stacking above page backgrounds (while keeping interactions untouched) and added fallback logic so homepage stats/live board can render approved report data even when leaderboard sync is missing.
verification: Flask test client `GET /` = 200 with homepage markers; CSS and route marker checks confirm patched stacking/fallback logic; human verification confirms browser behavior; after local seed command (`PYTHONPATH=. python database/test/seed_data.py`), counts are non-zero (`scammer_reports=10`, `leaderboard=10`, `articles=3`) and homepage data no longer appears empty.
files_changed: ["static/css/base.css", "routes/main.py"]
