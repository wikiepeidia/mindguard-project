# Conventions

> Mapped: 2026-04-13

## Code Style

- **Indentation**: 4 spaces
- **Formatter**: None configured
- **Linter**: None configured
- **Line length**: No enforced limit
- **Quotes**: Mixed single/double (no standard)

## Naming

- **Functions/variables**: snake_case (`generate_certificate_code`, `quiz_result`)
- **Classes**: PascalCase (`Registration`, `ScammerReport`, `AntiSpamDecisionService`)
- **Constants**: UPPERCASE (`DEFAULT_SYSTEM_PROMPT`, `MODELS`, `MAX_HISTORY`)
- **Templates**: snake_case (`admin_dashboard.html`, `quiz_result.html`)
- **CSS files**: snake_case matching template (`chatbot.css`, `leaderboard.css`)
- **JS files**: snake_case matching feature (`chatbot_page.js`, `chatbot_widget.js`)

## Import Style

Standard Python import ordering (not enforced):
1. Standard library (`os`, `json`, `hashlib`, `logging`)
2. Third-party (`flask`, `sqlalchemy`, `werkzeug`)
3. Local imports (`from models.models import ...`, `from utils.chatbot import ...`)

No path aliases. Relative imports within packages.

## Patterns

### Route Decorators
```python
@quiz_bp.route('/quiz/step/<int:step>', methods=['GET', 'POST'])
@limiter.limit("20/minute;3/second")
def quiz_step(step):
```

### Login Required (Custom)
```python
from utils.helpers import login_required

@chatbot_bp.route('/chatbot/send', methods=['POST'])
@login_required
def chatbot_send():
```

### Flash Messages for User Feedback
```python
flash("Đăng ký thành công!", "success")
flash("Sai mật khẩu!", "danger")
```

### Template Filters
```python
@app.template_filter('mask_phone')
def mask_phone_filter(phone):
    return mask_phone(phone)
```

## Error Handling

- Mix of bare `except` blocks (anti-pattern) and specific exception handling
- Flask `flash()` for user-visible errors
- `try/except` around external API calls (OpenRouter)
- Fallback patterns in chatbot (AI fails → `simple_bot_reply()`)
- No global error handler configured

## Comments & Documentation

- Vietnamese comments used extensively throughout codebase
- Docstrings on some complex functions and modules
- No JSDoc or typed JavaScript
- No README-style module documentation

## State Management

- Flask server-side sessions for user state (quiz progress, auth)
- `localStorage` for chatbot widget history (client-side)
- No client-side framework state management
