---
status: resolved
trigger: "Three UI bugs — chatbot icon overlapped by footer, homepage CTA button links to chatbot widget instead of /chatbot page, and login page missing a dev-mode Admin Login shortcut button."
created: 2026-03-23T00:00:00Z
updated: 2026-03-23T01:00:00Z
---

## Current Focus

hypothesis: CONFIRMED — all three bugs identified and fixed
test: verified file content + git log
expecting: all three fixes committed atomically
next_action: DONE

## Symptoms

expected:
1. Chatbot floating icon stays on top of ALL page elements including the footer
2. Homepage "Chatbot AI 24/7" CTA navigates to /chatbot page
3. Login page has visible "Admin Login" dev shortcut button

actual:
1. Chatbot floating icon hidden behind footer when scrolled to bottom
2. CTA button toggles chatbot widget popup instead of navigating to /chatbot
3. No admin login shortcut on /login page

errors: No runtime errors — purely visual/behavioral bugs.

reproduction:
1. Scroll to bottom of any page — chatbot icon disappears behind footer
2. On homepage, click "Chatbot AI 24/7" CTA — opens widget instead of /chatbot
3. Visit /login — no admin login button visible

started: Pre-existing. Bug 1 may have been partially addressed (position:fixed !important added) but footer z-index may be higher.

## Eliminated

(none yet)

## Evidence

- timestamp: 2026-03-23T01:00:00Z
  checked: static/css/base.css lines 62-130
  found: .chatbot-toggler and .chatbot-window both had z-index: 9999 without !important — susceptible to override by any positioned element or stacking context
  implication: bump to 10000 !important ensures chatbot floats above footer regardless of stacking context

- timestamp: 2026-03-23T01:00:00Z
  checked: templates/index.html line 268
  found: CTA button used onclick="document.body.classList.toggle('show-chatbot')" — opens widget popup, not /chatbot page
  implication: replace <button onclick=...> with <a href="{{ url_for('chatbot.chatbot_page') }}">

- timestamp: 2026-03-23T01:00:00Z
  checked: templates/login.html
  found: no admin link anywhere in the template
  implication: add subtle "Đăng nhập Admin →" link at bottom of card using url_for('admin.admin_login')

- timestamp: 2026-03-23T01:00:00Z
  checked: routes/admin.py line 13
  found: admin_bp uses url_prefix='/admin', login route is /admin/login, url_for name is 'admin.admin_login'
  implication: confirms correct url_for target for admin link

## Resolution

root_cause: |
  Bug 1: .chatbot-toggler and .chatbot-window z-index was 9999 without !important — any parent/sibling stacking context could override it.
  Bug 2: Index.html CTA button used JS toggle (show-chatbot class) instead of href navigation to /chatbot.
  Bug 3: login.html had no link to admin login; devs had to navigate manually.
fix: |
  Bug 1: static/css/base.css — changed z-index to 10000 !important on both .chatbot-toggler and .chatbot-window
  Bug 2: templates/index.html — replaced <button onclick="toggle"> with <a href="{{ url_for('chatbot.chatbot_page') }}">
  Bug 3: templates/login.html — added "Đăng nhập Admin →" link below register link, pointing to url_for('admin.admin_login')
verification: All three changes confirmed in file content. Committed atomically: ac19270, 761a4bf, 0f0135a
files_changed:
  - static/css/base.css
  - templates/index.html
  - templates/login.html
