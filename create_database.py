#!/usr/bin/env python3
"""
Script para criar e popular uma base de dados própria com dados filtrados do patch 7.38.
Foco em partidas profissionais de torneios Tier 1 e 2 para análise preditiva de apostas.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database_creator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("database_creator")

# Configurações
FILTERED_DIR = "filtered_data/patch_738"
DATABASE_DIR = "database"
DATABASE_FILE = f"{DATABASE_DIR}/dota2_patch738_database.db"

# Criar diretório para a base de dados
os.makedirs(DATABASE_DIR, exist_ok=True)

def load_json_file(file_path):
    """Carrega um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo {file_path}: {e}")
        return None

def create_database_schema(conn):
    """Cria o esquema da base de dados."""
    logger.info("Criando esquema da base de dados")
    
    cursor = conn.cursor()
    
    # Tabela de patches
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patches (
        patch_id INTEGER PRIMARY KEY,
        patch_name TEXT NOT NULL,
        release_date TEXT NOT NULL,
        patch_notes TEXT
    )
    ''')
    
    # Tabela de heróis
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS heroes (
        hero_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        localized_name TEXT,
        primary_attr TEXT,
        attack_type TEXT,
        roles TEXT,
        base_health INTEGER,
        base_mana INTEGER,
        base_armor REAL,
        base_attack_min INTEGER,
        base_attack_max INTEGER,
        base_str INTEGER,
        base_agi INTEGER,
        base_int INTEGER,
        str_gain REAL,
        agi_gain REAL,
        int_gain REAL,
        attack_range INTEGER,
        move_speed INTEGER,
        source TEXT,
        source_id TEXT,
        json_data TEXT
    )
    ''')
    
    # Tabela de equipes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        tag TEXT,
        logo_url TEXT,
        country TEXT,
        rating REAL,
        tier INTEGER,
        source TEXT,
        source_id TEXT,
        json_data TEXT
    )
    ''')
    
    # Tabela de jogadores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        full_name TEXT,
        country TEXT,
        team_id INTEGER,
        is_active BOOLEAN,
        source TEXT,
        source_id TEXT,
        json_data TEXT,
        FOREIGN KEY (team_id) REFERENCES teams (team_id)
    )
    ''')
    
    # Tabela de torneios/ligas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tournaments (
        tournament_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        tier INTEGER,
        prize_pool INTEGER,
        start_date TEXT,
        end_date TEXT,
        region TEXT,
        source TEXT,
        source_id TEXT,
        json_data TEXT
    )
    ''')
    
    # Tabela de partidas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY,
        tournament_id INTEGER,
        start_time TEXT,
        duration INTEGER,
        radiant_team_id INTEGER,
        dire_team_id INTEGER,
        radiant_score INTEGER,
        dire_score INTEGER,
        radiant_win BOOLEAN,
        patch_id INTEGER,
        game_mode INTEGER,
        source TEXT,
        source_id TEXT,
        json_data TEXT,
        FOREIGN KEY (tournament_id) REFERENCES tournaments (tournament_id),
        FOREIGN KEY (radiant_team_id) REFERENCES teams (team_id),
        FOREIGN KEY (dire_team_id) REFERENCES teams (team_id),
        FOREIGN KEY (patch_id) REFERENCES patches (patch_id)
    )
    ''')
    
    # Tabela de picks e bans
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS picks_bans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        hero_id INTEGER,
        is_pick BOOLEAN,
        is_radiant BOOLEAN,
        order_num INTEGER,
        FOREIGN KEY (match_id) REFERENCES matches (match_id),
        FOREIGN KEY (hero_id) REFERENCES heroes (hero_id)
    )
    ''')
    
    # Tabela de desempenho de jogadores em partidas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_performances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        hero_id INTEGER,
        is_radiant BOOLEAN,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        gold_per_min INTEGER,
        xp_per_min INTEGER,
        hero_damage INTEGER,
        tower_damage INTEGER,
        hero_healing INTEGER,
        last_hits INTEGER,
        denies INTEGER,
        net_worth INTEGER,
        level INTEGER,
        json_data TEXT,
        FOREIGN KEY (match_id) REFERENCES matches (match_id),
        FOREIGN KEY (player_id) REFERENCES players (player_id),
        FOREIGN KEY (hero_id) REFERENCES heroes (hero_id)
    )
    ''')
    
    # Tabela de estatísticas de heróis por patch
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hero_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hero_id INTEGER,
        patch_id INTEGER,
        pick_count INTEGER,
        ban_count INTEGER,
        win_count INTEGER,
        win_rate REAL,
        avg_kills REAL,
        avg_deaths REAL,
        avg_assists REAL,
        avg_gpm REAL,
        avg_xpm REAL,
        FOREIGN KEY (hero_id) REFERENCES heroes (hero_id),
        FOREIGN KEY (patch_id) REFERENCES patches (patch_id)
    )
    ''')
    
    # Tabela de estatísticas de equipes por patch
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER,
        patch_id INTEGER,
        matches_played INTEGER,
        wins INTEGER,
        losses INTEGER,
        win_rate REAL,
        avg_match_duration REAL,
        FOREIGN KEY (team_id) REFERENCES teams (team_id),
        FOREIGN KEY (patch_id) REFERENCES patches (patch_id)
    )
    ''')
    
    # Tabela de metadados da base de dados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    conn.commit()
    logger.info("Esquema da base de dados criado com sucesso")

