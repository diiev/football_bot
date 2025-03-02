import random

def calculate_total_score(player):
    """Рассчитывает общий рейтинг игрока."""
    return (
        player[3] +  # speed
        player[4] +  # stamina
        player[5] +  # shot_power
        player[6] +  # shot_accuracy
        player[7] +  # pass_accuracy
        player[9] +  # defense
        player[10]   # dribbling
    )

def split_teams_balanced(players, game_type, balance_threshold=50):
    """Генерация сбалансированных команд с учетом амплуа и характеристик."""
    # Фильтруем игроков, которые играют сегодня
    players = [p for p in players if p[11] == 1]
    
    # Разделяем игроков по амплуа
    defenders = [p for p in players if p[12] == "защитник"]
    midfielders = [p for p in players if p[12] == "полузащитник"]
    forwards = [p for p in players if p[12] == "нападающий"]
    
    # Определяем количество игроков каждого амплуа в зависимости от типа игры
    if game_type == "5v5":
        defenders_needed = 2
        midfielders_needed = 2
        forwards_needed = 1
    elif game_type == "6v6":
        defenders_needed = 3
        midfielders_needed = 2
        forwards_needed = 1
    elif game_type == "8v8":
        defenders_needed = 4
        midfielders_needed = 2
        forwards_needed = 2
    else:
        raise ValueError("Неверный тип игры. Допустимые значения: 5v5, 6v6, 8v8")
    
    # Проверяем, достаточно ли игроков каждого амплуа
    if len(defenders) < defenders_needed * 2 or len(midfielders) < midfielders_needed * 2 or len(forwards) < forwards_needed * 2:
        raise ValueError("Недостаточно игроков для формирования команд.")
    
    # Сортируем игроков по общему рейтингу
    defenders.sort(key=lambda x: calculate_total_score(x), reverse=True)
    midfielders.sort(key=lambda x: calculate_total_score(x), reverse=True)
    forwards.sort(key=lambda x: calculate_total_score(x), reverse=True)
    
    # Распределяем игроков по командам с учетом баланса
    team_a = []
    team_b = []
    
    # Функция для добавления игроков с балансом
    def add_players_to_teams(players_list, num_players):
        for i in range(num_players * 2):
            if i % 2 == 0:
                team_a.append(players_list[i])
            else:
                team_b.append(players_list[i])
    
    # Добавляем защитников
    add_players_to_teams(defenders, defenders_needed)
    
    # Добавляем полузащитников
    add_players_to_teams(midfielders, midfielders_needed)
    
    # Добавляем нападающих
    add_players_to_teams(forwards, forwards_needed)
    
    # Проверяем баланс команд по общему рейтингу
    total_score_a = sum(calculate_total_score(p) for p in team_a)
    total_score_b = sum(calculate_total_score(p) for p in team_b)
    
    # Если разница в рейтинге слишком большая, меняем игроков
    if abs(total_score_a - total_score_b) > balance_threshold:
        # Меняем одного защитника
        if len(defenders) > defenders_needed * 2:
            team_a[-1], team_b[-1] = team_b[-1], team_a[-1]
    
    # Выбираем вратарей случайно из защитников
    def choose_goalkeeper(team):
        defenders_in_team = [p for p in team if p[12] == "защитник"]
        if defenders_in_team:
            return random.choice(defenders_in_team)
        return None
    
    goalkeeper_a = choose_goalkeeper(team_a)
    goalkeeper_b = choose_goalkeeper(team_b)
    
    return team_a, team_b, goalkeeper_a, goalkeeper_b