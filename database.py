import sqlite3
from contextlib import contextmanager
from config import DATABASE_NAME

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
                speed INTEGER NOT NULL,          # Скорость (0-99)
                stamina INTEGER NOT NULL,        # Выносливость (0-99)
                shot_power INTEGER NOT NULL,     # Сила удара (0-99)
                shot_accuracy INTEGER NOT NULL,  # Точность удара (0-99)
                pass_accuracy INTEGER NOT NULL,  # Точность пасов (0-99)
                teamwork TEXT NOT NULL,         # Командная игра (да/нет)
                defense INTEGER NOT NULL,       # Защита (0-99)
                dribbling INTEGER NOT NULL,     # Дриблинг (0-99)
                position TEXT NOT NULL,         # Амплуа (защитник, полузащитник, нападающий)
                is_playing INTEGER DEFAULT 0    # Играет сегодня (0/1)
            )
        """)
        conn.commit()

def add_player(user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position):
    """Добавляет игрока в базу данных."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO players (user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position))
        conn.commit()

def get_players(user_id):
    """Возвращает список игроков пользователя."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        return cursor.fetchall()

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

def delete_player(user_id, player_name):
    """Удаляет игрока по имени."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE user_id = ? AND name = ?", (user_id, player_name))
        conn.commit()

def update_player(user_id, player_name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position):
    """Обновляет характеристики игрока."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE players
            SET speed = ?, stamina = ?, shot_power = ?, shot_accuracy = ?, pass_accuracy = ?, teamwork = ?, defense = ?, dribbling = ?, position = ?
            WHERE user_id = ? AND name = ?
        """, (speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position, user_id, player_name))
        conn.commit()