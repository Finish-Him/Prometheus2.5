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

# Função para fazer requisições à API
def make_request(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    
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
        # Partidas
        ("/dota2/matches", "matches.json", {"per_page": 5}),
        ("/dota2/matches/past", "past_matches.json", {"per_page": 5}),
        ("/dota2/matches/running", "running_matches.json", {"per_page": 5}),
        ("/dota2/matches/upcoming", "upcoming_matches.json", {"per_page": 5}),
        
        # Torneios
        ("/dota2/tournaments", "tournaments.json", {"per_page": 5}),
        
        # Equipes
        ("/dota2/teams", "teams.json", {"per_page": 5}),
        
        # Jogadores
        ("/dota2/players", "players.json", {"per_page": 5}),
        
        # Heróis
        ("/dota2/heroes", "heroes.json", {"per_page": 5}),
        
        # Ligas
        ("/dota2/leagues", "leagues.json", {"per_page": 5}),
        
        # Séries
        ("/dota2/series", "series.json", {"per_page": 5})
    ]
    
    results = {}
    
    # Testar cada endpoint
    for endpoint, filename, params in endpoints:
        print(f"\nTestando endpoint: {endpoint}")
        data = make_request(endpoint, params)
        
        if data:
            save_to_json(data, filename)
            results[endpoint] = {
                "status": "success",
                "count": len(data) if isinstance(data, list) else "N/A",
                "filename": filename
            }
        else:
            results[endpoint] = {
                "status": "error",
                "count": 0,
                "filename": None
            }
    
    # Salvar resumo dos resultados
    save_to_json(results, "endpoints_summary.json")
    return results

# Função para explorar um endpoint específico com mais detalhes
def explore_endpoint_details(endpoint, filename, params=None):
    print(f"\nExplorando detalhes do endpoint: {endpoint}")
    data = make_request(endpoint, params)
    
    if data:
        save_to_json(data, filename)
        return data
    return None

# Função principal
def main():
    print("Iniciando teste de endpoints da PandaScore para Dota 2...")
    
    # Testar todos os endpoints básicos
    results = test_endpoints()
    
    # Explorar detalhes de uma partida específica (se houver partidas disponíveis)
    if results.get("/dota2/matches", {}).get("status") == "success":
        matches_data = json.load(open("matches.json", 'r', encoding='utf-8'))
        if matches_data and len(matches_data) > 0:
            match_id = matches_data[0].get("id")
            if match_id:
                explore_endpoint_details(f"/dota2/matches/{match_id}", "match_details.json")
    
    # Explorar estatísticas de jogadores
    explore_endpoint_details("/dota2/players", "players_detailed.json", {"per_page": 10, "sort": "name"})
    
    # Explorar estatísticas de heróis
    explore_endpoint_details("/dota2/heroes", "heroes_detailed.json", {"per_page": 20})
    
    print("\nTeste de endpoints concluído!")

if __name__ == "__main__":
    main()
