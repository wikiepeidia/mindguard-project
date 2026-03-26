---
status: awaiting_human_verify
trigger: "Three bugs: leaderboard status all 'Chưa xác minh', OTP toast not auto-dismissing, chatbot 405 Method Not Allowed"
created: 2026-03-26T00:00:00Z
updated: 2026-03-26T00:00:00Z
---

## Current Focus

hypothesis: All 3 bugs confirmed and fixed
test: Manual verification by user
expecting: All 3 issues resolved
next_action: User verifies fixes

## Symptoms

expected: 1) Leaderboard shows correct verification status 2) OTP toast auto-dismisses after ~2s 3) Chatbot page loads and accepts messages
actual: 1) All entries show "Chưa xác minh" 2) Messages persist on screen 3) HTTP 405 "Method Not Allowed"
errors: Bug 3: "Method Not Allowed — The method is not allowed for the requested URL"
reproduction: 1) Visit /leaderboard 2) Trigger OTP send 3) Visit chatbot page
started: Ongoing

## Eliminated

## Evidence

- timestamp: 2026-03-26
  checked: Database scammer_reports table
  found: All 11 approved records have verification_status='unverified'
  implication: approve_report never sets verification_status

- timestamp: 2026-03-26
  checked: routes/admin.py approve_report function
  found: Only sets report.status='approved', never touches verification_status
  implication: Root cause of Bug 1 confirmed

- timestamp: 2026-03-26
  checked: static/js/base.js auto-dismiss code
  found: mouseenter handler with {once:true} permanently cancels timer with no mouseleave to restart
  implication: Root cause of Bug 2 — hovering once kills dismiss forever

- timestamp: 2026-03-26
  checked: routes/chatbot.py chatbot_page route
  found: Route only allows methods=["GET"] but chatbot.html forms use method="post"
  implication: Root cause of Bug 3 — POST requests get 405

## Resolution

root_cause: |
  Bug 1: approve_report() only sets status='approved' but never updates verification_status (stays 'unverified')
  Bug 2: mouseenter event permanently cancels auto-dismiss timer with no restart on mouseleave
  Bug 3: chatbot_page() route only allows GET, but template forms submit POST
fix: |
  Bug 1: Added report.verification_status='verified' in approve_report(); updated 11 existing DB rows
  Bug 2: Replaced one-shot mouseenter cancel with mouseenter/mouseleave pause/resume pattern
  Bug 3: Added POST to allowed methods; handle form message submission and pass history to template
verification: Pending user verification
files_changed:

- routes/admin.py
- static/js/base.js
- routes/chatbot.py
- database/mindguard_v2.db (11 rows updated)
