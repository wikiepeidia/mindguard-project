# QUY TRÌNH XỬ LÝ BÁO CÁO LỪA ĐẢO MINDGUARD

## 1. Mục đích

Tài liệu này mô tả quy trình chuẩn để quản trị viên MindGuard tiếp nhận, rà soát, phê duyệt, từ chối và xuất dữ liệu báo cáo lừa đảo một cách nhất quán, an toàn và có kiểm soát.

## 2. Phạm vi áp dụng

- Áp dụng cho khu vực quản trị xử lý báo cáo lừa đảo.
- Áp dụng cho các thao tác xem danh sách, kiểm tra bằng chứng, phê duyệt, từ chối và xuất dữ liệu.
- Không áp dụng cho cơ chế tự động phê duyệt bằng mô hình trong phiên bản v1.

## 3. Vai trò tham gia

- Quản trị viên: trực tiếp xử lý từng báo cáo.
- Người phụ trách theo dõi vận hành: giám sát việc tuân thủ quy trình và lưu trữ tài liệu liên quan.
- Hệ thống MindGuard: ghi nhận trạng thái báo cáo, bằng chứng và dữ liệu phục vụ đối soát nội bộ.

## 4. Màn hình và đường dẫn liên quan

- Trang kiểm duyệt: `/admin/scammer-reports`
- Phê duyệt báo cáo: `POST /approve-report/<report_id>`
- Từ chối báo cáo: `POST /reject-report/<report_id>`
- Xuất dữ liệu: `GET /export-dataset`

[PLACEHOLDER_HINH_01: Trang quản trị danh sách báo cáo với bộ lọc Tất cả / Chờ duyệt / Đã duyệt / Đã từ chối]
[PLACEHOLDER_HINH_02: Cửa sổ xem bằng chứng trong khu vực quản trị]
[PLACEHOLDER_HINH_03: Vị trí nút Phê duyệt và Từ chối trên bảng danh sách]
[PLACEHOLDER_HINH_04: Bước xuất dữ liệu và vị trí nhập lý do nếu xuất dữ liệu đầy đủ]

## 5. Trạng thái xử lý

- `pending` / Chờ duyệt: báo cáo mới tiếp nhận, chưa được xử lý.
- `approved` / Đã duyệt: báo cáo đã được xác nhận hợp lệ.
- `rejected` / Đã từ chối: báo cáo không đủ điều kiện hoặc không phù hợp.
- `verification_status = verified`: được gán sau khi báo cáo được phê duyệt.
- `verification_status = unverified`: trạng thái mặc định trước khi xác minh.

## 6. Nguyên tắc xử lý

1. Chỉ phê duyệt khi có đủ thông tin và bằng chứng để phục vụ cảnh báo cộng đồng.
2. Không chỉnh sửa thủ công dữ liệu gốc ngoài quy trình được phê duyệt.
3. Chỉ xuất dữ liệu đầy đủ khi có mục đích và lý do nội bộ rõ ràng.
4. Không làm lộ danh tính hoặc dấu vết có thể suy ngược tới người gửi báo cáo.
5. Khi có dấu hiệu spam hoặc dữ liệu bất thường, cần đối chiếu thêm trước khi ra quyết định.

## 7. Quy trình xử lý chuẩn

### Bước 1: Mở hàng đợi xử lý

1. Đăng nhập bằng tài khoản quản trị.
2. Truy cập trang `Kiểm duyệt tố cáo`.
3. Chọn bộ lọc `Chờ duyệt` để ưu tiên xử lý các báo cáo mới.

Checklist:

- Đúng tài khoản quản trị.
- Đúng bộ lọc cần xử lý.
- Không có cảnh báo hệ thống bất thường.

### Bước 2: Rà soát thông tin đối tượng

Cần kiểm tra:

- Loại đối tượng bị báo cáo: website, tài khoản ngân hàng, số điện thoại, mạng xã hội.
- Trường định danh đối tượng trong danh sách.
- `scam_type` để xác định nhóm hành vi lừa đảo.
- `description` để hiểu bối cảnh sự việc.

Dấu hiệu cần xem xét kỹ hơn:

- Mô tả quá ngắn hoặc thiếu tình tiết cụ thể.
- Nội dung nghiêm trọng nhưng không có bằng chứng đi kèm.
- Nhiều báo cáo giống nhau xuất hiện bất thường trong thời gian ngắn.

### Bước 3: Kiểm tra bằng chứng

1. Nếu có nút xem bằng chứng, mở cửa sổ xem ảnh.
2. Xem lần lượt từng tệp đính kèm.
3. Đối chiếu bằng chứng với mô tả và đối tượng bị báo cáo.

Ưu tiên xác nhận các dấu hiệu sau:

- Ảnh chụp màn hình hội thoại, SMS, email, website, giao dịch chuyển khoản.
- Dấu vết nhận dạng như số điện thoại, số tài khoản, URL, biệt danh.
- Nội dung bằng chứng phù hợp với loại lừa đảo được chọn.

Không nên phê duyệt khi:

- Bằng chứng mờ, thiếu liên quan hoặc không đọc được.
- Dữ liệu có dấu hiệu chỉnh sửa gây sai lệch nội dung.
- Báo cáo chỉ mang tính nhận xét chủ quan, không có căn cứ đối chiếu.

### Bước 4: Ra quyết định xử lý

