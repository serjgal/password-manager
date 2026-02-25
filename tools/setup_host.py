#!/usr/bin/env python3
import os
import json

EXTENSION_ID = "mohkcobfafifncafmfdkbknmknlbpcjo"
HOST_NAME = "com.serj.password_manager"

def setup():
    """Setup chrome native messaging host."""
    bp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bridge.py")
    manifest = {
        "name": HOST_NAME,
        "description": "Bridge for Password Manager",
        "path": bp,
        "type": "stdio",
        "allowed_origins": [f"chrome-extension://{EXTENSION_ID}/"]
    }
    td = os.path.expanduser("~/Library/Application Support/Google/Chrome/NativeMessagingHosts")
    os.makedirs(td, exist_ok=True)
    tp = os.path.join(td, f"{HOST_NAME}.json")
    with open(tp, "w") as f: json.dump(manifest, f, indent=2)
    print(f"Created: {tp}")

if __name__ == "__main__": setup()
