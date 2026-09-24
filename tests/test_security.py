import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from security import (
    hash_password, verify_password,
    encrypt_secret, decrypt_secret,
    create_access_token, decode_access_token
)

def test_password_hashing():
    pw = "SecretDevOps123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_credential_encryption():
    token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
    encrypted = encrypt_secret(token)
    assert encrypted != token
    assert encrypted is not None

    decrypted = decrypt_secret(encrypted)
    assert decrypted == token

def test_jwt_token():
    payload = {"sub": "admin@devops.ai", "role": "admin"}
    token = create_access_token(payload, expires_delta=3600)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "admin@devops.ai"
    assert decoded["role"] == "admin"
