#!/usr/bin/env python3
"""
Script combinado para receber atualizações de partidas do torneio PGL Wallachia Season 4 a cada 30 segundos
usando tanto a OpenDota API quanto a STRATZ API.
"""

import requests
import json
import time
import os
import threading
from datetime import datetime

# Configurações
OPENDOTA_API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
STRATZ_API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNWRhYmM3NGUtNzYxMS00MjNmLThlZjgtMWViYjgwMzU1YTg3IiwiU3RlYW1JZCI6IjEwNjU5NzkxMyIsIm5iZiI6MTc0NTYzOTI2NiwiZXhwIjoxNzc3MTc1MjY2LCJpYXQiOjE3NDU2MzkyNjYsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.KJgOXBLBd44AEWed8FmVP-gNQixPBlhlnA2aaYYw1Nc"
UPDATE_INTERVAL = 30  # Intervalo de atualização em segundos
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pgl_wallachia_matches")  # Diretório para salvar os resultados

# Criar diretório de resultados se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# IDs de ligas conhecidas do PGL Wallachia (podem variar)
PGL_LEAGUE_IDS = [15333, 15334, 15335]  # Possíveis IDs da liga PGL Wallachia

# Times conhecidos do PGL Wallachia Season 4
PGL_TEAMS = [
    'Team Spirit', 'Aurora', 'Tidebound', 'Natus Vincere', 'NAVI', 
    'Nigma Galaxy', 'BB Team', 'Parivision', 'Avulus'
]

# Query GraphQL para obter todas as partidas ao vivo da STRATZ API
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
    """Buscar o ID da liga PGL Wallachia Season 4 na STRATZ API."""
    url = "https://api.stratz.com/graphql"
    headers = {
        "Authorization": f"Bearer {STRATZ_API_TOKEN}",
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
                
            print("Nenhuma liga PGL Wallachia encontrada na STRATZ API.")
            return None
        else:
            print(f"Erro ao buscar liga: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro na requisição de busca de liga: {e}")
        return None

# Funções para OpenDota API
def get_opendota_live_matches():
    """Obter partidas ao vivo da OpenDota API."""
    url = f"https://api.opendota.com/api/live?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao obter partidas ao vivo da OpenDota: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro na requisição OpenDota: {e}")
        return []

def get_opendota_pro_matches():
    """Obter partidas profissionais recentes da OpenDota API."""
    url = f"https://api.opendota.com/api/proMatches?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao obter partidas profissionais da OpenDota: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro na requisição OpenDota: {e}")
        return []

def filter_opendota_pgl_matches(matches):
    """Filtrar apenas partidas do torneio PGL Wallachia Season 4 da OpenDota API."""
    pgl_matches = []
    
    for match in matches:
        # Verificar se é uma partida de liga
        league_id = match.get('league_id')
        if league_id in PGL_LEAGUE_IDS:
            pgl_matches.append(match)
            continue
            
        # Verificar nome da liga se disponível
        league_name = match.get('league_name', '').lower()
        if league_name and 'pgl' in league_name and 'wallachia' in league_name:
            pgl_matches.append(match)
            continue
            
        # Verificar times conhecidos do PGL Wallachia Season 4
        radiant_name = match.get('team_name_radiant', '').lower()
        dire_name = match.get('team_name_dire', '').lower()
        
        pgl_teams_lower = [team.lower() for team in PGL_TEAMS]
        if any(team in radiant_name for team in pgl_teams_lower) and any(team in dire_name for team in pgl_teams_lower):
            pgl_matches.append(match)
    
    return pgl_matches

