# Domain Pitfalls

**Domain:** Nền tảng web giáo dục an toàn mạng + báo cáo lừa đảo (Flask brownfield)
**Researched:** 2026-03-19
**Confidence tổng:** HIGH cho rủi ro codebase hiện tại, MEDIUM cho khuyến nghị mở rộng theo best-practice

## Critical Pitfalls

### Pitfall 1: Chỉ dựa vào IP/cookie để chặn spam

**What goes wrong:** Hệ thống gắn nhãn spam chỉ theo IP hoặc cookie, dẫn tới false positive (NAT, mạng trường/công ty) và false negative (đổi IP, incognito, botnet).
**Why it happens:** Thiết kế anti-spam quá đơn biến, thiếu risk scoring theo nhiều tín hiệu.
**Consequences:** Chặn nhầm người dùng thật, bỏ lọt spam có chủ đích, UX giảm mạnh.
**Prevention:**

- Dùng risk score đa tín hiệu: tần suất gửi, fingerprint nhẹ (ổn định nhưng tôn trọng riêng tư), tuổi tài khoản, chất lượng nội dung, lịch sử vi phạm.
- Tách action theo mức rủi ro: cảnh báo mềm -> CAPTCHA tăng cường -> cooldown -> review thủ công.
- Luôn có cơ chế appeal/unblock cho người dùng thật.
**Warning signs (Detection):**
- Tỷ lệ report bị chặn tăng mạnh từ cùng ASN/mạng nội bộ.
- Nhiều ticket “tôi không spam vẫn bị chặn”.
- Spam vẫn lọt dù đã bật block IP/cookie.
**Suggested phase mapping:** Pha 2 (Anti-spam engine) + Pha 4 (Tuning & policy).

### Pitfall 2: Thu thập tín hiệu chống gian lận nhưng thiếu ranh giới quyền riêng tư

**What goes wrong:** Ghi nhận IP, cookie, số điện thoại, evidence mà không phân lớp dữ liệu nhạy cảm, không giới hạn thời gian lưu.
**Why it happens:** Ưu tiên chống spam nhanh, bỏ qua data governance ngay từ đầu.
**Consequences:** Rủi ro lộ dữ liệu, khó tuân thủ, mất niềm tin người dùng.
**Prevention:**

- Phân loại dữ liệu: bắt buộc, tùy chọn, nhạy cảm cao.
- Ẩn/mask mặc định dữ liệu PII ở UI (ví dụ số điện thoại chỉ hiện 3 số cuối theo yêu cầu sản phẩm).
- Thiết kế retention policy (TTL), quyền truy cập tối thiểu, audit truy cập dữ liệu nhạy cảm.
- Không lưu plaintext secrets/password/OTP trong session phía client.
**Warning signs (Detection):**
- Session chứa thông tin đăng ký nhạy cảm.
- Admin UI hiển thị trực tiếp định danh đầy đủ.
- Không trả lời được câu hỏi “dữ liệu này giữ bao lâu, ai được xem?”.
**Suggested phase mapping:** Pha 1 (Data governance baseline) + Pha 3 (PII-safe UX).

### Pitfall 3: Không có guardrails bắt buộc trên endpoint thay đổi trạng thái

**What goes wrong:** Thiếu CSRF đồng bộ, thiếu rate limit tập trung, thiếu idempotency cho submit report.
**Why it happens:** Route xử lý nghiệp vụ trực tiếp, mỗi endpoint tự làm theo cách riêng.
**Consequences:** Dễ bị abuse login/register/report, duplicate submissions, moderation nhiễu.
**Prevention:**

- Bật CSRF token cho mọi POST/PUT/DELETE.
- Thêm rate-limit theo user + IP + route class (auth/report/chat).
- Dùng idempotency key hoặc dedup window cho báo cáo gửi lặp.
- Chuẩn hóa middleware/decorator dùng chung cho toàn bộ blueprint.
**Warning signs (Detection):**
- Burst request lớn vào auth/report mà không bị hãm.
- Bản ghi trùng cùng nội dung xuất hiện liên tục trong vài phút.
- Endpoint hành chính bị gọi từ phiên không hợp lệ.
**Suggested phase mapping:** Pha 1 (Security guardrails) trước mọi thay đổi anti-spam/UX.

### Pitfall 4: Logic chống gian lận nằm trực tiếp trong route handlers

**What goes wrong:** Rule spam, xử lý upload, persistence trộn trong routes nên khó test, khó thay đổi.
**Why it happens:** Codebase brownfield đã monolithic ở `routes/auth.py`, `routes/scammer.py`, `routes/main.py`.
**Consequences:** Mỗi lần chỉnh rule dễ kéo theo regression auth/report/UI.
**Prevention:**

