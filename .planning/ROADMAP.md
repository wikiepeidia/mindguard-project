# MindGuard v2 Roadmap

**Created:** 2026-03-19
**Granularity:** standard
**Coverage:** 16/16 v1.0 requirements mapped · 10/10 v1.1 requirements mapped · 17/17 v1.2 requirements mapped · 13/13 v1.3 requirements mapped · 17/17 v1.4 requirements mapped

## Phases

### v1.0 — Core Platform (Completed)

- [x] **Phase 1: Privacy & Data Governance Foundation** - Chuan hoa masking du lieu nhay cam va audit truy cap de tao nen tang tin cay.
 (completed 2026-03-20)
- [x] **Phase 2: Anti-Spam Monitor & Soft Enforce** - Trien khai chong spam da tin hieu theo lo trinh monitor truoc, soft-enforce sau.
 (completed 2026-03-20)
- [x] **Phase 3: Light Mode UX System** - Dong bo light mode, design tokens va mobile-first cho cac trang uu tien.
 (completed 2026-03-20)
- [x] **Phase 4: Quiz One-Question Flow** - Chuyen quiz sang luong 1 cau hoi/trang voi tien do ro rang va trang thai on dinh.
 (completed 2026-03-23)
- [x] **Phase 5: Leaderboard Integrity** - Ra mat bang vinh danh nguoi to cao nhieu nhat kem luat giam gian lan.
 (completed 2026-03-23)
- [x] **Phase 6: Reporting SOP & ML Readiness** - Chuan hoa tai lieu van hanh bao cao va dinh nghia lo trinh du lieu/ML cho giai doan sau v1.
 (completed 2026-03-26)

### v1.1 — PostgreSQL & Vercel Deployment

- [x] **Phase 7: PostgreSQL Configuration & Connection** - Fix config, them driver, chuyen URI sang NeonDB PostgreSQL va xac nhan ket noi local.
 (completed 2026-04-03)
- [x] **Phase 8: App Startup Cleanup & Data Seeding** - Xoa seed-on-cold-start, xac nhan create_all va chay seed 1 lan tren NeonDB.
 (completed 2026-04-04)
- [x] **Phase 9: Vercel Deployment & Verification** - Cau hinh env vars tren Vercel va xac nhan deployment tra ve 200.
 (completed 2026-04-04)

### v1.2 — Beta 1 Go-Live (Code Freeze)

- [x] **Phase 10: Infrastructure & Security Hardening** - Loai bo startup risk va di chuyen credentials sang env vars truoc khi Beta go-live. (completed 2026-04-13)
- [x] **Phase 11: UI Bug Fixes** - Sua het loi UI nghiem trong va polish tong the truoc Beta.
 (completed 2026-04-13)
- [x] **Phase 12: AI Safety** - Dam bao AI chatbot an toan, nhanh, va phu hop ngon ngu nguoi dung pho thong.
 (completed 2026-04-13)
- [x] **Phase 13: Rate Limiting & Trust Signals** - Chong drain API budget, logging baseline, banner quyen rieng tu, va nut gop y cho Beta.
 (completed 2026-04-13)
- [x] **Phase 14: Stress Test & Beta Sign-off** - Tim nguong CCU toi da va xac nhan toan bo he thong san sang cho Beta 1.
 (completed 2026-04-14)

### v1.3 — Hoàn thiện Tài liệu Kỹ thuật & SOP v1

- [x] **Phase 15: Conventions & Redaction Setup** - Thiết lập quy ước viết tài liệu và bảo vệ thông tin nhạy cảm trước khi viết.
 (completed 2026-04-14)
- [x] **Phase 16: Foundation Documents** - Document database schema và ghi nhận các quyết định kiến trúc (ADRs).
 (completed 2026-04-14)
- [x] **Phase 17: System Documents** - Viết ARCHITECTURE.md và API.md phản ánh đúng hệ thống hiện tại.
 (completed 2026-04-14)
- [x] **Phase 18: Operational SOPs** - Cập nhật và viết mới 3 SOP vận hành cho team.
 (completed 2026-04-14)
