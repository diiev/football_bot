from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import get_players, add_player, delete_player, update_player, set_player_playing, get_playing_players
from utils import validate_player_data, split_teams_balanced, split_teams_random, split_teams_optimal

# Глобальные переменные для хранения состояния
player_to_delete = None
current_page = 0
players_per_page = 5

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    keyboard = [
        ["Добавить игрока", "Показать игроков"],
        ["Сгенерировать команды", "Удалить игрока"],
        ["Редактировать игрока", "Найти игрока"],
        ["Отметить игроков"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=reply_markup
    )

async def show_players_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Показать игроков'."""
    global current_page
    current_page = 0
    await show_players_page(update, context)

async def show_players_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает страницу списка игроков."""
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
    players = get_players(user_id)
    
    if not players:
        await update.message.reply_text("Игроков пока нет. Добавьте их с помощью 'Добавить игрока'.")
        return
    
    # Пагинация
    start_index = current_page * players_per_page
    end_index = start_index + players_per_page
    players_page = players[start_index:end_index]
    
    message = "Ваши игроки:\n\n"
    for player in players_page:
        message += (
            f"Имя: {player[2]}\n"
            f"Навык: {player[3]}\n"
            f"Скорость: {player[4]}\n"
            f"Выносливость: {player[5]}\n"
            f"Защита: {player[6]}\n"
            f"Атака: {player[7]}\n"
            f"Играет сегодня: {'Да' if player[8] else 'Нет'}\n"
            "────────────\n"
        )
    
    # Кнопки пагинации
    keyboard = []
    if current_page > 0:
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="prev_page")])
    if end_index < len(players):
        keyboard.append([InlineKeyboardButton("Вперед ➡️", callback_data="next_page")])
    keyboard.append([InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик пагинации."""
    global current_page
    query = update.callback_query
    
    if query.data == "prev_page":
        current_page -= 1
    elif query.data == "next_page":
        current_page += 1
    elif query.data == "back_to_menu":
        await start(update, context)
        return
    
    await show_players_page(update, context)

async def mark_players_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Отметить игроков'."""
    user_id = update.message.from_user.id
    players = get_players(user_id)
    
    if not players:
        await update.message.reply_text("Игроков пока нет. Добавьте их с помощью 'Добавить игрока'.")
        return
    
    # Создаем inline-кнопки для каждого игрока
    keyboard = []
    for player in players:
        player_name = player[2]
        is_playing = "✅" if player[8] else "❌"
        keyboard.append([InlineKeyboardButton(f"{player_name} {is_playing}", callback_data=f"toggle_playing_{player_name}")])
    
    keyboard.append([InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Отметьте игроков, которые играют сегодня:",
        reply_markup=reply_markup
    )

async def handle_toggle_playing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отметки игроков."""
    query = update.callback_query
    user_id = query.from_user.id
    player_name = query.data.replace("toggle_playing_", "")
    
    # Получаем текущий статус игрока
    players = get_players(user_id)
    player = next((p for p in players if p[2] == player_name), None)
    if not player:
        await query.answer("Игрок не найден.")
        return
    
    # Меняем статус
    new_status = 0 if player[8] else 1
    set_player_playing(user_id, player_name, new_status)
    
    # Обновляем сообщение
    await mark_players_handler(update, context)

async def generate_teams_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Сгенерировать команды'."""
    user_id = update.message.from_user.id
    players = get_playing_players(user_id)  # Только игроки, которые играют сегодня
    
    if len(players) < 2:
        await update.message.reply_text("Добавьте больше игроков или отметьте их как играющих сегодня.")
        return
    
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






async def add_player_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Добавить игрока'."""
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Введите данные игрока в формате:\n"
        "<имя> <навык> <скорость> <выносливость> <защита> <атака>\n"
        "Пример: Игрок1 8 7 6 5 9",
        reply_markup=reply_markup
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
            "────────────\n"
        )
    
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

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

async def delete_player_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Удалить игрока'."""
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Введите имя игрока, которого хотите удалить:",
        reply_markup=reply_markup
    )