#### Trường hợp phê duyệt

Điều kiện:

- Mô tả rõ ràng, có thể hiểu được diễn biến.
- Có bằng chứng hoặc dấu hiệu nhận dạng hợp lý.
- Thông tin có giá trị cảnh báo cộng đồng.

Thao tác:

1. Chọn `Phê duyệt`.
2. Hệ thống chuyển `status` sang `approved`.
3. Hệ thống đồng thời chuyển `verification_status` sang `verified`.
4. Nếu đối tượng đã tồn tại trong hệ thống, dữ liệu liên quan có thể được cập nhật phục vụ tổng hợp.

Kết quả mong đợi:

- Báo cáo xuất hiện trong nhóm `Đã duyệt`.
- Có thể được đưa vào bộ dữ liệu đã duyệt khi xuất dữ liệu.
- Trạng thái đã xác minh được cập nhật đúng.

#### Trường hợp từ chối

Áp dụng khi:

- Thiếu căn cứ để cảnh báo cộng đồng.
- Nội dung sai mục đích, trùng lặp hoặc có dấu hiệu gây nhiễu.
- Bằng chứng không phù hợp hoặc không thể đối chiếu.

Thao tác:

1. Chọn `Từ chối`.
2. Xác nhận thao tác tại hộp thoại hiện ra.
3. Hệ thống chuyển `status` sang `rejected`.

Lưu ý:

- Giao diện hiện tại chưa bắt buộc nhập lý do từ chối trực tiếp trên form.
- Nếu cần ghi nhận nội bộ, lưu lý do ở kênh quản trị hoặc biên bản vận hành phù hợp.

### Bước 5: Kiểm tra sau xử lý

Sau mỗi đợt thao tác:

- Làm mới trang hoặc chuyển bộ lọc để xác nhận trạng thái mới.
- Kiểm tra lại số lượng báo cáo chờ xử lý.
- Nếu phát hiện thao tác nhầm, cần xử lý theo quy trình nội bộ và lưu dấu vết đối soát.

## 8. Quy trình xuất dữ liệu

### 8.1 Mục đích

Xuất dữ liệu phục vụ thống kê nội bộ, nghiên cứu, hoặc chuẩn bị dữ liệu cho giai đoạn sau v1.

### 8.2 Trường dữ liệu xuất hiện tại

Theo luồng hiện tại, bộ dữ liệu xuất gồm:

- `id`
- `identifier`
- `scam_type`
- `platform`
- `description`
- `report_count`
- `date`

### 8.3 Yêu cầu về bảo mật và quyền riêng tư

1. Ưu tiên bản xuất đã được làm giảm mức nhạy cảm của định danh.
2. Chỉ xuất dữ liệu đầy đủ khi có lý do nội bộ hợp lệ.
3. Không chia sẻ tệp dữ liệu qua kênh công khai hoặc không được kiểm soát.
4. Không cố gắng suy ngược `reporter_hash` hoặc dấu vết của người gửi báo cáo.

### 8.4 Các bước thực hiện

1. Xác định rõ mục đích sử dụng dữ liệu.
2. Nếu chỉ phục vụ tổng hợp hoặc trình bày, ưu tiên dùng bản xuất thông thường.
3. Nếu cần dữ liệu đầy đủ, chuẩn bị ghi chú lý do nội bộ trước khi thao tác.
4. Thực hiện xuất dữ liệu.
5. Lưu tệp tại thư mục hoặc hệ thống nội bộ được kiểm soát truy cập.

### 8.5 Các điều không được làm

- Không xuất dữ liệu đầy đủ khi chưa xác định rõ mục đích.
- Không gửi dữ liệu cho nhóm ngoài phạm vi công việc.
- Không xem bộ dữ liệu xuất là dữ liệu công khai.

## 9. Tình huống cần lưu ý

### 9.1 Báo cáo trùng đối tượng đã có

Hệ thống có thể cộng dồn `report_count` cho đối tượng đã tồn tại. Trong trường hợp này:

- Kiểm tra xem báo cáo mới có thêm giá trị xác minh hay không.
- Nếu đối tượng đã được duyệt, dữ liệu tổng hợp có thể thay đổi theo số lượt báo cáo.

### 9.2 Cảnh báo anti-spam

Khi người dùng bị giới hạn gửi báo cáo do cooldown:

- Giải thích đây là cơ chế bảo vệ chất lượng dữ liệu.
- Không hướng dẫn cách vượt qua giới hạn.
- Chỉ hỗ trợ sâu hơn sau khi đã đối chiếu thông tin cần thiết.

### 9.3 Chuẩn bị dữ liệu cho giai đoạn ML

- Chỉ sử dụng theo tài liệu readiness riêng.
- Chưa áp dụng tự động phê duyệt hoặc tự động từ chối trong v1.
- Human review vẫn là bước quyết định cuối cùng ở giai đoạn hiện tại.

## 10. Checklist nhanh cho quản trị viên

- [ ] Đã chọn đúng bộ lọc xử lý.
- [ ] Đã đọc đối tượng, loại lừa đảo và mô tả.
- [ ] Đã xem bằng chứng nếu có.
- [ ] Đã xác nhận trạng thái sau khi thao tác.
- [ ] Nếu xuất dữ liệu, đã xác định rõ mục đích và yêu cầu bảo mật.