- Tách service layer: `abuse_detection_service`, `report_ingestion_service`, `policy_service`.
- Route chỉ làm parse request + response, còn policy/risk chạy trong service.
- Viết contract tests cho service thay vì chỉ test end-to-end thủ công.
**Warning signs (Detection):**
- Một thay đổi nhỏ ở anti-spam làm hỏng luồng đăng ký/OTP.
- PR anti-spam chạm quá nhiều file route không liên quan.
- Không mock được logic để test unit.
**Suggested phase mapping:** Pha 1 (Refactor nền) + Pha 2 (Policy implementation).

### Pitfall 5: Thiết kế “block ngay” thay vì “degrade gracefully”

**What goes wrong:** Khi CAPTCHA/API ngoài chậm hoặc lỗi, toàn bộ luồng report/login thất bại cứng.
**Why it happens:** Gọi HTTP đồng bộ trên request path, chưa có fallback/circuit-breaker.
**Consequences:** Mất dữ liệu người dùng, tăng bounce rate, lỗi hàng loạt giờ cao điểm.
**Prevention:**

- Áp dụng fail-open có kiểm soát cho luồng ít rủi ro, fail-closed cho action nhạy cảm cao.
- Dùng timeout ngắn + retry có backoff + fallback policy rõ ràng.
- Tách các tác vụ không cần realtime sang background queue.
**Warning signs (Detection):**
- Latency p95 tăng theo thời gian phản hồi của dịch vụ ngoài.
- Tỷ lệ submit thất bại tăng đồng thời với timeout HTTP upstream.
- Người dùng phải gửi lại cùng một report nhiều lần.
**Suggested phase mapping:** Pha 2 (Reliability hardening) + Pha 5 (Scale readiness).

### Pitfall 6: Chuyển UX lớn (light mode + one-question-per-page) theo kiểu big-bang

**What goes wrong:** Đổi layout/flow toàn hệ thống một lần gây vỡ tương thích template, JS cũ, hành vi session quiz.
**Why it happens:** Không có migration UX theo từng lát cắt và thiếu đo lường trước/sau.
**Consequences:** Giảm completion rate quiz, tăng confusion, phát sinh bug khó truy vết.
**Prevention:**

- Rollout theo feature flag theo nhóm người dùng.
- Giữ tương thích ngược dữ liệu quiz/result trong giai đoạn chuyển đổi.
- Theo dõi metric bắt buộc: start-to-finish rate, abandon rate theo bước, thời gian mỗi câu.
- UAT với kịch bản mobile trước khi mở rộng toàn bộ.
**Warning signs (Detection):**
- Completion rate quiz giảm mạnh sau release UI.
- Tăng lỗi JS/template ở các trang quiz/result/profile.
- Người dùng quay lại trang trước nhiều bất thường.
**Suggested phase mapping:** Pha 3 (UX redesign incremental) + Pha 4 (Telemetry-based tuning).

### Pitfall 7: Không có audit trail cho hành động moderation/admin

**What goes wrong:** Duyệt/từ chối report, sửa/xóa dữ liệu nhưng không ghi ai làm, lúc nào, lý do gì.
**Why it happens:** Chỉ dựa vào `session.get('is_admin')` và mutate trực tiếp DB.
**Consequences:** Khó điều tra khi có khiếu nại, khó rollback quyết định sai.
**Prevention:**

- Ghi audit log có cấu trúc cho mọi hành động nhạy cảm.
- Yêu cầu reason code khi reject/approve.
- Thêm soft delete + event history cho report quan trọng.
**Warning signs (Detection):**
- Không truy vết được vì sao một report biến mất/chuyển trạng thái.
- Có tranh chấp moderation nhưng không có bằng chứng hệ thống.
- Không thể dựng timeline sự cố.
**Suggested phase mapping:** Pha 1 (Governance baseline) + Pha 4 (Operations hardening).

### Pitfall 8: Thiếu chiến lược migration DB cho thay đổi anti-fraud

**What goes wrong:** Thêm cột/bảng chống spam trực tiếp, thiếu script migration có thể lặp lại và rollback.
**Why it happens:** Brownfield SQLite + nhiều script thủ công rời rạc.
**Consequences:** Lệch schema giữa môi trường, lỗi runtime khó đoán, dữ liệu lịch sử không đồng nhất.
**Prevention:**

- Mọi thay đổi schema phải có script migration độc lập trong `database/` theo convention dự án.
- Mỗi migration có bước verify dữ liệu trước/sau, backup và rollback plan.
- Chuẩn hóa naming migration theo mục đích anti-spam/privacy/ux.
**Warning signs (Detection):**
- Máy dev A chạy được, máy dev B lỗi cột/bảng thiếu.
- Script seed/test phụ thuộc thứ tự chạy ngầm.
- Cần sửa tay DB để app hoạt động lại.
**Suggested phase mapping:** Pha 0 (Migration hygiene) trước các pha tính năng.

