from typing import List, Optional, Any
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import create_connection, add_password, get_password, get_all_passwords, update_password, delete_password
from core.security import encrypt, decrypt
from core.utils import copy_to_clipboard, check_pwned
from config import DB_FILE, SALT_FILE, VERIFY_FILE

class PasswordManager:
    """Controller for password operations."""
    def __init__(self, key: bytes):
        self.key = key
        self.conn = create_connection()

    def add(self, service: str, username: str, password: str, is_generated: bool = False) -> None:
        """Add new encrypted entry."""
        count = check_pwned(password)
        if count > 0:
            print(f"Warning: Password found in {count} breaches.")
            if input("Continue? (y/n): ").lower() != 'y': return
        add_password(self.conn, service, username, encrypt(password, self.key), is_generated)
        print("Success.")

    def get(self, service: str, username: Optional[str] = None) -> Optional[str]:
        """Retrieve and decrypt password."""
        rows = get_password(self.conn, service, username)
        if not rows: print("Not found.")
        elif len(rows) == 1:
            pwd = decrypt(rows[0][3], self.key)
            if pwd:
                copy_to_clipboard(pwd)
                return pwd
            print("Decryption error.")
        else:
            print("Multiple entries found. Specify username:")
            for r in rows: print(f"- {r[2]}")
        return None
    
    def list_all(self) -> None:
        """List all entries."""
        rows = get_all_passwords(self.conn)
        if rows:
            for r in rows:
                status = "(gen)" if r[4] else ""
                print(f"Service: {r[1]}, User: {r[2]} {status}")
        else: print("Vault empty.")

    def update(self, service: str, username: str, new_password: str, is_generated: bool = False) -> None:
        """Update entry."""
        rows = get_password(self.conn, service, username)
        if rows and len(rows) == 1:
            update_password(self.conn, rows[0][0], service, username, encrypt(new_password, self.key), is_generated)
            print("Updated.")
        else: print("Entry not found.")
            
    def delete(self, service: str, username: str) -> None:
        """Delete entry."""
        rows = get_password(self.conn, service, username)
        if rows and len(rows) == 1:
            delete_password(self.conn, rows[0][0])
            print("Deleted.")
        else: print("Entry not found.")
            
    def __del__(self):
        if hasattr(self, 'conn') and self.conn: self.conn.close()

def reset_vault() -> bool:
    """Wipe all data files."""
    if input("SURE? This wipes everything! (y/n): ").lower() == 'y':
        for f in [DB_FILE, SALT_FILE, VERIFY_FILE]:
            if os.path.exists(f): os.remove(f)
        print("Wiped.")
        return True
    return False
