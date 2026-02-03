
# Product TODO & Roadmap – Cảnh Báo Lừa Đảo (Beta → Launch)

## UX/UI Cải thiện ngay (trước khi cho nhiều người dùng)

- **Bảng LIVE**
  - [x] Thêm bộ lọc nhanh (Quick filters):
    - Loại lừa đảo: giả danh, đầu tư, tuyển dụng, vay online, tình yêu…
    - Mức độ rủi ro (thang màu hoặc Low/Medium/High)
    - Thời gian (24h, 7 ngày, 30 ngày…)
    - Nguồn: cộng đồng / đối tác / đã xác minh
  - [x] Hiển thị: Số báo cáo + Số người xác nhận (khác biệt rõ với chỉ “số report”)

- **Text contrast & readability**
  - [x] Tăng cỡ chữ + contrast cho phần mô tả/ghi chú trong card
  - [x] Subtitle và dòng hướng dẫn dưới thanh tìm kiếm → tăng nhẹ size + contrast (ít “chìm” hơn)

- **Thêm section “Cách hoạt động” ngay dưới hero / màn đầu**
  - [x] 3 bước rõ ràng:
    1. Nhập thông tin cần kiểm tra
    2. Hệ thống phân tích rủi ro
    3. Gợi ý hành động an toàn
  → Mục tiêu: tăng chuyển đổi beta (người dùng hiểu nhanh → muốn thử)

## P0 – Tính năng cốt lõi (phải có trước khi scale user)

- **Trang kết quả tra cứu chi tiết & đáng tin cậy**
  - [x] Risk Score (0–100) + giải thích ngắn gọn lý do điểm cao/thấp
  - [x] Bằng chứng / nguồn / link liên quan (nếu có)
  - [x] Lịch sử báo cáo theo thời gian (timeline)

- **Entity Profile (trang riêng cho mỗi SĐT / STK / URL)**
  - [x] Timeline báo cáo
  - [x] Tags / loại lừa đảo
  - [x] Liên kết liên quan (các entity khác xuất hiện cùng)

- **Quy trình báo cáo (Report flow)**
  - [x] Bắt buộc: mô tả + chọn danh mục + upload ảnh/chat/biên lai
  - [x] Tự động gợi ý che mờ thông tin cá nhân người tố cáo
  - [x] Chống spam: CAPTCHA (implemented full hybrid cloudflare/math) + rate limit + audit log
  - [x] Ẩn danh nhưng có mức độ tín nhiệm (dựa trên lịch sử user)

## P1 – Tạo cảm giác “đẳng cấp” (làm xong là khác biệt rõ)

- **Subscribe / Theo dõi cảnh báo**
  - [x] User follow 1 entity (SĐT/STK/URL) (Implemented DB & UI)
  - [ ] Có report mới → push notification / email / Zalo / Telegram (API deferred)

- **Chia sẻ cảnh báo nhanh**
  - [x] Tạo link “warning page” ngắn gọn → gửi cho người thân trước khi chuyển tiền (Implemented Share button)

- **Thư viện tình huống + mini game**
  - [x] Bộ sưu tập tình huống lừa đảo phổ biến (Implemented Warning Library)
  - [x] “Test IQ lừa đảo” cá nhân hóa (Upgraded Quiz with Gamification/Titles)

## P2 – Mở rộng dài hạn

- Extension trình duyệt + Bot Zalo/Telegram
  - [x] Extension trình duyệt (Source code provided in `browser_extension/`)
  - [ ] Phát hiện link lạ → cảnh báo realtime (Partially handled by extension demo)

- API công khai cho đối tác
  - [x] Ngân hàng, fintech, cộng đồng tra cứu rủi ro theo request (Implemented `/api/v1/check`)

## Machine Learning Roadmap (tích hợp dần)

### Stage 1 – Nhanh, hiệu quả cao, không cần dữ liệu quá lớn

