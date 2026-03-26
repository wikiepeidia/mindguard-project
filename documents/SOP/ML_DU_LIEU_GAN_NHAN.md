# KẾ HOẠCH DỮ LIỆU GÁN NHÃN CHO MODERATION BÁO CÁO

## 1. Mục tiêu

Tài liệu này xác định cách MindGuard thu thập dữ liệu trong 1 tháng để chuẩn bị cho giai đoạn hỗ trợ moderation bằng mô hình sau v1. Tài liệu chỉ phục vụ readiness và không đưa cơ chế tự động ra quyết định vào phiên bản hiện tại.

## 2. Nguyên tắc chung

1. Trong v1, quy trình moderation vẫn do quản trị viên quyết định.
2. Dữ liệu phục vụ huấn luyện phải được ẩn danh trước khi đưa vào tập phân tích.
3. Bộ dữ liệu huấn luyện phải tách biệt với dữ liệu nhạy cảm trong production.
4. Mục tiêu của tháng đầu là xây dựng bộ dữ liệu tốt, không phải triển khai mô hình sớm.

## 3. Cửa sổ thu thập đề xuất

- Thời gian: 1 tháng liên tục sau khi hệ thống vận hành ổn định.
- Đơn vị thu thập: từng `ScammerReport` cùng kết quả xử lý của quản trị viên.
- Nguồn bổ sung: bộ dữ liệu công khai chỉ được ghép sau khi đã chuẩn hóa schema và đánh giá tương thích.

## 4. Nguồn nhãn từ hệ thống hiện tại

Từ schema hiện tại có thể sử dụng:

- `status`: `approved`, `rejected`, `pending`;
- `verification_status`: `verified`, `unverified`;
- `scam_type`;
- `report_type`;
- `platform`;
- `report_count`;
- `confirmed_by_count`;
- `created_at`.

## 5. Đề xuất bộ nhãn

### 5.1 Nhãn mức 1: kết quả moderation

- `valid_scam_report`
- `insufficient_evidence`
- `duplicate_or_low_value`
- `invalid_or_noise`

Ghi chú:

- Hệ thống hiện tại chưa có trường riêng cho lý do từ chối.
- Trong giai đoạn thu thập dữ liệu, nên bổ sung nhãn tay hoặc bảng gán nhãn riêng để phân biệt chi tiết các trường hợp bị từ chối.

### 5.2 Nhãn mức 2: nhóm lừa đảo

Chuẩn hóa từ `scam_type` về các nhóm lớn:

- tài chính hoặc đầu tư;
- giả danh cơ quan hoặc ngân hàng;
- phishing hoặc website giả mạo;
- tuyển dụng hoặc cộng tác viên;
- mua bán hoặc giao dịch;
- nhóm khác.

### 5.3 Nhãn mức 3: chất lượng bằng chứng

- `high`
- `medium`
- `low`
- `missing`

## 6. Trường dữ liệu cho bản xuất train-ready

Bản xuất train-ready nên bao gồm:

- `report_id`
- `report_type`
- `platform`
- `scam_type_raw`
- `scam_category_normalized`
- `description_clean`
- `has_evidence`
- `evidence_count`
- `report_count`
- `confirmed_by_count`
- `status_final`
- `verification_status_final`
- `label_moderation_outcome`
- `label_evidence_quality`
- `created_date`

## 7. Trường dữ liệu không được rời khỏi vùng bảo vệ

Không đưa các trường sau vào bộ train-ready thông thường:

- định danh thô của đối tượng nếu chưa được che hoặc ẩn danh phù hợp;
- URL, số điện thoại hoặc số tài khoản ở dạng raw;
- `reporter_hash`;
- tệp bằng chứng gốc chưa xử lý metadata;
- lý do xuất dữ liệu nội bộ hoặc nhật ký truy cập nhạy cảm.

## 8. Quy tắc ẩn danh

1. Định danh phải được che hoặc băm trước khi vào pipeline huấn luyện.
2. `reporter_hash` không được dùng làm feature huấn luyện.
3. Văn bản mô tả cần được rà soát để loại bỏ dữ liệu cá nhân của người bị hại khi cần thiết.
4. Ảnh bằng chứng nếu dùng cho mục đích nghiên cứu phải được xử lý metadata và cân nhắc che thông tin nhạy cảm.

## 9. Quy trình thu thập trong 1 tháng

### Tuần 1

- Thống nhất tiêu chí moderation giữa các quản trị viên.
- Thiết lập bảng gán nhãn cho các trường hợp được duyệt và bị từ chối.
- Thử nghiệm một đợt xuất dữ liệu nhỏ để kiểm tra schema.

### Tuần 2 đến tuần 3

- Thu thập dữ liệu thực tế từ hệ thống.
- Gán thêm nhãn tay cho các bản ghi cần phân loại sâu hơn.
- Ghi nhận các trường hợp false-positive và false-negative để phục vụ đánh giá sau này.

### Tuần 4

- Chốt snapshot train-ready.
- Kiểm tra độ đầy đủ của nhãn.
- Tách tập train, validation và test theo thời gian hoặc theo đợt moderation.

## 10. Kết hợp với dữ liệu công khai

Nếu sử dụng dữ liệu công khai bên ngoài:

- chỉ lấy các trường có thể ánh xạ vào `scam_category`, `description`, `platform`;
- đánh dấu rõ nguồn là `public_external`;
- không trộn trực tiếp với dữ liệu nội bộ nếu chất lượng nhãn chưa tương đương.

## 11. Điều kiện để chuyển sang giai đoạn mô hình

- Có tối thiểu 1 tháng dữ liệu moderation thực tế.
- Có bộ nhãn đủ rõ cho các nhóm approved và rejected.
- Có quy trình ẩn danh và xuất dữ liệu ổn định.
- Có data dictionary đủ dùng cho nhóm phát triển mô hình.

## 12. Nội dung chưa đưa vào v1

Những nội dung sau chưa áp dụng trong v1:

- tự động phê duyệt báo cáo bằng mô hình;
- tự động từ chối không có human review;
- đưa điểm số mô hình tác động trực tiếp đến quyết định moderation.
