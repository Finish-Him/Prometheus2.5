#!/usr/bin/env python3
"""
Script para receber atualizações de partidas do Dota 2 a cada 30 segundos usando a STRATZ API.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configurações
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNWRhYmM3NGUtNzYxMS00MjNmLThlZjgtMWViYjgwMzU1YTg3IiwiU3RlYW1JZCI6IjEwNjU5NzkxMyIsIm5iZiI6MTc0NTYzOTI2NiwiZXhwIjoxNzc3MTc1MjY2LCJpYXQiOjE3NDU2MzkyNjYsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.KJgOXBLBd44AEWed8FmVP-gNQixPBlhlnA2aaYYw1Nc"
UPDATE_INTERVAL = 30  # Intervalo de atualização em segundos
OUTPUT_DIR = "resultados_stratz"  # Diretório para salvar os resultados
MAX_MATCHES = 3  # Número máximo de partidas para acompanhar

# Criar diretório de resultados se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Query GraphQL para obter partidas ao vivo
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

def save_match_data(match_data, match_id):
    """Salvar dados da partida em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_DIR}/match_{match_id}_{timestamp}.txt"
    
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
    
    print(f"Dados da partida {match_id} salvos em {filename}")
    return filename

def monitor_live_matches():
    """Monitorar partidas ao vivo e salvar atualizações a cada intervalo definido."""
    print(f"Iniciando monitoramento de partidas ao vivo a cada {UPDATE_INTERVAL} segundos...")
    print(f"Os resultados serão salvos no diretório '{OUTPUT_DIR}'")
    
    try:
        while True:
            # Obter partidas ao vivo
            matches = get_live_matches()
            
            if not matches:
                print("Nenhuma partida ao vivo encontrada. Tentando novamente...")
                time.sleep(UPDATE_INTERVAL)
                continue
            
            # Limitar ao número máximo de partidas
            matches = matches[:MAX_MATCHES]
            
            print(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Encontradas {len(matches)} partidas ao vivo. Salvando dados...")
            
            # Salvar dados de cada partida
            for match in matches:
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
    print("=== Monitor de Partidas ao Vivo do Dota 2 (STRATZ API) ===")
    monitor_live_matches()
