# config.py

# Security constants
SALT_FILE = "salt.bin"
VERIFY_FILE = "master_key_verify.bin"
ITERATIONS = 100_000
KEY_LENGTH = 32  # 256 bits for AES

# Database constants
DB_FILE = "vault.db"

# Utility constants
CLIPBOARD_CLEAR_DELAY = 30 # seconds
PASSWORD_DEFAULT_LENGTH = 16

# Master Password Attempts
MAX_MASTER_PASSWORD_ATTEMPTS = 3
