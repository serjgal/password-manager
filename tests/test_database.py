import sqlite3
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import create_table, add_password, get_password, get_all_passwords, update_password, delete_password

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    create_table(conn)
    yield conn
    conn.close()

def test_add_get(db):
    add_password(db, "s", "u", b"p")
    r = get_password(db, "s", "u")
    assert len(r) == 1
    assert r[0][1] == "s"

def test_all(db):
    add_password(db, "s1", "u1", b"p1")
    add_password(db, "s2", "u2", b"p2")
    assert len(get_all_passwords(db)) == 2

def test_update(db):
    rid = add_password(db, "s", "u", b"p")
    update_password(db, rid, "s2", "u2", b"p2", True)
    r = get_password(db, "s2", "u2")
    assert r[0][1] == "s2"
    assert r[0][4] == 1

def test_delete(db):
    rid = add_password(db, "s", "u", b"p")
    delete_password(db, rid)
    assert len(get_all_passwords(db)) == 0
