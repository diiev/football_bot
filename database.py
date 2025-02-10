import sqlite3
from contextlib import contextmanager
from config  import DATABASE_NAME
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                skill INTEGER NOT NULL,
                speed INTEGER NOT NULL,
                stamina INTEGER NOT NULL,
                defense INTEGER NOT NULL,
                attack INTEGER NOT NULL
            )
        """)
        conn.commit()

def add_player(user_id, name, skill, speed, stamina, defense, attack):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO players (user_id, name, skill, speed, stamina, defense, attack)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, skill, speed, stamina, defense, attack))
        conn.commit()

def get_players(user_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        return cursor.fetchall()  # Возвращает список кортежей