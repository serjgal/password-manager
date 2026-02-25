import secrets
import string
import time
import pyperclip
import requests
import hashlib
import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CLIPBOARD_CLEAR_DELAY

def generate_password(length=16):
    """Generate random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def copy_to_clipboard(text):
    """Copy text and trigger background clearing."""
    pyperclip.copy(text)
    print("Password copied. Clearing in 30s.")
    helper_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "clipboard_helper.py")
    subprocess.Popen([sys.executable, helper_path, str(CLIPBOARD_CLEAR_DELAY)])

def check_pwned(password: str) -> int:
    """Check password against Pwned API."""
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    if res.status_code != 200: return 0
    for h, count in (line.split(':') for line in res.text.splitlines()):
        if h == suffix: return int(count)
    return 0
