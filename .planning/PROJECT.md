# MindGuard v2

## What This Is

MindGuard v2 la nen tang giao duc an toan mang va phong chong lua dao duoc xay dung bang Flask. He thong cung cap bai quiz nhan thuc, chatbot huong dan, bao cao doi tuong lua dao, va dashboard quan tri de theo doi du lieu. Ung dung su dung NeonDB PostgreSQL va deploy len Vercel de san sang production.

## Core Value

Nguoi dung co the hoc, kiem tra nhan thuc va gui bao cao lua dao mot cach de dung, an toan, va dang tin cay.

## Current Milestone: v1.1 PostgreSQL & Vercel Deployment

**Goal:** Migrate toan bo SQLite sang NeonDB PostgreSQL va fix Vercel deployment (500 errors), dua MindGuard len production on dinh.

**Target features:**

- Migrate tat ca SQLAlchemy models sang NeonDB PostgreSQL
- Cau truc lai `.env/prosgressql_neondb.json` thanh JSON hop le
- Fix Vercel 500 errors khi deploy
- Seed data chi chay 1 lan (khong seed moi cold start)
- NeonDB dung cho ca local dev va production

## Requirements

### Validated

- ✓ Dang ky/dang nhap nguoi dung qua email va session — v1.0
- ✓ Lam quiz va xem ket qua/chung nhan — v1.0
- ✓ Gui bao cao lua dao kem bang chung — v1.0
- ✓ Chatbot ho tro hoi dap co fallback — v1.0
- ✓ Quan tri vien co dashboard rieng de quan ly — v1.0
- ✓ Light mode dong bo tren cac trang chinh — v1.0
- ✓ Design tokens thong nhat (mau, font, spacing) — v1.0
- ✓ Quiz 1 cau hoi/trang voi tien do ro rang — v1.0
- ✓ Anti-spam da tin hieu (IP + cookie + account) — v1.0
- ✓ Bang vinh danh voi integrity rules — v1.0
- ✓ SOP bao cao va ML readiness — v1.0

### Active

- [ ] Migrate toan bo database tu SQLite sang NeonDB PostgreSQL
- [ ] Fix Vercel deployment 500 errors
- [ ] Seed data strategy cho PostgreSQL (one-time, khong ephemeral)
- [ ] Config JSON hop le cho NeonDB connection

### Out of Scope

- Dark mode trong v1.1 — uu tien infrastructure stability
- Tinh nang khong lien quan truc tiep den giao duc/chong lua dao — khong phuc vu core value
- Auto-scaling/multi-region — v1.1 chi can 1 region on dinh
- Migration tool tu dong (Alembic/flask-migrate) — dung manual scripts theo conventions

## Context

Du an da hoan thanh v1.0 voi 6 phases (Privacy, Anti-Spam, Light Mode, Quiz Flow, Leaderboard, Docs/ML). Hien tai dang chay tren SQLite + Vercel nhung gap 500 errors khi deploy. NeonDB PostgreSQL da co connection string san. Can migrate toan bo models sang Postgres va fix Vercel config de ung dung chay on dinh tren production.

## Constraints

- **Tech stack**: Flask + NeonDB PostgreSQL + SQLAlchemy + Jinja — chuyen tu SQLite sang Postgres
- **Database**: NeonDB PostgreSQL cho ca local va production — khong phan tach env
- **Deployment**: Vercel serverless — read-only filesystem, ephemeral function instances
- **Compatibility**: Phai giu backward-compatible voi data structure hien tai — khong mat du lieu
- **Security**: Connection string va credentials phai duoc bao ve trong .env/ — khong commit secrets

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Uu tien light mode va UX quiz lam trung tam v1 | Nhu cau uu tien cao nhat tu nguoi dung la UI/UX | ✓ Good |
| Giu kien truc Flask brownfield, nang cap theo tung pha | Giam rui ro hoi quy va tan dung he thong dang chay | ✓ Good |
| Dua anti-spam (rule tan suat + IP/cookie tracking) vao v1 | Bao ve chat luong du lieu bao cao va han che gian lan | ✓ Good |
| Migrate toan bo sang NeonDB PostgreSQL cho v1.1 | SQLite khong phu hop Vercel serverless (ephemeral /tmp), NeonDB da co san | — Pending |
| NeonDB cho ca local va production | Don gian hoa config, tranh sqlite/postgres incompatibility | — Pending |
| Postgres truoc, Vercel fix sau | DB on dinh la tien quyet de debug deployment | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-03 after milestone v1.1 initialization*