- Auto-tagging & gợi ý loại lừa đảo từ nội dung tố cáo
- Entity extraction & chuẩn hóa (tách SĐT, STK, URL, tên…)
- Deduplication + similarity grouping (nhiều report cùng vụ → gộp lại)

### Stage 2 – Đưa sản phẩm lên mức “pro”

- Explainable Risk Scoring (rule-based trước, sau nâng ML)
  - Kết hợp: số report, độ tin cậy user, bằng chứng, độ mới, similarity…
  - Sử dụng Wilson score / Bayesian để tránh bias từ report ít
- Anomaly detection (bùng nổ report trong thời gian ngắn → “Cảnh báo nóng”)
- Graph-based detection (phát hiện mạng lưới: SĐT → STK → URL…)

### Stage 3 – Nâng cao (khi có đủ dữ liệu + nguồn crawl hợp pháp)

- Domain/URL risk scoring (tuổi domain, redirect chain, pattern phishing…)

## Combo 5 tính năng “ngắn hạn nhưng xịn” – Nên ưu tiên beta

1. Entity Profile + Timeline (trái tim sản phẩm)
2. Trạng thái xác minh + cơ chế khiếu nại/đính chính
3. Subscribe cảnh báo (Zalo/Telegram là kênh chính)
4. Auto-tag + deduplication/similarity (ML stage 1)
5. Risk score có giải thích (bắt đầu rule-based, sau nâng ML)

## completed

Nên cải thiện (ưu tiên cao)

- [x] ngrok them de teet cloudfare.
- [x] capcha them cloudfare (cloudfare.json) Login,signup,report....
- [x] Animation trang login phaầ đang nhaập, danf ky chuưa co
- [x] chatbot/api loi (Fixed config loading for OpenRouter key)
<http://127.0.0.1:5000/> chua login:
- [x] Tố cáo ẩn danh(<http://127.0.0.1:5000/>) sao lai bat login? (Removed login requirement)
- [x] Chatbot AI 24/7 (<http://127.0.0.1:5000/)ko> bam duoc -->route sang login (Enabled global widget for anonymous users)
- [x] Base html, 1 so file html co ca css/js trong html, tach ra file rieng de quan ly
- [x] Nhập thông tin :icon hidden behind circle reimplement whole (o trang<<http://127.0.0.1:5000/> )
- [x] Phân tích rủi ro -->icon hidden behind circle reimplement whole (o trang<<http://127.0.0.1:5000/> )
- [x] Gợi ý hành động-->icon hidden behind circle reimplement whole (o trang<<http://127.0.0.1:5000/> )
- [x] Background ko stretch full page
- [x] footer trash © 2025 MindGuard Community Project. Bảo mật & Minh bạch. fix footer.
- [x] Remove unused social icons and support links from footer. Add Github source link.
- [x] Fallback cloudfare:development : ko dung cloudfare (link 127.0.0.1 /localhost) dung capcha math con web thi dung , fallback neu cloudfare sap

Tăng “trust cues” + tránh rủi ro pháp lý

- [x] Ở mỗi cảnh báo nên có trạng thái: “Chưa xác minh” / “Đang xác minh” / “Đã xác minh (nếu có)”.

- [x] Ẩn/mask mặc định thông tin nhạy cảm: SĐT/ STK hiển thị kiểu 0123***789 (bấm “Xem đầy đủ” khi người dùng đăng nhập / đồng ý điều khoản).

- [x] Thêm dòng nhỏ gần ô tìm kiếm: “Dữ liệu do cộng đồng cung cấp, kết quả mang tính cảnh báo — vui lòng kiểm chứng trước khi giao dịch.”

Tối ưu ô tra cứu

- [x] Hiện bạn để “SĐT, STK, Link web…” rất tốt. Nên thêm “chips” gợi ý: SĐT | STK | URL (auto-detect vẫn được, nhưng chip giúp người dùng hiểu hệ thống làm gì).

- [x] Thêm ví dụ trong placeholder: VD: 090xxxxxxx • 123456789012 • https://...
