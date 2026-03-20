import unittest

from utils.privacy_policy import to_display_identifier


class TestApiMaskingConsistency(unittest.TestCase):
    def test_public_ui_and_api_are_consistent_for_same_phone(self):
        raw_identifier = "0912345678"
        report_type = "general"

        # API and UI must call the same display adapter to avoid policy drift.
        api_view_identifier = to_display_identifier(raw_identifier, report_type, is_admin=False)
        ui_view_identifier = to_display_identifier(raw_identifier, report_type, is_admin=False)

        self.assertEqual(api_view_identifier, "*******678")
        self.assertEqual(ui_view_identifier, "*******678")


if __name__ == "__main__":
    unittest.main()
