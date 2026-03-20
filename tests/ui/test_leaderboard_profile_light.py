import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEADERBOARD_TEMPLATE = ROOT / "templates" / "leaderboard.html"
PROFILE_TEMPLATE = ROOT / "templates" / "scammer_profile.html"
LEADERBOARD_CSS = ROOT / "static" / "css" / "leaderboard.css"
PROFILE_CSS = ROOT / "static" / "css" / "scammer_profile.css"


class TestLeaderboardProfileLight(unittest.TestCase):
    def test_templates_reference_page_stylesheets(self):
        leaderboard = LEADERBOARD_TEMPLATE.read_text(encoding="utf-8")
        profile = PROFILE_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("css/leaderboard.css", leaderboard)
        self.assertIn("css/scammer_profile.css", profile)

    def test_templates_avoid_dark_utility_fragments(self):
        forbidden_fragments = [
            "bg-dark",
            "text-white",
            "bg-black",
            "btn-close-white",
            "border-dark",
        ]

        for template in (LEADERBOARD_TEMPLATE, PROFILE_TEMPLATE):
            content = template.read_text(encoding="utf-8")
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, content, f"{fragment} found in {template.name}")

    def test_page_stylesheets_consume_tokens(self):
        leaderboard_css = LEADERBOARD_CSS.read_text(encoding="utf-8")
        profile_css = PROFILE_CSS.read_text(encoding="utf-8")

        self.assertRegex(leaderboard_css, re.compile(r"--mg-"))
        self.assertRegex(profile_css, re.compile(r"--mg-"))


if __name__ == "__main__":
    unittest.main()
