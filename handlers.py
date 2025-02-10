from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_players, add_player
from utils import validate_player_data, split_teams_balanced, split_teams_random, split_teams_optimal,calculate_total_score

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    keyboard = [
        ["Добавить игрока", "Показать игроков"],
        ["Сгенерировать команды"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=reply_markup
    )

async def add_player_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Добавить игрока'."""
    await update.message.reply_text(
        "Введите данные игрока в формате:\n"
        "<имя> <навык> <скорость> <выносливость> <защита> <атака>\n"
        "Пример: Игрок1 8 7 6 5 9"
    )

async def show_players_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Показать игроков'."""
    user_id = update.message.from_user.id
    players = get_players(user_id)
    
    if not players:
        await update.message.reply_text("Игроков пока нет. Добавьте их с помощью 'Добавить игрока'.")
        return
    
    message = "Ваши игроки:\n\n"
    for player in players:
        message += (
            f"Имя: {player[2]}\n"
            f"Навык: {player[3]}\n"
            f"Скорость: {player[4]}\n"
            f"Выносливость: {player[5]}\n"
            f"Защита: {player[6]}\n"
            f"Атака: {player[7]}\n"
            f"Итого: {calculate_total_score(player)}\n"
            "────────────\n"
        )
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)
    await update.message.reply_text(message)

async def generate_teams_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Сгенерировать команды'."""
    keyboard = [
        ["Случайно, но сбалансировано", "Полностью случайно"],
        ["Сбалансировано по силе"],
        ["Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Выберите тип генерации команд:",
        reply_markup=reply_markup
    )

async def handle_generate_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора типа генерации команд."""
    user_id = update.message.from_user.id
    players = get_players(user_id)
    
    if len(players) < 2:
        await update.message.reply_text("Добавьте больше игроков!")
        return
    
    text = update.message.text
    
    if text == "Случайно, но сбалансировано":
        team_a, team_b = split_teams_balanced(players)
    elif text == "Полностью случайно":
        team_a, team_b = split_teams_random(players)
    elif text == "Сбалансировано по силе":
        team_a, team_b = split_teams_optimal(players)
    else:
        await update.message.reply_text("Неверный выбор. Попробуйте снова.")
        return
    
    team_a_names = ", ".join([player["name"] for player in team_a])
    team_b_names = ", ".join([player["name"] for player in team_b])
    
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Команда A: {team_a_names}\nКоманда B: {team_b_names}",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений."""
    text = update.message.text
    
    if text == "Добавить игрока":
        await add_player_handler(update, context)
    elif text == "Показать игроков":
        await show_players_handler(update, context)
    elif text == "Сгенерировать команды":
        await generate_teams_handler(update, context)
    elif text in ["Случайно, но сбалансировано", "Полностью случайно", "Сбалансировано по силе"]:
        await handle_generate_teams(update, context)
    elif text == "Назад":
        await start(update, context)  # Возврат в главное меню
    else:
        # Если сообщение не является командой, пробуем добавить игрока
        try:
            args = text.split()
            if len(args) == 6:
                name, skill, speed, stamina, defense, attack = args
                skill, speed, stamina, defense, attack = map(int, [skill, speed, stamina, defense, attack])
                validate_player_data(skill, speed, stamina, defense, attack)
                
                user_id = update.message.from_user.id
                add_player(user_id, name, skill, speed, stamina, defense, attack)
                await update.message.reply_text(f"Игрок {name} добавлен!")
            else:
                await update.message.reply_text("Неверный формат. Используйте: <имя> <навык> <скорость> <выносливость> <защита> <атака>")
        except ValueError as e:
            await update.message.reply_text(str(e))