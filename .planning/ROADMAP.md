# MindGuard v2 Roadmap

**Created:** 2026-03-19
**Granularity:** standard
**Coverage:** 16/16 v1.0 requirements mapped · 10/10 v1.1 requirements mapped

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

- [ ] **Phase 7: PostgreSQL Configuration & Connection** - Fix config, them driver, chuyen URI sang NeonDB PostgreSQL va xac nhan ket noi local.
- [ ] **Phase 8: App Startup Cleanup & Data Seeding** - Xoa seed-on-cold-start, xac nhan create_all va chay seed 1 lan tren NeonDB.
- [ ] **Phase 9: Vercel Deployment & Verification** - Cau hinh env vars tren Vercel va xac nhan deployment tra ve 200.

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

## Progress Table

| Phase | Plans Complete | Status | Completed |
| ----- | -------------- | ------ | --------- |
| 1. Privacy & Data Governance Foundation | 0/2 | Complete | 2026-03-20 |
| 2. Anti-Spam Monitor & Soft Enforce | 3/3 | Complete | 2026-03-20 |
| 3. Light Mode UX System | 3/3 | Complete | 2026-03-20 |
| 4. Quiz One-Question Flow | 3/3 | Complete | 2026-03-23 |
| 5. Leaderboard Integrity | 2/2 | Complete | 2026-03-23 |
| 6. Reporting SOP & ML Readiness | 2/2 | Complete | 2026-03-26 |
| 7. PostgreSQL Configuration & Connection | 0/0 | Not started | - |
| 8. App Startup Cleanup & Data Seeding | 0/0 | Not started | - |
| 9. Vercel Deployment & Verification | 0/0 | Not started | - |
