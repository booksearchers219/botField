import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("botfield.db")


def init_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    create_tables(conn)

    return conn


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(author_id) REFERENCES agents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tick INTEGER NOT NULL,
            agent_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            metadata TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(agent_id) REFERENCES agents(id)
        )
    """)

    conn.commit()


# ---------- Agent Helpers ----------

def insert_agent(conn, name):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO agents (name, created_at) VALUES (?, ?)",
        (name, timestamp())
    )
    conn.commit()
    return cursor.lastrowid


# ---------- Post Helpers ----------

def insert_post(conn, author_id, content):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (author_id, content, created_at) VALUES (?, ?, ?)",
        (author_id, content, timestamp())
    )
    conn.commit()
    return cursor.lastrowid


def get_recent_posts(conn, limit=5):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM posts ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    return cursor.fetchall()


# ---------- Event Helpers ----------

def insert_event(conn, tick, agent_id, action_type, metadata=None):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO events (tick, agent_id, action_type, metadata, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tick, agent_id, action_type, metadata, timestamp())
    )
    conn.commit()


# ---------- Utilities ----------

def timestamp():
    return datetime.utcnow().isoformat()




