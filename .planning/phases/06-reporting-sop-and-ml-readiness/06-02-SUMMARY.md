---
phase: 06-reporting-sop-and-ml-readiness
plan: 02
status: complete
completed_at: "2026-03-26"
subsystem: ml-readiness-docs
tags: [documentation, ml, moderation, roadmap, data-labeling]
dependency_graph:
  requires: [06-01, models/models.py, routes/admin.py, routes/scammer.py, datasets/scam_dataset_export.csv]
  provides: [ml-data-contract, ml-moderation-roadmap]
  affects: [documents/SOP/ML_DU_LIEU_GAN_NHAN.md, documents/SOP/ML_MODERATION_ROADMAP.md]
key_files:
  created:
    - documents/SOP/ML_DU_LIEU_GAN_NHAN.md
    - documents/SOP/ML_MODERATION_ROADMAP.md
---

# Phase 06 Plan 02 Summary

Đã hoàn thành bộ tài liệu readiness cho dữ liệu và ML moderation sau v1 trong thư mục `documents/SOP/`.

## Ket qua chinh

- Định nghĩa schema nhãn, cửa sổ thu thập 1 tháng, quy tắc ẩn danh và bộ xuất train-ready.
- Xác định rõ các trường production không được rời khỏi vùng quản trị được bảo vệ.
- Tạo roadmap offline-first theo từng giai đoạn: QA dữ liệu, baseline ML, DL tùy chọn, offline evaluation, shadow mode, human-in-the-loop.
- Giữ rõ phạm vi chưa đưa auto moderation vào v1.

## Xac minh

- `rg "1 tháng|nhãn|ẩn danh|xuất dữ liệu|v1|moderation" documents/SOP/ML_DU_LIEU_GAN_NHAN.md`
- `rg "offline|shadow|human-in-the-loop|precision|false-positive|rollback" documents/SOP/ML_MODERATION_ROADMAP.md`

## Dau ra

- `documents/SOP/ML_DU_LIEU_GAN_NHAN.md`
- `documents/SOP/ML_MODERATION_ROADMAP.md`
