---
phase: 01
slug: privacy-data-governance-foundation
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-19
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python script-based checks (existing test scripts) |
| **Config file** | none — Wave 0 may standardize pytest later |
| **Quick run command** | `python -m unittest tests/privacy/test_masking_rules.py -v` |
| **Full suite command** | `python tests/test_stats.py && python tests/test_ai_quiz.py && python tests/test_openrouter_limits.py` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests/privacy/test_masking_rules.py -v`
- **After every plan wave:** Run `python -m unittest discover -s tests/privacy -p "test_*.py" -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | PRIV-01 | unit/integration | `python -m unittest discover -s tests/privacy -p "test_*.py" -v` | ✅ | ⬜ pending |
| 01-01-02 | 01 | 1 | PRIV-02 | unit | `python -m unittest tests/privacy/test_masking_rules.py -v` | ✅ | ⬜ pending |
| 01-01-03 | 01 | 1 | PRIV-01, PRIV-02 | integration | `python -m unittest tests/privacy/test_role_visibility.py tests/privacy/test_api_masking.py -v` | ✅ | ⬜ pending |
| 01-02-01 | 02 | 2 | PRIV-03 | integration | `python -m unittest tests/privacy/test_sensitive_access_audit.py -v` | ✅ | ⬜ pending |
| 01-02-02 | 02 | 2 | PRIV-03 | integration | `python -m unittest tests/privacy/test_admin_export_policy.py -v` | ✅ | ⬜ pending |
| 01-02-03 | 02 | 2 | PRIV-03 | integration | `python -m unittest tests/privacy/test_sensitive_access_audit.py -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/privacy/test_masking_rules.py` — stubs for PRIV-01 and PRIV-02
- [ ] `tests/privacy/test_role_visibility.py` — role-based display checks
- [ ] `tests/privacy/test_sensitive_access_audit.py` — audit log create/query checks for PRIV-03
- [ ] `tests/privacy/README.md` — execution instructions and expected fixtures

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Admin UI filter usability for audit log | PRIV-03 | UX filtering quality is hard to assert via current scripts | Login admin, open audit page, test time/actor/action filters with seeded events |
| Public masking annotation readability | PRIV-01 | Copy clarity and visual consistency need human review | Check public pages on desktop/mobile, verify masked values + explanatory label |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-19
