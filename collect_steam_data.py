import requests
import json
import os
import time
from datetime import datetime

# Configuração da API Steam
API_KEY = "116EF013E6A8537842C3436DE9FD7007"
BASE_URL = "https://api.steampowered.com"

# Função para fazer requisições à API
def make_request(interface, method, version, params=None):
    if params is None:
        params = {}
    
    # Adicionar API key aos parâmetros
    params['key'] = API_KEY
    
    url = f"{BASE_URL}/{interface}/{method}/v{version}/"
    
    print(f"Fazendo requisição para: {url}")
    print(f"Parâmetros: {params}")
    
    # Adicionar delay para evitar rate limiting
    time.sleep(1)
    
    response = requests.get(url, params=params)
    
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro: {response.text}")
        return None

# Função para salvar resultados em arquivo JSON
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em {filename}")

# Função para coletar partidas ao vivo
def collect_live_games():
    """
    Coleta informações sobre partidas ao vivo
    
    Returns:
        Dados de partidas ao vivo
    """
    print("\nColetando partidas ao vivo...")
    
    # Obter partidas ao vivo
    live_games = make_request("IDOTA2Match_570", "GetLiveLeagueGames", "1")
    
    if not live_games:
        return None
    
    print(f"Coletadas informações de partidas ao vivo")
    save_to_json(live_games, "live_games_detailed.json")
    
    return live_games

# Função para coletar histórico de partidas
def collect_match_history(limit=100):
    """
    Coleta histórico de partidas
    
    Args:
        limit: Número máximo de partidas a serem coletadas
    
    Returns:
        Dados do histórico de partidas
    """
    print(f"\nColetando até {limit} partidas do histórico...")
    
    # Calcular número de requisições necessárias (máximo de 100 partidas por requisição)
    num_requests = (limit + 99) // 100
    
    all_matches = []
    last_match_id = None
    
    for i in range(num_requests):
        params = {
            "matches_requested": min(100, limit - len(all_matches))
        }
        
        if last_match_id:
            params["start_at_match_id"] = last_match_id
        
        match_history = make_request("IDOTA2Match_570", "GetMatchHistory", "1", params)
        
        if not match_history or "result" not in match_history or "matches" not in match_history["result"]:
            break
        
        matches = match_history["result"]["matches"]
        if not matches:
            break
        
        all_matches.extend(matches)
        
        # Atualizar o último match_id para a próxima requisição
        last_match_id = matches[-1]["match_id"] - 1
        
        if len(all_matches) >= limit:
            break
    
    print(f"Coletadas {len(all_matches)} partidas do histórico")
    save_to_json({"result": {"matches": all_matches}}, "match_history_detailed.json")
    
    return all_matches

# Função para coletar detalhes de partidas específicas
def collect_match_details(match_ids):
    """
    Coleta detalhes de partidas específicas
    
    Args:
        match_ids: Lista de IDs de partidas
    
    Returns:
        Dicionário com detalhes das partidas
    """
    print(f"\nColetando detalhes de {len(match_ids)} partidas...")
    
    match_details = {}
    
    for match_id in match_ids:
        print(f"Obtendo detalhes da partida {match_id}...")
        
        details = make_request("IDOTA2Match_570", "GetMatchDetails", "1", {"match_id": match_id})
        
        if details and "result" in details:
            match_details[match_id] = details["result"]
        else:
            print(f"Falha ao obter detalhes da partida {match_id}")
    
    print(f"Coletados detalhes de {len(match_details)} partidas")
    save_to_json(match_details, "match_details_collection.json")
    
    return match_details

# Função para coletar informações de equipes
def collect_team_info(start_at_team_id=1, limit=100):
    """
    Coleta informações de equipes
    
    Args:
        start_at_team_id: ID da equipe para iniciar a coleta
        limit: Número máximo de equipes a serem coletadas
    
    Returns:
        Dados das equipes
    """
    print(f"\nColetando informações de equipes a partir do ID {start_at_team_id}...")
    
    # Obter informações de equipes
    team_info = make_request("IDOTA2Match_570", "GetTeamInfoByTeamID", "1", {
        "start_at_team_id": start_at_team_id,
        "teams_requested": limit
    })
    
    if not team_info:
        return None
    
    print(f"Coletadas informações de equipes")
    save_to_json(team_info, "team_info_detailed.json")
    
    return team_info

# Função para coletar heróis
def collect_heroes():
    """
    Coleta informações sobre heróis
    
    Returns:
        Dados dos heróis
    """
    print("\nColetando informações sobre heróis...")
    
    # Obter lista de heróis
    heroes = make_request("IEconDOTA2_570", "GetHeroes", "1", {"language": "en"})
    
    if not heroes:
        return None
    
    print(f"Coletadas informações de heróis")
    save_to_json(heroes, "heroes_detailed.json")
    
    return heroes

