# Phase 4: Quiz One-Question Flow - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase nay tap trung trien khai luong quiz 1 cau hoi moi trang va dong bo UX lien quan de dat QUIZ-01, QUIZ-02, QUIZ-03, QUIZ-04. Khong mo rong sang co che xep hang hay anti-spam ngoai pham vi quiz flow.

</domain>

<decisions>
## Implementation Decisions

### Locked decision from user
- Bat buoc: luong quiz theo kieu 1 cau hoi moi trang.

### Fast defaults (recommended)
- Thanh tien do luon hien thi ro rang o moi buoc.
- Giu trang thai bai lam hop ly khi refresh/back trong phien hop le.
- Mobile-first behavior khong duoc giam so voi flow hien tai.
- Bo cau hoi duoc bo sung theo chu de de phu hop flow moi.

### Claude's Discretion
- Kieu transition giua cac cau hoi (instant/fade/stepper).
- Hinh thuc luu state (session + guard rails) de tranh mat bai lam.
- Muc do gom/phan trang cho navigation controls (next/back/submit) theo do ro rang UX.

</decisions>

<specifics>
## Specific Ideas

- Giam roi cho nguoi dung bang focus tung cau hoi.
- Giu cam giac tien do lien tuc va phan hoi ket qua ro rang.
- Uu tien trai nghiem tren mobile de phu hop user context thuc te.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` (QUIZ-01..04)
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

### Existing quiz implementation
- `routes/quiz.py`
- `templates/quiz.html`
- `templates/quiz_result.html`
- `static/css/quiz.css`
- `static/js/quiz.js`
- `utils/ai_agent.py`
- `utils/quiz_data.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Quiz route flow da ton tai trong `routes/quiz.py` va co output result/certificate.
- CSS/JS quiz da tach rieng, phu hop rollout theo phase.

### Established Patterns
- Session-backed state duoc dung rong rai trong app.
- Template-driven rendering voi Bootstrap utility classes.

### Integration Points
- Main integration nam o route quiz + template quiz + client-side handlers cho navigation/submit.
- Ket noi du lieu cau hoi tu `utils/quiz_data.py`/AI question path can duoc giu on dinh khi doi flow.

</code_context>

<deferred>
## Deferred Ideas

- Leaderboard integrity mechanics thuoc Phase 5.
- Advanced adaptive quiz personalization ngoai scope v1.

</deferred>

---
*Phase: 04-quiz-one-question-flow*
*Context gathered: 2026-03-20*
