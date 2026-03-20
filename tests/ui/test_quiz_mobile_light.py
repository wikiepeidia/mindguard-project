import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "templates" / "quiz.html"
STYLESHEET = ROOT / "static" / "css" / "quiz.css"


class TestQuizMobileLight(unittest.TestCase):
    def test_template_has_mobile_light_structure(self):
        content = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("quiz-page", content)
        self.assertIn("quiz-question-card", content)
        self.assertIn("css/quiz.css", content)

    def test_template_avoids_dark_utility_fragments(self):
        content = TEMPLATE.read_text(encoding="utf-8")
        forbidden_fragments = ["bg-dark", "text-white", "btn-outline-dark", "bg-black"]
        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, content, f"{fragment} found in quiz.html")

    def test_stylesheet_uses_tokens_and_breakpoints(self):
        css = STYLESHEET.read_text(encoding="utf-8")
        self.assertRegex(css, re.compile(r"--mg-"), "quiz.css should consume mg tokens")
        self.assertIn("@media (min-width: 576px)", css)
        self.assertIn("@media (min-width: 768px)", css)
        self.assertIn("overflow-x: hidden", css)

    def test_checked_state_exists_for_quiz_options(self):
        css = STYLESHEET.read_text(encoding="utf-8")
        self.assertIn(".quiz-option-input:checked + .quiz-option-label", css)


if __name__ == "__main__":
    unittest.main()
