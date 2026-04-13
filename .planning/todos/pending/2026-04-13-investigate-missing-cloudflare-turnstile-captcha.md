---
created: 2026-04-13T14:18:35.422Z
title: Investigate missing Cloudflare Turnstile CAPTCHA
area: auth
files:
  - templates/register.html
  - templates/login.html
  - templates/report_scammer.html
  - utils/helpers.py
  - config.py
---

## Problem

Teammate có thể đã xóa Cloudflare Turnstile CAPTCHA khỏi app trong code drop. Cần kiểm tra xem CAPTCHA có còn hoạt động không. Hiện tại app có math CAPTCHA backup.

User hỏi: có nên dùng cả Math CAPTCHA + Cloudflare Turnstile không?

## Solution

- Kiểm tra các form templates (register, login, report_scammer) xem Cloudflare Turnstile widget còn không
- Kiểm tra `utils/helpers.py` cho hàm verify Turnstile
- Kiểm tra `config.py` và `.env/cloudflare.json` cho API keys
- **Đề xuất**: Dùng cả hai — Math CAPTCHA làm fallback khi Cloudflare không load được (đã có pattern này trong codebase). Cloudflare cho bảo vệ tốt hơn, Math CAPTCHA cho offline/fallback.
