# 🚀 Cải Tiến Hệ Thống Báo Cáo Lừa Đảo

## ✨ Tính Năng Mới (P0 - Ưu Tiên Cao)

### 1. **Trust Cues & Tránh Rủi Ro Pháp Lý**

#### 🔐 Trạng Thái Xác Minh
Mỗi báo cáo giờ đây có 3 trạng thái:
- ❓ **Chưa xác minh** (unverified) - Mặc định khi tạo mới
- ⏳ **Đang xác minh** (pending) - Đang được kiểm tra
- ✅ **Đã xác minh** (verified) - Đã được xác nhận

#### 🎭 Ẩn/Mask Thông Tin Nhạy Cảm
- SĐT: `0912345678` → `091***5678`
- STK: `123456789012` → `1234***9012`
- Người dùng phải bấm "Xem đầy đủ" để hiển thị

#### ⚖️ Disclaimer Rõ Ràng
Hiển thị ngay dưới ô tìm kiếm:
> "Dữ liệu do cộng đồng cung cấp, kết quả mang tính cảnh báo — vui lòng kiểm chứng trước khi giao dịch."

### 2. **Tối Ưu Ô Tra Cứu**

#### 🏷️ Chips Gợi Ý
- Hiển thị trực quan: `SĐT | STK | URL`
- Auto-detect vẫn hoạt động nhưng rõ ràng hơn

#### 📝 Placeholder Ví Dụ
```
VD: 090xxxxxxx • 123456789012 • https://...
```

### 3. **Bảng LIVE Nâng Cấp**

#### 🔍 Lọc Nhanh
- **Tất cả** - Hiển thị mọi báo cáo
- **Nguy hiểm** - Chỉ các báo cáo có risk score ≥ 60
- **Đã xác minh** - Chỉ báo cáo đã được xác thực

#### 📊 Hiển Thị Đầy Đủ
- Số báo cáo
- Số người xác nhận (confirmed_by_count)
- Trạng thái xác minh (badge màu)
- Icon theo loại (Phone/Bank/Web)

### 4. **Trang Entity Profile** ⭐

#### 📄 Chi Tiết Đầy Đủ
- **Risk Score** (0-100) với thanh progress và màu sắc:
  - 🔴 80-100: CỰC KỲ NGUY HIỂM
  - 🟡 60-79: RỦI RO CAO
  - 🔵 40-59: CẨN THẬN
  - ⚪ 0-39: RỦI RO THẤP

- **Timeline** hiển thị:
  - Báo cáo đầu tiên
  - Nhiều báo cáo (nếu có)
  - Cập nhật cuối

- **Bằng chứng đầy đủ**
- **Thông tin phân loại** (loại lừa đảo, nền tảng, ngân hàng)

#### 🎬 Actions
- Xác nhận báo cáo
- Chia sẻ cảnh báo
- Thêm báo cáo mới

### 5. **Section "Cách Hoạt Động"**

3 bước đơn giản:
1. 📝 **Nhập thông tin** - SĐT/STK/URL
2. 🔍 **Phân tích rủi ro** - AI quét database
3. 🛡️ **Gợi ý hành động** - Cảnh báo + hướng dẫn

### 6. **Form Report Cải Tiến**

#### 📋 Danh Mục Rõ Ràng
Thay vì nhập tự do, giờ có dropdown với các loại:
- **Lừa đảo tài chính**
  - Giả danh ngân hàng
  - Cho vay online
  - Đầu tư chứng khoán ảo
  - Tiền ảo/Crypto

- **Lừa đảo việc làm**
  - Tuyển cộng tác viên
  - Làm việc tại nhà
  - Kiếm tiền qua app

- **Giả danh**
  - Công an
  - Nhân viên giao hàng
  - Ngân hàng/tổ chức
  - Người thân

- **Mua bán**
  - Hàng giả
  - Nhận tiền không giao hàng
  - Mua hàng chiếm đoạt

- **Khác**
  - Trúng thưởng giả
  - Hẹn hò lừa tình

#### 🛡️ Disclaimer Bảo Vệ
Hiển thị rõ:
- Danh tính được mã hóa hoàn toàn
- Thông tin cá nhân không được chia sẻ
- Cam kết cung cấp thông tin chính xác

## 🗃️ Database Schema

### Các trường mới trong `ScammerReport`:
```python
verification_status = db.Column(db.String(20), default='unverified')
risk_score = db.Column(db.Integer, default=0)  # 0-100
confirmed_by_count = db.Column(db.Integer, default=0)
```

## 🛠️ Utility Functions

### `utils/helpers.py`:
- `mask_sensitive_data(data, data_type)` - Ẩn thông tin nhạy cảm
- `calculate_risk_score(...)` - Tính điểm rủi ro
- `get_verification_badge(status)` - Badge xác minh
- `get_risk_level_info(score)` - Thông tin level rủi ro

## 📦 Cài Đặt

### 1. Chạy Migration
```bash
python database/migrate_add_verification.py
```

### 2. Khởi động lại server
```bash
python app.py
```

## 🎯 Routes Mới

- `/scammer/<int:scammer_id>` - Trang entity profile chi tiết

## 🎨 UI/UX Improvements

### Chips & Badges
- Filter buttons với active state
- Verification badges (màu xanh/vàng/xám)
- Risk level badges (màu đỏ/vàng/xanh/xám)
- Confirmed count badge (màu xanh)

### Timeline
- Visual timeline với markers màu
- Hiển thị lịch sử hoạt động

### Modal & Masking
- Mask mặc định cho bảo mật
- Toggle để xem đầy đủ
- Image modal cho bằng chứng

## 📈 Tính Năng Sắp Tới (P1)

- [ ] Subscribe & theo dõi cảnh báo (email/Zalo/Telegram)
- [ ] Share link cảnh báo tùy chỉnh
- [ ] Test IQ cá nhân hóa
- [ ] Thư viện tình huống lừa đảo

## 🤖 ML Stage 1 (Tiếp Theo)

- [ ] Auto-tag loại lừa đảo từ description
- [ ] Entity extraction (tự tách SĐT/STK/URL)
- [ ] Deduplication & similarity detection

## 📝 Notes

- Risk score tự động tính khi xem profile nếu chưa có
- Masked identifier hiển thị mặc định, cần click để xem
- Filter hoạt động client-side, nhanh và mượt
- Timeline động theo số lượng báo cáo

## 🐛 Known Issues

- Migration script cần chạy 1 lần duy nhất
- Cần có ít nhất 1 scammer trong DB để test profile page

## 📞 Support

Nếu gặp vấn đề, check:
1. Database đã migrate chưa?
2. Import helpers có đúng không?
3. Template scammer_profile.html đã tạo chưa?
4. Route đã register trong app.py chưa?
