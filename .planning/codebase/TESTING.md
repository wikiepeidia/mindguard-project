# Testing

> Mapped: 2026-04-13

## Framework

- **Unit test framework**: unittest (Python standard library)
- **Test runner**: `python -m pytest` (pytest compatible)
- **Coverage tool**: None configured
- **E2E testing**: Not configured

## Structure

```
tests/
├── test_quiz.py           # Quiz flow tests
├── test_chatbot.py        # Chatbot tests
├── test_ai_quiz.py        # AI quiz generation tests
├── test_stats.py          # Statistics tests
├── test_openrouter_limits.py  # API limit tests
├── antispam/              # Anti-spam test suite
│   └── test_antispam_*.py
├── leaderboard/           # Leaderboard test suite
│   └── test_leaderboard_*.py
├── quizflow/              # Quiz flow test suite
│   └── test_quizflow_*.py
├── privacy/               # Privacy masking tests
│   └── test_privacy_*.py
├── ui/                    # UI contract tests
│   └── test_ui_*.py
├── fixer/                 # Fix verification tests
└── fixtures/              # Test data/fixtures
```

## Test Patterns

### Base Classes
Test base classes provide setup/teardown with in-memory SQLite:
```python
class QuizFlowTestBase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
```

### Database Isolation
- Uses SQLite with `StaticPool` for test isolation
- In-memory database created fresh per test class
- `StaticPool` ensures shared in-memory DB within a test

### Mocking
- `unittest.mock.patch` used extensively (`@patch` decorators)
- External API calls (OpenRouter) mocked in tests
- Session data injected via test client

### Test Types
- **Contract tests**: Verify route behavior (HTTP status, redirects, context)
- **Unit tests**: Business logic (risk scoring, masking rules, badge calculation)
- **Integration tests**: Test client with session injection

## Running Tests

```bash
python -m pytest              # Run all tests
python -m pytest tests/antispam/  # Run specific suite
```

## Coverage

- No coverage requirements enforced
- Tests exist for critical features (anti-spam, leaderboard, quiz flow, privacy)
- No CI integration for test runs
