#!/usr/bin/env python3
"""
Script para receber atualizações de partidas do Dota 2 a cada 30 segundos usando a OpenDota API.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configurações
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"  # Chave da OpenDota API
UPDATE_INTERVAL = 30  # Intervalo de atualização em segundos
OUTPUT_DIR = "resultados"  # Diretório para salvar os resultados
MAX_MATCHES = 3  # Número máximo de partidas para acompanhar

# Criar diretório de resultados se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def save_match_data(match_data, match_id):
    """Salvar dados da partida em um arquivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{OUTPUT_DIR}/match_{match_id}_{timestamp}.txt"
    
    with open(filename, "w") as f:
        # Cabeçalho com informações básicas
        f.write(f"=== Atualização da Partida {match_id} ===\n")
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
    print("=== Monitor de Partidas ao Vivo do Dota 2 (OpenDota API) ===")
    monitor_live_matches()
