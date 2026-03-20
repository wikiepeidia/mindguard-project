# Phase 4: Quiz One-Question Flow - Research

**Researched:** 2026-03-20
**Domain:** Flask server-rendered quiz wizard, session persistence, and compatibility-safe scoring/certificate flow
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Bat buoc: luong quiz theo kieu 1 cau hoi moi trang.

### Claude's Discretion
- Kieu transition giua cac cau hoi (instant/fade/stepper).
- Hinh thuc luu state (session + guard rails) de tranh mat bai lam.
- Muc do gom/phan trang cho navigation controls (next/back/submit) theo do ro rang UX.

### Deferred Ideas (OUT OF SCOPE)
- Leaderboard integrity mechanics thuoc Phase 5.
- Advanced adaptive quiz personalization ngoai scope v1.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| QUIZ-01 | Nguoi dung lam bai quiz theo luong 1 cau hoi moi trang. | Use server-side quiz attempt state with question index pointer and per-step POST->Redirect->GET workflow so each view renders exactly one question. |
| QUIZ-02 | Nguoi dung thay thanh tien do va trang thai ro rang trong suot bai quiz. | Add deterministic progress model from attempt state (current index, answered count, total) and render progress bar/text on each step. |
| QUIZ-03 | Trang thai bai lam duoc giu on dinh khi refresh/back trong phien hop le. | Persist answer map and current index in Flask session; use PRG pattern and guarded navigation to make refresh/back idempotent. |
| QUIZ-04 | He thong bo sung bo cau hoi theo chu de bao mat/lua dao de phu hop luong quiz moi. | Extend quiz question bank with topic metadata and keep AI/static question ingestion normalized before attempt starts. |
</phase_requirements>

## Summary

Current implementation in routes/quiz.py grades all questions in one POST and renders all questions at once in templates/quiz.html. The existing static/js/quiz.js appears to target a hidden/show block-based stepper contract (question-block, nav-btn-*, quizForm, btn-next/btn-prev), but that contract is not present in the current template. This mismatch is a key risk and supports moving the source of truth to server session state rather than fragile client-only state.

Best-fit implementation for this stack is a server-driven one-question flow with explicit attempt state in Flask session. Keep existing result and certificate routes unchanged as compatibility anchors, and only refactor the quiz entry/step/submit path. The flow should preserve existing pass threshold and QuizResult persistence semantics to avoid regressions in profile/admin consumption.

Question set preparation should happen once per attempt: resolve static + optional AI question, normalize IDs/options/answers/topic, store compact attempt state in session, then render a single active question per request. This gives deterministic progress, reliable refresh/back behavior, and safe handoff to existing quiz_result/certificate pages.

**Primary recommendation:** Implement a server-side session-backed quiz attempt wizard with PRG navigation and unchanged scoring/certificate persistence contracts.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 3.0.3 (pinned in requirements.txt) | Request routing, session management, flash messages, redirects | Native fit for existing blueprint app; official session + redirect patterns are documented and stable. |
| Flask-SQLAlchemy | 3.1.1 (pinned) | Persist final QuizResult records | Already integrated in models/routes and used by quiz_result/profile/admin reads. |
| Jinja2 templates | bundled with Flask 3.0.3 | Server-rendered one-question pages with progress state | Existing app is template-first; avoids SPA migration risk. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Bootstrap | 5.3.0 (CDN in base.html) | Layout and mobile-first controls for step UX | For consistent navigation, progress container, and responsive buttons. |
| Browser sessionStorage (existing JS usage) | native browser API | Optional non-authoritative UX hints (timer, transient UI) | Only for convenience; do not rely on it as grading source of truth. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Flask session-backed attempt | DB-persisted in-progress attempt table | Better cross-device resume, but unnecessary schema/migration complexity for current requirements. |
| Server-rendered PRG wizard | Client-only JS state wizard | Faster perceived transitions, but weaker refresh/back reliability and easier state desync. |

**Installation:**
```bash
pip install -r requirements.txt
```

**Version verification notes:**
- Python stack versions are pinned in requirements.txt.
- UI framework version is pinned by CDN URL in base.html.

## Architecture Patterns

### Recommended Project Structure
```text
routes/
├── quiz.py                  # quiz attempt lifecycle + result/certificate compatibility
utils/
├── quiz_data.py             # canonical question bank with topic metadata
templates/
├── quiz.html                # single-question view + progress
├── quiz_result.html         # unchanged compatibility target
└── certificate.html         # unchanged compatibility target
static/
├── js/quiz.js               # optional enhancement only
└── css/quiz.css             # one-question view styling
```

