# MindGuard Flask v2 - Changelog & Documentation

## 🎉 Version 2.0 - Major Refactoring & New Features

### ✨ What's New

#### 1. **Modular Code Structure** 
The application has been completely refactored into a clean, maintainable modular architecture:

```
mindguard_flask_v2/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── models.py              # Database models
├── routes/                # Blueprint routes
│   ├── main.py           # Main pages (home, leaderboard)
│   ├── scammer.py        # Scammer reporting system
│   ├── chatbot.py        # Chatbot functionality
│   ├── quiz.py           # Quiz and certificate
│   ├── auth.py           # User registration
│   └── admin.py          # Admin dashboard
├── utils/                 # Utility functions
│   ├── encryption.py     # Encryption & hashing
│   ├── helpers.py        # Helper functions
│   ├── chatbot.py        # Chatbot AI logic
│   └── quiz_data.py      # Quiz questions
└── templates/             # HTML templates
```

#### 2. **Scammer Reporting System** 🚨
A complete system for reporting scammers with maximum security:

**Features:**
- **Anonymous Reporting**: Reporter identity is hashed and encrypted
- **Evidence Validation**: Requires at least 1 piece of evidence
- **Auto-Approval System**: 
  - Auto-approves if scammer already reported ≥3 times
  - Auto-approves if strong evidence provided (≥2 pieces)
  - Manual review for new reports
- **Support Chatbot**: Integrated helper bot to guide users through reporting
- **Multiple Evidence Types**: Support for screenshots, links, videos, etc.

**Database Models:**
- `ScammerReport`: Stores encrypted scammer information
- `ScammerLeaderboard`: Tracks most reported scammers
- `ChatSupportMessage`: Logs support chat messages

#### 3. **Scammer Leaderboard** 🏆
Public "hall of shame" for most dangerous scammers:

**Features:**
- **Ranking System**: Top 50 most reported scammers
- **Danger Levels**: 
  - 🔴 Critical (≥20 reports)
  - 🟠 High (≥10 reports)
  - 🔵 Medium (≥5 reports)
  - ⚪ Low (<5 reports)
- **Visual Design**: Trophy icons for top 3, progress bars, color-coded badges
- **Statistics**: Total reports, danger level, last reported date
- **Real-time Updates**: Automatically updates when new reports approved

#### 4. **Enhanced Chatbot** 🤖
Two chatbot modes for different purposes:

**Scam Analysis Bot** (`/chatbot`):
- Analyzes messages for scam risk
- Provides risk score (0-100%)
- Gives actionable advice
- Detects 12+ scam keywords

**Support Chat Bot** (within reporting page):
- Guides users through reporting process
- Answers questions about evidence, privacy, approval process
- Real-time responses via AJAX
- Saved chat history in database

#### 5. **Improved Quiz System** 📝
Enhanced quiz with better feedback:

**New Features:**
- Shows "scam types avoided" count (score out of 15)
- Shows "scam types still vulnerable" count
- Better feedback messages
- Certificate includes avoidance statistics

#### 6. **Security & Privacy** 🔒

**Encryption:**
- Reporter IDs are SHA-256 hashed with salt
- Scammer identifiers are encrypted
- No way to trace reports back to reporters

**Evidence Validation:**
- Minimum 1 evidence required
- URL format validation
- Support for multiple evidence types

**Auto-Approval Rules:**
- Prevents spam while ensuring quality
- Reduces admin workload
- Faster community protection

### 📊 Database Changes

**New Tables:**
1. `scammer_reports` - Stores scammer reports
2. `scammer_leaderboard` - Tracks top scammers
3. `chat_support_messages` - Logs support chats

**Modified Tables:**
- All tables now use proper naming conventions
- Added foreign key relationships
- Added indexes for performance

### 🎨 UI/UX Improvements

1. **New Templates:**
   - `report_scammer.html` - Complete scammer reporting interface
   - `leaderboard.html` - Scammer hall of shame
   - `admin_scammer_reports.html` - Admin panel for reports

2. **Updated Homepage:**
   - Shows scammer report count
   - Preview of top 3 scammers
   - New action buttons (Tố Cáo, Bảng Vàng)

