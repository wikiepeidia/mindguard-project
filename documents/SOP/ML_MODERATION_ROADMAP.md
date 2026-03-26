# LỘ TRÌNH HỖ TRỢ ML CHO MODERATION SAU V1

## 1. Mục tiêu

Xây dựng lộ trình thực tế để MindGuard chuyển từ moderation thủ công sang moderation có mô hình hỗ trợ theo hướng offline-first và human-in-the-loop.

## 2. Nguyên tắc triển khai

1. Mô hình chỉ hỗ trợ, không thay thế quản trị viên ngay.
2. Mỗi giai đoạn phải có điều kiện chuyển tiếp rõ ràng.
3. Nếu false-positive cao hoặc dữ liệu không ổn định, phải rollback về chế độ chỉ có quản trị viên xử lý.

## 3. Giai đoạn 0: Ổn định dữ liệu và nhãn moderation

Điều kiện đầu vào:

- Đã hoàn thành kế hoạch dữ liệu gán nhãn.
- Đã thu thập đủ dữ liệu moderation tối thiểu 1 tháng.

Công việc chính:

- kiểm tra chất lượng nhãn;
- loại bỏ bản ghi lỗi, thiếu dữ liệu hoặc ngoại lệ rõ ràng;
- chốt dictionary cho `scam_category`, `moderation_outcome`, `evidence_quality`.

Đầu ra:

- snapshot dữ liệu đã QA;
- báo cáo phân bố nhãn;
- thống kê tỷ lệ approved và rejected.

## 4. Giai đoạn 1: Baseline ML cổ điển

Mục tiêu:

- tạo baseline nhanh, dễ giải thích và dễ kiểm soát.

Hướng tiếp cận có thể cân nhắc:

- TF-IDF kết hợp Logistic Regression;
- TF-IDF kết hợp Linear SVM;
- LightGBM hoặc XGBoost trên text và metadata phù hợp.

Feature có thể sử dụng:

- `description_clean`
- `scam_type_raw`
- `platform`
- `report_type`
- `report_count`
- `confirmed_by_count`
- `has_evidence`

Đánh giá bắt buộc:

- precision;
- recall;
- F1;
- confusion matrix;
- rà soát false-positive theo từng nhóm lừa đảo.

Điều kiện qua giai đoạn 1:

- baseline tốt hơn rule đơn giản đang dùng để đối chiếu;
- false-positive ở mức chấp nhận được sau khi xem tay.

## 5. Giai đoạn 2: Nâng cấp embedding hoặc DL khi cần

Chỉ thực hiện khi:

- dữ liệu đủ lớn;
- baseline cổ điển bắt đầu chạm trần hiệu quả;
- cần biểu diễn tốt hơn cho dữ liệu văn bản phức tạp.

Hướng có thể xem xét:

- sentence embedding kết hợp classifier;
- PhoBERT hoặc multilingual encoder fine-tune;
- mô hình gọn dùng cho phân loại hỗ trợ offline.

Lưu ý:

- không chuyển sang mô hình nặng khi dữ liệu và baseline chưa ổn định.

## 6. Giai đoạn 3: Đánh giá offline mở rộng

Mục tiêu:

- đánh giá mô hình trên tập holdout và các trường hợp mới gần thời gian vận hành thực tế.

Báo cáo cần có:

- precision theo từng nhãn scam;
- recall theo từng nhãn scam;
- ví dụ false-positive;
- ví dụ false-negative;
- phân bố confidence theo nhóm.

Tiêu chí rollback ở giai đoạn này:

- precision thấp ở nhóm rủi ro cao;
- false-positive có thể gây kết luận sai;
- kết quả không ổn định giữa các snapshot đánh giá.

## 7. Giai đoạn 4: Shadow mode

Mục tiêu:

- để mô hình chạy song song với quản trị viên nhưng chưa tác động đến quyết định thực tế.

Cách triển khai:

- mô hình tạo điểm gợi ý ở nền;
- kết quả được log riêng để so sánh với quyết định của quản trị viên;
- không hiển thị kết quả cho người dùng cuối.

Chỉ số cần theo dõi:

- mức độ đồng thuận giữa mô hình và quản trị viên;
- tần suất mô hình đề xuất sai;
- nhóm tình huống mà mô hình thường nhầm.

Điều kiện sang bước tiếp theo:

- shadow mode ổn định qua nhiều đợt đánh giá;
- false-positive nằm trong ngưỡng chấp nhận nội bộ.

## 8. Giai đoạn 5: Human-in-the-loop assist

Mục tiêu:

- mô hình chỉ đưa ra gợi ý, còn quản trị viên là người quyết định cuối cùng.

Gợi ý cách thể hiện:

- điểm nghi ngờ;
- nhãn dự kiến;
- lý do hoặc tín hiệu nổi bật nếu có thể giải thích;
- cảnh báo rõ rằng đây chỉ là thông tin hỗ trợ.

Điều kiện bắt buộc:

- quản trị viên có thể bỏ qua đề xuất của mô hình;
- hệ thống ghi nhận được khác biệt giữa gợi ý và quyết định cuối;
- chưa áp dụng auto-approve hoặc auto-reject ở giai đoạn này.

## 9. Giai đoạn 6: Xem xét tự động hóa từng phần

Chỉ xem xét khi:

- precision rất cao trên một nhóm trường hợp hẹp;
- false-positive rất thấp;
- có cơ chế rollback nhanh;
- đội ngũ vận hành chấp nhận mức rủi ro tương ứng.

Thứ tự ưu tiên nên bắt đầu từ:

- gợi ý ưu tiên hàng đợi;
- tự động gắn nhãn hỗ trợ;
- làm nổi bật các báo cáo cần xem kỹ.

Chưa nên chuyển thẳng sang auto moderation toàn phần.

## 10. Chỉ số theo dõi cho quản lý

- precision trên nhóm `valid_scam_report`;
- recall ở các nhóm lừa đảo quan trọng;
- false-positive rate;
- false-negative rate;
- mức tiết kiệm thời gian xử lý cho quản trị viên;
- tỷ lệ đồng ý hoặc không đồng ý của quản trị viên với gợi ý mô hình.

## 11. Điều kiện rollback

Rollback ngay về chế độ thủ công nếu:

- false-positive tăng bất thường;
- điểm số mô hình mất ổn định sau khi dữ liệu thay đổi;
- kết quả khó giải thích và gây cản trở quy trình;
- quản trị viên không còn tin cậy mức hỗ trợ hiện tại.

## 12. Kết luận

Lộ trình phù hợp cho MindGuard là:

1. thu thập dữ liệu thực tế trong 1 tháng;
2. xây dựng baseline offline;
3. đánh giá kỹ precision và false-positive;
4. chạy shadow mode;
5. chỉ sau đó mới đưa mô hình vào vai trò hỗ trợ có human-in-the-loop.

Trong giai đoạn hiện tại, không thay thế bước kiểm duyệt của quản trị viên bằng ML hoặc DL.