- [x] **Phase 19: Verification & Maintenance Setup** - Xác minh tài liệu đúng với codebase và thiết lập cơ chế chống docs drift.
 (completed 2026-04-14)

### v1.4 - OTP Email Reliability & QA

- [x] **Phase 20: OTP Security Policy Core** - Loai bo OTP hardcode va chuan hoa lifecycle verify an toan.
 (completed 2026-04-15)
- [x] **Phase 21: Production OTP Email Delivery** - Kich hoat gui OTP email that tren production voi xu ly loi ro rang.
 (completed 2026-04-15)
- [ ] **Phase 22: Resend & Verify Session Stability** - On dinh luong resend/verify va session contract khi refresh/het han.
- [ ] **Phase 23: OTP Abuse Guardrails** - Bao ve endpoint verify/resend bang throttling nhieu lop va anti-spam telemetry.
- [ ] **Phase 24: OTP QA Reliability Gate** - Khoa chat luong bang bo test tu dong cho cac nhanh OTP quan trong.

## Phase Details

### Phase 1: Privacy & Data Governance Foundation

**Goal**: Nguoi dung va admin chi nhin thay du lieu nhay cam o dang duoc bao ve, co kha nang kiem toan truy cap ro rang.
**Depends on**: Nothing (first phase)
**Requirements**: PRIV-01, PRIV-02, PRIV-03
**Success Criteria** (what must be TRUE):

1. So dien thoai o tat ca diem hien thi chi con dang che va chi lo 3 so cuoi.
2. Cung mot quy tac masking duoc ap dung nhat quan cho cac truong nhay cam tren cac trang uu tien.
3. Admin co the xem nhat ky truy cap du lieu nhay cam voi thong tin actor, thoi diem va hanh dong.
**Plans**: 2 plans

Plans:

- [ ] 01-01-PLAN.md - Privacy policy foundation va enforcement cho public/user output.
- [ ] 01-02-PLAN.md - Audit log schema + admin governance flow cho full-data access.

### Phase 2: Anti-Spam Monitor & Soft Enforce

**Goal**: He thong giam spam bao cao bang co che danh gia rui ro da tin hieu, uu tien giam false-positive.
**Depends on**: Phase 1
**Requirements**: ABUS-01, ABUS-02, ABUS-03, ABUS-04
**Success Criteria** (what must be TRUE):

1. Nguoi dung gui to cao qua nhanh trong cua so thoi gian se bi danh dau/canh bao theo rule tan suat.
2. Moi quyet dinh rui ro su dung ket hop IP, cookie va account thay vi mot tin hieu don le.
3. Van hanh co monitor mode truoc, sau do chuyen sang soft-enforce theo nguong cau hinh.
4. Khi bi cooldown hoac thay doi trang thai, nguoi dung nhan thong bao ly do ro rang va han cho.
**Plans**: 3 plans

Plans:

- [x] 02-01-PLAN.md - Anti-spam core service + telemetry schema + risk scoring tests.
- [x] 02-02-PLAN.md - Route integration monitor-first va soft-enforce gate cho report flow.
- [x] 02-03-PLAN.md - User cooldown/status messaging + admin anti-spam telemetry summary.

### Phase 3: Light Mode UX System

**Goal**: Nguoi dung trai nghiem giao dien light mode dong bo, de doc va de dung tren desktop/mobile.
**Depends on**: Phase 1
**Requirements**: UI-01, UI-02, UI-03
**Success Criteria** (what must be TRUE):

1. Cac trang auth, quiz, report, profile, leaderboard deu hien thi light mode thong nhat.
2. Mau, font va spacing tren cac trang uu tien dung chung bo design tokens da dinh nghia.
3. Nguoi dung tren man hinh di dong pho bien co the thao tac quiz/report de dang theo huong mobile-first.
**Plans**: 3 plans

Plans:

- [x] 03-01-PLAN.md - Light token foundation + base/auth/profile migration.
- [x] 03-02-PLAN.md - Report + quiz mobile-first light-mode rollout.
- [x] 03-03-PLAN.md - Leaderboard/scammer-profile convergence + token coverage guard.

