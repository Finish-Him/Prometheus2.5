#!/usr/bin/env python3
"""
Script combinado para receber atualizações de partidas do Dota 2 a cada 30 segundos
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
OUTPUT_DIR = "resultados_combinados"  # Diretório para salvar os resultados
MAX_MATCHES = 3  # Número máximo de partidas para acompanhar

# Criar diretório de resultados se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Query GraphQL para obter partidas ao vivo da STRATZ API
LIVE_MATCHES_QUERY = """
query LiveMatches {
  live {
    matches(request: {take: 5}) {
      matchId
      gameTime
      averageRank
      league {
        id
        displayName
      }
      radiantTeam {
        name
      }
      direTeam {
        name
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

def save_opendota_match_data(match_data, match_id):
    """Salvar dados da partida da OpenDota em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_DIR}/opendota_match_{match_id}_{timestamp}.txt"
    
    with open(filename, "w") as f:
        # Cabeçalho com informações básicas
        f.write(f"=== Atualização da Partida {match_id} (OpenDota API) ===\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Tempo de jogo: {match_data.get('game_time', 'N/A')} segundos\n")
        f.write(f"Delay: {match_data.get('delay', 'N/A')} segundos\n")
        f.write(f"Placar: Radiant {match_data.get('radiant_score', 0)} x {match_data.get('dire_score', 0)} Dire\n")
        f.write(f"Vantagem Radiant: {match_data.get('radiant_lead', 'N/A')} de ouro\n\n")
        
        # Informações dos jogadores
        f.write("=== Jogadores ===\n")
        for player in match_data.get('players', []):
            team = "Radiant" if player.get('team') == 0 else "Dire"
            f.write(f"ID: {player.get('account_id')}, Herói: {player.get('hero_id')}, Time: {team}\n")
        
        # Dados completos em formato JSON
        f.write("\n=== Dados Completos ===\n")
        f.write(json.dumps(match_data, indent=2))
    
    print(f"Dados da partida {match_id} (OpenDota) salvos em {filename}")
    return filename

def save_stratz_match_data(match_data, match_id):
    """Salvar dados da partida da STRATZ em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_DIR}/stratz_match_{match_id}_{timestamp}.txt"
    
    with open(filename, "w") as f:
        # Cabeçalho com informações básicas
        f.write(f"=== Atualização da Partida {match_id} (STRATZ API) ===\n")
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
    
    print(f"Dados da partida {match_id} (STRATZ) salvos em {filename}")
    return filename

def monitor_opendota_matches():
    """Monitorar partidas ao vivo da OpenDota API."""
    print(f"Iniciando monitoramento de partidas ao vivo da OpenDota a cada {UPDATE_INTERVAL} segundos...")
    
    try:
        while True:
            # Obter partidas ao vivo
            matches = get_opendota_live_matches()
            
            if not matches:
                print("Nenhuma partida ao vivo encontrada na OpenDota. Tentando novamente...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            # Limitar ao número máximo de partidas
            matches = matches[:MAX_MATCHES]
            
            print(f"\n=== OpenDota: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Encontradas {len(matches)} partidas ao vivo. Salvando dados...")
            
            # Salvar dados de cada partida
            for match in matches:
                match_id = match.get('match_id', 'unknown')
                filename = save_opendota_match_data(match, match_id)
            
            # Aguardar até o próximo intervalo
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoramento OpenDota interrompido.")
    except Exception as e:
        print(f"Erro durante o monitoramento OpenDota: {e}")

def monitor_stratz_matches():
    """Monitorar partidas ao vivo da STRATZ API."""
    print(f"Iniciando monitoramento de partidas ao vivo da STRATZ a cada {UPDATE_INTERVAL} segundos...")
    
    try:
        while True:
            # Obter partidas ao vivo
            matches = get_stratz_live_matches()
            
            if not matches:
                print("Nenhuma partida ao vivo encontrada na STRATZ. Tentando novamente...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            # Limitar ao número máximo de partidas
            matches = matches[:MAX_MATCHES]
            
            print(f"\n=== STRATZ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Encontradas {len(matches)} partidas ao vivo. Salvando dados...")
            
            # Salvar dados de cada partida
            for match in matches:
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
    print("=== Monitor Combinado de Partidas ao Vivo do Dota 2 ===")
    print(f"Os resultados serão salvos no diretório '{OUTPUT_DIR}'")
    
    # Iniciar threads para monitorar ambas as APIs simultaneamente
    opendota_thread = threading.Thread(target=monitor_opendota_matches)
    stratz_thread = threading.Thread(target=monitor_stratz_matches)
    
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
