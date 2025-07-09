#!/usr/bin/env python3
"""
Script para filtrar dados específicos do patch 7.38 das APIs PandaScore, OpenDota e Steam.
Foco em partidas profissionais de torneios Tier 1 e 2.
"""

import os
import json
import glob
import logging
import pandas as pd
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("patch_filter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("patch_filter")

# Configurações
BASE_DIR = "collected_data"
OUTPUT_DIR = "filtered_data/patch_738"
PATCH_738_DATE = datetime.strptime("2025-02-19T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
PATCH_738_TIMESTAMP = 1708300800  # 19 de fevereiro de 2025
PATCH_738_CODE = 138  # Código do patch 7.38 na OpenDota

# Criar diretórios de saída
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/pandascore", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/opendota", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/steam", exist_ok=True)

def load_json_file(file_path):
    """Carrega um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Salva dados em um arquivo JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo {file_path}: {e}")
        return False

def filter_pandascore_data():
    """Filtra dados da PandaScore para o patch 7.38."""
    logger.info("Filtrando dados da PandaScore para o patch 7.38")
    
    # Diretórios de dados da PandaScore
    pandascore_dir = f"{BASE_DIR}/pandascore"
    
    # Verificar se o diretório existe
    if not os.path.exists(pandascore_dir):
        logger.error(f"Diretório {pandascore_dir} não encontrado")
        return
    
    # Filtrar torneios
    tournaments_file = f"{pandascore_dir}/all_tournaments.json"
    if os.path.exists(tournaments_file):
        tournaments = load_json_file(tournaments_file)
        if tournaments:
            # Filtrar torneios que começaram após o lançamento do patch 7.38
            patch_tournaments = [t for t in tournaments if t.get("begin_at") and 
                                datetime.strptime(t.get("begin_at"), "%Y-%m-%dT%H:%M:%SZ") >= PATCH_738_DATE]
            
            # Filtrar torneios Tier 1 e 2
            tier1_tier2_tournaments = [t for t in patch_tournaments if t.get("tier") in ["1", "2", 1, 2]]
            
            # Salvar torneios filtrados
            save_json_file(patch_tournaments, f"{OUTPUT_DIR}/pandascore/patch_738_tournaments.json")
            save_json_file(tier1_tier2_tournaments, f"{OUTPUT_DIR}/pandascore/tier1_tier2_tournaments.json")
            
            logger.info(f"Filtrados {len(patch_tournaments)} torneios do patch 7.38, dos quais {len(tier1_tier2_tournaments)} são Tier 1 ou 2")
    
    # Filtrar partidas
    matches_file = f"{pandascore_dir}/all_matches.json"
    if os.path.exists(matches_file):
        matches = load_json_file(matches_file)
        if matches:
            # Filtrar partidas que começaram após o lançamento do patch 7.38
            patch_matches = [m for m in matches if m.get("begin_at") and 
                            datetime.strptime(m.get("begin_at"), "%Y-%m-%dT%H:%M:%SZ") >= PATCH_738_DATE]
            
            # Salvar partidas filtradas
            save_json_file(patch_matches, f"{OUTPUT_DIR}/pandascore/patch_738_matches.json")
            
            logger.info(f"Filtradas {len(patch_matches)} partidas do patch 7.38")
    
    # Processar arquivos individuais de partidas
    matches_dir = f"{pandascore_dir}/matches"
    if os.path.exists(matches_dir):
        match_files = glob.glob(f"{matches_dir}/*.json")
        patch_matches_count = 0
        
        for match_file in match_files:
            match = load_json_file(match_file)
            if match and match.get("begin_at") and datetime.strptime(match.get("begin_at"), "%Y-%m-%dT%H:%M:%SZ") >= PATCH_738_DATE:
                # Salvar partida filtrada
                match_id = os.path.basename(match_file)
                save_json_file(match, f"{OUTPUT_DIR}/pandascore/matches/{match_id}")
                patch_matches_count += 1
        
        logger.info(f"Processados {len(match_files)} arquivos de partidas, {patch_matches_count} são do patch 7.38")
    
    # Copiar dados de equipes, jogadores e heróis (não precisam ser filtrados por patch)
    for data_type in ["teams", "players", "heroes"]:
        source_file = f"{pandascore_dir}/all_{data_type}.json"
        if os.path.exists(source_file):
            data = load_json_file(source_file)
            if data:
                save_json_file(data, f"{OUTPUT_DIR}/pandascore/all_{data_type}.json")
                logger.info(f"Copiados dados de {len(data)} {data_type}")

def filter_opendota_data():
    """Filtra dados da OpenDota para o patch 7.38."""
    logger.info("Filtrando dados da OpenDota para o patch 7.38")
    
    # Diretórios de dados da OpenDota
    opendota_dir = f"{BASE_DIR}/opendota"
    
    # Verificar se o diretório existe
    if not os.path.exists(opendota_dir):
        logger.error(f"Diretório {opendota_dir} não encontrado")
        return
    
    # Filtrar partidas profissionais
    pro_matches_file = f"{opendota_dir}/all_pro_matches.json"
    if os.path.exists(pro_matches_file):
        pro_matches = load_json_file(pro_matches_file)
        if pro_matches:
            # Filtrar partidas do patch 7.38 (OpenDota já tem o campo patch)
            patch_matches = [m for m in pro_matches if m.get("patch") == PATCH_738_CODE]
            
            # Salvar partidas filtradas
            save_json_file(patch_matches, f"{OUTPUT_DIR}/opendota/patch_738_pro_matches.json")
            
            logger.info(f"Filtradas {len(patch_matches)} partidas profissionais do patch 7.38")
    
    # Processar arquivos individuais de detalhes de partidas
    match_details_dir = f"{opendota_dir}/match_details"
    if os.path.exists(match_details_dir):
        match_files = glob.glob(f"{match_details_dir}/*.json")
        patch_matches_count = 0
        
        for match_file in match_files:
            match = load_json_file(match_file)
            if match and match.get("patch") == PATCH_738_CODE:
                # Salvar partida filtrada
                match_id = os.path.basename(match_file)
                save_json_file(match, f"{OUTPUT_DIR}/opendota/match_details/{match_id}")
                patch_matches_count += 1
        
        logger.info(f"Processados {len(match_files)} arquivos de detalhes de partidas, {patch_matches_count} são do patch 7.38")
    
    # Filtrar ligas Tier 1 e 2
    leagues_file = f"{opendota_dir}/all_leagues.json"
    if os.path.exists(leagues_file):
        leagues = load_json_file(leagues_file)
        if leagues:
            # Filtrar ligas Tier 1 e 2
            tier1_tier2_leagues = [l for l in leagues if l.get("tier") in [1, 2]]
            
            # Salvar ligas filtradas
            save_json_file(tier1_tier2_leagues, f"{OUTPUT_DIR}/opendota/tier1_tier2_leagues.json")
            
            logger.info(f"Filtradas {len(tier1_tier2_leagues)} ligas Tier 1 ou 2")
    
    # Copiar dados de jogadores profissionais e heróis (não precisam ser filtrados por patch)
    for data_type in ["pro_players", "heroes", "hero_stats"]:
        source_file = f"{opendota_dir}/all_{data_type}.json"
        if os.path.exists(source_file):
            data = load_json_file(source_file)
            if data:
                save_json_file(data, f"{OUTPUT_DIR}/opendota/all_{data_type}.json")
                logger.info(f"Copiados dados de {len(data)} {data_type}")
    
    # Copiar resultados das consultas SQL do Explorer
    explorer_dir = f"{opendota_dir}/explorer"
    if os.path.exists(explorer_dir):
        explorer_files = glob.glob(f"{explorer_dir}/*.json")
        
        for explorer_file in explorer_files:
            data = load_json_file(explorer_file)
            if data:
                file_name = os.path.basename(explorer_file)
                save_json_file(data, f"{OUTPUT_DIR}/opendota/explorer/{file_name}")
        
        logger.info(f"Copiados {len(explorer_files)} arquivos de consultas SQL do Explorer")

def filter_steam_data():
    """Filtra dados da Steam Web API para o patch 7.38."""
    logger.info("Filtrando dados da Steam Web API para o patch 7.38")
    
    # Diretórios de dados da Steam
    steam_dir = f"{BASE_DIR}/steam"
    
    # Verificar se o diretório existe
    if not os.path.exists(steam_dir):
        logger.error(f"Diretório {steam_dir} não encontrado")
        return
    
    # Filtrar histórico de partidas
    match_history_file = f"{steam_dir}/match_history.json"
    if os.path.exists(match_history_file):
        matches = load_json_file(match_history_file)
        if matches:
            # Filtrar partidas que começaram após o lançamento do patch 7.38
            patch_matches = [m for m in matches if m.get("start_time", 0) >= PATCH_738_TIMESTAMP]
            
            # Salvar partidas filtradas
            save_json_file(patch_matches, f"{OUTPUT_DIR}/steam/patch_738_matches.json")
            
            logger.info(f"Filtradas {len(patch_matches)} partidas do patch 7.38")
    
    # Processar arquivos individuais de detalhes de partidas
    matches_dir = f"{steam_dir}/matches"
    if os.path.exists(matches_dir):
        match_files = glob.glob(f"{matches_dir}/*.json")
        patch_matches_count = 0
        
        for match_file in match_files:
            match = load_json_file(match_file)
            if match and match.get("start_time", 0) >= PATCH_738_TIMESTAMP:
                # Salvar partida filtrada
                match_id = os.path.basename(match_file)
                save_json_file(match, f"{OUTPUT_DIR}/steam/matches/{match_id}")
                patch_matches_count += 1
        
        logger.info(f"Processados {len(match_files)} arquivos de detalhes de partidas, {patch_matches_count} são do patch 7.38")
    
    # Copiar dados de partidas ao vivo, equipes e heróis (não precisam ser filtrados por patch)
    for data_type, file_name in [
        ("live_games", "live_games.json"),
        ("teams", "teams_0.json"),
        ("heroes", "heroes.json"),
        ("items", "items.json")
    ]:
        source_file = f"{steam_dir}/{file_name}"
        if os.path.exists(source_file):
            data = load_json_file(source_file)
            if data:
                save_json_file(data, f"{OUTPUT_DIR}/steam/{file_name}")
                logger.info(f"Copiados dados de {data_type}")

def generate_summary():
    """Gera um resumo dos dados filtrados."""
    logger.info("Gerando resumo dos dados filtrados")
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "pandascore": {},
        "opendota": {},
        "steam": {}
    }
    
    # Resumo dos dados da PandaScore
    pandascore_files = {
        "tournaments": f"{OUTPUT_DIR}/pandascore/patch_738_tournaments.json",
        "tier1_tier2_tournaments": f"{OUTPUT_DIR}/pandascore/tier1_tier2_tournaments.json",
        "matches": f"{OUTPUT_DIR}/pandascore/patch_738_matches.json",
        "teams": f"{OUTPUT_DIR}/pandascore/all_teams.json",
        "players": f"{OUTPUT_DIR}/pandascore/all_players.json",
        "heroes": f"{OUTPUT_DIR}/pandascore/all_heroes.json"
    }
    
    for key, file_path in pandascore_files.items():
        if os.path.exists(file_path):
            data = load_json_file(file_path)
            if data:
                summary["pandascore"][key] = len(data)
    
    # Resumo dos dados da OpenDota
    opendota_files = {
        "pro_matches": f"{OUTPUT_DIR}/opendota/patch_738_pro_matches.json",
        "tier1_tier2_leagues": f"{OUTPUT_DIR}/opendota/tier1_tier2_leagues.json",
        "pro_players": f"{OUTPUT_DIR}/opendota/all_pro_players.json",
        "heroes": f"{OUTPUT_DIR}/opendota/all_heroes.json",
        "hero_stats": f"{OUTPUT_DIR}/opendota/all_hero_stats.json"
    }
    
    for key, file_path in opendota_files.items():
        if os.path.exists(file_path):
            data = load_json_file(file_path)
            if data:
                summary["opendota"][key] = len(data)
    
    # Resumo dos dados da Steam
    steam_files = {
        "matches": f"{OUTPUT_DIR}/steam/patch_738_matches.json",
        "live_games": f"{OUTPUT_DIR}/steam/live_games.json",
        "teams": f"{OUTPUT_DIR}/steam/teams_0.json",
        "heroes": f"{OUTPUT_DIR}/steam/heroes.json"
    }
    
    for key, file_path in steam_files.items():
        if os.path.exists(file_path):
            data = load_json_file(file_path)
            if data:
                summary["steam"][key] = len(data)
    
    # Salvar resumo
    save_json_file(summary, f"{OUTPUT_DIR}/filter_summary.json")
    
    logger.info(f"Resumo dos dados filtrados: {json.dumps(summary, indent=2)}")
    
    return summary

def main():
    """Função principal."""
    start_time = datetime.now()
    logger.info(f"Iniciando filtragem de dados do patch 7.38 em {start_time}")
    
    # 1. Filtrar dados da PandaScore
    filter_pandascore_data()
    
    # 2. Filtrar dados da OpenDota
    filter_opendota_data()
    
    # 3. Filtrar dados da Steam
    filter_steam_data()
    
    # 4. Gerar resumo
    summary = generate_summary()
    
    # Resumo da filtragem
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info(f"Filtragem de dados concluída em {duration.total_seconds()} segundos")
    logger.info(f"Resumo: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    main()
