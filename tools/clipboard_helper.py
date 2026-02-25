import sys
import time
import pyperclip

if __name__ == "__main__":
    try:
        time.sleep(int(sys.argv[1]))
        pyperclip.copy("")
    except: pass
