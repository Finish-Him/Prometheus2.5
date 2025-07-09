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

# Testar endpoints principais para Dota 2
def test_endpoints():
    # Lista de endpoints a serem testados
    endpoints = [
        # IDOTA2Match_570
        {
            "interface": "IDOTA2Match_570",
            "method": "GetMatchHistory",
            "version": "1",
            "params": {},
            "filename": "match_history.json"
        },
        {
            "interface": "IDOTA2Match_570",
            "method": "GetMatchDetails",
            "version": "1",
            "params": {"match_id": "8268858629"},
            "filename": "match_details.json"
        },
        {
            "interface": "IDOTA2Match_570",
            "method": "GetLiveLeagueGames",
            "version": "1",
            "params": {},
            "filename": "live_league_games.json"
        },
        {
            "interface": "IDOTA2Match_570",
            "method": "GetTeamInfoByTeamID",
            "version": "1",
            "params": {"start_at_team_id": "1"},
            "filename": "team_info.json"
        },
        {
            "interface": "IDOTA2Match_570",
            "method": "GetTournamentPlayerStats",
            "version": "1",
            "params": {"account_id": "76561198028585363", "league_id": "14268"},
            "filename": "tournament_player_stats.json"
        },
        
        # IEconDOTA2_570
        {
            "interface": "IEconDOTA2_570",
            "method": "GetHeroes",
            "version": "1",
            "params": {"language": "en"},
            "filename": "heroes.json"
        },
        {
            "interface": "IEconDOTA2_570",
            "method": "GetGameItems",
            "version": "1",
            "params": {"language": "en"},
            "filename": "game_items.json"
        },
        {
            "interface": "IEconDOTA2_570",
            "method": "GetTournamentPrizePool",
            "version": "1",
            "params": {"leagueid": "14268"},
            "filename": "tournament_prize_pool.json"
        },
        
        # ISteamUser
        {
            "interface": "ISteamUser",
            "method": "GetPlayerSummaries",
            "version": "2",
            "params": {"steamids": "76561198028585363"},
            "filename": "player_summaries.json"
        },
        
        # ISteamUserStats
        {
            "interface": "ISteamUserStats",
            "method": "GetGlobalAchievementPercentagesForApp",
            "version": "2",
            "params": {"gameid": "570"},
            "filename": "global_achievement_percentages.json"
        }
    ]
    
    results = {}
    
    # Testar cada endpoint
    for endpoint in endpoints:
        interface = endpoint["interface"]
        method = endpoint["method"]
        version = endpoint["version"]
        params = endpoint["params"]
        filename = endpoint["filename"]
        
        print(f"\nTestando endpoint: {interface}/{method}/v{version}")
        data = make_request(interface, method, version, params)
        
        if data:
            save_to_json(data, filename)
            results[f"{interface}/{method}/v{version}"] = {
                "status": "success",
                "filename": filename
            }
        else:
            results[f"{interface}/{method}/v{version}"] = {
                "status": "error",
                "filename": None
            }
    
    # Salvar resumo dos resultados
    save_to_json(results, "endpoints_summary.json")
    return results

# Função para explorar histórico de partidas
def explore_match_history(hero_id=None, limit=10):
    print(f"\nExplorando histórico de partidas{' para herói ' + str(hero_id) if hero_id else ''}...")
    
    params = {}
    if hero_id:
        params["hero_id"] = hero_id
    
    # Limitar o número de partidas
    params["matches_requested"] = limit
    
    # Obter histórico de partidas
    match_history = make_request("IDOTA2Match_570", "GetMatchHistory", "1", params)
    
    if not match_history or "result" not in match_history:
        return None
    
    # Salvar histórico de partidas
    save_to_json(match_history, "match_history_detailed.json")
    
    # Obter detalhes de algumas partidas
    if "matches" in match_history["result"]:
        match_details = []
        for match in match_history["result"]["matches"][:3]:  # Limitar a 3 partidas para teste
            match_id = match["match_id"]
            print(f"Obtendo detalhes da partida {match_id}...")
            
            details = make_request("IDOTA2Match_570", "GetMatchDetails", "1", {"match_id": match_id})
            if details:
                match_details.append(details)
        
        # Salvar detalhes das partidas
        if match_details:
            save_to_json(match_details, "match_details_collection.json")
    
    return match_history

# Função para explorar partidas ao vivo
def explore_live_games():
    print("\nExplorando partidas ao vivo...")
    
    # Obter partidas ao vivo
    live_games = make_request("IDOTA2Match_570", "GetLiveLeagueGames", "1")
    
    if not live_games:
        return None
    
    # Salvar partidas ao vivo
    save_to_json(live_games, "live_games_detailed.json")
    
    return live_games

# Função para explorar heróis
def explore_heroes():
    print("\nExplorando heróis...")
    
    # Obter lista de heróis
    heroes = make_request("IEconDOTA2_570", "GetHeroes", "1", {"language": "en"})
    
    if not heroes:
        return None
    
    # Salvar lista de heróis
    save_to_json(heroes, "heroes_detailed.json")
    
    return heroes

# Função para explorar itens do jogo
def explore_game_items():
    print("\nExplorando itens do jogo...")
    
    # Obter lista de itens
    items = make_request("IEconDOTA2_570", "GetGameItems", "1", {"language": "en"})
    
    if not items:
        return None
    
    # Salvar lista de itens
    save_to_json(items, "game_items_detailed.json")
    
    return items

# Função para explorar informações de jogadores
def explore_player_info(steamids):
    print(f"\nExplorando informações de jogadores: {steamids}...")
    
    # Obter informações de jogadores
    player_info = make_request("ISteamUser", "GetPlayerSummaries", "2", {"steamids": steamids})
    
    if not player_info:
        return None
    
    # Salvar informações de jogadores
    save_to_json(player_info, "player_info_detailed.json")
    
    return player_info

# Função principal
def main():
    print("Iniciando teste de endpoints da Steam Web API para Dota 2...")
    
    # Testar todos os endpoints básicos
    results = test_endpoints()
    
    # Explorar histórico de partidas
    match_history = explore_match_history(limit=10)
    
    # Explorar histórico de partidas para um herói específico (Anti-Mage, ID 1)
    hero_match_history = explore_match_history(hero_id=1, limit=10)
    
    # Explorar partidas ao vivo
    live_games = explore_live_games()
    
    # Explorar heróis
    heroes = explore_heroes()
    
    # Explorar itens do jogo
    items = explore_game_items()
    
    # Explorar informações de jogadores
    player_info = explore_player_info("76561198028585363,76561197960265728")
    
    print("\nTeste de endpoints concluído!")

if __name__ == "__main__":
    main()