### Phase 4: Quiz One-Question Flow

**Goal**: Nguoi dung hoan thanh quiz theo tung buoc ro rang, giam roi va giam mat trang thai bai lam.
**Depends on**: Phase 3
**Requirements**: QUIZ-01, QUIZ-02, QUIZ-03, QUIZ-04
**Success Criteria** (what must be TRUE):

1. Nguoi dung lam quiz theo dung luong 1 cau hoi moi trang tu dau den cuoi.
2. Tien do va trang thai bai lam duoc hien thi ro rang o moi buoc quiz.
3. Neu refresh/back trong phien hop le, bai lam van giu duoc trang thai hop ly.
4. Bo cau hoi bo sung theo chu de bao mat/lua dao da san sang de phu hop luong quiz moi.
**Plans**: 3 plans

Plans:

- [ ] 04-01-PLAN.md - Session-backed one-question route flow + resume stability baseline tests.
- [ ] 04-02-PLAN.md - Quiz progress/status UI contract and one-question interaction clarity.
- [ ] 04-03-PLAN.md - Topic-expanded question bank and submit/result/certificate compatibility guards.

### Phase 5: Leaderboard Integrity

**Goal**: Nguoi dung thay bang vinh danh co y nghia va han che duoc hanh vi gian lan de leo hang.
**Depends on**: Phase 2, Phase 3
**Requirements**: LEAD-01, LEAD-02
**Success Criteria** (what must be TRUE):

1. Nguoi dung co the xem bang vinh danh nguoi to cao nhieu nhat tren giao dien.
2. Bang xep hang khong chi dua vao dem tho, ma co luat integrity de giam thao tung/gian lan.
3. Ket qua xep hang duoc cap nhat o muc chap nhan duoc va phan anh dung luat da cong bo.
**Plans**:

- [x] 05-01-PLAN.md - Reporter leaderboard data layer and integrity service.

### Phase 6: Reporting SOP & ML Readiness

**Goal**: Team van hanh duoc quy trinh bao cao mot cach nhat quan ngay trong v1, dong thoi co lo trinh du lieu/ML ro rang cho giai doan sau ma khong dua auto-moderation vao production som.
**Depends on**: Phase 1, Phase 2, Phase 5
**Requirements**: DOC-01, DOC-02, ML-01, ML-02
**Success Criteria** (what must be TRUE):

1. Co tai lieu SOP bang tieng Viet cho admin duyet/tu choi/xuat du lieu bao cao, co luu y privacy va placeholder anh minh hoa.
2. Co huong dan nguoi dung bang tieng Viet cho luong gui bao cao, bang chung, trang thai va cac canh bao can biet.
3. Co tai lieu readiness cho du lieu/ML mo ta 1 thang thu thap du lieu, schema gan nhan, quy tac an danh, offline evaluation va human-in-the-loop rollout sau v1.
**Plans**: 2 plans

Plans:

- [x] 06-01-PLAN.md - Reporting SOP va huong dan nguoi dung cho luong bao cao hien tai.
- [x] 06-02-PLAN.md - Data collection + ML moderation readiness roadmap (khong implement model trong v1).

### Phase 7: PostgreSQL Configuration & Connection

**Goal**: Flask app ket noi thanh cong toi NeonDB PostgreSQL thay vi SQLite, xac nhan local.
**Depends on**: Phase 6 (v1.0 complete)
**Requirements**: DBCFG-01, DBCFG-02, DBCFG-03, DBCFG-04, START-02
**Success Criteria** (what must be TRUE):

1. Flask app khoi dong local khong loi va ket noi duoc toi NeonDB PostgreSQL (SELECT 1 thanh cong).
2. `.env/prosgressql_neondb.json` la file JSON hop le, `json.load()` parse duoc va chua key `DATABASE_URL`.
3. `config.py` khong con bat ky logic SQLite hoac `IS_VERCEL` `/tmp` path nao.
4. Connection su dung NeonDB pooler endpoint voi `pool_pre_ping=True`, `sslmode=require` va pool tuning phu hop serverless.
**Plans**: 1 plan

Plans:

