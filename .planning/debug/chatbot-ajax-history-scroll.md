---
status: awaiting_human_verify
trigger: "Investigate and fix the remaining chatbot bugs in the MindGuard Flask app."
created: 2026-03-26T20:35:03+07:00
updated: 2026-03-26T20:42:04+07:00
---

## Current Focus

hypothesis: The applied fix removes the page/API split by routing both fallback POSTs and async sends through the same persistence helper, updates the DOM in place with returned session metadata, and limits initial auto-scroll to existing saved sessions only.
test: Human verification in the logged-in browser flow for composer submit, suggestion submit, sidebar update, reload persistence, and initial scroll behavior.
expecting: Sending from /chatbot/ should stay inline without a full refresh, create or reuse a saved session that appears in the sidebar, survive reload via session_id, and avoid jumping to the bottom on a fresh page load.
next_action: wait for user confirmation from the real browser workflow

## Symptoms

expected: Sending a message on /chatbot/ should happen inline like a real chat app without a full page refresh. Messages should persist into a session so the history sidebar works. The page should not jump to the bottom on initial load unless the user is opening an existing conversation and it makes sense to reveal the newest message.
actual: Every message submit reloads the entire page. The history sidebar/session flow does not work correctly. The page scrolls all the way to the bottom for some reason.
errors: No traceback reported. Current implementation suggests a flow bug rather than server crash.
reproduction: Open /chatbot/ while logged in, send a message from the main composer, then inspect whether the page reloads, whether a session is created and appears in history, and whether the viewport jumps to the bottom.
started: Current state after the chatbot visual revamp.

## Eliminated

## Evidence

- timestamp: 2026-03-26T20:35:03+07:00
 checked: templates/chatbot.html
 found: Both the empty-state suggestion cards and main composer are plain method="post" forms on /chatbot/ with no async hook or session state container.
 implication: Submitting a message triggers a full-page POST render instead of the existing JSON send endpoint.

- timestamp: 2026-03-26T20:35:03+07:00
 checked: static/js/chatbot_page.js
 found: The page script only registers DOMContentLoaded and always sets chatHistoryContainer.scrollTop = scrollHeight.
 implication: Any page load with a chat container will jump to the bottom regardless of whether the user opened a fresh page or an existing session.

- timestamp: 2026-03-26T20:35:03+07:00
 checked: routes/chatbot.py
 found: chatbot_page handles POST by building a local history list and rendering the page again, while /chatbot/send separately persists AiChatSession and AiChatMessage records and returns JSON.
 implication: The page route and async API are split paths; the UI currently uses the wrong one, so history sidebar state never gets real persisted data from normal sends.

- timestamp: 2026-03-26T20:35:03+07:00
 checked: tests/test_chatbot.py
 found: Existing tests cover the JSON send endpoint persistence but do not cover chatbot_page POST fallback, async render-state markers, or initial scroll conditions.
 implication: The current regression suite would not catch the UI being wired back to the full-page POST flow.

- timestamp: 2026-03-26T20:42:04+07:00
 checked: routes/chatbot.py, templates/chatbot.html, static/js/chatbot_page.js
 found: The page route now redirects POST fallback through the same DB-backed persistence helper as /chatbot/send, the template exposes stable async hooks and session state, and the page script updates messages/sidebar/URL inline while gating initial scroll behind data-initial-scroll.
 implication: The UI and backend now share a single session creation/update path, eliminating the transient history flow and unconditional load scroll.

- timestamp: 2026-03-26T20:42:04+07:00
 checked: python -m unittest tests.test_chatbot
 found: 6 chatbot tests passed, covering async page hooks, JSON send persistence metadata, POST fallback persistence redirect, session reuse, and initial-scroll markers for saved sessions.
 implication: The updated contract is covered by targeted regression tests and passed automated verification.

## Resolution

root_cause: The chatbot revamp left two independent message-send paths in place. The template still submitted plain POST forms to chatbot_page, but only /chatbot/send persisted AiChatSession and AiChatMessage records. As a result, normal sends reloaded the page and rendered a transient history list that never reached the sidebar. Separately, chatbot_page.js always scrolled the message container to the bottom on DOMContentLoaded, so even fresh loads jumped unexpectedly.
fix: Extracted a shared persistence helper in routes/chatbot.py and used it from both /chatbot/send and the page POST fallback. Updated templates/chatbot.html with explicit async hooks, sidebar/message containers, hidden session state, and a guarded data-initial-scroll flag. Replaced static/js/chatbot_page.js with an async client flow that intercepts composer and suggestion submits, posts to /chatbot/send, appends messages inline, updates the sidebar/session count/current URL, and only auto-scrolls on initial load for saved sessions.
verification: get_errors reported no issues in the edited route, template, JS, and test files. python -m unittest tests.test_chatbot passed with 6 tests. Those tests verify the async render markers, JSON send metadata persistence, page POST fallback persistence redirect, session reuse, and the initial-scroll flag for re-opened history.
files_changed: [routes/chatbot.py, templates/chatbot.html, static/js/chatbot_page.js, tests/test_chatbot.py]
