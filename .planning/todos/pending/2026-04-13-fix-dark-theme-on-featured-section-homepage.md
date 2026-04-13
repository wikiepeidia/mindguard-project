---
created: 2026-04-13T14:18:35.422Z
title: Fix dark theme on featured section homepage
area: ui
files:
  - templates/index.html
  - static/css/homepage.css
---

## Problem

Section "Tính năng nổi bật" trên trang chủ có giao diện rất xấu: text đen, icon robot đen, trông khủng khiếp ("horrible"). Cần redesign section này cho phù hợp với glassmorphism/light mode theme đã áp dụng cho phần còn lại của trang.

Nội dung section:
- "Chatbot AI 24/7"
- "Nghi ngờ một tin nhắn lạ? Copy và gửi ngay cho AI. Hệ thống phân tích ngôn ngữ, kiểm tra đường link và đưa ra cảnh báo trong vài giây."

## Solution

- Redesign section "Tính năng nổi bật" với light mode/glassmorphism theme matching rest of homepage
- Đổi icon robot sang màu phù hợp (primary color hoặc gradient)
- Text color phải phù hợp với design tokens đã có
- Cân nhắc card-based layout với subtle shadows/borders thay vì plain black text