- [x] 07-01-PLAN.md — Fix JSON config, add psycopg2 driver, rewrite config.py for NeonDB PostgreSQL, verify connection

### Phase 8: App Startup Cleanup & Data Seeding

**Goal**: App startup sach (khong seed moi cold start) va NeonDB co day du tables + seed data.
**Depends on**: Phase 7
**Requirements**: START-01, START-03, SEED-01
**Success Criteria** (what must be TRUE):

1. `app.py` khong con chay bat ky seed logic nao khi import hoac cold start.
2. `db.create_all()` tao thanh cong tat ca tables trong NeonDB (xac nhan bang query).
3. Seed data (quiz questions, scam types, admin user) ton tai trong NeonDB sau khi chay script 1 lan.
4. App khoi dong va serve pages voi du lieu tu NeonDB (cac trang quiz, leaderboard, report tra ve ket qua).
**Plans**: TBD

### Phase 9: Vercel Deployment & Verification

**Goal**: MindGuard deploy thanh cong tren Vercel va phuc vu tat ca cac trang khong con 500 errors.
**Depends on**: Phase 8
**Requirements**: VDEP-01, VDEP-02
**Success Criteria** (what must be TRUE):

1. Tat ca environment variables can thiet (DATABASE_URL, SECRET_KEY, API keys) duoc cau hinh trong Vercel dashboard.
2. Vercel deployment hoan tat khong co build errors.
3. Homepage, quiz, report va auth pages deu tra ve HTTP 200 tren production URL.
4. Cold start hoan thanh trong gioi han 10s cua Vercel hobby tier.
**Plans**: TBD

### Phase 10: Infrastructure & Security Hardening

**Goal**: App khong con chua bat ky startup risk hay hardcoded credentials nao truoc khi Beta go-live.
**Depends on**: Phase 9 (v1.1 complete)
**Requirements**: INFRA-01, INFRA-02, INFRA-03
**Success Criteria** (what must be TRUE):

1. Cold start khong thuc thi `db.create_all()` — app.py import nhanh, khong co DB operation nao xay ra truoc khi request den.
2. `ADMIN_PASSWORD`, `REPORT_ENCRYPTION_KEY`, va `SECRET_KEY` fallback khong con hardcode trong `config.py` — tat ca lay tu Vercel environment variables.
3. Frontend khong lo bat ky admin credential nao trong HTML, JS, hoac network response ma nguoi dung co the inspect.
4. Deploy Vercel sau khi thay doi van tra ve 200 tren cac trang chinh (homepage, quiz, auth).
**Plans**: 1 plan

Plans:

- [x] 10-01-PLAN.md — Remove db.create_all() from startup and move hardcoded credentials to env vars

### Phase 11: UI Bug Fixes

**Goal**: Nguoi dung co the su dung day du cac tinh nang chinh cua MindGuard ma khong gap loi UI nao truoc Beta.
**Depends on**: Phase 10
**Requirements**: UIFIX-01, UIFIX-02, UIFIX-03, UIFIX-04, UIFIX-05
**Success Criteria** (what must be TRUE):

1. Nguoi dung click "Dang xuat" trong dropdown menu va duoc dang xuat thanh cong.
2. Nguoi dung click vao "Ho so" trong menu va duoc dieu huong dung trang, hitbox du lon de click tren mobile.
3. Nguoi dung da dang nhap mo chatbot bubble, gui tin nhan, dong lai, mo lai — lich su hoi thoai van hien thi day du.
4. Huy hieu "Certification Verify" hien thi ro rang, dung style, va phan biet duoc voi cac badge khac.
5. Giao dien tong the gon dep, khong co element bi lech/tran/che khuat khi kiem tra bang mat thuong truoc Beta.
**Plans**: TBD
**UI hint**: yes

### Phase 12: AI Safety

**Goal**: AI chatbot tra loi an toan, dung thoi han, va bang ngon ngu de hieu cho tat ca nguoi dung.
**Depends on**: Phase 10
**Requirements**: AISF-01, AISF-02, AISF-03, AISF-04
**Success Criteria** (what must be TRUE):

