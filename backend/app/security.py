from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return an Argon2 password hash."""
    if not password:
        raise ValueError("Password cannot be empty")

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its stored hash."""
    if not password or not password_hash:
        return False

    return password_hasher.verify(password, password_hash)
