# 🎯 HƯỚNG DẪN NHANH - CHẠY CÁC TÍNH NĂNG MỚI

## ⚡ Bước 1: Chạy Migration Database

```bash
cd d:\Data_Ngoc\tailieu2025\giaodienapp\mindguard_flask_v2
python database/migrate_add_verification.py
```

## ⚡ Bước 2: Khởi động lại server

```bash
python app.py
```

## ✅ Các Tính Năng Đã Hoàn Thành

### 🏠 Trang Chủ (index.html)
- ✅ Chips gợi ý (SĐT | STK | URL)
- ✅ Placeholder ví dụ rõ ràng
- ✅ Disclaimer về dữ liệu cộng đồng
- ✅ Section "Cách hoạt động" (3 bước)
- ✅ Bảng LIVE với filter (Tất cả/Nguy hiểm/Đã xác minh)
- ✅ Hiển thị verification badge
- ✅ Hiển thị số người xác nhận
- ✅ Click vào scammer → chuyển đến profile page

### 📋 Form Tố Cáo (report_scammer.html)
- ✅ Disclaimer bảo vệ người tố cáo
- ✅ Dropdown danh mục lừa đảo rõ ràng (40+ loại)
- ✅ Phân loại theo nhóm:
  - Lừa đảo tài chính
  - Lừa đảo việc làm
  - Giả danh
  - Mua bán
  - Khác

### 👤 Trang Profile Scammer (NEW)
- ✅ URL: `/scammer/<id>`
- ✅ Hiển thị risk score (0-100) với màu sắc
- ✅ Timeline hoạt động
- ✅ Mask/unmask thông tin nhạy cảm
- ✅ Verification badge
- ✅ Số người xác nhận
- ✅ Bằng chứng đầy đủ
- ✅ Actions: Xác nhận, Chia sẻ, Báo cáo mới

### 🛠️ Backend & Utils
- ✅ Model: verification_status, risk_score, confirmed_by_count
- ✅ `mask_sensitive_data()` - Ẩn SĐT/STK
- ✅ `calculate_risk_score()` - Tính điểm rủi ro
- ✅ `get_verification_badge()` - Badge xác minh
- ✅ `get_risk_level_info()` - Thông tin level
- ✅ Route: `/scammer/<id>` cho profile page

## 🎨 UI/UX Improvements

### Màu Sắc & Badges
- 🔴 Risk ≥ 80: DANGER (Cực kỳ nguy hiểm)
- 🟡 Risk 60-79: WARNING (Rủi ro cao)
- 🔵 Risk 40-59: INFO (Cẩn thận)
- ⚪ Risk < 40: SECONDARY (Rủi ro thấp)

### Verification Status
- ✅ Verified: Badge xanh
- ⏳ Pending: Badge vàng
- ❓ Unverified: Badge xám

## 📊 Test Checklist

- [ ] Trang chủ hiển thị chips và disclaimer
- [ ] Filter LIVE hoạt động (click Nguy hiểm/Đã xác minh)
- [ ] Click scammer → vào profile page
- [ ] Profile page hiển thị risk score đúng
- [ ] Toggle mask/unmask hoạt động
- [ ] Timeline hiển thị đúng thời gian
- [ ] Form report có dropdown danh mục
- [ ] Disclaimer hiển thị trong form

## 🚀 Tính Năng Tiếp Theo (P1)

### Ưu tiên cao:
1. **Subscribe & Cảnh báo**
   - Theo dõi SĐT/STK/URL
   - Push notification khi có báo cáo mới

2. **Share Link Cảnh báo**
   - Tạo link chia sẻ tùy chỉnh
   - QR code cho dễ share

3. **Xác nhận báo cáo**
   - User có thể confirm báo cáo
   - Tăng confirmed_by_count
   - Tăng risk_score

### ML Stage 1:
1. **Auto-tag**
   - Từ description → suggest loại
   - NLP cơ bản

2. **Entity Extraction**
   - Tự tách SĐT/STK/URL từ text
   - Chuẩn hóa format

3. **Deduplication**
   - Phát hiện báo cáo trùng
   - Similarity scoring

## 📝 Files Đã Thay Đổi

### Modified:
- `models.py` - Thêm 3 fields mới
- `utils/helpers.py` - Thêm 4 functions
- `routes/main.py` - Thêm route profile + update index
- `templates/index.html` - Chips, disclaimer, section, filter
- `templates/report_scammer.html` - Disclaimer, dropdown danh mục

### Created:
- `templates/scammer_profile.html` - NEW profile page
- `database/migrate_add_verification.py` - Migration script
- `documents/IMPROVEMENTS_REPORT.md` - Tài liệu chi tiết

## ⚠️ Lưu Ý Quan Trọng

1. **Phải chạy migration** trước khi test
2. **Risk score** tự động tính lần đầu xem profile
3. **Mask data** mặc định, cần click "Xem đầy đủ"
4. **Filter** hoạt động client-side (nhanh)

## 🐛 Troubleshooting

### Lỗi "column not found"
→ Chưa chạy migration, run `migrate_add_verification.py`

### Profile page 404
→ Check route đã register trong `app.py` chưa

### Mask function không hoạt động
→ Check import `mask_sensitive_data` trong route

### Risk score = 0
→ Bình thường, sẽ tự tính khi vào profile page lần đầu