1. Cac endpoint chatbot khong bao gio vuot qua 8 giay cho OpenRouter call — Vercel function khong bi kill do timeout.
2. Khi nguoi dung hoi ve chu de chinh tri, ton giao, hoac tu hai, chatbot tra loi bang thong diep cung dinh nghia san va hien thi so hotline Cong an HN 113 thay vi tiep tuc tro chuyen.
3. Khi AI khong chac chan ve cau tra loi, nguoi dung thay canh bao ro rang kem huong dan lien he co quan chuc nang — khong nhan thong tin co ve chinh xac nhung sai.
4. System prompt viet bang ngon ngu binh dan, cau tra loi AI khong dung thuat ngu ky thuat trong tuong tac thuc te.
**Plans**: 1 plan

Plans:

- [x] 12-01-PLAN.md — Fix chatbot timeout 8s + set Vercel env vars + redeploy

### Phase 13: Rate Limiting & Trust Signals

**Goal**: Nguoi dung thay MindGuard bao ve quyen rieng tu cua ho, API budget duoc bao ve, va co the gop y de cai thien san pham.
**Depends on**: Phase 12
**Requirements**: INFRA-04, TRUST-01, TRUST-02, TRUST-03
**Success Criteria** (what must be TRUE):

1. Sau khi vuot nguong so luong request, `/chatbot/api`, `/chatbot/support`, va `/chatbot/send` tra ve thong bao rate limit — khong the tiep tuc gui lien tuc de drain API.
2. Rate limit counter luu tren NeonDB — hoat dong nhat quan tren nhieu Vercel function instance (khong bi reset giua cac cold start).
3. Trang chu hien thi banner quyen rieng tu ro rang: MindGuard KHONG luu thong tin ca nhan, KHONG yeu cau quyen truy cap danh ba/tin nhan.
4. Request, error, va audit logs duoc ghi lai va luu tru an toan tren Vercel — co the truy xuat khi can debug.
5. Nguoi dung thay nut "Bao cao sai / Gop y" tren giao dien chatbot va co the gui phan hoi duoc luu vao DB.
**Plans**: TBD
**UI hint**: yes

### Phase 14: Stress Test & Beta Sign-off

**Goal**: Team biet chinh xac ngung CCU toi da cua he thong va co bang chung he thong san sang cho Beta 1 Ha Noi.
**Depends on**: Phase 13
**Requirements**: INFRA-05
**Success Criteria** (what must be TRUE):

1. Locust chay thanh cong voi tai tang dan — tim duoc nguong CCU noi error rate bat dau tang > 5%.
2. Co bao cao stress test ghi ro: nguong CCU on dinh, P50/P95 latency, diem that bai dau tien (endpoint nao, loi gi).
3. Neu nguong CCU thap hon muc chap nhan cho Beta, co ke hoach giam thieu cu the truoc khi go-live.
4. Tat ca 17 yeu cau v1.2 da duoc xac nhan hoat dong tren production URL truoc khi ky Beta sign-off.
**Plans**: TBD

### Phase 15: Conventions & Redaction Setup

**Goal**: Quy ước viết tài liệu và bảo vệ thông tin nhạy cảm được thiết lập trước khi viết bất kỳ tài liệu nào.
**Depends on**: Phase 14 (v1.2 complete)
**Requirements**: CONV-01, CONV-02
**Success Criteria** (what must be TRUE):

1. File  tồn tại trong repo, liệt kê tất cả biến môi trường cần thiết với giá trị placeholder — không chứa secret thật.
2. Có file quy ước ngôn ngữ Việt-Anh rõ ràng: prose viết bằng tiếng Việt, thuật ngữ kỹ thuật giữ nguyên tiếng Anh, bảng thuật ngữ (glossary) đi kèm.
3. Tất cả tài liệu viết ở các phase sau tuân thủ quy ước ngôn ngữ và không chứa bất kỳ credential/secret thật nào.
**Plans**: 1 plan

Plans:

- [x] 15-01-PLAN.md — Create .env.example and docs/technical/CONVENTIONS.md

### Phase 16: Foundation Documents (DECISIONS.md + DATABASE.md)

