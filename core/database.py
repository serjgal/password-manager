import sqlite3
import os
from typing import List, Optional, Any, Tuple
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_FILE

def create_connection(db_path: str = DB_FILE) -> Optional[sqlite3.Connection]:
    """Connect to SQLite database."""
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Connection error: {e}")
    return None

def create_table(conn: sqlite3.Connection) -> None:
    """Create passwords table."""
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password BLOB NOT NULL,
                is_generated BOOLEAN NOT NULL DEFAULT 0
            );
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Table creation error: {e}")

def add_password(conn: sqlite3.Connection, service: str, username: str, 
                 encrypted_password: bytes, is_generated: bool = False) -> int:
    """Add new password entry."""
    sql = 'INSERT INTO passwords(service,username,encrypted_password,is_generated) VALUES(?,?,?,?)'
    cur = conn.cursor()
    cur.execute(sql, (service, username, encrypted_password, is_generated))
    conn.commit()
    return cur.lastrowid

def get_password(conn: sqlite3.Connection, service: str, 
                 username: Optional[str] = None) -> List[Tuple[Any, ...]]:
    """Retrieve passwords by service and optional username."""
    cur = conn.cursor()
    if username:
        cur.execute("SELECT * FROM passwords WHERE service=? AND username=?", (service, username))
    else:
        cur.execute("SELECT * FROM passwords WHERE service=?", (service,))
    return cur.fetchall()

def get_all_passwords(conn: sqlite3.Connection) -> List[Tuple[Any, ...]]:
    """Retrieve all passwords."""
    cur = conn.cursor()
    cur.execute("SELECT * FROM passwords")
    return cur.fetchall()

def update_password(conn: sqlite3.Connection, row_id: int, service: str, 
                    username: str, encrypted_password: bytes, 
                    is_generated: bool = False) -> None:
    """Update existing entry."""
    sql = 'UPDATE passwords SET service=?, username=?, encrypted_password=?, is_generated=? WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (service, username, encrypted_password, is_generated, row_id))
    conn.commit()

def delete_password(conn: sqlite3.Connection, row_id: int) -> None:
    """Delete entry by ID."""
    cur = conn.cursor()
    cur.execute('DELETE FROM passwords WHERE id=?', (row_id,))
    conn.commit()

def init_db() -> None:
    """Initialize database and schema."""
    if not os.path.exists(DB_FILE):
        conn = create_connection()
        if conn:
            create_table(conn)
            conn.close()
    else:
        conn = create_connection()
        if conn:
            try:
                conn.cursor().execute("SELECT is_generated FROM passwords LIMIT 1")
            except sqlite3.OperationalError:
                os.rename(DB_FILE, f"{DB_FILE}.bak")
                init_db()
            conn.close()
