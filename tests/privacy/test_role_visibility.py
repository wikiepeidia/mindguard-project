import unittest

from utils.privacy_policy import can_view_full_sensitive, to_display_identifier


class TestRoleVisibility(unittest.TestCase):
    def test_guest_and_non_admin_are_always_masked(self):
        raw_phone = "0912345678"
        self.assertFalse(can_view_full_sensitive(False))
        self.assertEqual(to_display_identifier(raw_phone, "general", is_admin=False), "*******678")
        self.assertEqual(to_display_identifier(raw_phone, "general", is_admin=False), "*******678")

    def test_admin_can_see_full_data(self):
        raw_identifier = "abcdef123456"
        self.assertTrue(can_view_full_sensitive(True))
        self.assertEqual(to_display_identifier(raw_identifier, "bank", is_admin=True), raw_identifier)


if __name__ == "__main__":
    unittest.main()
