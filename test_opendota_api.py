import requests
import json
import os
import time
from datetime import datetime

# Configuração da API OpenDota
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
BASE_URL = "https://api.opendota.com/api"

# Função para fazer requisições à API
def make_request(endpoint, params=None):
    if params is None:
        params = {}
    
    # Adicionar API key aos parâmetros se fornecida
    if API_KEY:
        params['api_key'] = API_KEY
    
    url = f"{BASE_URL}{endpoint}"
    
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

# Testar endpoints principais
def test_endpoints():
    # Lista de endpoints a serem testados
    endpoints = [
        # Partidas
        ("/matches/5000000000", "match_details.json"),  # ID de exemplo
        
        # Jogadores
        ("/players/76561198028585363", "player_details.json"),  # ID de exemplo
        ("/players/76561198028585363/wl", "player_wl.json"),
        ("/players/76561198028585363/recentMatches", "player_recent_matches.json"),
        ("/players/76561198028585363/matches", "player_matches.json", {"limit": 5}),
        ("/players/76561198028585363/heroes", "player_heroes.json", {"limit": 5}),
        ("/players/76561198028585363/peers", "player_peers.json", {"limit": 5}),
        ("/players/76561198028585363/totals", "player_totals.json"),
        ("/players/76561198028585363/counts", "player_counts.json"),
        
        # Partidas profissionais e públicas
        ("/proMatches", "pro_matches.json", {"limit": 5}),
        ("/publicMatches", "public_matches.json", {"limit": 5}),
        
        # Heróis e estatísticas
        ("/heroes", "heroes.json"),
        ("/heroStats", "hero_stats.json"),
        
        # Metadados
        ("/metadata", "metadata.json"),
        
        # Distribuições
        ("/distributions", "distributions.json"),
        
        # Rankings
        ("/rankings", "rankings.json"),
        
        # Benchmarks
        ("/benchmarks", "benchmarks.json"),
        
        # Status
        ("/status", "status.json"),
        
        # Ligas
        ("/leagues", "leagues.json")
    ]
    
    results = {}
    
    # Testar cada endpoint
    for endpoint_info in endpoints:
        if len(endpoint_info) == 2:
            endpoint, filename = endpoint_info
            params = {}
        else:
            endpoint, filename, params = endpoint_info
            
        print(f"\nTestando endpoint: {endpoint}")
        data = make_request(endpoint, params)
        
        if data:
            save_to_json(data, filename)
            results[endpoint] = {
                "status": "success",
                "filename": filename
            }
        else:
            results[endpoint] = {
                "status": "error",
                "filename": None
            }
    
    # Salvar resumo dos resultados
    save_to_json(results, "endpoints_summary.json")
    return results

# Função para explorar partidas recentes
def explore_recent_matches(limit=10):
    print(f"\nExplorando {limit} partidas profissionais recentes...")
    
    # Obter partidas profissionais recentes
    pro_matches = make_request("/proMatches", {"limit": limit})
    
    if not pro_matches:
        return None
    
    # Salvar partidas profissionais
    save_to_json(pro_matches, "recent_pro_matches.json")
    
    # Obter detalhes de cada partida
    match_details = []
    for match in pro_matches[:3]:  # Limitar a 3 partidas para teste
        match_id = match["match_id"]
        print(f"Obtendo detalhes da partida {match_id}...")
        
        details = make_request(f"/matches/{match_id}")
        if details:
            match_details.append(details)
    
    # Salvar detalhes das partidas
    if match_details:
        save_to_json(match_details, "pro_match_details.json")
    
    return pro_matches

# Função para explorar estatísticas de heróis
def explore_hero_stats():
    print("\nExplorando estatísticas de heróis...")
    
    # Obter estatísticas de heróis
    hero_stats = make_request("/heroStats")
    
    if not hero_stats:
        return None
    
    # Salvar estatísticas de heróis
    save_to_json(hero_stats, "detailed_hero_stats.json")
    
    return hero_stats

# Função para explorar estatísticas de jogadores profissionais
def explore_pro_players():
    print("\nExplorando jogadores profissionais...")
    
    # Obter lista de jogadores profissionais
    pro_players = make_request("/proPlayers")
    
    if not pro_players:
        return None
    
    # Salvar lista de jogadores profissionais
    save_to_json(pro_players, "pro_players.json")
    
    # Obter detalhes de alguns jogadores
    if pro_players and len(pro_players) > 0:
        player_details = []
        for player in pro_players[:3]:  # Limitar a 3 jogadores para teste
            account_id = player["account_id"]
            print(f"Obtendo detalhes do jogador {account_id}...")
            
            details = make_request(f"/players/{account_id}")
            if details:
                player_details.append(details)
        
        # Salvar detalhes dos jogadores
        if player_details:
            save_to_json(player_details, "pro_player_details.json")
    
    return pro_players

# Função para explorar distribuições de MMR e outros dados
def explore_distributions():
    print("\nExplorando distribuições de MMR e outros dados...")
    
    # Obter distribuições
    distributions = make_request("/distributions")
    
    if not distributions:
        return None
    
    # Salvar distribuições
    save_to_json(distributions, "detailed_distributions.json")
    
    return distributions

# Função principal
def main():
    print("Iniciando teste de endpoints da OpenDota API...")
    
    # Testar todos os endpoints básicos
    results = test_endpoints()
    
    # Explorar partidas recentes
    pro_matches = explore_recent_matches(limit=10)
    
    # Explorar estatísticas de heróis
    hero_stats = explore_hero_stats()
    
    # Explorar jogadores profissionais
    pro_players = explore_pro_players()
    
    # Explorar distribuições
    distributions = explore_distributions()
    
    print("\nTeste de endpoints concluído!")

if __name__ == "__main__":
    main()
