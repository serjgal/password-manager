import os
import sys
import argparse
from getpass import getpass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import init_db
from core.security import get_key, load_salt, verify_master_password
from core.utils import generate_password, copy_to_clipboard
from core.manager import PasswordManager, reset_vault
from config import VERIFY_FILE, PASSWORD_DEFAULT_LENGTH

def parse_pwd(pwd):
    if pwd.lower().startswith("gen"):
        try:
            l = int(pwd[4:-1] if pwd.lower().startswith("gen[") else pwd[3:] or PASSWORD_DEFAULT_LENGTH)
            p = generate_password(l)
            copy_to_clipboard(p)
            print(f"Gen {l} pwd copied.")
            return p, True
        except ValueError: pass
    return pwd, False

def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    a = s.add_parser("add")
    a.add_argument("service"); a.add_argument("user"); a.add_argument("pwd")
    g = s.add_parser("get")
    g.add_argument("service"); g.add_argument("user", nargs='?', default=None)
    s.add_parser("list")
    u = s.add_parser("update")
    u.add_argument("service"); u.add_argument("user"); u.add_argument("pwd")
    d = s.add_parser("delete")
    d.add_argument("service"); d.add_argument("user")
    gen = s.add_parser("generate")
    gen.add_argument("len", nargs='?', type=int, default=PASSWORD_DEFAULT_LENGTH)
    s.add_parser("reset")

    args = p.parse_args()
    if args.cmd == "generate":
        pwd = generate_password(args.len)
        copy_to_clipboard(pwd)
        print(pwd); return
    if args.cmd == "reset": reset_vault(); return

    init_db()
    if not os.path.exists(VERIFY_FILE): return print("Run main.py first.")
    
    mp = getpass("Master: ")
    if not verify_master_password(mp): return print("Wrong.")
    key = get_key(mp, load_salt())
    pm = PasswordManager(key)

    if args.cmd == "add":
        pwd, gen = parse_pwd(args.pwd)
        pm.add(args.service, args.user, pwd, gen)
    elif args.cmd == "get": pm.get(args.service, args.user)
    elif args.cmd == "list": pm.list_all()
    elif args.cmd == "update":
        pwd, gen = parse_pwd(args.pwd)
        pm.update(args.service, args.user, pwd, gen)
    elif args.cmd == "delete": pm.delete(args.service, args.user)

if __name__ == "__main__": main()