**Goal**: Các quyết định kiến trúc được ghi nhận chính thức và schema database được document đầy đủ làm nền tảng tham chiếu cho mọi tài liệu sau.
**Depends on**: Phase 15
**Requirements**: TECH-03, ADR-01, ADR-02, ADR-03, ADR-04
**Success Criteria** (what must be TRUE):

1. DATABASE.md chứa tất cả bảng từ models.py (tên bảng, cột, kiểu dữ liệu, quan hệ) kèm ER diagram Mermaid render được trên GitHub.
2. ADR-002 (NeonDB migration) ghi rõ context, decision, rationale, consequences — reader hiểu tại sao chuyển từ SQLite sang PostgreSQL.
3. ADR-003 (Vercel deployment) giải thích serverless constraints (ephemeral filesystem, cold start, 10s timeout) và cách MindGuard thích ứng.
4. ADR-004 (AI safety) document chiến lược hard-block chủ đề nhạy cảm + fallback khi AI không chắc chắn + timeout 8s.
5. ADR-005 (Rate limiting) giải thích lựa chọn DB-backed @limiter thay vì in-memory counter và tại sao phù hợp serverless.
**Plans**: 2 plans

Plans:

- [x] 16-01-PLAN.md — Viết DATABASE.md với schema đầy đủ và Mermaid ER diagram
- [x] 16-02-PLAN.md — Thêm ADR-002 đến ADR-005 và cập nhật ADR-001

### Phase 17: System Documents (ARCHITECTURE.md + API.md)

**Goal**: Team member mới có thể hiểu kiến trúc tổng thể và tất cả API endpoints của MindGuard từ tài liệu mà không cần đọc source code.
**Depends on**: Phase 16
**Requirements**: TECH-01, TECH-02
**Success Criteria** (what must be TRUE):

1. ARCHITECTURE.md phản ánh đúng stack hiện tại (Flask + NeonDB PostgreSQL + Vercel serverless) với ít nhất 2 Mermaid diagrams (system overview, request flow).
2. API.md liệt kê đầy đủ tất cả routes (8 blueprints) với method, path, auth requirement, và mô tả response.
3. API.md phân loại rõ ràng giữa HTML page routes và JSON API endpoints — reader biết endpoint nào trả HTML, endpoint nào trả JSON.
4. Cross-references giữa ARCHITECTURE.md ↔ DATABASE.md ↔ API.md nhất quán — không có tên bảng, route, hay model nào mâu thuẫn giữa các file.
**Plans**: 2 plans

Plans:

- [x] 17-01-PLAN.md — Rewrite ARCHITECTURE.md cho NeonDB + Vercel stack với 2 Mermaid diagrams
- [x] 17-02-PLAN.md — Rewrite API.md với đầy đủ routes từ 8 blueprints

### Phase 18: Operational SOPs

**Goal**: Bất kỳ team member nào cũng có thể vận hành, quản trị, và kiểm duyệt báo cáo trên MindGuard theo tài liệu SOP mà không cần hỏi developer gốc.
**Depends on**: Phase 17
**Requirements**: SOP-01, SOP-02, SOP-03
**Success Criteria** (what must be TRUE):

1. SOP_BAO_CAO.md được cập nhật đúng theo routes/models hiện tại — không còn reference đến schema SQLite cũ hay routes không tồn tại.
2. SOP Vận hành hệ thống document đầy đủ quy trình: deploy lên Vercel, xem logs trên Vercel dashboard, rollback deployment, xử lý sự cố thường gặp.
3. SOP Quản trị viên document workflow: đăng nhập admin, duyệt/từ chối báo cáo, export data, moderation flow với các bước cụ thể.
4. Cả 3 SOP cross-reference đúng đến API.md và DATABASE.md khi đề cập endpoints hoặc bảng dữ liệu.
**Plans**: 2 plans

Plans:

- [x] 18-01-PLAN.md — Cập nhật SOP_BAO_CAO.md (fix routes, cross-refs)
- [x] 18-02-PLAN.md — Tạo SOP_VAN_HANH.md + SOP_QUAN_TRI.md

