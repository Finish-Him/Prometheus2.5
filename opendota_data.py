#!/usr/bin/env python3
"""
Script para baixar dados de partidas profissionais do patch atual (7.38) usando a API OpenDota
para o Database Oráculo versão 6.
"""

import requests
import json
import time
import os
import csv
from datetime import datetime

# Configurações
OPENDOTA_API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
OUTPUT_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(os.path.join(OUTPUT_DIR, "json"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "csv"), exist_ok=True)

# Constantes
PATCH_VERSION = "7.38"
TARGET_MATCH_COUNT = 500  # Número de partidas a serem baixadas

# Função para fazer requisições à API OpenDota
def opendota_request(endpoint, params=None):
    """
    Faz uma requisição à API OpenDota
    """
    base_url = "https://api.opendota.com/api"
    url = f"{base_url}/{endpoint}"
    
    # Adicionar a chave da API aos parâmetros
    if params is None:
        params = {}
    params["api_key"] = OPENDOTA_API_KEY
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para {endpoint}: {e}")
        return None

# Função para obter informações sobre patches
def get_patches():
    """
    Obtém informações sobre todos os patches do Dota 2
    """
    print("Obtendo informações sobre patches...")
    patches = opendota_request("constants/patches")
    
    if patches:
        # Salvar informações dos patches
        with open(os.path.join(OUTPUT_DIR, "json", "patches.json"), "w") as f:
            json.dump(patches, f, indent=2)
        
        # Criar CSV com informações dos patches
        with open(os.path.join(OUTPUT_DIR, "csv", "patches.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "date"])
            
            for patch in patches:
                writer.writerow([
                    patch.get("id", ""),
                    patch.get("name", ""),
                    patch.get("date", "")
                ])
        
        # Encontrar o patch atual (7.38)
        current_patch = None
        for patch in patches:
            if patch.get("name") == PATCH_VERSION:
                current_patch = patch
                break
        
        if current_patch:
            print(f"Patch atual encontrado: {current_patch['name']}")
            print(f"ID do patch: {current_patch['id']}")
            
            # Salvar informações do patch atual
            with open(os.path.join(OUTPUT_DIR, "json", "current_patch.json"), "w") as f:
                json.dump(current_patch, f, indent=2)
            
            return current_patch
        else:
            print(f"Patch {PATCH_VERSION} não encontrado")
    else:
        print("Falha ao obter informações sobre patches")
    
    return None

# Função para obter informações sobre heróis
def get_heroes():
    """
    Obtém informações sobre todos os heróis do Dota 2
    """
    print("Obtendo informações sobre heróis...")
    heroes = opendota_request("constants/heroes")
    
    if heroes:
        # Converter de dicionário para lista
        heroes_list = [{"id": int(hero_id), **hero_data} for hero_id, hero_data in heroes.items()]
        
        print(f"Total de heróis encontrados: {len(heroes_list)}")
        
        # Salvar informações dos heróis
        with open(os.path.join(OUTPUT_DIR, "json", "heroes.json"), "w") as f:
            json.dump(heroes_list, f, indent=2)
        
        # Criar CSV com informações dos heróis
        with open(os.path.join(OUTPUT_DIR, "csv", "heroes.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "name", "localized_name", "primary_attr", "attack_type", 
                "roles", "legs", "base_health", "base_mana", "base_armor"
            ])
            
            for hero in heroes_list:
                writer.writerow([
                    hero.get("id", ""),
                    hero.get("name", ""),
                    hero.get("localized_name", ""),
                    hero.get("primary_attr", ""),
                    hero.get("attack_type", ""),
                    "|".join(hero.get("roles", [])),
                    hero.get("legs", ""),
                    hero.get("base_health", ""),
                    hero.get("base_mana", ""),
                    hero.get("base_armor", "")
                ])
        
        # Obter estatísticas dos heróis
        hero_stats = opendota_request("heroStats")
        
        if hero_stats:
            # Salvar estatísticas dos heróis
            with open(os.path.join(OUTPUT_DIR, "json", "hero_stats.json"), "w") as f:
                json.dump(hero_stats, f, indent=2)
            
            # Criar CSV com estatísticas dos heróis
            with open(os.path.join(OUTPUT_DIR, "csv", "hero_stats.csv"), "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "id", "name", "localized_name", "pro_pick", "pro_win", 
                    "pro_ban", "pro_winrate", "turbo_picks", "turbo_wins"
                ])
                
                for hero in hero_stats:
                    pro_picks = hero.get("pro_pick", 0) or 0
                    pro_wins = hero.get("pro_win", 0) or 0
                    pro_winrate = (pro_wins / pro_picks * 100) if pro_picks > 0 else 0
                    
                    writer.writerow([
                        hero.get("id", ""),
                        hero.get("name", ""),
                        hero.get("localized_name", ""),
                        pro_picks,
                        pro_wins,
                        hero.get("pro_ban", 0) or 0,
                        f"{pro_winrate:.2f}%",
                        hero.get("turbo_picks", 0) or 0,
                        hero.get("turbo_wins", 0) or 0
                    ])
        
        return heroes_list
    else:
        print("Falha ao obter informações sobre heróis")
    
    return None

# Função para obter informações sobre itens
def get_items():
    """
    Obtém informações sobre todos os itens do Dota 2
    """
    print("Obtendo informações sobre itens...")
    items = opendota_request("constants/items")
    
    if items:
        # Converter de dicionário para lista
        items_list = [{"id": item_data.get("id"), "name": item_name, **item_data} for item_name, item_data in items.items()]
        
        print(f"Total de itens encontrados: {len(items_list)}")
        
        # Salvar informações dos itens
        with open(os.path.join(OUTPUT_DIR, "json", "items.json"), "w") as f:
            json.dump(items_list, f, indent=2)
        
        # Criar CSV com informações dos itens
        with open(os.path.join(OUTPUT_DIR, "csv", "items.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "name", "cost", "secret_shop", "side_shop", "recipe", 
                "localized_name", "quality", "notes", "created"
            ])
            
            for item in items_list:
                writer.writerow([
                    item.get("id", ""),
                    item.get("name", ""),
                    item.get("cost", ""),
                    item.get("secret_shop", ""),
                    item.get("side_shop", ""),
                    item.get("recipe", ""),
                    item.get("dname", ""),
                    item.get("qual", ""),
                    item.get("notes", ""),
                    item.get("created", "")
                ])
        
        return items_list
    else:
        print("Falha ao obter informações sobre itens")
    
    return None

# Função para obter partidas profissionais
def get_pro_matches(limit=100):
    """
    Obtém informações sobre partidas profissionais recentes
    """
    print(f"Obtendo informações sobre {limit} partidas profissionais recentes...")
    matches = opendota_request("proMatches", {"limit": limit})
    
    if matches:
        print(f"Total de partidas encontradas: {len(matches)}")
        
        # Salvar informações das partidas
        with open(os.path.join(OUTPUT_DIR, "json", "pro_matches.json"), "w") as f:
            json.dump(matches, f, indent=2)
        
        # Criar CSV com informações das partidas
        with open(os.path.join(OUTPUT_DIR, "csv", "pro_matches.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "match_id", "duration", "start_time", "radiant_team_id", "radiant_name",
                "dire_team_id", "dire_name", "league_id", "league_name", "series_id",
                "series_type", "radiant_score", "dire_score", "radiant_win", "patch"
            ])
            
            for match in matches:
                writer.writerow([
                    match.get("match_id", ""),
                    match.get("duration", ""),
                    match.get("start_time", ""),
                    match.get("radiant_team_id", ""),
                    match.get("radiant_name", ""),
                    match.get("dire_team_id", ""),
                    match.get("dire_name", ""),
                    match.get("leagueid", ""),
                    match.get("league_name", ""),
                    match.get("series_id", ""),
                    match.get("series_type", ""),
                    match.get("radiant_score", ""),
                    match.get("dire_score", ""),
                    match.get("radiant_win", ""),
                    match.get("patch", "")
                ])
        
        return matches
    else:
        print("Falha ao obter informações sobre partidas profissionais")
    
    return None

# Função para obter ligas profissionais
def get_leagues():
    """
    Obtém informações sobre ligas profissionais
    """
    print("Obtendo informações sobre ligas profissionais...")
    leagues = opendota_request("leagues")
    
    if leagues:
        print(f"Total de ligas encontradas: {len(leagues)}")
        
        # Salvar informações das ligas
        with open(os.path.join(OUTPUT_DIR, "json", "leagues.json"), "w") as f:
            json.dump(leagues, f, indent=2)
        
        # Criar CSV com informações das ligas
        with open(os.path.join(OUTPUT_DIR, "csv", "leagues.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "league_id", "name", "tier", "banner"
            ])
            
            for league in leagues:
                writer.writerow([
                    league.get("leagueid", ""),
                    league.get("name", ""),
                    league.get("tier", ""),
                    league.get("banner", "")
                ])
        
        # Classificar ligas por tier
        tier1_leagues = [league for league in leagues if league.get("tier") == "premium"]
        tier2_leagues = [league for league in leagues if league.get("tier") == "professional"]
        
        print(f"Ligas Tier 1 (premium): {len(tier1_leagues)}")
        print(f"Ligas Tier 2 (professional): {len(tier2_leagues)}")
        
        # Salvar informações das ligas por tier
        with open(os.path.join(OUTPUT_DIR, "json", "tier1_leagues.json"), "w") as f:
            json.dump(tier1_leagues, f, indent=2)
        
        with open(os.path.join(OUTPUT_DIR, "json", "tier2_leagues.json"), "w") as f:
            json.dump(tier2_leagues, f, indent=2)
        
        return {
            "all": leagues,
            "tier1": tier1_leagues,
            "tier2": tier2_leagues
        }
    else:
        print("Falha ao obter informações sobre ligas")
    
    return None

# Função para obter detalhes de uma partida
def get_match_details(match_id):
    """
    Obtém detalhes completos de uma partida específica
    """
    print(f"Obtendo detalhes da partida {match_id}...")
    match = opendota_request(f"matches/{match_id}")
    
    if match:
        # Salvar detalhes da partida
        with open(os.path.join(OUTPUT_DIR, "json", f"match_{match_id}.json"), "w") as f:
            json.dump(match, f, indent=2)
        
        return match
    else:
        print(f"Falha ao obter detalhes da partida {match_id}")
    
    return None

# Função para baixar detalhes de múltiplas partidas
def download_match_details(matches, patch_id=None, limit=None):
    """
    Baixa detalhes completos de múltiplas partidas
    """
    count = 0
    detailed_matches = []
    
    # Filtrar partidas pelo patch, se especificado
    if patch_id is not None:
        filtered_matches = [m for m in matches if m.get("patch") == patch_id]
        print(f"Filtradas {len(filtered_matches)} partidas do patch {patch_id} de {len(matches)} partidas")
    else:
        filtered_matches = matches
    
    # Limitar o número de partidas, se especificado
    if limit is not None and limit < len(filtered_matches):
        filtered_matches = filtered_matches[:limit]
    
    total = len(filtered_matches)
    print(f"Baixando detalhes de {total} partidas...")
    
    for i, match in enumerate(filtered_matches):
        match_id = match.get("match_id")
        print(f"[{i+1}/{total}] Baixando detalhes da partida {match_id}...")
        
        details = get_match_details(match_id)
        if details:
            detailed_matches.append(details)
            count += 1
            
            # Pequena pausa para não sobrecarregar a API
            time.sleep(1)
    
    print(f"Baixados detalhes de {count} partidas")
    
    # Salvar todos os detalhes em um único arquivo
    with open(os.path.join(OUTPUT_DIR, "json", "detailed_matches.json"), "w") as f:
        json.dump(detailed_matches, f, indent=2)
    
    return detailed_matches

# Função para processar detalhes de partidas em CSV
def process_match_details_to_csv(detailed_matches):
    """
    Processa os detalhes das partidas e cria arquivos CSV
    """
    print("Processando detalhes das partidas para CSV...")
    
    # CSV com informações básicas das partidas
    with open(os.path.join(OUTPUT_DIR, "csv", "match_details.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "match_id", "duration", "start_time", "patch", "region", "cluster",
            "radiant_win", "radiant_score", "dire_score", "league_id", "series_id",
            "series_type", "radiant_team_id", "radiant_team_name", "dire_team_id",
            "dire_team_name", "first_blood_time", "barracks_status_radiant",
            "barracks_status_dire", "tower_status_radiant", "tower_status_dire"
        ])
        
        for match in detailed_matches:
            writer.writerow([
                match.get("match_id", ""),
                match.get("duration", ""),
                match.get("start_time", ""),
                match.get("patch", ""),
                match.get("region", ""),
                match.get("cluster", ""),
                match.get("radiant_win", ""),
                match.get("radiant_score", ""),
                match.get("dire_score", ""),
                match.get("leagueid", ""),
                match.get("series_id", ""),
                match.get("series_type", ""),
                match.get("radiant_team_id", ""),
                match.get("radiant_name", ""),
                match.get("dire_team_id", ""),
                match.get("dire_name", ""),
                match.get("first_blood_time", ""),
                match.get("barracks_status_radiant", ""),
                match.get("barracks_status_dire", ""),
                match.get("tower_status_radiant", ""),
                match.get("tower_status_dire", "")
            ])
    
    # CSV com informações dos jogadores
    with open(os.path.join(OUTPUT_DIR, "csv", "players_from_matches.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "mat
(Content truncated due to size limit. Use line ranges to read in chunks)