import os
import pytest
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.security import encrypt, decrypt, get_key

def test_encryption_decryption():
    key = os.urandom(32)
    t = "Secret123!"
    enc = encrypt(t, key)
    assert enc != t.encode()
    assert decrypt(enc, key) == t

def test_wrong_key():
    k1, k2 = os.urandom(32), os.urandom(32)
    assert decrypt(encrypt("data", k1), k2) is None

def test_kdf():
    p, s = "pass", os.urandom(16)
    assert get_key(p, s) == get_key(p, s)
    assert len(get_key(p, s)) == 32

def test_diff_salt():
    p = "pass"
    assert get_key(p, os.urandom(16)) != get_key(p, os.urandom(16))

def test_invalid_payload():
    assert decrypt(b"short", os.urandom(32)) is None