# Função para coletar informações de jogadores
def collect_player_info(steamids):
    """
    Coleta informações de jogadores
    
    Args:
        steamids: String com IDs Steam separados por vírgula
    
    Returns:
        Dados dos jogadores
    """
    print(f"\nColetando informações de jogadores: {steamids}...")
    
    # Obter informações de jogadores
    player_info = make_request("ISteamUser", "GetPlayerSummaries", "2", {"steamids": steamids})
    
    if not player_info:
        return None
    
    print(f"Coletadas informações de jogadores")
    save_to_json(player_info, "player_info_detailed.json")
    
    return player_info

# Função para coletar informações de torneios
def collect_tournament_info(league_id):
    """
    Coleta informações sobre torneios
    
    Args:
        league_id: ID da liga/torneio
    
    Returns:
        Dados do torneio
    """
    print(f"\nColetando informações do torneio {league_id}...")
    
    # Obter informações do torneio
    tournament_info = make_request("IEconDOTA2_570", "GetTournamentPrizePool", "1", {"leagueid": league_id})
    
    if not tournament_info:
        return None
    
    print(f"Coletadas informações do torneio {league_id}")
    save_to_json(tournament_info, "tournament_info_detailed.json")
    
    return tournament_info

# Função principal
def main():
    print("Iniciando coleta detalhada de dados da Steam Web API para Dota 2...")
    
    # Criar diretório para os dados se não existir
    os.makedirs("dados_detalhados", exist_ok=True)
    os.chdir("dados_detalhados")
    
    # Coletar partidas ao vivo
    live_games = collect_live_games()
    
    # Coletar histórico de partidas
    match_history = collect_match_history(limit=50)
    
    # Coletar detalhes de algumas partidas
    if match_history and len(match_history) > 0:
        match_ids = [match["match_id"] for match in match_history[:10]]  # Limitar a 10 partidas
        match_details = collect_match_details(match_ids)
    
    # Coletar informações de equipes
    team_info = collect_team_info(start_at_team_id=1, limit=50)
    
    # Coletar heróis
    heroes = collect_heroes()
    
    # Coletar informações de jogadores
    # Usar IDs de jogadores das partidas coletadas
    if match_history and len(match_history) > 0:
        player_ids = set()
        for match in match_history[:5]:  # Limitar a 5 partidas
            for player in match.get("players", []):
                if "account_id" in player and player["account_id"] != 4294967295:  # Ignorar jogadores anônimos
                    player_ids.add(player["account_id"] + 76561197960265728)  # Converter para steamID64
        
        if player_ids:
            steamids = ",".join(str(pid) for pid in list(player_ids)[:20])  # Limitar a 20 jogadores
            player_info = collect_player_info(steamids)
    
    # Coletar informações de torneios
    # Usar IDs de ligas das partidas ao vivo
    if live_games and "result" in live_games and "games" in live_games["result"]:
        league_ids = set()
        for game in live_games["result"]["games"]:
            if "league_id" in game:
                league_ids.add(game["league_id"])
        
        if league_ids:
            for league_id in list(league_ids)[:3]:  # Limitar a 3 torneios
                tournament_info = collect_tournament_info(league_id)
    
    # Criar resumo dos dados coletados
    summary = {
        "timestamp": datetime.now().isoformat(),
        "live_games_count": len(live_games["result"]["games"]) if live_games and "result" in live_games and "games" in live_games["result"] else 0,
        "match_history_count": len(match_history) if match_history else 0,
        "match_details_count": len(match_details) if 'match_details' in locals() else 0,
        "heroes_count": len(heroes["result"]["heroes"]) if heroes and "result" in heroes and "heroes" in heroes["result"] else 0,
        "team_info_count": len(team_info["result"]["teams"]) if team_info and "result" in team_info and "teams" in team_info["result"] else 0,
        "player_info_count": len(player_info["response"]["players"]) if 'player_info' in locals() and player_info and "response" in player_info and "players" in player_info["response"] else 0
    }
    
    save_to_json(summary, "summary.json")
    
    print("\nColeta de dados concluída!")
    print(f"Total de partidas ao vivo: {summary['live_games_count']}")
    print(f"Total de partidas do histórico: {summary['match_history_count']}")
    print(f"Total de detalhes de partidas: {summary['match_details_count']}")
    print(f"Total de heróis: {summary['heroes_count']}")
    print(f"Total de equipes: {summary['team_info_count']}")
    print(f"Total de jogadores: {summary['player_info_count']}")

if __name__ == "__main__":
    main()
