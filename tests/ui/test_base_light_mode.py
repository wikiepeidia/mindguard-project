import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    ROOT / "templates" / "base.html",
    ROOT / "templates" / "login.html",
    ROOT / "templates" / "register.html",
    ROOT / "templates" / "profile.html",
]


class TestBaseLightMode(unittest.TestCase):
    def test_tokens_stylesheet_is_in_base_template(self):
        content = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
        self.assertIn("css/tokens.css", content)

    def test_no_dark_utility_classes_in_scoped_templates(self):
        forbidden_fragments = [
            "bg-dark",
            "text-white",
            "btn-close-white",
            "border-dark",
        ]
        for template in TARGETS:
            content = template.read_text(encoding="utf-8")
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, content, f"{fragment} found in {template.name}")

    def test_turnstile_theme_is_light_on_auth_pages(self):
        for name in ("login.html", "register.html"):
            content = (ROOT / "templates" / name).read_text(encoding="utf-8")
            self.assertIn('data-theme="light"', content, f"Turnstile theme should be light in {name}")


if __name__ == "__main__":
    unittest.main()
