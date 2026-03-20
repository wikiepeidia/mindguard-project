# Requirements: MindGuard v2

**Defined:** 2026-03-19
**Core Value:** Nguoi dung co the hoc, kiem tra nhan thuc va gui bao cao lua dao mot cach de dung, an toan, va dang tin cay.

## v1 Requirements

### UI/UX

- [x] **UI-01**: Nguoi dung thay light mode dong bo tren cac trang chinh (auth, quiz, report, profile, leaderboard).
- [x] **UI-02**: He thong su dung design tokens thong nhat (mau, font, spacing) cho cac trang uu tien.
- [x] **UI-03**: Trang quiz va report dam bao trai nghiem mobile-first o kich thuoc man hinh pho bien.

### Quiz

- [ ] **QUIZ-01**: Nguoi dung lam bai quiz theo luong 1 cau hoi moi trang.
- [ ] **QUIZ-02**: Nguoi dung thay thanh tien do va trang thai ro rang trong suot bai quiz.
- [ ] **QUIZ-03**: Trang thai bai lam duoc giu on dinh khi refresh/back trong phien hop le.
- [ ] **QUIZ-04**: He thong bo sung bo cau hoi theo chu de bao mat/lua dao de phu hop luong quiz moi.

### Privacy

- [ ] **PRIV-01**: So dien thoai duoc che, chi hien 3 so cuoi o tat ca diem hien thi.
- [ ] **PRIV-02**: Quy tac masking du lieu nhay cam duoc ap dung nhat quan trong toan he thong.
- [ ] **PRIV-03**: Admin co nhat ky truy cap du lieu nhay cam de phuc vu kiem toan.

### Anti-Spam

- [x] **ABUS-01**: He thong ap dung rule tan suat gui to cao theo cua so thoi gian de chan spam.
- [x] **ABUS-02**: He thong danh gia rui ro dua tren da tin hieu (IP + cookie + account).
- [x] **ABUS-03**: Trien khai monitor mode truoc, sau do soft-enforce theo nguong duoc cau hinh.
- [x] **ABUS-04**: Nguoi dung nhan thong bao cooldown/chuyen trang thai voi ly do ro rang.

### Leaderboard

- [ ] **LEAD-01**: Hien thi bang vinh danh nguoi to cao nhieu nhat.
- [ ] **LEAD-02**: Ap dung integrity rule de giam gian lan tren leaderboard.

## v2 Requirements

### Anti-Fraud Nang Cao

- **ABUS-05**: Adaptive friction theo muc rui ro (step-up challenge linh hoat).
- **ABUS-06**: Co che machine-learning ho tro phat hien bat thuong sau khi co du telemetry.

### Leaderboard Nang Cao

- **LEAD-03**: Co che diem co trong so chat luong (khong chi dem so luong).
- **LEAD-04**: Giai thich minh bach ve cach tinh diem va dieu kien xep hang.

### Mo Rong Nen Tang

- **ARCH-01**: Dinh nghia tieu chi kich hoat migration SQLite -> PostgreSQL theo nguong tai va SLO.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Dark mode trong v1 | Uu tien chinh hien tai la light mode de de nhin va dong bo UX |
| Replatform sang SPA/microservices | Rui ro hoi quy cao, khong can thiet cho muc tieu v1 |
| Hard-block chi dua tren IP | De false-positive cao va khong dap ung yeu cau da tin hieu |
| Big-bang redesign toan bo IA/navigation | Vuot scope, de lam cham tien do va tang rui ro |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| UI-01 | Phase 3 | Complete |
| UI-02 | Phase 3 | Complete |
| UI-03 | Phase 3 | Complete |
| QUIZ-01 | Phase 4 | Pending |
| QUIZ-02 | Phase 4 | Pending |
| QUIZ-03 | Phase 4 | Pending |
| QUIZ-04 | Phase 4 | Pending |
| PRIV-01 | Phase 1 | Pending |
| PRIV-02 | Phase 1 | Pending |
| PRIV-03 | Phase 1 | Pending |
| ABUS-01 | Phase 2 | Completed |
| ABUS-02 | Phase 2 | Completed |
| ABUS-03 | Phase 2 | Completed |
| ABUS-04 | Phase 2 | Completed |
| LEAD-01 | Phase 5 | Pending |
| LEAD-02 | Phase 5 | Pending |

**Coverage:**

- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-03-20 after Phase 3 completion (03-03) updates*
