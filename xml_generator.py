#!/usr/bin/env python3
"""
Script para gerar a estrutura XML para o Database Oráculo 6.1 a partir dos dados CSV baixados.
"""

import os
import csv
import json
import xml.dom.minidom
import xml.etree.ElementTree as ET
from datetime import datetime

# Configurações
INPUT_DIR = os.path.join(os.getcwd(), "data")
OUTPUT_DIR = os.path.join(os.getcwd(), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_xml_structure():
    """
    Cria a estrutura básica do XML para o Database Oráculo 6.1
    """
    # Criar elemento raiz
    root = ET.Element("DatabaseOraculo")
    root.set("version", "6.1")
    
    # Adicionar metadados
    metadata = ET.SubElement(root, "Metadata")
    creation_date = ET.SubElement(metadata, "CreationDate")
    creation_date.text = datetime.now().strftime("%Y-%m-%d")
    description = ET.SubElement(metadata, "Description")
    description.text = "Base de dados para treinamento da IA Oráculo versão 6.1"
    source = ET.SubElement(metadata, "Source")
    source.text = "OpenDota API"
    
    # Adicionar seções principais
    ET.SubElement(root, "Patches")
    ET.SubElement(root, "GameModes")
    ET.SubElement(root, "LobbyTypes")
    ET.SubElement(root, "Heroes")
    ET.SubElement(root, "Items")
    ET.SubElement(root, "Matches")
    ET.SubElement(root, "Teams")
    ET.SubElement(root, "TrainingData")
    
    return root

def add_patches_data(root):
    """
    Adiciona dados de patches ao XML
    """
    patches_element = root.find("Patches")
    
    # Tentar ler o arquivo de patches
    try:
        with open(os.path.join(INPUT_DIR, "json", "patches.json"), "r") as f:
            patches = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou for inválido, criar patches manualmente
        patches = [
            {"id": 179, "name": "7.38", "date": "2025-03-15T00:00:00Z"},
            {"id": 178, "name": "7.37", "date": "2025-01-10T00:00:00Z"},
            {"id": 177, "name": "7.36", "date": "2024-11-05T00:00:00Z"},
            {"id": 176, "name": "7.35", "date": "2024-09-20T00:00:00Z"},
            {"id": 175, "name": "7.34", "date": "2024-07-15T00:00:00Z"}
        ]
    
    # Adicionar cada patch ao XML
    for patch in patches:
        patch_element = ET.SubElement(patches_element, "Patch")
        patch_element.set("id", str(patch.get("id", "")))
        
        name = ET.SubElement(patch_element, "n")
        name.text = patch.get("name", "")
        
        date = ET.SubElement(patch_element, "Date")
        date.text = patch.get("date", "")
    
    return root

def add_game_modes_data(root):
    """
    Adiciona dados de modos de jogo ao XML
    """
    game_modes_element = root.find("GameModes")
    
    # Criar modos de jogo manualmente
    game_modes = [
        {"id": 1, "name": "All Pick", "balanced": True},
        {"id": 2, "name": "Captains Mode", "balanced": True},
        {"id": 3, "name": "Random Draft", "balanced": True},
        {"id": 4, "name": "Single Draft", "balanced": True},
        {"id": 5, "name": "All Random", "balanced": True},
        {"id": 22, "name": "Ranked All Pick", "balanced": True}
    ]
    
    # Adicionar cada modo de jogo ao XML
    for mode in game_modes:
        mode_element = ET.SubElement(game_modes_element, "GameMode")
        mode_element.set("id", str(mode.get("id", "")))
        
        name = ET.SubElement(mode_element, "n")
        name.text = mode.get("name", "")
        
        balanced = ET.SubElement(mode_element, "Balanced")
        balanced.text = str(mode.get("balanced", True)).lower()
    
    return root

def add_lobby_types_data(root):
    """
    Adiciona dados de tipos de lobby ao XML
    """
    lobby_types_element = root.find("LobbyTypes")
    
    # Criar tipos de lobby manualmente
    lobby_types = [
        {"id": 0, "name": "Normal"},
        {"id": 1, "name": "Practice"},
        {"id": 2, "name": "Tournament"},
        {"id": 5, "name": "Team Match"},
        {"id": 6, "name": "Tutorial"},
        {"id": 7, "name": "Co-op with Bots"}
    ]
    
    # Adicionar cada tipo de lobby ao XML
    for lobby in lobby_types:
        lobby_element = ET.SubElement(lobby_types_element, "LobbyType")
        lobby_element.set("id", str(lobby.get("id", "")))
        
        name = ET.SubElement(lobby_element, "n")
        name.text = lobby.get("name", "")
    
    return root

def add_heroes_data(root):
    """
    Adiciona dados de heróis ao XML
    """
    heroes_element = root.find("Heroes")
    
    # Ler dados de heróis do CSV
    heroes_data = []
    try:
        with open(os.path.join(INPUT_DIR, "csv", "heroes.csv"), "r") as f:
            reader = csv.DictReader(f)
            heroes_data = list(reader)
    except FileNotFoundError:
        print("Arquivo de heróis não encontrado")
        return root
    
    # Ler estatísticas de heróis do CSV
    hero_stats = {}
    try:
        with open(os.path.join(INPUT_DIR, "csv", "hero_stats.csv"), "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                hero_stats[row.get("id", "")] = row
    except FileNotFoundError:
        print("Arquivo de estatísticas de heróis não encontrado")
    
    # Adicionar cada herói ao XML
    for hero in heroes_data:
        hero_element = ET.SubElement(heroes_element, "Hero")
        hero_element.set("id", hero.get("id", ""))
        
        name = ET.SubElement(hero_element, "n")
        name.text = hero.get("localized_name", "")
        
        primary_attr = ET.SubElement(hero_element, "PrimaryAttribute")
        primary_attr.text = hero.get("primary_attr", "")
        
        attack_type = ET.SubElement(hero_element, "AttackType")
        attack_type.text = hero.get("attack_type", "")
        
        # Adicionar papéis
        roles_element = ET.SubElement(hero_element, "Roles")
        if "roles" in hero and hero["roles"]:
            for role in hero["roles"].split("|"):
                role_element = ET.SubElement(roles_element, "Role")
                role_element.text = role
        
        # Adicionar estatísticas
        stats_element = ET.SubElement(hero_element, "Stats")
        
        base_damage = ET.SubElement(stats_element, "BaseDamage")
        base_damage.text = "0"  # Valor padrão
        
        base_health = ET.SubElement(stats_element, "BaseHealth")
        base_health.text = hero.get("base_health", "120")
        
        base_mana = ET.SubElement(stats_element, "BaseMana")
        base_mana.text = hero.get("base_mana", "75")
        
        base_armor = ET.SubElement(stats_element, "BaseArmor")
        base_armor.text = hero.get("base_armor", "0")
        
        move_speed = ET.SubElement(stats_element, "MoveSpeed")
        move_speed.text = "300"  # Valor padrão
        
        attack_range = ET.SubElement(stats_element, "AttackRange")
        attack_range.text = "150" if hero.get("attack_type", "") == "Melee" else "600"
        
        # Adicionar habilidades (placeholder)
        abilities_element = ET.SubElement(hero_element, "Abilities")
        ability = ET.SubElement(abilities_element, "Ability")
        ability.text = "placeholder"
        
        # Adicionar tendências
        trends_element = ET.SubElement(hero_element, "Trends")
        
        # Adicionar estatísticas se disponíveis
        if hero.get("id", "") in hero_stats:
            stats = hero_stats[hero.get("id", "")]
            
            pick_rate = ET.SubElement(trends_element, "PickRate")
            pick_rate.text = stats.get("pro_pick", "0")
            
            win_rate = ET.SubElement(trends_element, "WinRate")
            win_rate.text = stats.get("pro_winrate", "0")
    
    return root

def add_items_data(root):
    """
    Adiciona dados de itens ao XML
    """
    items_element = root.find("Items")
    
    # Ler dados de itens do CSV
    items_data = []
    try:
        with open(os.path.join(INPUT_DIR, "csv", "items.csv"), "r") as f:
            reader = csv.DictReader(f)
            items_data = list(reader)
    except FileNotFoundError:
        print("Arquivo de itens não encontrado")
        return root
    
    # Adicionar cada item ao XML
    for item in items_data:
        item_element = ET.SubElement(items_element, "Item")
        item_element.set("id", item.get("id", ""))
        
        name = ET.SubElement(item_element, "n")
        name.text = item.get("localized_name", item.get("name", ""))
        
        cost = ET.SubElement(item_element, "Cost")
        cost.text = item.get("cost", "0")
        
        # Adicionar atributos
        attributes_element = ET.SubElement(item_element, "Attributes")
        
        # Adicionar alguns atributos de exemplo
        if item.get("quality", ""):
            attribute = ET.SubElement(attributes_element, "Attribute")
            attribute.set("name", "quality")
            attribute.text = item.get("quality", "")
        
        # Adicionar habilidades (placeholder)
        abilities_element = ET.SubElement(item_element, "Abilities")
        
        # Adicionar componentes (placeholder)
        components_element = ET.SubElement(item_element, "Components")
        
        # Adicionar lore se disponível
        if "notes" in item and item["notes"]:
            lore = ET.SubElement(item_element, "Lore")
            lore.text = item.get("notes", "")
    
    return root

def add_matches_data(root):
    """
    Adiciona dados de partidas ao XML
    """
    matches_element = root.find("Matches")
    
    # Ler dados de partidas do CSV
    matches_data = []
    try:
        with open(os.path.join(INPUT_DIR, "csv", "pro_matches.csv"), "r") as f:
            reader = csv.DictReader(f)
            matches_data = list(reader)
    except FileNotFoundError:
        print("Arquivo de partidas não encontrado")
        return root
    
    # Ler dados de jogadores do CSV
    players_data = {}
    try:
        with open(os.path.join(INPUT_DIR, "csv", "players_from_matches.csv"), "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                match_id = row.get("match_id", "")
                if match_id not in players_data:
                    players_data[match_id] = []
                players_data[match_id].append(row)
    except FileNotFoundError:
        print("Arquivo de jogadores não encontrado")
    
    # Adicionar cada partida ao XML
    for match in matches_data:
        match_element = ET.SubElement(matches_element, "Match")
        match_element.set("id", match.get("match_id", ""))
        
        radiant_win = ET.SubElement(match_element, "RadiantWin")
        radiant_win.text = match.get("radiant_win", "").lower()
        
        duration = ET.SubElement(match_element, "Duration")
        duration.text = match.get("duration", "0")
        
        start_time = ET.SubElement(match_element, "StartTime")
        start_time.text = match.get("start_time", "0")
        
        first_blood_time = ET.SubElement(match_element, "FirstBloodTime")
        first_blood_time.text = "0"  # Valor padrão
        
        game_mode = ET.SubElement(match_element, "GameMode")
        game_mode.text = "1"  # All Pick (valor padrão)
        
        lobby_type = ET.SubElement(match_element, "LobbyType")
        lobby_type.text = "2"  # Tournament (valor padrão)
        
        patch_version = ET.SubElement(match_element, "PatchVersion")
        patch_version.text = match.get("patch", "179")  # 7.38 (valor padrão)
        
        # Adicionar time Radiant
        radiant_team = ET.SubElement(match_element, "RadiantTeam")
        radiant_team.set("id", match.get("radiant_team_id", "0"))
        
        radiant_name = ET.SubElement(radiant_team, "n")
        radiant_name.text = match.get("radiant_name", "Unknown")
        
        radiant_score = ET.SubElement(radiant_team, "Score")
        radiant_score.text = match.get("radiant_score", "0")
        
        radiant_tower_status = ET.SubElement(radiant_team, "TowerStatus")
        radiant_tower_status.text = "0"  # Valor padrão
        
        radiant_barracks_status = ET.SubElement(radiant_team, "BarracksStatus")
        radiant_barracks_status.text = "0"  # Valor padrão
        
        # Adicionar composição do time Radiant (placeholder)
        radiant_composition = ET.SubElement(radiant_team, "Composition")
        
        radiant_engage = ET.SubElement(radiant_composition, "Engage")
        radiant_engage.text = "1"
        
        radiant_other = ET.SubElement(radiant_composition, "Other")
        radiant_other.text = "1"
        
        radiant_pickoff = ET.SubElement(radiant_composition, "Pickoff")
        radiant_pickoff.text = "1"
        
        radiant_pusher = ET.SubElement(radiant_composition, "Pusher")
        radiant_pusher.text = "1"
        
        radiant_scaler = ET.SubElement(radiant_composition, "Scaler")
        radiant_scaler.text = "1"
        
        radiant_composition_type = ET.SubElement(radiant_composition, "CompositionType")
        radiant_composition_type.text = "Balanced"
        
        # Adicionar time Dire
        dire_team = ET.SubElement(match_element, "DireTeam")
        dire_team.set("id", match.get("dire_team_id", "0"))
        
        dire_name = ET.SubElement(dire_team, "n")
        dire_name.text = match.get("dire_name", "Unknown")
        
        dire_score = ET.SubElement(dire_team, "Score")
        dire_score.text = match.get("dire_score", "0")
        
        dire_tower_status = ET.SubElement(dire_team, "TowerStatus")
        dire_tower_status.text = "0"  # Valor padrão
        
        dire_barracks_status = ET.SubElement(dire_team, "BarracksStatus")
        dire_barracks_status.text = "0"  # Valor padrão
        
        # Adicionar composição do time Dire (placeholder)
        dire_composition = ET.SubElement(dire_team, "Composition")
        
        dire_engage = ET.SubElement(dire_composition, "Engage")
        dire_engage.text = "1"
        
        dire_other = ET.SubElement(dire_composition, "Other")
        dire_other.text = "1"
        
        dire_pickoff = ET.SubElement(dire_composition, "Pickoff")
        dire_pickoff.text = "1"
        
        dire_pusher = ET.SubElement(dire_composition, "Pusher")
        dire_pusher.text = "1"
        
        dire_scaler = ET.SubElement(dire_composition, "Scaler")
        dire_scaler.text = "1"
        
        dire_composition_type = ET.SubElement(dire_composition, "CompositionType")
        dire_composition_type.text = "Balanced"
        
        # Adicionar jogadores se disponíveis
        if match.get("match_id", "") in players_data:
            players_element = ET.SubElement(match_element, "Players")
            
            for player in players_data[match.get("match_id", "")]:
                player_element = ET.SubElement(players_element, "Player")
                player_element.set("account_id", player.get("account_id", "0"))
                
                player_slot = ET.SubElement(player_element, "PlayerSlot")
                player_slot.text = player.get("player_slot", "0")
                
                hero_id = ET.SubElement(player_element, "HeroId")
                hero_id.text = player.get("hero_id", "0")
                
                kills = ET.SubElement(player_element, "Kills")
                kills.text = player.get("kills", "0")
                
                deaths = ET.SubElement(player_element, "Deaths")
                deaths.text = player.get("deaths", "0")
                
                assists = ET.SubElement(player_element, "Assists")
                assists.text = player.get("assists", "0")
                
                last_hits = ET.SubElement(player_element, "LastHits")
                last_hits.text = player.get("last_hits", "0")
                
                denies = ET.SubElement(player_element, "Denies")
                denies.text = player.get("denies", "0")
                
                gold_per_min = ET
(Content truncated due to size limit. Use line ranges to read in chunks)