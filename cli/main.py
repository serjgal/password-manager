import os
import sys
from getpass import getpass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import init_db
from core.security import get_key, load_salt, set_master_password, verify_master_password
from core.utils import generate_password, copy_to_clipboard, check_pwned
from core.manager import PasswordManager, reset_vault
from config import VERIFY_FILE, PASSWORD_DEFAULT_LENGTH

def get_input_pwd(prompt="Enter password: "):
    """Handle normal and gen input."""
    pwd = getpass(prompt)
    if pwd.lower().startswith("gen"):
        l = PASSWORD_DEFAULT_LENGTH
        try:
            ls = pwd[4:-1] if pwd.lower().startswith("gen[") else pwd[3:]
            if ls: l = int(ls)
            pwd = generate_password(l)
            copy_to_clipboard(pwd)
            return pwd, True
        except ValueError: return None, False
    return pwd, False

def loop(key):
    pm = PasswordManager(key)
    while True:
        print("\n1.Add 2.Get 3.List 4.Update 5.Delete 6.Gen 7.Pwned 8.Reset 9.Exit")
        c = input("> ")
        if c == '9': break
        elif c == '1':
            s, u = input("Service: "), input("User: ")
            p, g = get_input_pwd()
            if p: pm.add(s, u, p, g)
        elif c == '2': pm.get(input("Service: "), input("User (opt): "))
        elif c == '3': pm.list_all()
        elif c == '4':
            s, u = input("Service: "), input("User: ")
            p, g = get_input_pwd("New pwd: ")
            if p: pm.update(s, u, p, g)
        elif c == '5': pm.delete(input("Service: "), input("User: "))
        elif c == '6':
            try:
                l = int(input(f"Len ({PASSWORD_DEFAULT_LENGTH}): ") or PASSWORD_DEFAULT_LENGTH)
                p = generate_password(l)
                print(f"Pwd: {p}")
                copy_to_clipboard(p)
            except ValueError: pass
        elif c == '7':
            count = check_pwned(getpass("Pwd to check: "))
            print(f"Breaches: {count}" if count > 0 else "Clean.")
        elif c == '8':
            if reset_vault(): return True
    return False

def main():
    init_db()
    if not os.path.exists(VERIFY_FILE):
        while True:
            p1, p2 = getpass("New Master: "), getpass("Confirm: ")
            if p1 == p2:
                set_master_password(p1)
                break
            print("Mismatch.")
    
    while True:
        p = getpass("Master: ")
        if verify_master_password(p):
            if loop(get_key(p, load_salt())):
                main()
            break
        print("Wrong.")
        if input("Reset? (y/n): ").lower() == 'y':
            if reset_vault():
                main()
                break

if __name__ == "__main__":
    main()
