import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "templates" / "report_scammer.html"
STYLESHEET = ROOT / "static" / "css" / "report_scammer.css"


class TestReportMobileLight(unittest.TestCase):
    def test_template_uses_light_turnstile(self):
        content = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn('data-theme="light"', content)

    def test_template_avoids_dark_utility_drift(self):
        content = TEMPLATE.read_text(encoding="utf-8")
        forbidden_fragments = [
            "bg-dark",
            "text-white",
            "bg-black",
            "btn-outline-dark",
        ]
        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, content, f"{fragment} found in report_scammer.html")

    def test_mobile_first_structure_exists(self):
        content = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("report-page", content)
        self.assertIn("report-mode-grid", content)

    def test_stylesheet_consumes_tokens_and_breakpoints(self):
        css = STYLESHEET.read_text(encoding="utf-8")
        self.assertRegex(css, re.compile(r"--mg-"), "report_scammer.css should consume mg tokens")
        self.assertIn("@media (min-width: 576px)", css)
        self.assertIn("@media (min-width: 768px)", css)
        self.assertIn("overflow-x: hidden", css)


if __name__ == "__main__":
    unittest.main()
