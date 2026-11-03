import unittest

from backend.app.security import hash_password, verify_password


class TestPasswordSecurity(unittest.TestCase):

    def test_password_hash_is_not_plaintext(self):
        password = "SecureBankTest@123"
        password_hash = hash_password(password)

        self.assertNotEqual(password, password_hash)

    def test_correct_password_is_accepted(self):
        password = "SecureBankTest@123"
        password_hash = hash_password(password)

        self.assertTrue(verify_password(password, password_hash))

    def test_incorrect_password_is_rejected(self):
        password_hash = hash_password("SecureBankTest@123")

        self.assertFalse(
            verify_password("WrongPassword@123", password_hash)
        )

    def test_empty_password_is_rejected(self):
        password_hash = hash_password("SecureBankTest@123")

        self.assertFalse(verify_password("", password_hash))

    def test_empty_password_cannot_be_hashed(self):
        with self.assertRaises(ValueError):
            hash_password("")


if __name__ == "__main__":
    unittest.main()
