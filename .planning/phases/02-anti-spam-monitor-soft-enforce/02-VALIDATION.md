---
phase: 02
slug: anti-spam-monitor-soft-enforce
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-20
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python unittest (repo pattern) |
| **Config file** | none |
| **Quick run command** | `python -m unittest tests/antispam/test_decision_service.py -v` |
| **Full suite command** | `python -m unittest discover -s tests/antispam -p "test_*.py" -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests/antispam/test_decision_service.py -v`
- **After every plan wave:** Run `python -m unittest discover -s tests/antispam -p "test_*.py" -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | ABUS-01, ABUS-02 | unit | `python -m unittest tests/antispam/test_decision_service.py -v` | ✅ | ⬜ pending |
| 02-01-02 | 01 | 1 | ABUS-03 | integration | `python -m unittest tests/antispam/test_monitor_mode.py -v` | ✅ | ⬜ pending |
| 02-01-03 | 01 | 1 | ABUS-04 | integration | `python -m unittest tests/antispam/test_user_feedback.py -v` | ✅ | ⬜ pending |
| 02-02-01 | 02 | 2 | ABUS-01, ABUS-02 | integration | `python -m unittest tests/antispam/test_signal_scoring.py -v` | ✅ | ⬜ pending |
| 02-02-02 | 02 | 2 | ABUS-03 | integration | `python -m unittest tests/antispam/test_soft_enforce.py -v` | ✅ | ⬜ pending |
| 02-02-03 | 02 | 2 | ABUS-04 | integration/manual hybrid | `python -m unittest tests/antispam/test_user_feedback.py -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/antispam/test_decision_service.py` — monitor decision logic and cooldown windows
- [ ] `tests/antispam/test_signal_scoring.py` — account/cookie/IP scoring precedence
- [ ] `tests/antispam/test_monitor_mode.py` — monitor-only path without hard blocking
- [ ] `tests/antispam/test_soft_enforce.py` — soft-enforce transitions and action output
- [ ] `tests/antispam/test_user_feedback.py` — cooldown/challenge messaging behavior

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cooldown/challenge copy clarity on report form | ABUS-04 | Readability and tone must be judged by humans | Submit rapid reports to trigger cooldown; confirm wording/time remaining is understandable |
| False-positive acceptability in real flows | ABUS-03 | Needs realistic browser behavior and mixed traffic patterns | Run normal vs burst submissions from same browser/IP and inspect monitor logs + user impact |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-20
