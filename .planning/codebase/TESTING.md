# Testing Patterns

**Analysis Date:** 2026-03-19

## Test Framework

**Runner:**
- `unittest` (stdlib) is used for formal test cases in `tests/test_stats.py`.
- Config: Not detected (`pytest.ini`, `tox.ini`, `pyproject.toml` test config not detected at root).

**Assertion Library:**
- `unittest.TestCase` assertions (`self.assertEqual(...)`) in `tests/test_stats.py`.
- Script-style checks rely on print-and-inspect outputs in `tests/test_ai_quiz.py`, `tests/test_openrouter_limits.py`, and `tests/ai_chat_eval.py`.

**Run Commands:**
```bash
python -m unittest tests/test_stats.py     # Run the formal unittest suite
python tests/test_ai_quiz.py               # Execute AI quiz generation smoke script
python tests/test_openrouter_limits.py     # Probe OpenRouter model availability
python tests/ai_chat_eval.py               # Run conversational evaluation over fixtures
```

## Test File Organization

**Location:**
- Primary testing scripts are in `tests/`.
- Additional DB validation scripts are in `database/test/`.
- Fixture data lives in `tests/fixtures/`.
- Generated evaluation outputs are written to `tests/output/`.

**Naming:**
- Mixed pattern:
  - `test_*.py` for test-like files (`tests/test_stats.py`, `tests/test_ai_quiz.py`, `tests/test_openrouter_limits.py`).
  - Verb-based operational scripts (`tests/create_admin.py`, `tests/scan_unique.py`, `tests/debug_config.py`).
  - DB scripts in `database/test/` are migration/check utilities rather than unit tests.

**Structure:**
```
tests/
  test_stats.py                # unittest-based database counter checks
  test_ai_quiz.py              # manual script for AI quiz generation flow
  test_openrouter_limits.py    # manual API model probe script
  ai_chat_eval.py              # dataset-driven model evaluation script
  fixtures/
    chat_eval.jsonl
    test_one.jsonl
  output/                      # JSON result artifacts
database/test/
  createdatabase.py
  check_data.py
  seed_data.py
  ... (DB setup/migration helper scripts)
```

## Test Structure

**Suite Organization:**
```python
class TestDatabaseStats(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_stats_counters(self):
        with app.app_context():
            ...
            self.assertEqual(scam_count, 2)
```

**Patterns:**
- Setup pattern: In-memory SQLite configured in `setUp`, schema created per test class (`tests/test_stats.py`).
- Teardown pattern: Session removal and schema drop in `tearDown` (`tests/test_stats.py`).
- Assertion pattern: `self.assertEqual(...)` for DB aggregate counters.
- Script validation pattern: print diagnostics and manual success/failure interpretation (`tests/test_ai_quiz.py`, `tests/test_openrouter_limits.py`).

## Mocking

**Framework:** Not detected

**Patterns:**
```python
# Current test-like scripts call live services directly (no mocks)
new_qs = generate_batch_quiz_questions(count=2)
test_model(model, api_key)
reply, used_model = openrouter_chat_chain(args.models, prompt, args.system)
```

**What to Mock:**
- OpenRouter network requests in `utils.chatbot` and AI generation flows from `utils.ai_agent`.
- Cloudflare Turnstile verification calls in `routes/auth.py` and `routes/scammer.py`.
- Time-dependent behaviors where deterministic assertions are needed.

**What NOT to Mock:**
- SQLAlchemy model behavior for local unit tests that validate schema-level constraints.
- Pure helper functions in `utils/helpers.py` (`calculate_risk_score`, masking utilities), which can be tested directly.

## Fixtures and Factories

**Test Data:**
```python
dummy_reports = [
    ScammerReport(..., status='approved'),
    ScammerReport(..., status='approved'),
    ScammerReport(..., status='approved'),
]
db.session.add_all(dummy_reports)
db.session.commit()
```

**Location:**
- JSONL fixtures in `tests/fixtures/chat_eval.jsonl` and `tests/fixtures/test_one.jsonl`.
- Most DB objects are created inline inside each test or script; shared factories are not detected.

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
Not configured (no coverage runner/config detected)
```

## Test Types

**Unit Tests:**
- Limited to DB counter behavior in `tests/test_stats.py`.
- Isolated with in-memory SQLite and no external network dependency.

**Integration Tests:**
- Script-based integration probes exist for external AI APIs:
  - `tests/test_openrouter_limits.py`
  - `tests/ai_chat_eval.py`
  - `tests/test_ai_quiz.py`
- These are not assertion-driven CI tests; they are operational diagnostics.

**E2E Tests:**
- Not detected (no browser automation framework/config observed).

## Common Patterns

**Async Testing:**
```python
# No async test framework detected; external pacing is done with sleep
time.sleep(1)
time.sleep(args.delay)
```

**Error Testing:**
```python
try:
    reply, used_model = openrouter_chat_chain(args.models, prompt, args.system)
except Exception as exc:
    reply = f"ERROR: {exc}"
    used_model = "none"
```

## Coverage Gaps (Observed)

- Route behavior has no formal automated tests for:
  - Authentication flow and session transitions in `routes/auth.py`.
  - CAPTCHA fallback logic in `routes/auth.py` and `routes/scammer.py`.
  - Leaderboard/search/profile APIs in `routes/main.py`.
  - Chat session lifecycle endpoints in `routes/chatbot.py`.
- Utility and security-critical logic lacks direct tests:
  - Encryption/hash/validation paths in `utils/encryption.py`.
  - AI fallback and parsing paths in `utils/chatbot.py` and `utils/ai_agent.py`.
  - Risk scoring and masking edge cases in `utils/helpers.py`.
- Model and migration health checks are mostly script-based (`database/test/*.py`) and not assertion-backed regression tests.
- No CI-oriented test orchestration file (no `pytest`, `tox`, or `nox` config) is detected.
- The `.gitignore` includes `tests/` and `test/`, which can prevent test files from being tracked consistently and weakens long-term regression safety.

## Prescriptive Guidance For New Tests

- Add new deterministic unit tests under `tests/` using `unittest` unless the project adopts `pytest` explicitly.
- Keep external API probes separated from core regression tests to avoid flaky CI.
- Use in-memory SQLite for model/service tests that only need DB semantics.
- Introduce mock layers for network calls (`requests`, `urllib`) to verify fallback branches reliably.
- Add assertion-based tests for each blueprint endpoint group (`auth`, `scammer`, `chatbot`, `main`, `quiz`, `admin`) using Flask test client.

---

*Testing analysis: 2026-03-19*