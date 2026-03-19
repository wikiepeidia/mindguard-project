# MindGuard v2 Roadmap

**Created:** 2026-03-19
**Granularity:** standard
**Coverage:** 16/16 v1 requirements mapped

## Phases

- [ ] **Phase 1: Privacy & Data Governance Foundation** - Chuan hoa masking du lieu nhay cam va audit truy cap de tao nen tang tin cay.
- [ ] **Phase 2: Anti-Spam Monitor & Soft Enforce** - Trien khai chong spam da tin hieu theo lo trinh monitor truoc, soft-enforce sau.
- [ ] **Phase 3: Light Mode UX System** - Dong bo light mode, design tokens va mobile-first cho cac trang uu tien.
- [ ] **Phase 4: Quiz One-Question Flow** - Chuyen quiz sang luong 1 cau hoi/trang voi tien do ro rang va trang thai on dinh.
- [ ] **Phase 5: Leaderboard Integrity** - Ra mat bang vinh danh nguoi to cao nhieu nhat kem luat giam gian lan.

## Phase Details

### Phase 1: Privacy & Data Governance Foundation
**Goal**: Nguoi dung va admin chi nhin thay du lieu nhay cam o dang duoc bao ve, co kha nang kiem toan truy cap ro rang.
**Depends on**: Nothing (first phase)
**Requirements**: PRIV-01, PRIV-02, PRIV-03
**Success Criteria** (what must be TRUE):
1. So dien thoai o tat ca diem hien thi chi con dang che va chi lo 3 so cuoi.
2. Cung mot quy tac masking duoc ap dung nhat quan cho cac truong nhay cam tren cac trang uu tien.
3. Admin co the xem nhat ky truy cap du lieu nhay cam voi thong tin actor, thoi diem va hanh dong.
**Plans**: TBD

### Phase 2: Anti-Spam Monitor & Soft Enforce
**Goal**: He thong giam spam bao cao bang co che danh gia rui ro da tin hieu, uu tien giam false-positive.
**Depends on**: Phase 1
**Requirements**: ABUS-01, ABUS-02, ABUS-03, ABUS-04
**Success Criteria** (what must be TRUE):
1. Nguoi dung gui to cao qua nhanh trong cua so thoi gian se bi danh dau/canh bao theo rule tan suat.
2. Moi quyet dinh rui ro su dung ket hop IP, cookie va account thay vi mot tin hieu don le.
3. Van hanh co monitor mode truoc, sau do chuyen sang soft-enforce theo nguong cau hinh.
4. Khi bi cooldown hoac thay doi trang thai, nguoi dung nhan thong bao ly do ro rang va han cho.
**Plans**: TBD

### Phase 3: Light Mode UX System
**Goal**: Nguoi dung trai nghiem giao dien light mode dong bo, de doc va de dung tren desktop/mobile.
**Depends on**: Phase 1
**Requirements**: UI-01, UI-02, UI-03
**Success Criteria** (what must be TRUE):
1. Cac trang auth, quiz, report, profile, leaderboard deu hien thi light mode thong nhat.
2. Mau, font va spacing tren cac trang uu tien dung chung bo design tokens da dinh nghia.
3. Nguoi dung tren man hinh di dong pho bien co the thao tac quiz/report de dang theo huong mobile-first.
**Plans**: TBD

### Phase 4: Quiz One-Question Flow
**Goal**: Nguoi dung hoan thanh quiz theo tung buoc ro rang, giam roi va giam mat trang thai bai lam.
**Depends on**: Phase 3
**Requirements**: QUIZ-01, QUIZ-02, QUIZ-03, QUIZ-04
**Success Criteria** (what must be TRUE):
1. Nguoi dung lam quiz theo dung luong 1 cau hoi moi trang tu dau den cuoi.
2. Tien do va trang thai bai lam duoc hien thi ro rang o moi buoc quiz.
3. Neu refresh/back trong phien hop le, bai lam van giu duoc trang thai hop ly.
4. Bo cau hoi bo sung theo chu de bao mat/lua dao da san sang de phu hop luong quiz moi.
**Plans**: TBD

### Phase 5: Leaderboard Integrity
**Goal**: Nguoi dung thay bang vinh danh co y nghia va han che duoc hanh vi gian lan de leo hang.
**Depends on**: Phase 2, Phase 3
**Requirements**: LEAD-01, LEAD-02
**Success Criteria** (what must be TRUE):
1. Nguoi dung co the xem bang vinh danh nguoi to cao nhieu nhat tren giao dien.
2. Bang xep hang khong chi dua vao dem tho, ma co luat integrity de giam thao tung/gian lan.
3. Ket qua xep hang duoc cap nhat o muc chap nhan duoc va phan anh dung luat da cong bo.
**Plans**: TBD

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Privacy & Data Governance Foundation | 0/2 | Not started | - |
| 2. Anti-Spam Monitor & Soft Enforce | 0/3 | Not started | - |
| 3. Light Mode UX System | 0/2 | Not started | - |
| 4. Quiz One-Question Flow | 0/3 | Not started | - |
| 5. Leaderboard Integrity | 0/2 | Not started | - |