### Pattern 1: Session Attempt Envelope
**What:** Store a compact server-side attempt envelope in Flask session.
**When to use:** Immediately after starting/restarting quiz attempt.
**Example:**
```python
# Source: project pattern in routes/quiz.py + Flask session docs
session["quiz_attempt"] = {
    "questions": prepared_questions,   # id, options, answer, topic, is_ai
    "answers": {},                    # question_id -> selected_option_index
    "current_index": 0,
    "started_at": now_iso,
    "version": 1,
}
```

### Pattern 2: POST Redirect GET Per Step
**What:** After handling answer submit, redirect to next step URL.
**When to use:** Every answer submit and navigation action.
**Example:**
```python
# Source: Flask redirect/url_for pattern docs
@app.post("/quiz/step")
def quiz_step_post():
    # validate + save answer in session
    return redirect(url_for("quiz.quiz_step", index=next_index))
```

### Pattern 3: Compatibility-Preserving Finalization
**What:** Final step computes score once, writes QuizResult once, then redirects to existing result/certificate routes.
**When to use:** Submit on final question.
**Example:**
```python
# Source: current routes/quiz.py persistence flow
result = QuizResult(name=name, email=email, score=score, max_score=max_score)
db.session.add(result)
db.session.commit()

if score >= int(max_score * Config.QUIZ_PASS_PERCENTAGE):
    session["certificate_code"] = generate_certificate_code()
    return redirect(url_for("quiz.certificate"))
return redirect(url_for("quiz.quiz_result"))
```

### Anti-Patterns to Avoid
- **Client-only truth for answers:** Easy desync on refresh/back and vulnerable to DOM contract drift.
- **Rebuilding random questions every GET:** Breaks answer index mapping and persistence consistency.
- **Changing result/certificate route contracts in this phase:** High regression risk for profile/admin screens.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Session integrity | Custom token/cookie parser | Flask built-in signed session | Already secure-by-default for this architecture and documented by Flask. |
| Multi-step state transitions | Ad-hoc JS-only finite-state machine | Server PRG with session current_index | Better back/refresh consistency and easier testing. |
| Flash feedback transport | Custom query-parameter messaging | Flask flash categories | Existing base.html already renders categorized flashes. |

**Key insight:** For this phase, complexity belongs in deterministic server state transitions, not in bespoke front-end state engines.

## Common Pitfalls

### Pitfall 1: Question Identity Drift
**What goes wrong:** Questions reshuffle between steps/reloads, causing answer-to-question mismatch.
**Why it happens:** Random sampling on each request instead of once per attempt.
**How to avoid:** Freeze sampled question list at attempt start in session.
**Warning signs:** User answer map contains IDs that are not in currently rendered step.

### Pitfall 2: Stale JS Contract
**What goes wrong:** JS expects elements (quizForm/question-block/nav-btn-*) absent in template.
**Why it happens:** Legacy script retained while template evolved.
**How to avoid:** Either realign template contract or reduce JS to progressive enhancement only.
**Warning signs:** console errors on DOMContentLoaded and non-functional next/prev controls.

### Pitfall 3: Result/Certificate Regression
**What goes wrong:** Score or certificate flow breaks downstream pages.
**Why it happens:** Altered session keys or pass/fail criteria during refactor.
**How to avoid:** Keep session keys last_quiz_score/max_quiz_score/certificate_code and QuizResult write semantics stable.
**Warning signs:** profile page missing latest score, certificate redirect loops, admin quiz metrics anomalies.

### Pitfall 4: Session Payload Bloat
**What goes wrong:** Session cookie approaches browser size limits.
**Why it happens:** Storing excessive per-question text/explanations in session.
**How to avoid:** Keep only minimum attempt data (IDs/options index/answer index/topic tags); avoid large explanation blobs.
**Warning signs:** Session values intermittently not persisting across requests.

## Code Examples

Verified patterns from official sources and current codebase:

### One-question Step Render
```python
# Source: Flask request/session pattern + current route style
@app.get("/quiz")
@login_required
def quiz_step():
    attempt = session.get("quiz_attempt")
    if not attempt:
        return redirect(url_for("quiz.quiz_start"))

    idx = int(request.args.get("index", attempt["current_index"]))
    question = attempt["questions"][idx]
    return render_template(
        "quiz.html",
        question=question,
        current_index=idx,
        total_questions=len(attempt["questions"]),
        answered_count=len(attempt["answers"]),
    )
```

