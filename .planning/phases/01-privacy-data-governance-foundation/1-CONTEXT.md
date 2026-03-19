# Phase 1: Privacy & Data Governance Foundation - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase nay tap trung vao PRIV-01, PRIV-02, PRIV-03: chuan hoa masking du lieu nhay cam, ap dung nhat quan theo vai tro hien thi, va tao audit log cho truy cap full-data cua admin. Khong mo rong sang anti-spam engine hay UI redesign tong the trong phase nay.

</domain>

<decisions>
## Implementation Decisions

### Quy tac masking du lieu

- So dien thoai: giu 3 so cuoi, phan con lai che bang `*`.
- Identifier khong phai so dien thoai: giu 2 ky tu dau + 2 ky tu cuoi, phan giua che.
- Cac diem bat buoc masking trong Phase 1: index/leaderboard/public search, scammer profile khi khong du quyen, va API public responses.
- Hien chu thich ro rang: "Du lieu da duoc che de bao mat".

### Pham vi hien thi theo vai tro

- Khach chua dang nhap: chi thay du lieu da che o moi noi.
- User da dang nhap (khong admin): van chi thay du lieu da che.
- Admin: duoc xem full-data, nhung moi lan truy cap full-data phai ghi audit log.
- Export admin: mac dinh masked; neu can full thi bat buoc co reason.

### Thiet ke audit log truy cap

- Truong bat buoc: actor (admin id/email), timestamp, action (view/export/update), object bi truy cap, reason khi full-data, IP + user-agent.
- Retention cho Phase 1: 90 ngay.
- Admin UI: bang co filter theo thoi gian, actor, action.
- Canh bao: bat alert khi tan suat truy cap full-data vuot nguong theo actor/IP.

### Claude's Discretion

- Chi tiet UI component cho bang audit (pagination/filter chips/table density).
- Rule cu the cho format mask voi cac edge-case chuoi ngan.
- Cach to chuc service/helper de tai su dung masking logic giua route va template.

</decisions>

<specifics>
## Specific Ideas

- User uu tien ro rang privacy theo huong "masked by default" cho public va user thong thuong.
- Admin van can full-data cho nghiep vu, nhung phai co truy vet (auditability) va ly do khi export full.
- Pha 1 can tao nen tang governance truoc khi mo rong phase anti-spam.

</specifics>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product scope and requirements

- `.planning/PROJECT.md` - Product context, constraints, and current priorities.
- `.planning/REQUIREMENTS.md` - PRIV-01, PRIV-02, PRIV-03 definitions and traceability.
- `.planning/ROADMAP.md` - Phase boundary and success criteria for Phase 1.
- `.planning/STATE.md` - Current phase state and next command continuity.

### Existing implementation touchpoints

- `utils/helpers.py` - Existing `mask_sensitive_data` helper and auth decorators.
- `routes/main.py` - Public/profile rendering paths currently using masked identifier.
- `routes/admin.py` - Admin dashboard/report listing and data display points.
- `routes/api.py` - Public API responses with identifier exposure risk.
- `models/models.py` - User phone fields and scammer report related schema.
- `templates/index.html` - Public listing and current masking behavior in template.
- `templates/admin_dashboard.html` - Admin display/edit paths involving sensitive fields.
- `templates/admin_scammer_reports.html` - Admin report list where identifier visibility must follow role policy.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `utils/helpers.py::mask_sensitive_data` da co san, co the nang cap thanh single source of truth cho masking policy.
- `utils/encryption.py` da co hash/encrypt cho reporter/scammer identifiers, co the phoi hop voi masking de tach biet display vs storage.
- Session role checks (`session.get('is_admin')`, `session.get('registration_email')`) da ton tai, phu hop role-based display gating.

### Established Patterns

- Flask blueprint monolith: routes tu xu ly validation/rendering, utility layer ho tro business logic.
- Sensitive data hien dang xuat hien truc tiep o mot so admin/public views; can chuan hoa mot policy chung.
- Manual DB migration scripts trong `database/` la pattern bat buoc khi them schema audit log.

### Integration Points

- Public display enforcement: `routes/main.py`, `routes/api.py`, `templates/index.html`.
- Admin full-data access + audit capture: `routes/admin.py`, `templates/admin_dashboard.html`, `templates/admin_scammer_reports.html`.
- Schema/supporting models: `models/models.py` + migration script moi trong `database/` de luu audit events.

</code_context>

<deferred>
## Deferred Ideas

- Anti-spam multi-signal engine, monitor -> soft-enforce logic (Phase 2).
- Light mode token system va UX redesign (Phase 3).
- Quiz 1-question-per-page flow (Phase 4).
- Leaderboard integrity hardening (Phase 5).

</deferred>

---
*Phase: 01-privacy-data-governance-foundation*
*Context gathered: 2026-03-19*
