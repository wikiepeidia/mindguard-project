import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOKENS_FILE = ROOT / "static" / "css" / "tokens.css"
STYLE_FILE = ROOT / "static" / "css" / "style.css"
BASE_FILE = ROOT / "static" / "css" / "base.css"


class TestLightTokenContract(unittest.TestCase):
    def test_tokens_css_exists(self):
        self.assertTrue(TOKENS_FILE.exists(), "tokens.css must exist")

    def test_required_token_groups_exist(self):
        content = TOKENS_FILE.read_text(encoding="utf-8")
        required_tokens = [
            "--mg-canvas",
            "--mg-surface",
            "--mg-text-primary",
            "--mg-border",
            "--mg-accent",
            "--mg-warning",
            "--mg-danger",
            "--mg-focus",
            "--mg-space-4",
            "--mg-radius-md",
            "--mg-shadow-md",
        ]
        for token in required_tokens:
            self.assertIn(token, content, f"missing token: {token}")

    def test_global_css_consumes_mg_tokens(self):
        style_content = STYLE_FILE.read_text(encoding="utf-8")
        base_content = BASE_FILE.read_text(encoding="utf-8")
        self.assertRegex(style_content, re.compile(r"--mg-"), "style.css should consume mg tokens")
        self.assertRegex(base_content, re.compile(r"--mg-"), "base.css should consume mg tokens")


if __name__ == "__main__":
    unittest.main()
