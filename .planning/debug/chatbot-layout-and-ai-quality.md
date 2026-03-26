---
status: awaiting_human_verify
trigger: "Investigate and fix the chatbot page and AI response quality issues in the MindGuard Flask app."
created: 2026-03-26T00:00:00Z
updated: 2026-03-26T00:00:00Z
---

## Current Focus

hypothesis: The applied fix removed duplicated top offset handling and replaced stale/unsafe model handling with a reliable provider-or-fallback reply path.
test: Human verification in the real browser session: confirm the chatbot page sits flush under the navbar and a high-risk prompt now returns coherent guidance.
expecting: No large blank band above the chatbot header, and chatbot replies should be coherent even when OpenRouter rate-limits because the response will degrade to the structured local fallback.
next_action: wait for user confirmation from real workflow/browser

## Symptoms

expected: The chatbot page should render flush under the navbar without large blank gaps or shifted header layout; chat history/sidebar and message area should display correctly; AI responses should be relevant, coherent, and based on the configured AI provider or a sane fallback.
actual: Screenshot shows a large blank area above the chatbot header/content, suggesting the page layout is still offset or overlaid incorrectly. The user also reports the AI responses are nonsense/garbage, implying a broken API call, bad prompt/response handling, or bad fallback behavior.
errors: No explicit traceback provided. Prior issues included 405 on chatbot POST and layout regressions from CSS overrides. Current issue is visual breakage and poor AI output quality.
reproduction: Open <http://127.0.0.1:5000/chatbot/> while logged in; observe top blank region and layout problems. Send a chatbot message such as "Tôi đã bị lừa tiền, phải làm sao?" and inspect the returned response quality.
started: Ongoing after recent chatbot UI/CSS changes.

## Eliminated

## Evidence

- timestamp: 2026-03-26T00:00:00Z
  checked: .planning/debug/knowledge-base.md
  found: No resolved knowledge-base entry had a strong 2+ keyword overlap for this combined chatbot layout plus AI quality regression.
  implication: Proceed with fresh investigation instead of biasing toward an older fix.

- timestamp: 2026-03-26T00:00:00Z
  checked: templates/chatbot.html, templates/base.html, static/css/chatbot.css, static/css/base.css
  found: The chatbot page renders through base.html, which still injects a global 80px spacer div and an absolutely positioned flash container near the top while chatbot.css also fixes the page wrapper to the viewport with its own 76px top padding.
  implication: The page likely has stacked top-offset mechanisms from both shared layout and page-specific CSS, making the blank region/layout shift a high-probability root cause.

- timestamp: 2026-03-26T00:00:00Z
  checked: routes/chatbot.py, utils/chatbot.py, config.py
  found: Chat routes call query_ai_model() directly and silently fall back to simple_bot_reply(); the AI helper cycles through a free-model list with minimal validation and generic prompting, and config prioritizes several low-quality/free models ahead of Gemini.
  implication: Coherent responses depend on whichever free model replies first, and failures degrade to a very generic fallback with no observability in the HTTP response.

- timestamp: 2026-03-26T00:00:00Z
  checked: live query through utils.chatbot.query_ai_model with prompt "Tôi đã bị lừa tiền, phải làm sao?"
  found: The current helper returned garbled Vietnamese text instead of a coherent incident-response answer.
  implication: The chatbot issue is reproducible in the real provider path, not just a user perception problem.

- timestamp: 2026-03-26T00:00:00Z
  checked: direct OpenRouter calls for configured model list
  found: liquid/lfm-2.5-1.2b-instruct:free and liquid/lfm-2.5-1.2b-thinking:free returned low-quality/garbled Vietnamese; allenai/molmo-2-8b:free returned HTTP 404; google/gemini-2.0-flash-lite-preview-02-05:free returned HTTP 400.
  implication: The configured model chain is both stale and quality-unsafe, so the helper must stop trusting the first successful response and config must prefer live text models.

- timestamp: 2026-03-26T00:00:00Z
  checked: live OpenRouter model catalog and spot checks of current free text models
  found: The current catalog exposes different free text models such as mistralai/mistral-small-3.1-24b-instruct:free and qwen/qwen3-next-80b-a3b-instruct:free, while multiple candidate requests were temporarily rate-limited with HTTP 429.
  implication: Provider availability is volatile, so a sane on-box fallback is required even after updating the model list.

- timestamp: 2026-03-26T00:00:00Z
  checked: python -m unittest tests.test_chatbot
  found: 4 targeted regression tests passed, covering layout override rendering, low-quality AI reply detection, actionable fallback content, and chatbot send-route metadata/session persistence.
  implication: The code changes are consistent with the intended layout and chatbot reply behavior under automated verification.

- timestamp: 2026-03-26T00:00:00Z
  checked: test-client GET /chatbot/ and runtime generate_chatbot_reply probe
  found: Rendered chatbot HTML no longer contains the shared 80px spacer or floating global flash wrapper, and a live high-risk prompt now returns a coherent Vietnamese fallback response with source=fallback when OpenRouter is rate-limited.
  implication: The layout regression is removed at template-render level and the chatbot no longer surfaces garbage text when the provider path is unhealthy.

## Resolution

root_cause: The chatbot page was inheriting shared base spacer/flash layout while also applying its own fixed fullscreen offset, creating duplicated top spacing; meanwhile the chatbot AI pipeline trusted stale or low-quality free OpenRouter model IDs and surfaced the first provider response without meaningful guardrails, so broken model output reached users directly.
fix: Added override blocks in base.html so chatbot.html can disable the shared navbar spacer and floating flash wrapper, simplified chatbot viewport positioning to a single top offset, replaced the stale OpenRouter model list with live text-capable IDs, routed chatbot replies through a new metadata-aware helper, rejected obviously broken provider output, and expanded the local Vietnamese fallback so rate limits or provider failures still produce useful guidance.
verification: get_errors reported no file errors; python -m unittest tests.test_chatbot passed (4 tests); a test-client GET /chatbot/ confirmed the shared spacer/global flash markup is absent; a live generate_chatbot_reply probe for "Tôi đã bị lừa tiền, phải làm sao?" returned coherent fallback guidance with source=fallback while OpenRouter was returning HTTP 429 upstream.
files_changed: [templates/base.html, templates/chatbot.html, static/css/chatbot.css, config.py, utils/chatbot.py, routes/chatbot.py, tests/test_chatbot.py]