## Moderate Pitfalls

### Pitfall M1: Rule chống spam hard-code, không quan sát được

**What goes wrong:** Ngưỡng cố định trong code, không có dashboard theo dõi hiệu quả rule.
**Prevention:** Đưa threshold vào config, log score distribution, review theo tuần.
**Warning signs:** Mỗi lần đổi rule phải deploy code; team không biết rule nào đang tạo false positives.
**Suggested phase mapping:** Pha 2.

### Pitfall M2: Không tách “dữ liệu bằng chứng” và “dữ liệu hiển thị”

**What goes wrong:** Dữ liệu upload được phục vụ gần public path, rủi ro lộ chứng cứ.
**Prevention:** Lưu private storage, cấp quyền truy cập có kiểm soát/signed URL ngắn hạn.
**Warning signs:** Link evidence truy cập được khi không đăng nhập.
**Suggested phase mapping:** Pha 1 + Pha 4.

### Pitfall M3: Không có test hồi quy cho các đường nhạy cảm

**What goes wrong:** Mỗi lần đổi UX/anti-spam làm hỏng auth/report mà không phát hiện sớm.
**Prevention:** Bắt buộc test cho CSRF/rate-limit/OTP expiry/dedup/report moderation side-effects.
**Warning signs:** Hotfix tăng sau mỗi đợt release UX hoặc anti-spam.
**Suggested phase mapping:** Pha 1 (test harness) duy trì xuyên suốt.

## Minor Pitfalls

### Pitfall m1: Thông điệp UX chống spam quá mơ hồ

**What goes wrong:** Người dùng bị chặn nhưng không hiểu vì sao và làm gì tiếp theo.
**Prevention:** Viết copy rõ ràng: lý do chung, thời gian thử lại, kênh hỗ trợ.
**Warning signs:** Ticket hỗ trợ “không biết lỗi gì”.
**Suggested phase mapping:** Pha 3.

### Pitfall m2: Không đồng bộ style/token giữa các trang sau redesign

**What goes wrong:** Light mode không nhất quán, trải nghiệm bị “vá chỗ”.
**Prevention:** Chuẩn hóa design tokens và checklist UI regression desktop/mobile.
**Warning signs:** Cùng một component hiển thị khác nhau giữa trang.
**Suggested phase mapping:** Pha 3 + Pha 4.

## Suggested Phase Mapping (Roadmap-oriented)

| Phase Topic | Mục tiêu | Pitfalls cần chặn ngay |
|-------------|----------|-------------------------|
| Pha 0 - Migration hygiene | Ổn định nền DB trước khi thêm anti-fraud | Pitfall 8 |
| Pha 1 - Security & governance baseline | CSRF, rate-limit, audit log, phân lớp dữ liệu | Pitfall 2, 3, 4, 7, M2, M3 |
| Pha 2 - Anti-spam engine | Risk scoring đa tín hiệu + reliability | Pitfall 1, 5, M1 |
| Pha 3 - UX redesign incremental | Light mode + quiz one-question/page theo rollout | Pitfall 6, m1, m2 |
| Pha 4 - Tuning & operations | Giảm false positive, vận hành moderation ổn định | Pitfall 1, 6, 7, M2 |
| Pha 5 - Scale readiness | Tách tác vụ nền, chuẩn bị tăng tải | Pitfall 5, 8 |

## Phase-Specific Warning Triggers

| Phase Topic | Warning trigger thực tế | Mitigation ngay |
|-------------|-------------------------|-----------------|
| Pha 1 | Endpoint POST chưa có CSRF/rate-limit đồng nhất | Chặn release đến khi pass security checklist |
| Pha 2 | Tỷ lệ block tăng nhưng spam vẫn lọt | Hiệu chỉnh score + thêm lớp challenge thay vì block cứng |
| Pha 3 | Completion rate quiz giảm >10% sau rollout | Rollback flag + phân tích funnel theo bước |
| Pha 4 | Khiếu nại moderation tăng, không truy vết được | Bắt buộc reason code + audit timeline |
| Pha 5 | Timeout dịch vụ ngoài kéo sập luồng report | Queue hóa tác vụ chậm + timeout/fallback profile |

## Sources

- `.planning/PROJECT.md` (HIGH, bối cảnh mục tiêu và phạm vi active)
- `.planning/codebase/CONCERNS.md` (HIGH, bằng chứng rủi ro bảo mật/kiến trúc/vận hành hiện tại)
- `.planning/codebase/CONVENTIONS.md` (HIGH, ràng buộc triển khai theo style và cấu trúc hiện có)
- Kinh nghiệm triển khai Flask security/abuse-prevention trong ngành (MEDIUM, cần xác thực chi tiết khi vào từng phase implementation)
