---
created: 2026-04-13T14:18:35.422Z
title: Fix blurry red badge stats on homepage
area: ui
files:
  - templates/index.html
  - static/css/homepage.css
---

## Problem

Các huy hiệu/badge đỏ chứa text trắng trên trang chủ (LIVE, 42 Tố cáo, Đánh cắp tài khoản (Phishing)) hiển thị cực kỳ mờ (blur). Text trắng trên nền đỏ không rõ ràng, khó đọc. Có thể do CSS filter, opacity, hoặc font rendering issues.

## Solution

- Kiểm tra `templates/index.html` và `static/css/homepage.css` cho các badge/stat elements
- Tìm CSS `filter: blur()`, `opacity`, hoặc `backdrop-filter` ảnh hưởng đến badge
- Đảm bảo contrast ratio đủ (text trắng trên nền đỏ)
- Test trên multiple browsers (Chrome, Firefox)
