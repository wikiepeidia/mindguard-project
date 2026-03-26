---
phase: 06-reporting-sop-and-ml-readiness
plan: 01
status: complete
completed_at: "2026-03-26"
subsystem: reporting-docs
tags: [documentation, reporting, sop, user-guide, operations]
dependency_graph:
  requires: [routes/scammer.py, routes/admin.py, templates/report_scammer.html, templates/admin_scammer_reports.html]
  provides: [reporting-user-guide, admin-reporting-sop]
  affects: [documents/SOP/HUONG_DAN_BAO_CAO_NGUOI_DUNG.md, documents/SOP/SOP_BAO_CAO.md, documents/SOP/README.md]
key_files:
  created:
    - documents/SOP/HUONG_DAN_BAO_CAO_NGUOI_DUNG.md
    - documents/SOP/SOP_BAO_CAO.md
    - documents/SOP/README.md
---

# Phase 06 Plan 01 Summary

Đã hoàn thành bộ tài liệu vận hành báo cáo bằng tiếng Việt trong thư mục `documents/SOP/`.

## Ket qua chinh

- Tạo hướng dẫn người dùng cho luồng gửi báo cáo với các bước, bằng chứng, CAPTCHA, điều khoản và giải thích trạng thái.
- Tạo quy trình xử lý cho quản trị viên về kiểm duyệt báo cáo, xem bằng chứng, phê duyệt, từ chối và xuất dữ liệu theo workflow hiện tại.
- Gom tài liệu vào thư mục `documents/SOP/` để dễ quản lý và bàn giao.
- Chèn placeholder ảnh minh họa theo format `PLACEHOLDER_HINH_XX` để bổ sung sau.

## Xac minh

- `rg "PLACEHOLDER_HINH_|Trạng thái|bằng chứng|CAPTCHA|điều khoản" documents/SOP/HUONG_DAN_BAO_CAO_NGUOI_DUNG.md`
- `rg "PLACEHOLDER_HINH_|Phê duyệt|Từ chối|Xuất dữ liệu|bảo mật|quyền riêng tư" documents/SOP/SOP_BAO_CAO.md`

## Dau ra

- `documents/SOP/HUONG_DAN_BAO_CAO_NGUOI_DUNG.md`
- `documents/SOP/SOP_BAO_CAO.md`
- `documents/SOP/README.md`
