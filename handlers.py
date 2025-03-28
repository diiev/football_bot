from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from database import get_players, add_player, delete_player, update_player, set_player_playing, get_playing_players
from utils import calculate_total_score, split_teams_balanced, validate_player_data

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

async def add_player_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Добавить игрока'."""
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Введите данные игрока в формате:\n"
        "<имя> <скорость> <выносливость> <сила удара> <точность удара> <точность пасов> <командная игра (да/нет)> <защита> <дриблинг> <амплуа (защитник/полузащитник/нападающий)>\n"
        "Пример: Игрок1 80 70 85 90 75 да 60 80 нападающий",
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
            f"Скорость: {player[3]}\n"
            f"Выносливость: {player[4]}\n"
            f"Сила удара: {player[5]}\n"
            f"Точность удара: {player[6]}\n"
            f"Точность пасов: {player[7]}\n"
            f"Командная игра: {player[8]}\n"
            f"Защита: {player[9]}\n"
            f"Дриблинг: {player[10]}\n"
            f"Амплуа: {player[11]}\n"
            f"Играет сегодня: {'Да' if player[12] else 'Нет'}\n"
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
    
    if update.message:
        user_id = update.message.from_user.id  # Если это обычное сообщение
    elif update.callback_query:
        user_id = update.callback_query.from_user.id  # Если это callback-запрос
    else:
        return  # Неизвестный тип update, игнорируем

    players = get_players(user_id)
    if not players:
        await update.message.reply_text("Игроков пока нет. Добавьте их с помощью 'Добавить игрока'.")
        return
    
    # Создаем inline-кнопки для каждого игрока
    keyboard = []
    for player in players:
        player_name = player[2]
        is_playing = "✅" if player[12] else "❌"
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
    new_status = 0 if player[12] else 1
    set_player_playing(user_id, player_name, new_status)
    
    # Обновляем сообщение
    await mark_players_handler(update, context)

BALANCE_THRESHOLD = range(1)  # Шаг диалога

async def handle_generate_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинаем процесс генерации команд, запрашивая порог баланса."""
    user_id = update.message.from_user.id
    context.user_data["user_id"] = user_id  # Сохраняем user_id
    context.user_data["game_type"] = update.message.text  # Сохраняем тип игры

    await update.message.reply_text("Введите порог баланса (максимальная разница в рейтинге, например, 50):")
    return BALANCE_THRESHOLD  # Переходим на следующий шаг

async def handle_balance_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатываем ввод порога баланса и создаем команды."""
    try:
        balance_threshold = int(update.message.text)
        context.user_data["balance_threshold"] = balance_threshold  # Сохраняем порог

        user_id = context.user_data["user_id"]
        game_type = context.user_data["game_type"]

        players = get_players(user_id)
        team_a, team_b, goalkeeper_a, goalkeeper_b = split_teams_balanced(players, game_type, balance_threshold)

        def format_team(team, goalkeeper):
            team_info = "\n".join(
                f"{player[2]} ({player[12]}) - Рейтинг: {calculate_total_score(player)}"
                for player in team
            )
            if goalkeeper:
                team_info += f"\nВратарь: {goalkeeper[2]} (защитник) - Рейтинг: {calculate_total_score(goalkeeper)}"
            return team_info

        team_a_message = format_team(team_a, goalkeeper_a)
        team_b_message = format_team(team_b, goalkeeper_b)

        await update.message.reply_text(
            f"Команда A:\n{team_a_message}\n\nКоманда B:\n{team_b_message}"
        )
        return ConversationHandler.END  # Завершаем диалог ✅

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return BALANCE_THRESHOLD  # Ожидаем ввод снова

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")
        return ConversationHandler.END  # Закрываем диалог при ошибке


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отмены диалога."""
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

async def delete_player_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды 'Удалить игрока'."""
    global player_to_delete
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Введите имя игрока, которого хотите удалить:",
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
        "<имя> <скорость> <выносливость> <сила удара> <точность удара> <точность пасов> <командная игра (да/нет)> <защита> <дриблинг> <амплуа (защитник/полузащитник/нападающий)>\n"
        "Пример: Игрок1 80 70 85 90 75 да 60 80 нападающий",
        reply_markup=reply_markup
    )

async def handle_edit_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик редактирования игрока."""
    user_id = update.message.from_user.id
    args = update.message.text.split()
    
    if len(args) != 10:
        await update.message.reply_text("Неверный формат. Используйте: <имя> <скорость> <выносливость> <сила удара> <точность удара> <точность пасов> <командная игра (да/нет)> <защита> <дриблинг> <амплуа (защитник/полузащитник/нападающий)>")
        return
    
    name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position = args
    try:
        speed, stamina, shot_power, shot_accuracy, pass_accuracy, defense, dribbling = map(int, [speed, stamina, shot_power, shot_accuracy, pass_accuracy, defense, dribbling])
        validate_player_data(speed, stamina, shot_power, shot_accuracy, pass_accuracy, defense, dribbling)
        
        update_player(user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position)
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
        f"Скорость: {player[3]}\n"
        f"Выносливость: {player[4]}\n"
        f"Сила удара: {player[5]}\n"
        f"Точность удара: {player[6]}\n"
        f"Точность пасов: {player[7]}\n"
        f"Командная игра: {player[8]}\n"
        f"Защита: {player[9]}\n"
        f"Дриблинг: {player[10]}\n"
        f"Амплуа: {player[11]}\n"
        f"Играет сегодня: {'Да' if player[12] else 'Нет'}\n"
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
        await handle_generate_teams(update, context)
    elif text == "Удалить игрока":
        await delete_player_handler(update, context)
    elif text == "Редактировать игрока":
        await edit_player_handler(update, context)
    elif text == "Найти игрока":
        await find_player_handler(update, context)
    elif text == "Отметить игроков":
        await mark_players_handler(update, context)
    elif text in ["5v5", "6v6", "8v8"]:
        await handle_generate_teams(update, context)
    elif text == "Назад":
        await start(update, context)
    else:
        # Если сообщение не является командой, пробуем добавить или редактировать игрока
        try:
            args = text.split()
            if len(args) == 10:
                name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position = args
                speed, stamina, shot_power, shot_accuracy, pass_accuracy, defense, dribbling = map(int, [speed, stamina, shot_power, shot_accuracy, pass_accuracy, defense, dribbling])
                validate_player_data(speed, stamina, shot_power, shot_accuracy, pass_accuracy, defense, dribbling)
                
                user_id = update.message.from_user.id
                # Проверяем, существует ли игрок
                players = get_players(user_id)
                player_names = [p[2] for p in players]
                if name in player_names:
                    update_player(user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position)
                    await update.message.reply_text(f"Игрок {name} обновлен!")
                else:
                    add_player(user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, dribbling, position)
                    await update.message.reply_text(f"Игрок {name} добавлен!")
            else:
                await update.message.reply_text("Неверный формат. Используйте: <имя> <скорость> <выносливость> <сила удара> <точность удара> <точность пасов> <командная игра (да/нет)> <защита> <дриблинг> <амплуа (защитник/полузащитник/нападающий)>")
        except ValueError as e:
            await update.message.reply_text(str(e))