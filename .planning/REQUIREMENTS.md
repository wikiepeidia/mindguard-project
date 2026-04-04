# Requirements: MindGuard v2

**Defined:** 2026-03-19
**Core Value:** Nguoi dung co the hoc, kiem tra nhan thuc va gui bao cao lua dao mot cach de dung, an toan, va dang tin cay.

## v1.0 Requirements (Completed)

### UI/UX

- [x] **UI-01**: Nguoi dung thay light mode dong bo tren cac trang chinh (auth, quiz, report, profile, leaderboard).
- [x] **UI-02**: He thong su dung design tokens thong nhat (mau, font, spacing) cho cac trang uu tien.
- [x] **UI-03**: Trang quiz va report dam bao trai nghiem mobile-first o kich thuoc man hinh pho bien.

### Quiz

- [x] **QUIZ-01**: Nguoi dung lam bai quiz theo luong 1 cau hoi moi trang.
- [x] **QUIZ-02**: Nguoi dung thay thanh tien do va trang thai ro rang trong suot bai quiz.
- [x] **QUIZ-03**: Trang thai bai lam duoc giu on dinh khi refresh/back trong phien hop le.
- [x] **QUIZ-04**: He thong bo sung bo cau hoi theo chu de bao mat/lua dao de phu hop luong quiz moi.

### Privacy

- [x] **PRIV-01**: So dien thoai duoc che, chi hien 3 so cuoi o tat ca diem hien thi.
- [x] **PRIV-02**: Quy tac masking du lieu nhay cam duoc ap dung nhat quan trong toan he thong.
- [x] **PRIV-03**: Admin co nhat ky truy cap du lieu nhay cam de phuc vu kiem toan.

### Anti-Spam

- [x] **ABUS-01**: He thong ap dung rule tan suat gui to cao theo cua so thoi gian de chan spam.
- [x] **ABUS-02**: He thong danh gia rui ro dua tren da tin hieu (IP + cookie + account).
- [x] **ABUS-03**: Trien khai monitor mode truoc, sau do soft-enforce theo nguong duoc cau hinh.
- [x] **ABUS-04**: Nguoi dung nhan thong bao cooldown/chuyen trang thai voi ly do ro rang.

### Leaderboard

- [x] **LEAD-01**: Hien thi bang vinh danh nguoi to cao nhieu nhat.
- [x] **LEAD-02**: Ap dung integrity rule de giam gian lan tren leaderboard.

### Documentation & Operations

- [x] **DOC-01**: Admin co tai lieu SOP bang tieng Viet cho luong kiem duyet bao cao.
- [x] **DOC-02**: Nguoi dung co tai lieu huong dan bang tieng Viet de gui bao cao dung cach.

### ML Readiness

- [x] **ML-01**: Team co schema du lieu/gan nhan va quy tac an danh de thu thap du lieu moderation.
- [x] **ML-02**: Team co lo trinh offline-first cho baseline ML/DL va human-in-the-loop rollout.

## v1.1 Requirements

Requirements for PostgreSQL migration and Vercel deployment fix.

### Database Configuration

- [x] **DBCFG-01**: `.env/prosgressql_neondb.json` duoc cau truc lai thanh JSON hop le voi key `DATABASE_URL`
- [x] **DBCFG-02**: `config.py` chuyen `SQLALCHEMY_DATABASE_URI` tu SQLite sang NeonDB PostgreSQL
- [x] **DBCFG-03**: `psycopg2-binary` duoc them vao `requirements.txt`
- [x] **DBCFG-04**: SQLAlchemy engine duoc cau hinh `pool_pre_ping=True` va NeonDB pooler endpoint

### App Startup

- [ ] **START-01**: Cold-start seeding bi xoa khoi `app.py` (khong chay `seed_all.py` moi Vercel invocation)
- [x] **START-02**: Logic `IS_VERCEL` SQLite `/tmp` path bi xoa khoi `config.py`
- [ ] **START-03**: `db.create_all()` duoc xac nhan hoat dong voi NeonDB pooler connection

### Data Seeding

- [ ] **SEED-01**: Seed scripts chay 1 lan duy nhat de tao du lieu ban dau tren NeonDB

### Vercel Deployment

- [ ] **VDEP-01**: `DATABASE_URL` va cac secrets hien co duoc cau hinh trong Vercel environment variables
- [ ] **VDEP-02**: Vercel deployment tra ve 200 (khong con 500 errors)

## v2 Requirements (Deferred)

### Anti-Fraud Nang Cao

- **ABUS-05**: Adaptive friction theo muc rui ro (step-up challenge linh hoat).
- **ABUS-06**: Co che machine-learning ho tro phat hien bat thuong sau khi co du telemetry.

### Leaderboard Nang Cao

- **LEAD-03**: Co che diem co trong so chat luong (khong chi dem so luong).
- **LEAD-04**: Giai thich minh bach ve cach tinh diem va dieu kien xep hang.

### Platform

- **ARCH-01**: Cloud storage cho file uploads (evidence images) thay cho local disk.
- **ARCH-02**: NeonDB branching cho Vercel preview deployments.

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| File upload cloud storage | Deferred — evidence images khong critical cho deploy fix |
| NeonDB branching for preview deploys | Complexity khong can thiet cho initial deployment |
| Alembic/flask-migrate | Project dung manual migration scripts theo conventions |
| Auto-scaling/multi-region | v1.1 chi can 1 region on dinh |
| Dark mode | Uu tien infrastructure stability |
| SPA/microservices replatform | Rui ro hoi quy cao, khong can thiet |

## Traceability

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| UI-01 | Phase 3 | Complete |
| UI-02 | Phase 3 | Complete |
| UI-03 | Phase 3 | Complete |
| QUIZ-01 | Phase 4 | Complete |
| QUIZ-02 | Phase 4 | Complete |
| QUIZ-03 | Phase 4 | Complete |
| QUIZ-04 | Phase 4 | Complete |
| PRIV-01 | Phase 1 | Complete |
| PRIV-02 | Phase 1 | Complete |
| PRIV-03 | Phase 1 | Complete |
| ABUS-01 | Phase 2 | Complete |
| ABUS-02 | Phase 2 | Complete |
| ABUS-03 | Phase 2 | Complete |
| ABUS-04 | Phase 2 | Complete |
| LEAD-01 | Phase 5 | Complete |
| LEAD-02 | Phase 5 | Complete |
| DOC-01 | Phase 6 | Complete |
| DOC-02 | Phase 6 | Complete |
| ML-01 | Phase 6 | Complete |
| ML-02 | Phase 6 | Complete |
| DBCFG-01 | Phase 7 | Complete |
| DBCFG-02 | Phase 7 | Complete |
| DBCFG-03 | Phase 7 | Complete |
| DBCFG-04 | Phase 7 | Complete |
| START-01 | Phase 8 | Pending |
| START-02 | Phase 7 | Complete |
| START-03 | Phase 8 | Pending |
| SEED-01 | Phase 8 | Pending |
| VDEP-01 | Phase 9 | Pending |
| VDEP-02 | Phase 9 | Pending |

**Coverage:**

- v1.0 requirements: 20 total — all complete
- v1.1 requirements: 10 total — all mapped ✓
- Mapped to phases: 10/10
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-04-03 after v1.1 roadmap creation*
