#!/usr/bin/env python3
"""
Script para receber atualizações de partidas do torneio PGL Wallachia Season 4 a cada 30 segundos
usando a STRATZ API.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configurações
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNWRhYmM3NGUtNzYxMS00MjNmLThlZjgtMWViYjgwMzU1YTg3IiwiU3RlYW1JZCI6IjEwNjU5NzkxMyIsIm5iZiI6MTc0NTYzOTI2NiwiZXhwIjoxNzc3MTc1MjY2LCJpYXQiOjE3NDU2MzkyNjYsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.KJgOXBLBd44AEWed8FmVP-gNQixPBlhlnA2aaYYw1Nc"
UPDATE_INTERVAL = 30  # Intervalo de atualização em segundos
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pgl_wallachia_matches")  # Diretório para salvar os resultados

# Criar diretório de resultados se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Query GraphQL para obter todas as partidas ao vivo
LIVE_MATCHES_QUERY = """
query LiveMatches {
  live {
    matches(request: {take: 50}) {
      matchId
      gameTime
      averageRank
      league {
        id
        displayName
        tier
        region
      }
      radiantTeam {
        name
        id
      }
      direTeam {
        name
        id
      }
      radiantScore
      direScore
      players {
        steamAccountId
        heroId
        isRadiant
        name
        networth
        kills
        deaths
        assists
      }
    }
  }
}
"""

# Query GraphQL para buscar ligas com nome específico
SEARCH_LEAGUE_QUERY = """
query SearchLeague {
  leagues(request: {name: "PGL Wallachia"}) {
    id
    displayName
    tier
    region
  }
}
"""

def search_pgl_wallachia_league():
    """Buscar o ID da liga PGL Wallachia Season 4."""
    url = "https://api.stratz.com/graphql"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": SEARCH_LEAGUE_QUERY
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "leagues" in data["data"]:
                leagues = data["data"]["leagues"]
                for league in leagues:
                    if "Season 4" in league.get("displayName", ""):
                        print(f"Encontrada liga PGL Wallachia Season 4: ID {league['id']}, Nome: {league['displayName']}")
                        return league['id']
                
                if leagues:
                    print(f"Encontradas ligas PGL Wallachia, mas nenhuma Season 4 específica. Usando a primeira: {leagues[0]['displayName']}")
                    return leagues[0]['id']
                
            print("Nenhuma liga PGL Wallachia encontrada.")
            return None
        else:
            print(f"Erro ao buscar liga: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro na requisição de busca de liga: {e}")
        return None

def get_live_matches():
    """Obter partidas ao vivo da STRATZ API usando GraphQL."""
    url = "https://api.stratz.com/graphql"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": LIVE_MATCHES_QUERY
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "live" in data["data"] and "matches" in data["data"]["live"]:
                return data["data"]["live"]["matches"]
            else:
                print(f"Formato de resposta inesperado: {data}")
                return []
        else:
            print(f"Erro ao obter partidas ao vivo: {response.status_code}")
            print(f"Resposta: {response.text}")
            return []
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return []

def filter_pgl_wallachia_matches(matches, league_id=None):
    """Filtrar apenas partidas do torneio PGL Wallachia Season 4."""
    pgl_matches = []
    
    for match in matches:
        league = match.get('league', {})
        league_name = league.get('displayName', '').lower() if league else ''
        
        # Filtrar por ID da liga se disponível
        if league_id and league.get('id') == league_id:
            pgl_matches.append(match)
            continue
            
        # Filtrar por nome da liga como fallback
        if 'pgl' in league_name and 'wallachia' in league_name:
            if 'season 4' in league_name or 'season4' in league_name or 's4' in league_name:
                pgl_matches.append(match)
                continue
                
        # Verificar times conhecidos do PGL Wallachia Season 4
        radiant_team = match.get('radiantTeam', {}).get('name', '').lower()
        dire_team = match.get('direTeam', {}).get('name', '').lower()
        
        pgl_teams = ['team spirit', 'aurora', 'tidebound', 'natus vincere', 'navi', 'nigma galaxy']
        if any(team in radiant_team for team in pgl_teams) and any(team in dire_team for team in pgl_teams):
            pgl_matches.append(match)
    
    return pgl_matches

def save_match_data(match_data, match_id):
    """Salvar dados da partida em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_DIR, f"pgl_match_{match_id}_{timestamp}.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        # Cabeçalho com informações básicas
        f.write(f"=== Atualização da Partida PGL Wallachia Season 4 - ID: {match_id} ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Tempo de jogo: {match_data.get('gameTime', 'N/A')} segundos\n")
        
        # Informações dos times
        radiant_name = match_data.get('radiantTeam', {}).get('name', 'Radiant')
        dire_name = match_data.get('direTeam', {}).get('name', 'Dire')
        f.write(f"Placar: {radiant_name} {match_data.get('radiantScore', 0)} x {match_data.get('direScore', 0)} {dire_name}\n")
        
        # Informações da liga
        league = match_data.get('league', {})
        if league and league.get('displayName'):
            f.write(f"Liga: {league.get('displayName')} (ID: {league.get('id')})\n")
        
        # Informações dos jogadores
        f.write("\n=== Jogadores ===\n")
        for player in match_data.get('players', []):
            team = "Radiant" if player.get('isRadiant') else "Dire"
            f.write(f"Nome: {player.get('name', 'Desconhecido')}, Herói: {player.get('heroId')}, Time: {team}\n")
            f.write(f"  K/D/A: {player.get('kills', 0)}/{player.get('deaths', 0)}/{player.get('assists', 0)}, Patrimônio: {player.get('networth', 0)}\n")
        
        # Dados completos em formato JSON
        f.write("\n=== Dados Completos ===\n")
        f.write(json.dumps(match_data, indent=2))
    
    print(f"Dados da partida PGL Wallachia {match_id} salvos em {filename}")
    return filename

