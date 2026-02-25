#!/usr/bin/env python3
import sys
import json
import struct
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.security import get_key, load_salt, verify_master_password, decrypt
from core.manager import PasswordManager
from core.database import init_db, get_password, get_all_passwords

DEBUG_LOG = "/tmp/bridge_debug.log"

def log(msg):
    with open(DEBUG_LOG, "a") as f: f.write(str(msg) + "\n")

def read_msg():
    try:
        raw_len = sys.stdin.buffer.read(4)
        if not raw_len: return None
        msg_len = struct.unpack('=I', raw_len)[0]
        return json.loads(sys.stdin.buffer.read(msg_len).decode('utf-8'))
    except: return None

def send_msg(msg):
    content = json.dumps(msg).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('=I', len(content)))
    sys.stdout.buffer.write(content)
    sys.stdout.buffer.flush()

def main():
    init_db()
    while True:
        msg = read_msg()
        if msg is None: break
        mp = msg.get("master_password")
        if not verify_master_password(mp):
            send_msg({"status": "error", "message": "Invalid master password"})
            continue
        key = get_key(mp, load_salt())
        pm = PasswordManager(key)
        action = msg.get("action")
        if action == "get":
            rows = get_password(pm.conn, msg.get("service"), msg.get("username"))
            if rows:
                pwd = decrypt(rows[0][3], key)
                send_msg({"status": "success", "password": pwd})
            else: send_msg({"status": "error", "message": "Not found"})
        elif action == "list":
            rows = get_all_passwords(pm.conn)
            send_msg({"status": "success", "services": [{"s": r[1], "u": r[2]} for r in rows]})
        else: send_msg({"status": "error", "message": "Unknown action"})

if __name__ == "__main__": main()
