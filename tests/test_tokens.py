import unittest

import jwt

from backend.app.tokens import create_access_token, decode_access_token


class TestJWTAuthentication(unittest.TestCase):

    def test_token_creation_and_decoding(self):
        token = create_access_token(
            user_id=1,
            username="testuser",
            role="Customer",
        )

        payload = decode_access_token(token)

        self.assertEqual(payload["sub"], "1")
        self.assertEqual(payload["username"], "testuser")
        self.assertEqual(payload["role"], "Customer")

    def test_invalid_token_is_rejected(self):
        with self.assertRaises(jwt.InvalidTokenError):
            decode_access_token("invalid.token.value")


if __name__ == "__main__":
    unittest.main()
