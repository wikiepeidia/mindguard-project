---
id: "002"
title: "Fix chatbot 405 Method Not Allowed error"
status: "todo"
area: "backend"
agent: "@backend-developer"
priority: "high"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: ["FR-030", "FR-031"]
blocks: []
blocked_by: []
---

## Description

The chatbot feature returns a `405 Method Not Allowed` error. This means a route is being accessed with an HTTP method (GET/POST) that the route handler does not accept. The chatbot is a core feature (FR-030) and must be functional for v1.

## Acceptance Criteria

- [ ] Chatbot page loads without errors at `/chatbot`
- [ ] Users can send messages and receive AI responses
- [ ] Chat session persistence works correctly (FR-031)
- [ ] Relevant tests written and passing

## Technical Notes

- Check `routes/chatbot.py` for route definitions — verify `methods=["GET", "POST"]` are both allowed
- Check if the AJAX/fetch calls from `templates/chatbot.html` use the correct HTTP method
- Check `utils/chatbot.py` and `utils/ai_agent.py` for the message handling pipeline
- The OpenRouter API key in `.env/chatbot.json` must be valid for AI responses to work

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