async def handle_delete_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик удаления игрока."""
    global player_to_delete
    user_id = update.message.from_user.id
    player_name = update.message.text
    
    # Проверяем, существует ли игрок
    players = get_players(user_id)
    player_names = [p[2] for p in players]
    if player_name not in player_names:
        await update.message.reply_text(f"Игрок {player_name} не найден.")
        return
    
    # Сохраняем имя игрока для подтверждения
    player_to_delete = player_name
    
    # Создаем inline-клавиатуру для подтверждения
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="delete_yes")],
        [InlineKeyboardButton("Нет", callback_data="delete_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Вы уверены, что хотите удалить игрока {player_name}?",
        reply_markup=reply_markup
    )

async def confirm_delete_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик подтверждения удаления игрока."""
    global player_to_delete
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "delete_yes":
        delete_player(user_id, player_to_delete)
        await query.edit_message_text(f"Игрок {player_to_delete} удален!")
    else:
        await query.edit_message_text("Удаление отменено.")
    
    player_to_delete = None

async def edit_player_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Редактировать игрока'."""
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Введите данные игрока в формате:\n"
        "<имя> <навык> <скорость> <выносливость> <защита> <атака>\n"
        "Пример: Игрок1 8 7 6 5 9",
        reply_markup=reply_markup
    )

async def handle_edit_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик редактирования игрока."""
    user_id = update.message.from_user.id
    args = update.message.text.split()
    
    if len(args) != 6:
        await update.message.reply_text("Неверный формат. Используйте: <имя> <навык> <скорость> <выносливость> <защита> <атака>")
        return
    
    name, skill, speed, stamina, defense, attack = args
    try:
        skill, speed, stamina, defense, attack = map(int, [skill, speed, stamina, defense, attack])
        validate_player_data(skill, speed, stamina, defense, attack)
        
        update_player(user_id, name, skill, speed, stamina, defense, attack)
        await update.message.reply_text(f"Игрок {name} обновлен!")
    except ValueError as e:
        await update.message.reply_text(str(e))

async def find_player_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Найти игрока'."""
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Введите имя игрока, которого хотите найти:",
        reply_markup=reply_markup
    )

async def handle_find_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик поиска игрока."""
    user_id = update.message.from_user.id
    player_name = update.message.text
    
    players = get_players(user_id)
    player = next((p for p in players if p[2] == player_name), None)
    
    if not player:
        await update.message.reply_text(f"Игрок {player_name} не найден.")
        return
    
    message = (
        f"Имя: {player[2]}\n"
        f"Навык: {player[3]}\n"
        f"Скорость: {player[4]}\n"
        f"Выносливость: {player[5]}\n"
        f"Защита: {player[6]}\n"
        f"Атака: {player[7]}\n"
    )
    
    await update.message.reply_text(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений."""
    text = update.message.text
    
    if text == "Добавить игрока":
        await add_player_handler(update, context)
    elif text == "Показать игроков":
        await show_players_handler(update, context)
    elif text == "Сгенерировать команды":
        await generate_teams_handler(update, context)
    elif text == "Удалить игрока":
        await delete_player_handler(update, context)
    elif text == "Редактировать игрока":
        await edit_player_handler(update, context)
    elif text == "Найти игрока":
        await find_player_handler(update, context)
    elif text in ["Случайно, но сбалансировано", "Полностью случайно", "Сбалансировано по силе"]:
        await handle_generate_teams(update, context)
    elif text == "Назад":
        await start(update, context)
    else:
        # Если сообщение не является командой, пробуем добавить или редактировать игрока
        try:
            args = text.split()
            if len(args) == 6:
                name, skill, speed, stamina, defense, attack = args
                skill, speed, stamina, defense, attack = map(int, [skill, speed, stamina, defense, attack])
                validate_player_data(skill, speed, stamina, defense, attack)
                
                user_id = update.message.from_user.id
                # Проверяем, существует ли игрок
                players = get_players(user_id)
                player_names = [p[2] for p in players]
                if name in player_names:
                    update_player(user_id, name, skill, speed, stamina, defense, attack)
                    await update.message.reply_text(f"Игрок {name} обновлен!")
                else:
                    add_player(user_id, name, skill, speed, stamina, defense, attack)
                    await update.message.reply_text(f"Игрок {name} добавлен!")
            else:
                await update.message.reply_text("Неверный формат. Используйте: <имя> <навык> <скорость> <выносливость> <защита> <атака>")
        except ValueError as e:
            await update.message.reply_text(str(e))