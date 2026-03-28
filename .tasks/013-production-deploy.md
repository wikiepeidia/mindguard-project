---
id: "013"
title: "Set up production deployment"
status: "todo"
area: "infra"
agent: "@docker-expert"
priority: "low"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: []
blocks: []
blocked_by: ["008"]
---

## Description

Set up a production deployment pipeline. This is blocked until secrets are moved to environment variables (#008) and a hosting target is decided (open question in PRD). Options include: VPS with Docker, Railway, Render, or Fly.io.

## Acceptance Criteria

- [ ] Dockerfile created for the Flask application
- [ ] docker-compose.yml for local production-like testing
- [ ] Production configuration (gunicorn/waitress instead of Flask dev server)
- [ ] Health check endpoint added
- [ ] Deployment documentation written
- [ ] ARCHITECTURE.md infrastructure section updated

## Technical Notes

- Currently using Flask's built-in dev server (`python app.py`) — not production-ready
- Consider gunicorn (Linux) or waitress (Windows-compatible) as WSGI server
- Static files may need a reverse proxy (nginx) in production
- The `.env/` JSON config system needs to work in containerized environments
- Hosting target decision is an open question — design for portability

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