### Phase 19: Verification & Maintenance Setup

**Goal**: Tất cả tài liệu v1.3 được xác minh chính xác với codebase hiện tại và có cơ chế ngăn docs drift trong tương lai.
**Depends on**: Phase 18
**Requirements**: Cross-cutting (verifies all v1.3 deliverables: CONV-01 → SOP-03)
**Success Criteria** (what must be TRUE):

1. Mỗi fact trong tài liệu (tên bảng, route path, config key, model name) đã được kiểm tra chéo với codebase — không có thông tin sai hoặc outdated.
2. Không còn PLACEHOLDER nào chưa được xử lý trong tất cả tài liệu v1.3.
3. Mỗi tài liệu có metadata header ghi rõ owner, last updated date, và source files tham chiếu.
4. Conventions file có quy tắc cập nhật tài liệu khi code thay đổi — team biết khi nào và file nào cần update.

**Plans:** 2/2 plans complete

Plans:

- [x] 19-01-PLAN.md — Cross-check all facts in docs vs codebase + PLACEHOLDER audit
- [x] 19-02-PLAN.md — Metadata headers on all docs + docs maintenance rules in CONVENTIONS.md

### Phase 20: OTP Security Policy Core

**Goal**: Nguoi dung nhan OTP ngau nhien, OTP co TTL/attempt/single-use va khong con bat ky duong hardcode nao.
**Depends on**: Phase 19 (v1.3 complete)
**Requirements**: OTPSEC-01, OTPSEC-02, OTPSEC-03, OTPPOL-01, OTPPOL-02, OTPPOL-03
**Success Criteria** (what must be TRUE):

1. Moi challenge OTP moi deu la ma 6 chu so ngau nhien va khong co gia tri fallback tinh nao co the xac thuc.
2. OTP het hieu luc dung theo TTL cau hinh (mac dinh 5 phut) va he thong tu choi ma da het han.
3. Nguoi dung nhap sai OTP qua nguong se bi khoa tam thoi va nhin thay thong bao thoi gian thu lai.
4. OTP xac thuc thanh cong chi dung duoc mot lan, va OTP cu bi vo hieu ngay khi resend/new challenge.
5. Kiem tra logs va persistence khong tim thay OTP plaintext duoc luu hoac hien thi.
**Plans**: 3 plans

Plans:

- [x] 20-01-PLAN.md — OTP challenge schema + crypto helper foundation.
- [x] 20-02-PLAN.md — Register/verify lifecycle enforcement (TTL, lockout, single-use).
- [x] 20-03-PLAN.md — OTP security regression tests + validation evidence update.

### Phase 21: Production OTP Email Delivery

**Goal**: Nguoi dung nhan OTP email that tren production va duoc huong dan retry ro rang khi gui that bai.
**Depends on**: Phase 20
**Requirements**: OTPMAIL-01, OTPMAIL-02, OTPMAIL-03
**Success Criteria** (what must be TRUE):

1. Sau khi dang ky/xac minh, nguoi dung nhan duoc email OTP qua provider cau hinh tren production.
2. Neu gui email OTP that bai, tai khoan khong duoc kich hoat va nguoi dung nhan huong dan thu lai ro rang.
3. Kiem tra runtime config xac nhan tat ca mail/OTP credentials duoc nap tu environment variables, khong hardcode secrets.
**Plans**: 3 plans

Plans:

- [x] 21-01-PLAN.md - Resend provider config + OTP email delivery service foundation.
- [x] 21-02-PLAN.md - Register flow integration with fail-closed OTP delivery handling.
- [x] 21-03-PLAN.md - OTP delivery tests + validation evidence mapping.

### Phase 22: Resend & Verify Session Stability

**Goal**: Nguoi dung co the resend OTP an toan va giu duoc trang thai verify on dinh trong suot phien dang ky.
**Depends on**: Phase 21
**Requirements**: OTPRES-01, OTPRES-02, OTPSES-01
**Success Criteria** (what must be TRUE):

