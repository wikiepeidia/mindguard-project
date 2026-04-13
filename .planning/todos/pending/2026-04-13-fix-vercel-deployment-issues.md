---
created: 2026-04-13T14:18:35.422Z
title: Fix Vercel deployment issues
area: infra
files:
  - vercel.json
  - app.py
  - config.py
  - requirements.txt
---

## Problem

Vercel deployment đang bị lỗi sau code drop từ teammate. Chi tiết lỗi cần được điều tra — có thể do:
- Thay đổi trong `requirements.txt` (packages mới/xóa)
- Thay đổi trong `app.py` hoặc `config.py` ảnh hưởng startup
- Env vars trên Vercel dashboard cần cập nhật
- `db.create_all()` vẫn chạy on cold start (liên quan INFRA-01)

## Solution

- Kiểm tra Vercel deployment logs cho error messages cụ thể
- So sánh `requirements.txt` hiện tại vs trước code drop
- Verify env vars trên Vercel dashboard match config
- Fix INFRA-01 (xóa `db.create_all()`) có thể giải quyết một phần
- Redeploy sau khi fix các issues trong Phase 10