# Funções para STRATZ API
def get_stratz_live_matches():
    """Obter partidas ao vivo da STRATZ API usando GraphQL."""
    url = "https://api.stratz.com/graphql"
    headers = {
        "Authorization": f"Bearer {STRATZ_API_TOKEN}",
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
                print(f"Formato de resposta STRATZ inesperado: {data}")
                return []
        else:
            print(f"Erro ao obter partidas ao vivo da STRATZ: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro na requisição STRATZ: {e}")
        return []

def filter_stratz_pgl_matches(matches, league_id=None):
    """Filtrar apenas partidas do torneio PGL Wallachia Season 4 da STRATZ API."""
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
        
        pgl_teams_lower = [team.lower() for team in PGL_TEAMS]
        if any(team in radiant_team for team in pgl_teams_lower) and any(team in dire_team for team in pgl_teams_lower):
            pgl_matches.append(match)
    
    return pgl_matches

# Funções para salvar dados
def save_opendota_match_data(match_data, match_id):
    """Salvar dados da partida da OpenDota em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_DIR, f"opendota_pgl_match_{match_id}_{timestamp}.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        # Cabeçalho com informações básicas
        f.write(f"=== Atualização da Partida PGL Wallachia Season 4 - ID: {match_id} (OpenDota) ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Tempo de jogo: {match_data.get('game_time', 'N/A')} segundos\n")
        f.write(f"Delay: {match_data.get('delay', 'N/A')} segundos\n")
        
        # Informações dos times
        radiant_name = match_data.get('team_name_radiant', 'Radiant')
        dire_name = match_data.get('team_name_dire', 'Dire')
        f.write(f"Placar: {radiant_name} {match_data.get('radiant_score', 0)} x {match_data.get('dire_score', 0)} {dire_name}\n")
        f.write(f"Vantagem Radiant: {match_data.get('radiant_lead', 'N/A')} de ouro\n\n")
        
        # Informações dos jogadores
        f.write("=== Jogadores ===\n")
        for player in match_data.get('players', []):
            team = "Radiant" if player.get('team') == 0 else "Dire"
            f.write(f"ID: {player.get('account_id')}, Herói: {player.get('hero_id')}, Time: {team}\n")
        
        # Dados completos em formato JSON
        f.write("\n=== Dados Completos ===\n")
        f.write(json.dumps(match_data, indent=2))
    
    print(f"Dados da partida PGL Wallachia {match_id} (OpenDota) salvos em {filename}")
    return filename

def save_stratz_match_data(match_data, match_id):
    """Salvar dados da partida da STRATZ em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_DIR, f"stratz_pgl_match_{match_id}_{timestamp}.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        # Cabeçalho com informações básicas
        f.write(f"=== Atualização da Partida PGL Wallachia Season 4 - ID: {match_id} (STRATZ) ===\n")
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
    
    print(f"Dados da partida PGL Wallachia {match_id} (STRATZ) salvos em {filename}")
    return filename

# Funções de monitoramento
def monitor_opendota_pgl_matches(league_id=None):
    """Monitorar partidas do torneio PGL Wallachia Season 4 na OpenDota API."""
    print(f"Iniciando monitoramento de partidas do PGL Wallachia Season 4 na OpenDota a cada {UPDATE_INTERVAL} segundos...")
    
    try:
        while True:
            # Obter todas as partidas ao vivo
            all_live_matches = get_opendota_live_matches()
            
            # Filtrar apenas partidas do PGL Wallachia Season 4
            pgl_matches = filter_opendota_pgl_matches(all_live_matches)
            
            if not pgl_matches:
                print("Nenhuma partida ao vivo do PGL Wallachia Season 4 encontrada na OpenDota.")
                
                # Tentar buscar partidas profissionais recentes como fallback
                print("Buscando partidas profissionais recentes na OpenDota...")
                pro_matches = get_opendota_pro_matches()
                pgl_pro_matches = filter_opendota_pgl_matches(pro_matches)
                
                if pgl_pro_matches:
                    print(f"Encontradas {len(pgl_pro_matches)} partidas recentes do PGL Wallachia Season 4 na OpenDota.")
                    # Usar apenas a partida mais recente
                    pgl_matches = [pgl_pro_matches[0]]
                else:
                    print("Nenhuma partida do PGL Wallachia Season 4 encontrada na OpenDota. Tentando novamente...")
                    time.sleep(UPDATE_INTERVAL)
                    continue
            
            print(f"\n=== OpenDota: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Encontradas {len(pgl_matches)} partidas do PGL Wallachia Season 4. Salvando dados...")
            
            # Salvar dados de cada partida
            for match in pgl_matches:
                match_id = match.get('match_id', 'unknown')
                filename = save_opendota_match_data(match, match_id)
            
            # Aguardar até o próximo intervalo
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoramento OpenDota interrompido.")
    except Exception as e:
        print(f"Erro durante o monitoramento OpenDota: {e}")

def monitor_stratz_pgl_matches(league_id=None):
    """Monitorar partidas do torneio PGL Wallachia Season 4 na STRATZ API."""
    print(f"Iniciando monitoramento de partidas do PGL Wallachia Season 4 na STRATZ a cada {UPDATE_INTERVAL} segundos...")
    
    try:
        while True:
            # Obter todas as partidas ao vivo
            all_matches = get_stratz_live_matches()
            
            if not all_matches:
                print("Nenhuma partida ao vivo encontrada na STRATZ. Tentando novamente...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            # Filtrar apenas partidas do PGL Wallachia Season 4
            pgl_matches = filter_stratz_pgl_matches(all_matches, league_id)
            
            if not pgl_matches:
                print("Nenhuma partida do PGL Wallachia Season 4 encontrada na STRATZ. Tentando novamente...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            print(f"\n=== STRATZ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Encontradas {len(pgl_matches)} partidas do PGL Wallachia Season 4. Salvando dados...")
            
            # Salvar dados de cada partida
            for match in pgl_matches:
                match_id = match.get('matchId', 'unknown')
                filename = save_stratz_match_data(match, match_id)
            
            # Aguardar até o próximo intervalo
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoramento STRATZ interrompido.")
    except Exception as e:
        print(f"Erro durante o monitoramento STRATZ: {e}")

def main():
    """Função principal para iniciar o monitoramento de ambas as APIs."""
    print("=== Monitor Combinado de Partidas do PGL Wallachia Season 4 ===")
    print(f"Versão para desktop - salvando resultados em: {OUTPUT_DIR}")
    
    # Buscar ID da liga PGL Wallachia Season 4
    league_id = search_pgl_wallachia_league()
    if league_id:
        print(f"Usando ID da liga PGL Wallachia: {league_id}")
    else:
        print("Nenhum ID de liga específico encontrado. Usando filtro por nome.")
    
    # Iniciar threads para monitorar ambas as APIs simultaneamente
    opendota_thread = threading.Thread(target=monitor_opendota_pgl_matches, args=(league_id,))
    stratz_thread = threading.Thread(target=monitor_stratz_pgl_matches, args=(league_id,))
    
    opendota_thread.daemon = True
    stratz_thread.daemon = True
    
    opendota_thread.start()
    stratz_thread.start()
    
    try:
        # Manter o programa em execução
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")

if __name__ == "__main__":
    main()
