---
phase: 12-ai-safety
plan: 01
status: complete
started: 2026-04-13T14:40:00.000Z
completed: 2026-04-13T14:55:00.000Z
---

## One-liner

Reduced chatbot OpenRouter timeout from 10s to 8s (AISF-01) and deployed to Vercel production with ADMIN_PASSWORD + REPORT_ENCRYPTION_KEY env vars set.

## What Changed

### Task 1: Fix chatbot timeout (AISF-01)
- `utils/chatbot.py:66` — `timeout=10` → `timeout=8`
- Rationale: Vercel hobby tier kills functions after 10s. timeout=10 races with the kill signal; buffer of 2s ensures response serializes and returns before kill.
- Commit: `fix(chatbot): reduce OpenRouter timeout 10s -> 8s to avoid Vercel kill (AISF-01)`

### Task 2: Set Vercel env vars (INFRA-02 carry-over)
- User set `ADMIN_PASSWORD` via `vercel env add ADMIN_PASSWORD production`
- User set `REPORT_ENCRYPTION_KEY` via `vercel env add REPORT_ENCRYPTION_KEY production`
- Code was already correct from Phase 10 — this closes the env var gap

### Task 3: Deploy + verify
- `vercel --prod --yes` — deployment ✅ Ready in 27s
- Production URL: `https://mindguard-five.vercel.app`

## Verify Results

```
grep timeout=8 utils/chatbot.py → line 66 confirmed
grep timeout=10 utils/chatbot.py → no results

Health checks (mindguard-five.vercel.app):
  / → HTTP 200 ✅
  /quiz → HTTP 200 ✅
  /admin/login → HTTP 200 ✅
  /chatbot/api → HTTP 200, 3.6s ✅ (under 8s limit)

Chatbot API response: Vietnamese fraud warning about bank scams — AI responding correctly.
```

## Key Files

- `utils/chatbot.py` — timeout=8 at line 66

## Self-Check: PASSED

- [x] `utils/chatbot.py` contains `timeout=8`
- [x] `utils/chatbot.py` does NOT contain `timeout=10`
- [x] Vercel deployment ✅ Ready (27s build)
- [x] Homepage returns 200
- [x] Chatbot API returns 200 in < 8s (3.6s actual)
- [x] AISF-01 requirement satisfied

## Known Pre-existing Issues (not caused by Phase 12)

- `/auth/login` returns 404 on production — pre-existing Flask routing issue
- `/report` returns 404 on production — pre-existing issue
- `/quiz/start` returns 404 on production — pre-existing issue
- These routes work locally but something in Vercel routing/blueprint registration is broken

## Deviations

None — all tasks completed as planned.

## AISF Requirements Status

| Req | Description | Status | Notes |
|-----|-------------|--------|-------|
| AISF-01 | Chatbot timeout ≤ 8s | ✅ Complete | timeout=8 deployed, 3.6s actual response |
| AISF-02 | Sensitive topic safe reply + 113 hotline | ✅ Pre-done by teammate | `_SENSITIVE_KEYWORDS` + `_SAFE_FALLBACK` in chatbot.py |
| AISF-03 | Uncertainty warning + contact guidance | ✅ Pre-done by teammate | System prompt rule #4 in `SYSTEM_PROMPT_DEFAULT` |
| AISF-04 | Plain language system prompt | ✅ Pre-done by teammate | System prompt in Vietnamese, no tech jargon |
