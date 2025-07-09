import requests
import json
import os
from datetime import datetime

# Configuração da API PandaScore
API_KEY = "efEXDM0DC_oKaesfsy3RBQ4MdXvnjGEfLTZNeZEOs4W5FMjoKbc"
BASE_URL = "https://api.pandascore.co"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

# Função para fazer requisições à API com paginação
def get_all_pages(endpoint, params=None, max_pages=10):
    """
    Obtém todos os dados de um endpoint com paginação
    
    Args:
        endpoint: Endpoint da API
        params: Parâmetros adicionais
        max_pages: Número máximo de páginas a serem obtidas
    
    Returns:
        Lista com todos os dados obtidos
    """
    if params is None:
        params = {}
    
    all_data = []
    page = 1
    
    while page <= max_pages:
        page_params = params.copy()
        page_params["page"] = page
        page_params["per_page"] = 100  # Máximo permitido pela API
        
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, headers=HEADERS, params=page_params)
        
        print(f"Página {page} - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if not data or len(data) == 0:
                break
                
            all_data.extend(data)
            page += 1
        else:
            print(f"Erro: {response.text}")
            break
    
    return all_data

# Função para salvar resultados em arquivo JSON
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em {filename}")

# Função para coletar dados de partidas recentes
def collect_recent_matches(limit=200):
    """
    Coleta dados de partidas recentes de Dota 2
    
    Args:
        limit: Número máximo de partidas a serem coletadas
    
    Returns:
        Dados das partidas coletadas
    """
    print(f"\nColetando até {limit} partidas recentes de Dota 2...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    # Coletar partidas passadas
    past_matches = get_all_pages("/dota2/matches/past", 
                                {"sort": "-end_at"}, 
                                max_pages=pages_needed)
    
    # Limitar ao número desejado
    if len(past_matches) > limit:
        past_matches = past_matches[:limit]
    
    print(f"Coletadas {len(past_matches)} partidas recentes")
    save_to_json(past_matches, "recent_matches.json")
    
    return past_matches

# Função para coletar dados de partidas ao vivo e futuras
def collect_live_and_upcoming_matches():
    """
    Coleta dados de partidas ao vivo e futuras de Dota 2
    
    Returns:
        Tupla com (partidas ao vivo, partidas futuras)
    """
    print("\nColetando partidas ao vivo e futuras de Dota 2...")
    
    # Coletar partidas ao vivo
    live_matches = get_all_pages("/dota2/matches/running", {"sort": "begin_at"})
    print(f"Coletadas {len(live_matches)} partidas ao vivo")
    save_to_json(live_matches, "live_matches.json")
    
    # Coletar partidas futuras
    upcoming_matches = get_all_pages("/dota2/matches/upcoming", {"sort": "begin_at"})
    print(f"Coletadas {len(upcoming_matches)} partidas futuras")
    save_to_json(upcoming_matches, "upcoming_matches.json")
    
    return live_matches, upcoming_matches

# Função para coletar dados de torneios recentes
def collect_recent_tournaments(limit=50):
    """
    Coleta dados de torneios recentes de Dota 2
    
    Args:
        limit: Número máximo de torneios a serem coletados
    
    Returns:
        Dados dos torneios coletados
    """
    print(f"\nColetando até {limit} torneios recentes de Dota 2...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    # Coletar torneios
    tournaments = get_all_pages("/dota2/tournaments", 
                               {"sort": "-end_at"}, 
                               max_pages=pages_needed)
    
    # Limitar ao número desejado
    if len(tournaments) > limit:
        tournaments = tournaments[:limit]
    
    print(f"Coletados {len(tournaments)} torneios recentes")
    save_to_json(tournaments, "recent_tournaments.json")
    
    return tournaments

# Função para coletar dados de equipes
def collect_teams(limit=100):
    """
    Coleta dados de equipes de Dota 2
    
    Args:
        limit: Número máximo de equipes a serem coletadas
    
    Returns:
        Dados das equipes coletadas
    """
    print(f"\nColetando até {limit} equipes de Dota 2...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    # Coletar equipes
    teams = get_all_pages("/dota2/teams", 
                         {"sort": "-modified_at"}, 
                         max_pages=pages_needed)
    
    # Limitar ao número desejado
    if len(teams) > limit:
        teams = teams[:limit]
    
    print(f"Coletadas {len(teams)} equipes")
    save_to_json(teams, "teams.json")
    
    return teams

# Função para coletar dados de jogadores
def collect_players(limit=200):
    """
    Coleta dados de jogadores de Dota 2
    
    Args:
        limit: Número máximo de jogadores a serem coletados
    
    Returns:
        Dados dos jogadores coletados
    """
    print(f"\nColetando até {limit} jogadores de Dota 2...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    # Coletar jogadores
    players = get_all_pages("/dota2/players", 
                           {"sort": "-modified_at"}, 
                           max_pages=pages_needed)
    
    # Limitar ao número desejado
    if len(players) > limit:
        players = players[:limit]
    
    print(f"Coletados {len(players)} jogadores")
    save_to_json(players, "players.json")
    
    return players

# Função para coletar dados de heróis
def collect_heroes():
    """
    Coleta dados de todos os heróis de Dota 2
    
    Returns:
        Dados dos heróis coletados
    """
    print("\nColetando heróis de Dota 2...")
    
    # Coletar heróis (geralmente são poucos, então uma página deve ser suficiente)
    heroes = get_all_pages("/dota2/heroes")
    
    print(f"Coletados {len(heroes)} heróis")
    save_to_json(heroes, "heroes.json")
    
    return heroes

# Função para coletar estatísticas de partidas por herói
def collect_hero_stats(heroes):
    """
    Coleta estatísticas de partidas por herói
    
    Args:
        heroes: Lista de heróis
    
    Returns:
        Dicionário com estatísticas por herói
    """
    print("\nColetando estatísticas de partidas por herói...")
    
    hero_stats = {}
    
    # Para cada herói, coletar partidas recentes
    for hero in heroes[:5]:  # Limitando a 5 heróis para teste
        hero_id = hero["id"]
        hero_name = hero["name"]
        
        print(f"Coletando estatísticas para {hero_name}...")
        
        # Coletar partidas recentes com este herói
        matches = get_all_pages("/dota2/matches/past", 
                               {"filter[hero_id]": hero_id, "sort": "-end_at"}, 
                               max_pages=1)
        
        hero_stats[hero_id] = {
            "name": hero_name,
            "matches_count": len(matches),
            "matches": matches
        }
    
    print(f"Coletadas estatísticas para {len(hero_stats)} heróis")
    save_to_json(hero_stats, "hero_stats.json")
    
    return hero_stats

# Função principal
def main():
    print("Iniciando coleta detalhada de dados da PandaScore para Dota 2...")
    
    # Criar diretório para os dados se não existir
    os.makedirs("dados_detalhados", exist_ok=True)
    os.chdir("dados_detalhados")
    
    # Coletar dados de partidas recentes
    recent_matches = collect_recent_matches(limit=200)
    
    # Coletar dados de partidas ao vivo e futuras
    live_matches, upcoming_matches = collect_live_and_upcoming_matches()
    
    # Coletar dados de torneios recentes
    recent_tournaments = collect_recent_tournaments(limit=50)
    
    # Coletar dados de equipes
    teams = collect_teams(limit=100)
    
    # Coletar dados de jogadores
    players = collect_players(limit=200)
    
    # Coletar dados de heróis
    heroes = collect_heroes()
    
    # Coletar estatísticas de partidas por herói
    hero_stats = collect_hero_stats(heroes)
    
    # Criar resumo dos dados coletados
    summary = {
        "timestamp": datetime.now().isoformat(),
        "recent_matches_count": len(recent_matches),
        "live_matches_count": len(live_matches),
        "upcoming_matches_count": len(upcoming_matches),
        "recent_tournaments_count": len(recent_tournaments),
        "teams_count": len(teams),
        "players_count": len(players),
        "heroes_count": len(heroes),
        "hero_stats_count": len(hero_stats)
    }
    
    save_to_json(summary, "summary.json")
    
    print("\nColeta de dados concluída!")
    print(f"Total de partidas recentes: {len(recent_matches)}")
    print(f"Total de partidas ao vivo: {len(live_matches)}")
    print(f"Total de partidas futuras: {len(upcoming_matches)}")
    print(f"Total de torneios: {len(recent_tournaments)}")
    print(f"Total de equipes: {len(teams)}")
    print(f"Total de jogadores: {len(players)}")
    print(f"Total de heróis: {len(heroes)}")

if __name__ == "__main__":
    main()