### Safe Answer Save + Redirect
```python
# Source: Flask form + redirect patterns
@app.post("/quiz/step")
@login_required
def quiz_step_submit():
    attempt = session.get("quiz_attempt")
    selected = request.form.get("selected_option")
    qid = request.form.get("question_id")

    attempt["answers"][qid] = int(selected)
    attempt["current_index"] = min(attempt["current_index"] + 1, len(attempt["questions"]) - 1)
    session["quiz_attempt"] = attempt

    return redirect(url_for("quiz.quiz_step", index=attempt["current_index"]))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Render all questions and submit once | Wizard-style one-question flow with explicit progress and persistent attempt state | Modern UX baseline for educational assessments | Lower cognitive load, stronger completion rates, easier mobile interaction |
| Client-side navigation as primary state | Server-trusted state with optional client enhancement | Adopted broadly as reliability pattern in form workflows | Better refresh/back consistency and simpler testability |

**Deprecated/outdated:**
- Treating randomized question order as per-request behavior: replaced by per-attempt frozen ordering.

## Open Questions

1. **Should AI-generated question always be included in every attempt or remain conditional?**
   - What we know: Current route conditionally prepends ai_question and varies sample_size.
   - What's unclear: Product intent for fairness/consistency across users.
   - Recommendation: Lock policy in plan phase and keep max_score derived from actual attempt question count.

2. **Should timer enforcement remain client-side only?**
   - What we know: Existing static/js/quiz.js has sessionStorage-based timer hooks.
   - What's unclear: Whether strict server-side timeout is required.
   - Recommendation: Keep timer advisory in this phase; defer strict server timeout unless explicitly required.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | unittest (stdlib, Python 3.12) |
| Config file | none - discovery via unittest defaults |
| Quick run command | python -m unittest tests.ui.test_quiz_mobile_light -v |
| Full suite command | python -m unittest discover -s tests -p "test_*.py" |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QUIZ-01 | One-question-per-page flow and step navigation | integration (Flask test client) | python -m unittest tests.quiz.test_quiz_one_question_flow -v | ❌ Wave 0 |
| QUIZ-02 | Progress label/bar reflects current and completed state | integration + template contract | python -m unittest tests.quiz.test_quiz_progress_visibility -v | ❌ Wave 0 |
| QUIZ-03 | Refresh/back keeps in-session answer/index stable | integration (session_transaction + redirects) | python -m unittest tests.quiz.test_quiz_state_persistence -v | ❌ Wave 0 |
| QUIZ-04 | Expanded topic-tagged question bank loads into attempt | unit + integration | python -m unittest tests.quiz.test_quiz_topic_bank -v | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** python -m unittest tests.quiz.test_quiz_one_question_flow tests.quiz.test_quiz_progress_visibility -v
- **Per wave merge:** python -m unittest discover -s tests -p "test_*.py"
- **Phase gate:** Full suite green before /gsd-verify-work

### Wave 0 Gaps
- [ ] tests/quiz/__init__.py - quiz phase test package scaffold
- [ ] tests/quiz/test_quiz_one_question_flow.py - covers QUIZ-01
- [ ] tests/quiz/test_quiz_progress_visibility.py - covers QUIZ-02
- [ ] tests/quiz/test_quiz_state_persistence.py - covers QUIZ-03
- [ ] tests/quiz/test_quiz_topic_bank.py - covers QUIZ-04
- [ ] App factory-like test helper or fixture utility for authenticated quiz client setup

## Sources

### Primary (HIGH confidence)
- Workspace code: routes/quiz.py, templates/quiz.html, static/js/quiz.js, templates/quiz_result.html, templates/certificate.html, utils/quiz_data.py, models/models.py
- Flask official docs (3.0.x): https://flask.palletsprojects.com/en/3.0.x/quickstart/#sessions
- Flask official docs (3.0.x): https://flask.palletsprojects.com/en/3.0.x/patterns/flashing/
- Flask official docs (3.0.x): https://flask.palletsprojects.com/en/3.0.x/testing/

### Secondary (MEDIUM confidence)
- None

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all recommended tools already exist in repository and are version-pinned.
- Architecture: HIGH - derived from concrete route/template mismatch analysis and official Flask session/redirect/testing patterns.
- Pitfalls: HIGH - observed directly from current code contracts and validated by current test-command behavior.

**Research date:** 2026-03-20
**Valid until:** 2026-04-19
