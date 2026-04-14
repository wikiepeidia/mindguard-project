# Phase 15: Conventions & Redaction Setup — Context

**Created**: 2026-04-14
**Phase Goal**: Quy ước viết tài liệu và bảo vệ thông tin nhạy cảm được thiết lập trước khi viết bất kỳ tài liệu nào.
**Requirements**: CONV-01, CONV-02

## Decisions Made

### 1. `.env.example` — Flat, Vercel-oriented (Option A)

**Decision**: Tạo một file `.env.example` phẳng liệt kê tất cả env vars cần thiết — không tạo example JSON files.

**Rationale**:
- Vercel deployment dùng env vars, không dùng JSON files.
- JSON pattern (`.env/*.json`) là legacy cho local dev — team đã quen, không cần document lại.
- Một file duy nhất đơn giản hơn để maintain.
- Comments trong file sẽ giải thích nguồn gốc (Vercel Dashboard, OpenRouter, Cloudflare).

**Env vars cần liệt kê** (từ `config.py`):
- `SECRET_KEY` — Flask session secret
- `DATABASE_URL` — NeonDB PostgreSQL connection string
- `OPENROUTER_API_KEY` — AI chatbot API key
- `CLOUDFLARE_SITE_KEY` — Turnstile CAPTCHA public key
- `CLOUDFLARE_SECRET_KEY` — Turnstile CAPTCHA secret key
- `ADMIN_PASSWORD` — Admin login password
- `REPORT_ENCRYPTION_KEY` — Encryption key for sensitive report data
- `ADMIN_UNSUSPEND_SECRET` — Secret to unlock suspended admin accounts
- `ABUS_MODE` — Anti-spam mode (monitor/enforce), default: monitor
- `ABUS_WINDOW_MINUTES` — Anti-spam time window, default: 10
- `ABUS_THRESHOLD_COUNT` — Anti-spam threshold, default: 3
- `ABUS_COOLDOWN_MINUTES` — Anti-spam cooldown, default: 15
- `ABUS_ACCOUNT_WEIGHT` — Anti-spam account weight, default: 70
- `ABUS_COOKIE_WEIGHT` — Anti-spam cookie weight, default: 20
- `ABUS_IP_WEIGHT` — Anti-spam IP weight, default: 10

### 2. Conventions file — `docs/technical/CONVENTIONS.md`

**Decision**: Đặt file quy ước ngôn ngữ tại `docs/technical/CONVENTIONS.md`.

**Rationale**:
- `.planning/codebase/CONVENTIONS.md` là file GSD-internal (code conventions), không phải doc conventions.
- `docs/technical/` là nơi tự nhiên cho tài liệu kỹ thuật dành cho team.
- Tách biệt rõ: code conventions (GSD) vs doc conventions (team-facing).

### 3. Glossary — Minimal (~20-30 terms)

**Decision**: Bảng thuật ngữ chỉ bao gồm ~20-30 thuật ngữ kỹ thuật cốt lõi.

**Rationale**:
- Team nhỏ, đọc code hàng ngày — không cần glossary dài.
- Tập trung vào thuật ngữ dễ nhầm (vd: "blueprint" vs "route", "serverless function" vs "endpoint").
- Dễ maintain hơn comprehensive glossary.

### 4. Redaction — Docs-only rules, không thay đổi code

**Decision**: Phase 15 chỉ thiết lập rules ngăn secrets xuất hiện trong tài liệu. Không chỉnh sửa `config.py`.

**Rationale**:
- v1.3 là docs-only milestone — không thay đổi code.
- `config.py` hardcoded fallbacks (SECRET_KEY, ADMIN_UNSUSPEND_SECRET) là vấn đề INFRA-02 thuộc v1.2.
- Redaction rules sẽ bao gồm: never copy real values, use `<PLACEHOLDER>` format, list known danger patterns.

## Codebase References

### Config pattern (`config.py`)
- `load_local_env()` reads `.env/*.json` (cloudflare.json, chatbot.json, postgresql_neondb.json, ngrok.json)
- Env vars take priority: `os.environ.get("KEY") or json_config.get("KEY")`
- Anti-spam vars have default values via `int(os.environ.get("KEY", default))`

### Existing docs state
- `docs/technical/ARCHITECTURE.md` — Outdated (says SQLite)
- `docs/technical/API.md` — Empty template, wrong assumptions
- `docs/technical/DATABASE.md` — Empty template, wrong schema
- `docs/technical/DECISIONS.md` — Only ADR-001
- `documents/SOP/SOP_BAO_CAO.md` — Exists, needs update

### Existing conventions
- `.planning/codebase/CONVENTIONS.md` — GSD-internal code conventions (snake_case, Flask patterns, etc.)
- Vietnamese comments in code, Vietnamese flash messages
- No formal doc-writing conventions exist yet

## Constraints

- Không thay đổi bất kỳ file code nào (routes, models, utils, config).
- `.env.example` phải được thêm vào `.gitignore` review — đảm bảo `.env/` bị ignore nhưng `.env.example` thì không.
- Tất cả output bằng tiếng Việt, thuật ngữ kỹ thuật giữ nguyên tiếng Anh.

## Success Criteria (from ROADMAP.md)

1. `.env.example` tồn tại, liệt kê tất cả biến môi trường cần thiết với giá trị placeholder — không chứa secret thật.
2. Có file quy ước ngôn ngữ Việt-Anh: prose viết bằng tiếng Việt, thuật ngữ kỹ thuật giữ nguyên tiếng Anh, bảng thuật ngữ đi kèm.
3. Tất cả tài liệu viết ở các phase sau tuân thủ quy ước ngôn ngữ và không chứa credential/secret thật.
