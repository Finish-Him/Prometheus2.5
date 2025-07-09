#!/usr/bin/env python3
"""
Script para receber atualizações de partidas do torneio PGL Wallachia Season 4 a cada 30 segundos
usando a OpenDota API.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configurações
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"  # Chave da OpenDota API
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

def get_live_matches():
    """Obter partidas ao vivo da OpenDota API."""
    url = f"https://api.opendota.com/api/live?api_key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao obter partidas ao vivo: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return []

def get_pro_matches():
    """Obter partidas profissionais recentes da OpenDota API."""
    url = f"https://api.opendota.com/api/proMatches?api_key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao obter partidas profissionais: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return []

def filter_pgl_wallachia_matches(matches):
    """Filtrar apenas partidas do torneio PGL Wallachia Season 4."""
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

def save_match_data(match_data, match_id):
    """Salvar dados da partida em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_DIR, f"opendota_pgl_match_{match_id}_{timestamp}.txt")
    
    with open(filename, "w", encoding="utf-8") as f:
        # Cabeçalho com informações básicas
        f.write(f"=== Atualização da Partida PGL Wallachia Season 4 - ID: {match_id} ===\n")
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
    
    print(f"Dados da partida PGL Wallachia {match_id} salvos em {filename}")
    return filename

def monitor_pgl_wallachia_matches():
    """Monitorar partidas do torneio PGL Wallachia Season 4 e salvar atualizações a cada intervalo definido."""
    print(f"Iniciando monitoramento de partidas do PGL Wallachia Season 4 a cada {UPDATE_INTERVAL} segundos...")
    print(f"Os resultados serão salvos no diretório '{OUTPUT_DIR}'")
    
    try:
        while True:
            # Obter todas as partidas ao vivo
            all_live_matches = get_live_matches()
            
            # Filtrar apenas partidas do PGL Wallachia Season 4
            pgl_matches = filter_pgl_wallachia_matches(all_live_matches)
            
            if not pgl_matches:
                print("Nenhuma partida ao vivo do PGL Wallachia Season 4 encontrada.")
                
                # Tentar buscar partidas profissionais recentes como fallback
                print("Buscando partidas profissionais recentes...")
                pro_matches = get_pro_matches()
                pgl_pro_matches = filter_pgl_wallachia_matches(pro_matches)
                
                if pgl_pro_matches:
                    print(f"Encontradas {len(pgl_pro_matches)} partidas recentes do PGL Wallachia Season 4.")
                    # Usar apenas a partida mais recente
                    pgl_matches = [pgl_pro_matches[0]]
                else:
                    print("Nenhuma partida do PGL Wallachia Season 4 encontrada. Tentando novamente...")
                    time.sleep(UPDATE_INTERVAL)
                    continue
            
            print(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"Encontradas {len(pgl_matches)} partidas do PGL Wallachia Season 4. Salvando dados...")
            
            # Salvar dados de cada partida
            for match in pgl_matches:
                match_id = match.get('match_id', 'unknown')
                filename = save_match_data(match, match_id)
            
            # Aguardar até o próximo intervalo
            print(f"Próxima atualização em {UPDATE_INTERVAL} segundos...")
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro durante o monitoramento: {e}")

if __name__ == "__main__":
    print("=== Monitor de Partidas do PGL Wallachia Season 4 (OpenDota API) ===")
    print(f"Versão para desktop - salvando resultados em: {OUTPUT_DIR}")
    monitor_pgl_wallachia_matches()
