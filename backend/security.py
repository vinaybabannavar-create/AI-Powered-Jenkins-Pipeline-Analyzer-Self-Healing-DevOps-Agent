import os
import time
import base64
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
import jwt

# Secret keys from environment or generated
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "devops-agent-super-secret-key-change-in-prod-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days

# Generate or read encryption key for Fernet
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Use deterministic key derived from SECRET_KEY so restart preserves ability to decrypt
    hashed = hashlib.sha256(SECRET_KEY.encode()).digest()
    ENCRYPTION_KEY = base64.urlsafe_b64encode(hashed).decode()

_fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt_secret(plain_text: Optional[str]) -> Optional[str]:
    """Encrypts a sensitive string (token, password) at rest."""
    if not plain_text:
        return None
    try:
        return _fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")
    except Exception as e:
        print(f"Encryption error: {e}")
        return None


def decrypt_secret(cipher_text: Optional[str]) -> Optional[str]:
    """Decrypts an encrypted string."""
    if not cipher_text:
        return None
    try:
        return _fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
    except Exception as e:
        print(f"Decryption error: {e}")
        return None


def hash_password(password: str) -> str:
    """Secure password hashing using PBKDF2 with SHA256 and unique salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return base64.b64encode(salt + key).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored hash."""
    try:
        decoded = base64.b64decode(hashed_password.encode("ascii"))
        salt = decoded[:16]
        stored_key = decoded[16:]
        computed_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100000)
        return computed_key == stored_key
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    expire = time.time() + (expires_delta or ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT access token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None
