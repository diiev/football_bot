import random

def validate_player_data(skill, speed, stamina, defense, attack):
    """Проверяет, что характеристики в диапазоне от 1 до 10."""
    if not all(1 <= value <= 10 for value in [skill, speed, stamina, defense, attack]):
        raise ValueError("Все характеристики должны быть от 1 до 10.")
    return True


def calculate_total_score(player):
    """Рассчитывает общий рейтинг игрока."""
    return player[3] + player[4] + player[5] + player[6] + player[7]

def split_teams_balanced(players):
    """Случайно, но сбалансировано."""
    players_with_total = [
        {
            "name": p[2], 
            "skill": p[3], 
            "speed": p[4], 
            "stamina": p[5], 
            "defense": p[6], 
            "attack": p[7], 
            "total": calculate_total_score(p)
        } 
        for p in players
    ]
    
    # Сортируем игроков по общему рейтингу
    players_with_total.sort(key=lambda x: x['total'], reverse=True)
    
    # Разделяем на две команды, чередуя сильных и слабых
    team_a = []
    team_b = []
    for i, player in enumerate(players_with_total):
        if i % 2 == 0:
            team_a.append(player)
        else:
            team_b.append(player)
    
    # Перемешиваем команды для случайности
    random.shuffle(team_a)
    random.shuffle(team_b)
    
    return team_a, team_b

def split_teams_random(players):
    """Полностью случайно."""
    players_with_total = [
        {
            "name": p[2], 
            "skill": p[3], 
            "speed": p[4], 
            "stamina": p[5], 
            "defense": p[6], 
            "attack": p[7], 
            "total": calculate_total_score(p)
        } 
        for p in players
    ]
    
    # Перемешиваем всех игроков
    random.shuffle(players_with_total)
    
    # Разделяем на две команды
    team_a = players_with_total[:len(players_with_total)//2]
    team_b = players_with_total[len(players_with_total)//2:]
    
    return team_a, team_b

def split_teams_optimal(players):
    """Сбалансировано по силе (оптимальное распределение)."""
    players_with_total = [
        {
            "name": p[2], 
            "skill": p[3], 
            "speed": p[4], 
            "stamina": p[5], 
            "defense": p[6], 
            "attack": p[7], 
            "total": calculate_total_score(p)
        } 
        for p in players
    ]
    
    # Сортируем игроков по общему рейтингу
    players_with_total.sort(key=lambda x: x['total'], reverse=True)
    
    # Разделяем на две команды, чередуя сильных и слабых
    team_a = []
    team_b = []
    for i, player in enumerate(players_with_total):
        if i % 2 == 0:
            team_a.append(player)
        else:
            team_b.append(player)
    
    return team_a, team_b