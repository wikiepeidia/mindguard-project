# Light Mode Hotspot Scan

Ngày quét: 2026-03-20
Phạm vi: templates/ + static/css/
Mục tiêu: tìm vị trí có nguy cơ xung đột Light mode do class màu cứng hoặc hardcode màu tối.

## Kết quả nhanh

- Đã xác nhận các fix regression trước đó vẫn hoạt động ổn ở route công khai chính.
- Có nhiều điểm chứa text-white/bg-dark/hardcode màu tối, nhưng một phần lớn thuộc trang admin hoặc block có chủ ý dark-style.
- Chưa tự động sửa hàng loạt để tránh gây hồi quy giao diện toàn cục.

## Hotspot ưu tiên kiểm tra thủ công

1. Homepage
- templates/index.html
- static/css/homepage.css
- static/css/style.css

2. Footer + flash + dropdown toàn cục
- templates/base.html
- static/css/style.css
- static/js/base.js

3. Report scammer
- templates/report_scammer.html
- static/css/report_scammer.css

4. Nhóm trang nội dung có nhiều text-white
- templates/library.html
- templates/library_detail.html
- templates/quiz_result.html

5. Admin (không tự động đổi trong pass này)
- templates/admin_dashboard.html
- templates/admin_scammer_reports.html
- templates/admin_sensitive_access_logs.html

## Gợi ý sửa an toàn ở pass kế tiếp

- Ưu tiên thêm override theo scope trang (ví dụ .library-page, .quiz-result-page) thay vì sửa global utility class.
- Tránh thay thế text-white trên toàn hệ thống vì sẽ phá các badge/button tối.
- Với trang admin: chỉ chuyển light mode nếu có yêu cầu riêng cho admin UI.

## Smoke kết quả

- / -> 200
- /login -> 200
- /register -> 200
- /leaderboard -> 200
- /scammer/report -> 200
- /quiz -> 302 (đúng do cần đăng nhập)
- /chatbot/ -> 302 (đúng do cần đăng nhập)
