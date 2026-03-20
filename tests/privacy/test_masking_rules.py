import unittest

from utils.privacy_policy import mask_identifier_keep_2_2, mask_phone_keep_last3


class TestMaskingRules(unittest.TestCase):
    def test_phone_mask_keeps_only_last_three_digits(self):
        self.assertEqual(mask_phone_keep_last3("0912345678"), "*******678")
        masked = mask_phone_keep_last3("+84 912-345-678")
        self.assertTrue(masked.endswith("678"))
        self.assertEqual(len(masked), len("+84 912-345-678"))
        self.assertTrue(set(masked[:-3]) <= {"*"})

    def test_non_phone_identifier_keeps_first_two_last_two(self):
        self.assertEqual(mask_identifier_keep_2_2("abcd1234"), "ab****34")
        masked = mask_identifier_keep_2_2("user_name@example.com")
        self.assertTrue(masked.startswith("us"))
        self.assertTrue(masked.endswith("om"))
        self.assertEqual(len(masked), len("user_name@example.com"))
        self.assertTrue(set(masked[2:-2]) <= {"*"})

    def test_short_identifier_edge_cases(self):
        self.assertEqual(mask_identifier_keep_2_2("ab"), "ab")
        self.assertEqual(mask_identifier_keep_2_2("abc"), "a*c")
        self.assertEqual(mask_phone_keep_last3("123"), "123")


if __name__ == "__main__":
    unittest.main()
