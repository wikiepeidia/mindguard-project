# Phase 3: Light Mode UX System - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase nay dat muc tieu dong bo light mode, token hoa style, va mobile-first cho cac trang uu tien theo requirements UI-01, UI-02, UI-03. Khong mo rong sang them capability moi ngoai pham vi giao dien va nhat quan UX.

</domain>

<decisions>
## Implementation Decisions

### Visual direction light mode (locked)
- Palette: nen trang/xam sang, giu accent cyan de bao toan nhan dien san pham.
- Contrast: uu tien readability dat muc WCAG AA.
- Surface style: card/section nen trang, border mong, shadow nhe (khong glass-heavy).
- Alert semantics: warning dung amber/vang, danger dung do.

### Fast defaults for remaining areas
- Design token scope (default): uu tien token hoa `base.css`/`style.css` truoc, sau do apply vao `quiz`, `report_scammer`, `leaderboard`, `scammer_profile`.
- Rollout order (default): base layout/nav -> report flow -> quiz flow -> leaderboard/profile.
- Mobile-first baseline (default): optimized cho viewport pho bien 360-430px va breakpoint Bootstrap hien co.

### Claude's Discretion
- Naming cu the cho token map (color, spacing, radius, typography).
- Motion/transitions nhe de tang cam giac hien dai nhung khong gay roi.
- Cach gop style duplicate giua `style.css`, `base.css`, va css page-level theo lo trinh an toan.

</decisions>

<specifics>
## Specific Ideas

- Giu linh hon cybersecurity hien dai, de nhin ban ngay, dong bo tren desktop/mobile.
- Uu tien tinh de doc va huong dan hanh dong ro rang trong cac trang co canh bao/an toan.
- Giam style drift giua cac trang quan trong bang token chung.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/PROJECT.md` - Product vision and constraints.
- `.planning/REQUIREMENTS.md` - UI-01, UI-02, UI-03.
- `.planning/ROADMAP.md` - Phase 3 goal and success criteria.
- `.planning/STATE.md` - Current milestone position.

### Existing UI stack touchpoints
- `templates/base.html` - Shared layout shell and global includes.
- `static/css/style.css` - Global style layer with current dark-leaning tokens.
- `static/css/base.css` - Shared base variables/utilities.
- `static/css/quiz.css` - Quiz surface and interaction styles.
- `static/css/report_scammer.css` - Report flow styling.
- `static/css/leaderboard.css` - Leaderboard visual behaviors.
- `static/css/scammer_profile.css` - Profile detail visuals.
- `templates/quiz.html`, `templates/report_scammer.html`, `templates/leaderboard.html`, `templates/scammer_profile.html` - Priority pages for rollout.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Bootstrap 5 utility classes da duoc dung rong rai, co the tiep tuc lam backbone layout.
- `base.html` centralize static include, phu hop cho token rollout theo mot diem vao.

### Established Patterns
- CSS hien tai chia theo page-level file + global file, co nhieu gia tri mau hardcode va dark-oriented class utility.
- Theme consistency hien tai chua dong nhat giua pages (quiz/report co style light nhung base/style con dark-heavy).

### Integration Points
- Global token injection: `static/css/style.css`, `static/css/base.css`.
- High-impact pages: `templates/report_scammer.html`, `templates/quiz.html`, `templates/leaderboard.html`, `templates/scammer_profile.html`.
- Mobile behavior verification via page-specific JS/CSS coupling o `static/js/*` + corresponding templates.

</code_context>

<deferred>
## Deferred Ideas

- Quiz one-question-per-page chi tiet thuoc Phase 4.
- Leaderboard integrity behavior thuoc Phase 5.
- Advanced animation system ngoai nhu cau UX can ban cua v1.

</deferred>

---
*Phase: 03-light-mode-ux-system*
*Context gathered: 2026-03-20*
