#!/usr/bin/env python3
"""
Script para monitorar a partida atual entre Team Spirit e Tidebound no torneio PGL Wallachia Season 4.
"""

import requests
import json
import time
import os
from datetime import datetime

# Configurações
OPENDOTA_API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
STRATZ_API_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJTdWJqZWN0IjoiNWRhYmM3NGUtNzYxMS00MjNmLThlZjgtMWViYjgwMzU1YTg3IiwiU3RlYW1J"
    "ZCI6IjEwNjU5NzkxMyIsIm5iZiI6MTc0NTYzOTI2NiwiZXhwIjoxNzc3MTc1MjY2LCJpYXQiOjE3"
    "NDU2MzkyNjYsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ."
    "KJgOXBLBd44AEWed8FmVP-gNQixPBlhlnA2aaYYw1Nc"
)

# Times alvo
TARGET_TEAMS = ['Team Spirit', 'Tidebound']

# Função para obter partidas ao vivo da OpenDota
def get_opendota_live_matches():
    url = f"https://api.opendota.com/api/live?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter partidas ao vivo da OpenDota: {e}")
        return []

# Função para filtrar partidas dos times alvo
def filter_target_teams_matches(matches):
    target_matches = []
    target_teams_lower = [team.lower() for team in TARGET_TEAMS]
    
    for match in matches:
        radiant_name = match.get("team_name_radiant", "").lower()
        dire_name = match.get("team_name_dire", "").lower()
        
        # Verificar se algum dos times alvo está jogando
        if any(team in radiant_name for team in target_teams_lower) or any(team in dire_name for team in target_teams_lower):
            target_matches.append(match)
    
    return target_matches

# Função para obter informações sobre heróis
def get_hero_info():
    url = f"https://api.opendota.com/api/constants/heroes?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter informações sobre heróis: {e}")
        return {}

# Função para obter informações sobre a partida atual
def get_match_info():
    # Obter partidas ao vivo
    live_matches = get_opendota_live_matches()
    
    # Filtrar partidas dos times alvo
    target_matches = filter_target_teams_matches(live_matches)
    
    if not target_matches:
        print("Nenhuma partida ao vivo encontrada para Team Spirit vs Tidebound")
        return None
    
    # Obter informações sobre heróis
    heroes_info = get_hero_info()
    
    # Processar a primeira partida encontrada (assumindo que é a partida Team Spirit vs Tidebound)
    match = target_matches[0]
    
    # Extrair informações relevantes
    match_info = {
        "match_id": match.get("match_id"),
        "radiant_team": match.get("team_name_radiant", "Desconhecido"),
        "dire_team": match.get("team_name_dire", "Desconhecido"),
        "radiant_score": match.get("radiant_score", 0),
        "dire_score": match.get("dire_score", 0),
        "game_time": match.get("game_time", 0),
        "players": []
    }
    
    # Processar informações dos jogadores
    for player in match.get("players", []):
        hero_id = player.get("hero_id")
        hero_name = "Desconhecido"
        
        # Obter nome do herói
        if str(hero_id) in heroes_info:
            hero_name = heroes_info[str(hero_id)].get("localized_name", "Desconhecido")
        
        player_info = {
            "account_id": player.get("account_id"),
            "hero_id": hero_id,
            "hero_name": hero_name,
            "team": "Radiant" if player.get("team") == 0 else "Dire"
        }
        
        match_info["players"].append(player_info)
    
    return match_info

# Função principal
def main():
    print("Monitorando partida Team Spirit vs Tidebound...")
    
    # Obter informações sobre a partida
    match_info = get_match_info()
    
    if match_info:
        print(f"\nPartida encontrada: {match_info['match_id']}")
        print(f"{match_info['radiant_team']} (Radiant) vs {match_info['dire_team']} (Dire)")
        print(f"Placar atual: {match_info['radiant_score']} - {match_info['dire_score']}")
        print(f"Tempo de jogo: {match_info['game_time']} segundos")
        
        print("\nJogadores:")
        for player in match_info["players"]:
            print(f"  {player['team']}: {player['hero_name']} (ID: {player['hero_id']})")
        
        # Salvar informações em um arquivo JSON
        output_file = f"team_spirit_vs_tidebound_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(match_info, f, indent=2)
        
        print(f"\nInformações salvas em {output_file}")
    else:
        print("Não foi possível obter informações sobre a partida")

if __name__ == "__main__":
    main()
