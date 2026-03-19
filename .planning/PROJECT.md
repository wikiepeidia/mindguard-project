# MindGuard v2

## What This Is

MindGuard v2 la nen tang giao duc an toan mang va phong chong lua dao duoc xay dung bang Flask. He thong cung cap bai quiz nhan thuc, chatbot huong dan, bao cao doi tuong lua dao, va dashboard quan tri de theo doi du lieu. Muc tieu gan nhat la nang cap trai nghiem UI/UX, uu tien giao dien light mode de de su dung va cai thien co che chong spam/gian lan.

## Core Value

Nguoi dung co the hoc, kiem tra nhan thuc va gui bao cao lua dao mot cach de dung, an toan, va dang tin cay.

## Requirements

### Validated

- ✓ Dang ky/dang nhap nguoi dung qua email va session — existing
- ✓ Lam quiz va xem ket qua/chung nhan — existing
- ✓ Gui bao cao lua dao kem bang chung — existing
- ✓ Chatbot ho tro hoi dap co fallback — existing
- ✓ Quan tri vien co dashboard rieng de quan ly — existing

### Active

- [ ] Chuyen giao dien sang light mode de de nhin, dong bo UX toan he thong
- [ ] Thiet ke lai quiz theo kieu 1 cau hoi moi trang
- [ ] Them bang vinh danh nguoi to cao nhieu nhat
- [ ] Bao ve thong tin ca nhan: so dien thoai chi hien 3 so cuoi
- [ ] Them luat phat hien spam khi gui bao cao nhieu lan trong thoi gian ngan
- [ ] Theo doi IP va cookie de phat hien spam/gian lan
- [ ] Bo sung bo cau hoi neu can de phu hop giao dien quiz moi

### Out of Scope

- Dark mode trong v1 — nguoi dung uu tien light mode cho de dung
- Tinh nang khong lien quan truc tiep den giao duc/chong lua dao (vi du: mang xa hoi tong quat) — khong phuc vu core value
- Tai cau truc lon toan bo backend — v1 tap trung nang cap UX va anti-spam

## Context

Du an dang o trang thai brownfield, da co codebase map trong `.planning/codebase/` va da co cac module chinh (auth, quiz, scammer report, chatbot, admin). Nguoi dung uu tien trai nghiem giao dien theo huong cybersecurity hien dai (tham chieu cam hung chongluadao.com), dong nhat ngon ngu thiet ke va bo cuc. Huong nang cap chinh cua v1 la can bang giua UX va do tin cay he thong thong qua bao ve du lieu ca nhan va co che chong spam/gian lan.

## Constraints

- **Tech stack**: Tiep tuc dung Flask + SQLite + Jinja + static assets hien co — tranh vo kien truc hien tai
- **Product scope**: Uu tien UI/UX quiz va light mode truoc — theo yeu cau uu tien cao nhat cua nguoi dung
- **Security/Privacy**: Thong tin nhay cam phai duoc an/bam va co guard rails chong lam dung — tranh lo du lieu va spam he thong
- **Compatibility**: Phai hoat dong tren giao dien desktop va mobile — khong lam giam trai nghiem hien tai

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Uu tien light mode va UX quiz lam trung tam v1 | Nhu cau uu tien cao nhat tu nguoi dung la UI/UX | — Pending |
| Giu kien truc Flask brownfield, nang cap theo tung pha | Giam rui ro hoi quy va tan dung he thong dang chay | — Pending |
| Dua anti-spam (rule tan suat + IP/cookie tracking) vao v1 | Bao ve chat luong du lieu bao cao va han che gian lan | — Pending |

---
*Last updated: 2026-03-19 after initialization*