def insert_patch_data(conn):
    """Insere dados do patch 7.38."""
    logger.info("Inserindo dados do patch 7.38")
    
    cursor = conn.cursor()
    
    # Inserir dados do patch 7.38
    cursor.execute('''
    INSERT OR REPLACE INTO patches (patch_id, patch_name, release_date, patch_notes)
    VALUES (?, ?, ?, ?)
    ''', (
        138,  # ID do patch 7.38 na OpenDota
        "7.38",
        "2025-02-19",
        "Patch 7.38 para Dota 2, lançado em 19 de fevereiro de 2025."
    ))
    
    # Inserir metadados
    cursor.execute('''
    INSERT OR REPLACE INTO metadata (key, value)
    VALUES (?, ?)
    ''', (
        "current_patch",
        "7.38"
    ))
    
    cursor.execute('''
    INSERT OR REPLACE INTO metadata (key, value)
    VALUES (?, ?)
    ''', (
        "database_created",
        datetime.now().isoformat()
    ))
    
    conn.commit()
    logger.info("Dados do patch 7.38 inseridos com sucesso")

def import_heroes_data(conn):
    """Importa dados de heróis para a base de dados."""
    logger.info("Importando dados de heróis")
    
    cursor = conn.cursor()
    
    # Tentar carregar dados de heróis da OpenDota (mais completos)
    heroes_file = f"{FILTERED_DIR}/opendota/all_heroes.json"
    hero_stats_file = f"{FILTERED_DIR}/opendota/all_hero_stats.json"
    
    if os.path.exists(heroes_file):
        heroes = load_json_file(heroes_file)
        hero_stats = load_json_file(hero_stats_file) if os.path.exists(hero_stats_file) else []
        
        if heroes:
            for hero in heroes:
                # Encontrar estatísticas correspondentes
                stats = next((s for s in hero_stats if s.get("id") == hero.get("id")), {})
                
                cursor.execute('''
                INSERT OR REPLACE INTO heroes (
                    hero_id, name, localized_name, primary_attr, attack_type, roles,
                    base_health, base_mana, base_armor, base_attack_min, base_attack_max,
                    base_str, base_agi, base_int, str_gain, agi_gain, int_gain,
                    attack_range, move_speed, source, source_id, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    hero.get("id"),
                    hero.get("name"),
                    hero.get("localized_name"),
                    hero.get("primary_attr"),
                    stats.get("attack_type"),
                    json.dumps(hero.get("roles", [])),
                    stats.get("base_health"),
                    stats.get("base_mana"),
                    stats.get("base_armor"),
                    stats.get("base_attack_min"),
                    stats.get("base_attack_max"),
                    stats.get("base_str"),
                    stats.get("base_agi"),
                    stats.get("base_int"),
                    stats.get("str_gain"),
                    stats.get("agi_gain"),
                    stats.get("int_gain"),
                    stats.get("attack_range"),
                    stats.get("move_speed"),
                    "opendota",
                    str(hero.get("id")),
                    json.dumps(hero)
                ))
            
            conn.commit()
            logger.info(f"Importados {len(heroes)} heróis da OpenDota")
    
    # Se não houver dados da OpenDota, tentar da PandaScore
    else:
        heroes_file = f"{FILTERED_DIR}/pandascore/all_heroes.json"
        
        if os.path.exists(heroes_file):
            heroes = load_json_file(heroes_file)
            
            if heroes:
                for hero in heroes:
                    cursor.execute('''
                    INSERT OR REPLACE INTO heroes (
                        hero_id, name, localized_name, source, source_id, json_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        hero.get("id"),
                        hero.get("name"),
                        hero.get("name"),
                        "pandascore",
                        str(hero.get("id")),
                        json.dumps(hero)
                    ))
                
                conn.commit()
                logger.info(f"Importados {len(heroes)} heróis da PandaScore")
    
    # Se ainda não houver dados, tentar da Steam
    heroes_count = cursor.execute("SELECT COUNT(*) FROM heroes").fetchone()[0]
    
    if heroes_count == 0:
        heroes_file = f"{FILTERED_DIR}/steam/heroes.json"
        
        if os.path.exists(heroes_file):
            heroes_data = load_json_file(heroes_file)
            
            if heroes_data and "heroes" in heroes_data:
                heroes = heroes_data["heroes"]
                
                for hero in heroes:
                    cursor.execute('''
                    INSERT OR REPLACE INTO heroes (
                        hero_id, name, localized_name, source, source_id, json_data
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        hero.get("id"),
                        hero.get("name"),
                        hero.get("localized_name"),
                        "steam",
                        str(hero.get("id")),
                        json.dumps(hero)
                    ))
                
                conn.commit()
                logger.info(f"Importados {len(heroes)} heróis da Steam")

def import_teams_data(conn):
    """Importa dados de equipes para a base de dados."""
    logger.info("Importando dados de equipes")
    
    cursor = conn.cursor()
    
    # Tentar carregar dados de equipes da PandaScore (mais completos)
    teams_file = f"{FILTERED_DIR}/pandascore/all_teams.json"
    
    if os.path.exists(teams_file):
        teams = load_json_file(teams_file)
        
        if teams:
            for team in teams:
                cursor.execute('''
                INSERT OR REPLACE INTO teams (
                    team_id, name, tag, logo_url, country, rating, tier, source, source_id, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    team.get("id"),
                    team.get("name"),
                    team.get("acronym"),
                    team.get("image_url"),
                    team.get("location"),
                    None,  # rating não disponível na PandaScore
                    None,  # tier não disponível na PandaScore
                    "pandascore",
                    str(team.get("id")),
                    json.dumps(team)
                ))
            
            conn.commit()
            logger.info(f"Importados {len(teams)} equipes da PandaScore")
    
    # Se não houver dados da PandaScore, tentar da Steam
    teams_count = cursor.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
    
    if teams_count == 0:
        teams_file = f"{FILTERED_DIR}/steam/teams_0.json"
        
        if os.path.exists(teams_file):
            teams = load_json_file(teams_file)
            
            if teams:
                for team in teams:
                    cursor.execute('''
                    INSERT OR REPLACE INTO teams (
                        team_id, name, tag, logo_url, source, source_id, json_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        team.get("team_id"),
                        team.get("name"),
                        team.get("tag"),
                        None,  # logo_url não disponível na Steam
                        "steam",
                        str(team.get("team_id")),
                        json.dumps(team)
                    ))
                
                conn.commit()
                logger.info(f"Importados {len(teams)} equipes da Steam")

def import_players_data(conn):
    """Importa dados de jogadores para a base de dados."""
    logger.info("Importando dados de jogadores")
    
    cursor = conn.cursor()
    
    # Tentar carregar dados de jogadores da PandaScore (mais completos)
    players_file = f"{FILTERED_DIR}/pandascore/all_players.json"
    
    if os.path.exists(players_file):
        players = load_json_file(players_file)
        
        if players:
            for player in players:
                # Obter team_id se disponível
                team_id = None
                if player.get("current_team") and player["current_team"].get("id"):
                    team_id = player["current_team"]["id"]
                
                # Tratar nomes para evitar erro de NoneType
                first_name = player.get("first_name", "") or ""
                last_name = player.get("last_name", "") or ""
                full_name = (first_name + " " + last_name).strip()
                
                cursor.execute('''
                INSERT OR REPLACE INTO players (
                    player_id, name, full_name, country, team_id, is_active, source, source_id, json_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player.get("id"),
                    player.get("name"),
                    full_name,
                    player.get("nationality"),
                    team_id,
                    True,  # assumir que jogadores atuais estão ativos
                    "pandascore",
                   
(Content truncated due to size limit. Use line ranges to read in chunks)