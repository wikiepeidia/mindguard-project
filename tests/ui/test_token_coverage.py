import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "templates"

PRIORITY_TEMPLATE_MAP = {
    "login.html": {
        "expected_fragments": ["glass-card", "cf-turnstile", "data-theme=\"light\""],
        "category": "auth",
    },
    "register.html": {
        "expected_fragments": ["glass-card", "cf-turnstile", "data-theme=\"light\""],
        "category": "auth",
    },
    "profile.html": {
        "expected_fragments": ["glass-card", "Hồ sơ cá nhân"],
        "category": "profile",
    },
    "report_scammer.html": {
        "expected_fragments": ["css/report_scammer.css", "report-page", "data-theme=\"light\""],
        "category": "report",
    },
    "quiz.html": {
        "expected_fragments": ["css/quiz.css", "quiz-page"],
        "category": "quiz",
    },
    "leaderboard.html": {
        "expected_fragments": ["css/leaderboard.css", "leaderboard-page"],
        "category": "leaderboard",
    },
    "scammer_profile.html": {
        "expected_fragments": ["css/scammer_profile.css", "scammer-profile-page"],
        "category": "scammer_profile",
    },
}

FORBIDDEN_DARK_UTILITIES = [
    "bg-dark",
    "text-white",
    "bg-black",
    "btn-close-white",
    "border-dark",
]


class TestTokenCoverage(unittest.TestCase):
    def test_base_includes_token_layer(self):
        base_template = (TEMPLATES / "base.html").read_text(encoding="utf-8")
        self.assertIn("css/tokens.css", base_template, "base.html must load tokens.css")

    def test_priority_templates_have_expected_tokenized_fragments(self):
        for template_name, config in PRIORITY_TEMPLATE_MAP.items():
            content = (TEMPLATES / template_name).read_text(encoding="utf-8")
            for fragment in config["expected_fragments"]:
                self.assertIn(
                    fragment,
                    content,
                    f"Missing '{fragment}' in {template_name} ({config['category']})",
                )

    def test_priority_templates_do_not_use_forbidden_dark_utilities(self):
        violations = []
        for template_name in PRIORITY_TEMPLATE_MAP:
            content = (TEMPLATES / template_name).read_text(encoding="utf-8")
            for fragment in FORBIDDEN_DARK_UTILITIES:
                if fragment in content:
                    violations.append(f"{template_name}: contains '{fragment}'")

        self.assertFalse(
            violations,
            "Dark utility regression detected:\n" + "\n".join(violations),
        )


if __name__ == "__main__":
    unittest.main()