def monitor_pgl_wallachia_matches():
    """Monitorar partidas do torneio PGL Wallachia Season 4 e salvar atualizações a cada intervalo definido."""
    print(f"Iniciando monitoramento de partidas do PGL Wallachia Season 4 a cada {UPDATE_INTERVAL} segundos...")
    print(f"Os resultados serão salvos no diretório '{OUTPUT_DIR}'")
    
    # Buscar ID da liga PGL Wallachia Season 4
    league_id = search_pgl_wallachia_league()
    if league_id:
        print(f"Usando ID da liga PGL Wallachia: {league_id}")
    else:
        print("Nenhum ID de liga específico encontrado. Usando filtro por nome.")
    
    try:
        while True:
            # Obter todas as partidas ao vivo
            all_matches = get_live_matches()
            
            if not all_matches:
                print("Nenhuma partida ao vivo encontrada. Tentando novamente...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            # Filtrar apenas partidas do PGL Wallachia Season 4
            pgl_matches = filter_pgl_wallachia_matches(all_matches, league_id)
            
            if not pgl_matches:
                print("Nenhuma partida do PGL Wallachia Season 4 encontrada. Tentando novamente...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            print(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Encontradas {len(pgl_matches)} partidas do PGL Wallachia Season 4. Salvando dados...")
            
            # Salvar dados de cada partida
            for match in pgl_matches:
                match_id = match.get('matchId', 'unknown')
                filename = save_match_data(match, match_id)
            
            # Aguardar até o próximo intervalo
            print(f"Próxima atualização em {UPDATE_INTERVAL} segundos...")
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro durante o monitoramento: {e}")

if __name__ == "__main__":
    print("=== Monitor de Partidas do PGL Wallachia Season 4 (STRATZ API) ===")
    print(f"Versão para desktop - salvando resultados em: {OUTPUT_DIR}")
    monitor_pgl_wallachia_matches()
