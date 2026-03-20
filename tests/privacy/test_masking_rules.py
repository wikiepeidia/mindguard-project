import unittest

from utils.privacy_policy import mask_identifier_keep_2_2, mask_phone_keep_last3


class TestMaskingRules(unittest.TestCase):
    def test_phone_mask_keeps_only_last_three_digits(self):
        self.assertEqual(mask_phone_keep_last3("0912345678"), "*******678")
        self.assertEqual(mask_phone_keep_last3("+84 912-345-678"), "***********678")

    def test_non_phone_identifier_keeps_first_two_last_two(self):
        self.assertEqual(mask_identifier_keep_2_2("abcd1234"), "ab****34")
        self.assertEqual(mask_identifier_keep_2_2("user_name@example.com"), "us***************om")

    def test_short_identifier_edge_cases(self):
        self.assertEqual(mask_identifier_keep_2_2("ab"), "ab")
        self.assertEqual(mask_identifier_keep_2_2("abc"), "a*c")
        self.assertEqual(mask_phone_keep_last3("123"), "123")


if __name__ == "__main__":
    unittest.main()