1. Tu verify flow, nguoi dung resend OTP ma khong can nhap lai toan bo form dang ky.
2. Cooldown va resend cap duoc ap dung ro rang; nguoi dung nhin thay trang thai cho truoc khi gui lai.
3. Refresh verify page van giu dung pending state; pending state thieu/het han se duoc redirect an toan ve dang ky.
**Plans**: TBD
**UI hint**: yes

### Phase 23: OTP Abuse Guardrails

**Goal**: Luong OTP chong brute-force/spam on dinh nho route-level rate limit va challenge-level throttling ket hop anti-spam telemetry.
**Depends on**: Phase 22
**Requirements**: OTPREL-01, OTPREL-02
**Success Criteria** (what must be TRUE):

1. Verify va resend requests vuot nguong bi chan boi rate limit thay vi tiep tuc xu ly OTP.
2. Cooldown resend va lockout attempts phoi hop nhat quan voi anti-spam telemetry tren cung challenge.
3. Nguoi dung hop le voi toc do thao tac binh thuong van hoan tat xac thuc ma khong bi chan sai.
**Plans**: TBD

### Phase 24: OTP QA Reliability Gate

**Goal**: Team co bo kiem thu tu dong dang tin cay de chan hoi quy OTP truoc moi lan release.
**Depends on**: Phase 23
**Requirements**: OTPQA-01, OTPQA-02, OTPQA-03
**Success Criteria** (what must be TRUE):

1. Unit tests bao phu generation, expiry, resend policy va lockout transitions cho OTP logic.
2. Route tests bao phu register -> OTP send -> verify cho ca nhanh thanh cong va that bai.
3. Integration tests mock mail-provider failure va concurrent verify edge cases, chi chap nhan mot verify success hop le.
4. Test suite OTP chay pass on dinh truoc khi milestone duoc xem la san sang deploy.
**Plans**: TBD

## Progress Table

| Phase | Plans Complete | Status | Completed |
| ----- | -------------- | ------ | --------- |
| 1. Privacy & Data Governance Foundation | 0/2 | Complete | 2026-03-20 |
| 2. Anti-Spam Monitor & Soft Enforce | 3/3 | Complete | 2026-03-20 |
| 3. Light Mode UX System | 3/3 | Complete | 2026-03-20 |
| 4. Quiz One-Question Flow | 3/3 | Complete | 2026-03-23 |
| 5. Leaderboard Integrity | 2/2 | Complete | 2026-03-23 |
| 6. Reporting SOP & ML Readiness | 2/2 | Complete | 2026-03-26 |
| 7. PostgreSQL Configuration & Connection | 1/1 | Complete | 2026-04-03 |
| 8. App Startup Cleanup & Data Seeding | 1/1 | Complete | 2026-04-04 |
| 9. Vercel Deployment & Verification | 1/1 | Complete | 2026-04-04 |
| 10. Infrastructure & Security Hardening | 1/1 | Complete    | 2026-04-13 |
| 11. UI Bug Fixes | 0/0 | Complete (all 5 reqs done by teammate) | 2026-04-13 |
| 12. AI Safety | 1/1 | Complete | 2026-04-13 |
| 13. Rate Limiting & Trust Signals | 0/? | Complete (4/4 reqs done — TRUST-03 feedback button added) | 2026-04-13 |
| 14. Stress Test & Beta Sign-off | 1/1 | Complete | 2026-04-14 |
| 15. Conventions & Redaction Setup | 1/1 | Complete    | 2026-04-14 |
| 16. Foundation Documents | 2/2 | Complete    | 2026-04-14 |
| 17. System Documents | 2/2 | Complete    | 2026-04-14 |
| 18. Operational SOPs | 2/2 | Complete    | 2026-04-14 |
| 19. Verification & Maintenance Setup | 2/2 | Complete    | 2026-04-14 |
| 20. OTP Security Policy Core | 3/3 | Complete   | 2026-04-15 |
| 21. Production OTP Email Delivery | 3/3 | Complete    | 2026-04-15 |
| 22. Resend & Verify Session Stability | 0/TBD | Not started | - |
| 23. OTP Abuse Guardrails | 0/TBD | Not started | - |
| 24. OTP QA Reliability Gate | 0/TBD | Not started | - |
