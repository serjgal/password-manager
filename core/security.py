import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import sys

# Add parent directory to path to find config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SALT_FILE, VERIFY_FILE, ITERATIONS, KEY_LENGTH

VERIFICATION_STRING: bytes = b"this is a verification string"

def get_key(password: str, salt: bytes) -> bytes:
    """Derive 256-bit key using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def generate_salt() -> bytes:
    """Generate and save 16-byte random salt."""
    salt = os.urandom(16)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    return salt

def load_salt() -> Optional[bytes]:
    """Load salt from file."""
    try:
        with open(SALT_FILE, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None

def encrypt(data: str, key: bytes) -> bytes:
    """Encrypt string using AES-256-GCM."""
    iv = os.urandom(12)
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
    return iv + encryptor.tag + ciphertext

def decrypt(encrypted_data: bytes, key: bytes) -> Optional[str]:
    """Decrypt AES-256-GCM byte string."""
    if len(encrypted_data) < 28:
        return None
    iv, tag, ciphertext = encrypted_data[:12], encrypted_data[12:28], encrypted_data[28:]
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    try:
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode()
    except Exception:
        return None

def set_master_password(password: str) -> None:
    """Set master password and save verification blob."""
    salt = generate_salt()
    key = get_key(password, salt)
    encrypted_verification = encrypt(VERIFICATION_STRING.decode(), key)
    with open(VERIFY_FILE, "wb") as f:
        f.write(encrypted_verification)

def verify_master_password(password: str) -> bool:
    """Verify master password against stored blob."""
    salt = load_salt()
    if not salt: return False
    try:
        with open(VERIFY_FILE, "rb") as f:
            encrypted_verification = f.read()
    except FileNotFoundError: return False
    key = get_key(password, salt)
    decrypted_verification = decrypt(encrypted_verification, key)
    return decrypted_verification == VERIFICATION_STRING.decode()
