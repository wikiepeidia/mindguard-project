---
created: 2026-04-13T14:18:35.422Z
title: Fix toast notification hidden behind header
area: ui
files:
  - templates/base.html
  - static/css/base.css
  - static/js/base.js
---

## Problem

Toast notifications (thông báo) đang bị ẩn phía sau header/navbar. Đôi khi không hiển thị gì cả, ví dụ khi đăng nhập thất bại không thấy thông báo lỗi. Nguyên nhân có thể do z-index thấp hơn navbar, hoặc vị trí top bị che bởi fixed header.

## Solution

- Kiểm tra z-index của toast container so với navbar trong `base.html` / `base.css`
- Navbar đang dùng `z-index: 9999` cho dropdown — toast cần cao hơn hoặc đặt vị trí dưới header
- Kiểm tra Flash messages rendering trong `base.html` — có thể bị position issue
- Test case: đăng nhập sai mật khẩu → phải thấy thông báo lỗi rõ ràng
