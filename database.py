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
                attack INTEGER NOT NULL,
                is_playing INTEGER DEFAULT 0  # 0 - не играет, 1 - играет
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
    

def delete_player(user_id, player_name):
    """Удаляет игрока по имени."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = ? AND name = ?", (user_id, player_name))
        conn.commit()

def update_player(user_id, player_name, skill, speed, stamina, defense, attack):
    """Обновляет характеристики игрока."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE players
            SET skill = ?, speed = ?, stamina = ?, defense = ?, attack = ?
            WHERE user_id = ? AND name = ?
        """, (skill, speed, stamina, defense, attack, user_id, player_name))
        conn.commit()

def set_player_playing(user_id, player_name, is_playing):
    """Устанавливает статус игрока (играет/не играет)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE players
            SET is_playing = ?
            WHERE user_id = ? AND name = ?
        """, (is_playing, user_id, player_name))
        conn.commit()

def get_playing_players(user_id):
    """Возвращает список игроков, которые играют сегодня."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = ? AND is_playing = 1", (user_id,))
        return cursor.fetchall()