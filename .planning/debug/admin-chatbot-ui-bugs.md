---
status: awaiting_human_verify
trigger: "Multiple UI and runtime bugs across admin panel, chatbot page, and a Jinja2 UndefinedError crash"
created: 2026-03-23T00:00:00Z
updated: 2026-03-23T00:02:00Z
---

## Current Focus

hypothesis: All 5 root causes confirmed and fixed
test: Code analysis + targeted edits applied
expecting: All bugs resolved — awaiting user verification
next_action: User verifies

## Symptoms

expected:

1. Admin panel uses light-mode consistent with rest of app (Phase 3 design tokens)
2. Page scroll stops when content ends — no excessive empty scroll space
3. Chatbot logo/icon positioned in bottom-right corner
4. Navigation has a button/link for users to reach the Chatbot page
5. No Jinja2 crash: 'dict object' has no attribute 'scammer'

actual:

1. Admin panel: many text elements still white/unstyled, dark background — not synced with light mode
2. Admin pages: content ends but page keeps scrolling (empty space below content)
3. Chatbot UI: logo is misaligned, not in bottom-right corner
4. No nav button linking users to the chatbot page
5. Jinja2 crash: "jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'scammer'"

errors:

- jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'scammer'

reproduction:

1. Admin: log in as admin, browse any admin page
2. Chatbot: go to /chatbot page
3. Jinja2 error: leaderboard page with scammer data

started: Pre-existing bugs, noticed now that v1 phases are complete

## Eliminated

- hypothesis: Jinja2 error is in scammer_profile.html
  evidence: Both scammer_profile.html and routes/main.py correctly use SQLAlchemy model attributes — the crash is in leaderboard.html iterating `scammers` which is a list of plain dicts
  timestamp: 2026-03-23

## Evidence

- timestamp: 2026-03-23
  checked: leaderboard.html line ~127
  found: Template uses `entry.scammer.report_type` but `entry` is a plain dict from `scammers_payload` in routes/main.py (which has `report_type` as a top-level key, not nested under `scammer`)
  implication: UndefinedError thrown whenever the leaderboard table renders any row

- timestamp: 2026-03-23
  checked: admin_dashboard.html, admin_scammer_reports.html
  found: 7 occurrences of explicit `text-white` class on headings inside `.glass-card` (light background). `.stat-card-admin h3` CSS uses `!important` but class `text-white` has Bootstrap's `!important` too, creating conflicts on some elements
  implication: White text on white/light background → invisible text

- timestamp: 2026-03-23
  checked: base.css — `body > :not(#network-canvas)` rule vs `.chatbot-toggler`/`.chatbot-window` position
  found: `body > :not(#network-canvas) { position: relative; z-index: 1; }` has specificity (1,0,1) which is HIGHER than `.chatbot-toggler { position: fixed; }` at (0,1,0). This causes the chatbot toggler and window to be rendered as `position: relative` in document flow instead of `position: fixed`. The `.chatbot-window` has `height: 550px` and `opacity: 0` — invisible but occupying 550px of page height after the admin content
  implication: Bug 2 (excessive scroll) AND Bug 3 (chatbot icon not at bottom-right) are the same root cause

- timestamp: 2026-03-23
  checked: base.html — all `{% block %}` definitions
  found: base.html only has `{% block title %}` and `{% block content %}`. No `{% block head_css %}`, `{% block main_wrapper %}`, or `{% block scripts %}`. chatbot.html uses all three missing blocks. In Jinja2, child blocks on undefined parent blocks are silently discarded — chatbot page renders empty content, chatbot.css never loads
  implication: Chatbot page shows blank content area; chatbot.css styles including `overflow: hidden` and full-screen layout never apply

- timestamp: 2026-03-23
  checked: base.html nav for logged-in users
  found: "AI Chat" nav item uses `href="#" onclick="toggle show-chatbot"` — opens a pop-up widget, NOT a link to `/chatbot` full page
  implication: No navigation route from navbar to /chatbot page (Bug 4)

## Resolution

root_cause:
  Bug 1 (Jinja2): leaderboard.html used `entry.scammer.report_type` on plain dict entries
  Bug 2 (excessive scroll) + Bug 3 (chatbot misaligned): base.css rule `body > :not(#network-canvas)` overrides `position: fixed` on .chatbot-toggler and .chatbot-window due to higher CSS specificity, placing 550px invisible chatbot-window in document flow
  Bug 4 (missing nav link): nav "AI Chat" used onclick toggle, not href to /chatbot
  Bug 5 (chatbot page empty): base.html missing {% block head_css %}, {% block main_wrapper %}, {% block scripts %} blocks that chatbot.html depends on

fix:

  1. leaderboard.html: `entry.scammer.report_type` → `entry.report_type` (2 occurrences)
  2. admin_dashboard.html: 6x `text-white` → `text-body` on headings
  3. admin_scammer_reports.html: 1x `text-white` → `text-body` on h2
  4. base.css: `.chatbot-toggler` and `.chatbot-window` → `position: fixed !important`
  5. base.html: Added `{% block head_css %}`, `{% block main_wrapper %}`, `{% block scripts %}` blocks; fixed "AI Chat" nav link to `url_for('chatbot.chatbot_page')`
  6. chatbot.css: Added `.chatbot-toggler, .chatbot-window` to the hide rule (to suppress base widget on full-page chat)

verification: Awaiting user confirmation
files_changed:

- templates/leaderboard.html
- templates/admin_dashboard.html
- templates/admin_scammer_reports.html
- static/css/base.css
- templates/base.html
- static/css/chatbot.css

## Symptoms

expected:

1. Admin panel uses light-mode consistent with rest of app (Phase 3 design tokens)
2. Page scroll stops when content ends — no excessive empty scroll space
3. Chatbot logo/icon positioned in bottom-right corner
4. Navigation has a button/link for users to reach the Chatbot page
5. No Jinja2 crash: 'dict object' has no attribute 'scammer'

actual:

1. Admin panel: many text elements still white/unstyled, dark background — not synced with light mode
2. Admin pages: content ends but page keeps scrolling (empty space below content)
3. Chatbot UI: logo is misaligned, not in bottom-right corner
4. No nav button linking users to the chatbot page
5. Jinja2 crash: "jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'scammer'"

errors:

- jinja2.exceptions.UndefinedError: 'dict object' has no attribute 'scammer'

reproduction:

1. Admin: log in as admin, browse any admin page
2. Chatbot: go to /chatbot page
3. Jinja2 error: likely on scammer_profile or leaderboard detail page

started: Pre-existing bugs, noticed now that v1 phases are complete

## Eliminated

(none yet)

## Evidence

(none yet)

## Resolution

root_cause:
fix:
verification:
files_changed: []
