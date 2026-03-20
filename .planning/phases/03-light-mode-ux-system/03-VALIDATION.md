---
phase: 03
slug: light-mode-ux-system
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-20
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python unittest + static asset assertions |
| **Config file** | none |
| **Quick run command** | `python -m unittest tests/ui/test_light_tokens.py -v` |
| **Full suite command** | `python -m unittest discover -s tests/ui -p "test_*.py" -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests/ui/test_light_tokens.py -v`
- **After every plan wave:** Run `python -m unittest discover -s tests/ui -p "test_*.py" -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | UI-02 | unit/static | `python -m unittest tests/ui/test_light_tokens.py -v` | ✅ | ⬜ pending |
| 03-01-02 | 01 | 1 | UI-01 | integration | `python -m unittest tests/ui/test_base_light_mode.py -v` | ✅ | ⬜ pending |
| 03-02-01 | 02 | 2 | UI-01, UI-03 | integration | `python -m unittest tests/ui/test_report_mobile_light.py -v` | ✅ | ⬜ pending |
| 03-02-02 | 02 | 2 | UI-01, UI-03 | integration | `python -m unittest tests/ui/test_quiz_mobile_light.py -v` | ✅ | ⬜ pending |
| 03-03-01 | 03 | 3 | UI-01 | integration | `python -m unittest tests/ui/test_leaderboard_profile_light.py -v` | ✅ | ⬜ pending |
| 03-03-02 | 03 | 3 | UI-02 | integration | `python -m unittest tests/ui/test_token_coverage.py -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/ui/test_light_tokens.py` — token presence and key var checks
- [ ] `tests/ui/test_base_light_mode.py` — base shell light-mode assertions
- [ ] `tests/ui/test_report_mobile_light.py` — report flow on mobile viewport assumptions
- [ ] `tests/ui/test_quiz_mobile_light.py` — quiz view mobile/light behavior checks
- [ ] `tests/ui/test_leaderboard_profile_light.py` — leaderboard/profile consistency
- [ ] `tests/ui/test_token_coverage.py` — key templates use tokenized classes/variables

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Visual comfort and hierarchy on bright screens | UI-01 | Subjective readability and contrast perception | Open priority pages under daylight-like brightness, confirm text hierarchy and focus cues |
| Mobile tap ergonomics and flow continuity | UI-03 | Touch usability cannot be fully asserted by static tests | Test report/quiz on phone widths, verify spacing, tap targets, and no horizontal overflow |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-20