3. **Support Chat Widget:**
   - Modal popup design
   - Real-time messaging
   - Markdown support in responses

### 🔧 Configuration

New configuration options in `config.py`:

```python
# Quiz settings
QUIZ_PASS_PERCENTAGE = 0.75  # 75% to pass

# Reporting settings
MIN_EVIDENCE_COUNT = 1       # Minimum evidence required
AUTO_APPROVE_THRESHOLD = 3   # Auto-approve threshold

# Encryption
REPORT_ENCRYPTION_KEY = "..."  # Encryption key
```

### 🚀 Getting Started

#### Installation

1. **Activate virtual environment:**
   ```bash
   .venv\Scripts\activate  # Windows
   ```

2. **Dependencies are already installed:**
   - Flask 3.0.3
   - Flask-SQLAlchemy 3.1.1

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   - Homepage: http://127.0.0.1:5000
   - Admin Panel: http://127.0.0.1:5000/admin/login
     - Username: `admin`
     - Password: `mindguard2025`

### 📖 API Documentation

#### Chatbot APIs

**1. Scam Analysis API**
```http
POST /chatbot/api
Content-Type: application/json

{
  "message": "Người ta bảo tôi trúng thưởng và yêu cầu OTP"
}

Response:
{
  "reply": "⚠️ Nguy cơ CAO (85%)..."
}
```

**2. Support Chat API**
```http
POST /chatbot/support
Content-Type: application/json

{
  "message": "Cần những bằng chứng gì?"
}

Response:
{
  "reply": "📸 Bằng chứng cần thiết...",
  "session_id": "CHAT-20250111-1234"
}
```

### 🔐 Admin Features

**Scammer Report Management:**
- View all reports (pending, approved, rejected)
- One-click approve/reject
- Auto-updates leaderboard on approval
- Filter by status

**Dashboard Stats:**
- Total scam reports
- Total scammer reports
- Pending reports count
- Recent activity

### 🎯 How It Works

#### Reporting Flow

1. **User submits report** with scammer info + evidence
2. **System hashes** reporter ID for anonymity
3. **System encrypts** scammer identifier
4. **System validates** evidence (min 1 required)
5. **Auto-approval check:**
   - If scammer already has ≥3 reports → Auto-approve
   - If evidence count ≥2 → Auto-approve
   - Otherwise → Pending review
6. **If approved:** Add to leaderboard with danger level
7. **Update stats** and notify user

#### Leaderboard Ranking

```python
danger_level = {
    reports >= 20: 'critical',  # 🔴 
    reports >= 10: 'high',      # 🟠
    reports >= 5:  'medium',    # 🔵
    reports < 5:   'low'        # ⚪
}
```

### 🐛 Bug Fixes

1. ✅ Fixed missing Flask-SQLAlchemy dependency
2. ✅ Fixed blueprint routing issues
3. ✅ Fixed database initialization
4. ✅ Improved error handling
5. ✅ Fixed URL routing for new structure

### 📝 TODO / Future Improvements

- [ ] Add image upload for evidence
- [ ] Implement email notifications
- [ ] Add reporting analytics dashboard
- [ ] Implement search functionality in leaderboard
- [ ] Add export reports to CSV
- [ ] Implement rate limiting
- [ ] Add CAPTCHA for spam prevention
- [ ] Create mobile-responsive design improvements
- [ ] Add multilanguage support
- [ ] Implement OAuth login

### 🤝 Contributing

The codebase is now well-organized and documented. To add new features:

1. Create models in `models.py`
2. Add utility functions in `utils/`
3. Create blueprint routes in `routes/`
4. Add templates in `templates/`
5. Update `app.py` to register new blueprints

### 📄 License

See LICENSE file

### 👥 Credits

- Original concept: MindGuard Team
- Refactoring: AI Assistant (January 2026)
- Community contributions welcome!

---

## 🎊 Summary

This version transforms MindGuard from a simple educational tool into a **complete community protection platform** with:

✅ Anonymous scammer reporting
✅ Community leaderboard
✅ AI-powered risk analysis
✅ Support chatbot
✅ Auto-moderation system
✅ Clean, maintainable code
✅ Production-ready structure

**The code is now properly organized, scalable, and ready for future enhancements!**
