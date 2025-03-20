import sqlite3
import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "7159540137:AAEU4QGYSKcvs_psDYzNgjzPjaRm8NnUSQA"  # Замените на ваш токен
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключение к базе данных
conn = sqlite3.connect("players.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    speed INTEGER,
                    stamina INTEGER,
                    shot_power INTEGER,
                    shot_accuracy INTEGER,
                    pass_accuracy INTEGER,
                    teamwork INTEGER,
                    defense INTEGER,
                    dribbling INTEGER,
                    total INTEGER)''')
conn.commit()

# Состояния для FSM
class AddPlayerStates(StatesGroup):
    NAME = State()
    SPEED = State()
    STAMINA = State()
    SHOT_POWER = State()
    SHOT_ACCURACY = State()
    PASS_ACCURACY = State()
    TEAMWORK = State()
    DEFENSE = State()
    DRIBBLING = State()

# Создаем меню с кнопками
def main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/add_player")],
            [KeyboardButton(text="/players")],
            [KeyboardButton(text="/generate_teams")],
        ],
        resize_keyboard=True,  # Клавиатура подстраивается под размер экрана
    )
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для управления футбольными командами. Выбери команду:",
        reply_markup=main_menu_keyboard(),
    )

# Обработчик команды /add_player
@dp.message(Command("add_player"))
async def cmd_add_player(message: types.Message, state: FSMContext):
    await message.answer("Введите имя игрока:")
    await state.set_state(AddPlayerStates.NAME)

# Обработчик для ввода имени
@dp.message(AddPlayerStates.NAME)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите скорость игрока (0-100):")
    await state.set_state(AddPlayerStates.SPEED)

# Обработчик для ввода скорости
@dp.message(AddPlayerStates.SPEED)
async def process_speed(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return
    await state.update_data(speed=int(message.text))
    await message.answer("Введите выносливость игрока (0-100):")
    await state.set_state(AddPlayerStates.STAMINA)

# Обработчик для ввода выносливости
@dp.message(AddPlayerStates.STAMINA)
async def process_stamina(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return
    await state.update_data(stamina=int(message.text))
    await message.answer("Введите силу удара игрока (0-100):")
    await state.set_state(AddPlayerStates.SHOT_POWER)

# Обработчик для ввода силы удара
@dp.message(AddPlayerStates.SHOT_POWER)
async def process_shot_power(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return
    await state.update_data(shot_power=int(message.text))
    await message.answer("Введите точность удара игрока (0-100):")
    await state.set_state(AddPlayerStates.SHOT_ACCURACY)

# Обработчик для ввода точности удара
@dp.message(AddPlayerStates.SHOT_ACCURACY)
async def process_shot_accuracy(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return
    await state.update_data(shot_accuracy=int(message.text))
    await message.answer("Введите точность пасов игрока (0-100):")
    await state.set_state(AddPlayerStates.PASS_ACCURACY)

# Обработчик для ввода точности пасов
@dp.message(AddPlayerStates.PASS_ACCURACY)
async def process_pass_accuracy(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return
    await state.update_data(pass_accuracy=int(message.text))
    await message.answer("Введите командную игру игрока (0-100):")
    await state.set_state(AddPlayerStates.TEAMWORK)

# Обработчик для ввода командной игры
@dp.message(AddPlayerStates.TEAMWORK)
async def process_teamwork(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return
    await state.update_data(teamwork=int(message.text))
    await message.answer("Введите защиту игрока (0-100):")
    await state.set_state(AddPlayerStates.DEFENSE)

# Обработчик для ввода защиты
@dp.message(AddPlayerStates.DEFENSE)
async def process_defense(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return
    await state.update_data(defense=int(message.text))
    await message.answer("Введите дриблинг игрока (0-100):")
    await state.set_state(AddPlayerStates.DRIBBLING)

# Обработчик для ввода дриблинга
@dp.message(AddPlayerStates.DRIBBLING)
async def process_dribbling(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("Пожалуйста, введите число от 0 до 100.")
        return

    # Сохраняем дриблинг и завершаем сбор данных
    await state.update_data(dribbling=int(message.text))
    data = await state.get_data()

    # Вычисляем общий рейтинг
    total = (
        data["speed"] + data["stamina"] + data["shot_power"] +
        data["shot_accuracy"] + data["pass_accuracy"] +
        data["teamwork"] + data["defense"] + data["dribbling"]
    )

    # Сохраняем игрока в базу данных
    cursor.execute(
        "INSERT INTO players (user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, total) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (message.from_user.id, data["name"], data["speed"], data["stamina"],
         data["shot_power"], data["shot_accuracy"], data["pass_accuracy"],
         data["teamwork"], data["defense"], data["dribbling"], total)
    )
    conn.commit()

    await message.answer(f"Игрок {data['name']} успешно добавлен с общим рейтингом {total}!", reply_markup=main_menu_keyboard())
    await state.clear()

# Обработчик команды /players
@dp.message(Command("players"))
async def show_players(message: types.Message):
    cursor.execute("SELECT id, name, total FROM players WHERE user_id=?", (message.from_user.id,))
    players = cursor.fetchall()
    if not players:
        await message.answer("У вас пока нет игроков.", reply_markup=main_menu_keyboard())
        return

    response = "Ваши игроки:\n"
    for player in players:
        response += f"{player[1]} (Сила: {player[2]})\n"
    await message.answer(response, reply_markup=main_menu_keyboard())

# Обработчик команды /generate_teams
@dp.message(Command("generate_teams"))
async def generate_teams(message: types.Message):
    cursor.execute("SELECT name, total FROM players WHERE user_id=?", (message.from_user.id,))
    players = cursor.fetchall()
    if len(players) < 4:
        await message.answer("Недостаточно игроков для генерации команд.", reply_markup=main_menu_keyboard())
        return

    # Случайное разделение на команды
    random.shuffle(players)
    mid = len(players) // 2
    team1 = players[:mid]
    team2 = players[mid:]

    response = "⚽ Команда 1:\n"
    response += "\n".join([f"{p[0]} (Сила: {p[1]})" for p in team1])
    response += "\n\n⚽ Команда 2:\n"
    response += "\n".join([f"{p[0]} (Сила: {p[1]})" for p in team2])
    await message.answer(response, reply_markup=main_menu_keyboard())

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())