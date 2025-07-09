#!/usr/bin/env python3
"""
Script para coleta de dados da API OpenDota para Dota 2.
Foco em partidas profissionais do patch 7.38 em torneios Tier 1 e 2.
"""

import requests
import json
import os
import time
from datetime import datetime
import logging
import urllib.parse

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("opendota_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("opendota_collector")

# Configurações
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
BASE_URL = "https://api.opendota.com/api"
PATCH_738_CODE = 138  # Código do patch 7.38 na OpenDota
PATCH_738_TIMESTAMP = 1708300800  # 19 de fevereiro de 2025
OUTPUT_DIR = "collected_data/opendota"

# Criar diretórios de saída
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/pro_matches", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/match_details", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/leagues", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/players", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/heroes", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/explorer", exist_ok=True)

def make_request(endpoint, params=None):
    """Faz uma requisição à API OpenDota com tratamento de rate limit."""
    if params is None:
        params = {}
    
    # Adicionar API key se fornecida
    if API_KEY:
        params["api_key"] = API_KEY
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, params=params)
        
        # Verificar rate limit (60 requisições por minuto no plano gratuito)
        if response.status_code == 429:
            logger.warning("Rate limit atingido. Aguardando 60 segundos.")
            time.sleep(60)
            return make_request(endpoint, params)
        
        # Verificar outros erros
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        return None

def get_pro_matches(limit=1000):
    """Coleta partidas profissionais recentes."""
    logger.info(f"Coletando até {limit} partidas profissionais recentes")
    
    matches = []
    last_match_id = None
    
    while len(matches) < limit:
        params = {}
        if last_match_id:
            params["less_than_match_id"] = last_match_id
        
        result = make_request("/proMatches", params)
        
        if not result or len(result) == 0:
            break
        
        # Filtrar partidas após o lançamento do patch 7.38
        patch_matches = [m for m in result if int(m.get("start_time", 0)) >= PATCH_738_TIMESTAMP]
        
        if patch_matches:
            matches.extend(patch_matches)
            logger.info(f"Coletadas {len(patch_matches)} partidas do patch 7.38 (total: {len(matches)})")
            
            # Salvar cada partida individualmente
            for match in patch_matches:
                match_id = match.get("match_id")
                with open(f"{OUTPUT_DIR}/pro_matches/{match_id}.json", "w") as f:
                    json.dump(match, f, indent=2)
            
            last_match_id = result[-1]["match_id"]
        else:
            # Se não há mais partidas do patch 7.38, interromper
            logger.info("Não há mais partidas do patch 7.38")
            break
        
        # Verificar se atingimos o limite
        if len(matches) >= limit:
            break
        
        time.sleep(1)  # Respeitar rate limit
    
    # Salvar todas as partidas em um único arquivo
    with open(f"{OUTPUT_DIR}/all_pro_matches.json", "w") as f:
        json.dump(matches, f, indent=2)
    
    logger.info(f"Total de {len(matches)} partidas profissionais do patch 7.38 coletadas")
    return matches

def get_match_details(match_ids):
    """Coleta detalhes completos de partidas específicas."""
    logger.info(f"Coletando detalhes de {len(match_ids)} partidas")
    
    match_details = []
    
    for match_id in match_ids:
        result = make_request(f"/matches/{match_id}")
        
        if not result:
            logger.warning(f"Falha ao coletar detalhes da partida {match_id}")
            continue
        
        # Verificar se é do patch 7.38
        if result.get("patch") == PATCH_738_CODE:
            match_details.append(result)
            
            # Salvar detalhes da partida
            with open(f"{OUTPUT_DIR}/match_details/{match_id}.json", "w") as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Detalhes da partida {match_id} coletados (patch: {result.get('patch')})")
        else:
            logger.info(f"Partida {match_id} não é do patch 7.38 (patch: {result.get('patch')})")
        
        time.sleep(1)  # Respeitar rate limit
    
    logger.info(f"Detalhes de {len(match_details)} partidas do patch 7.38 coletados")
    return match_details

def get_leagues():
    """Coleta informações sobre ligas/torneios."""
    logger.info("Coletando informações sobre ligas/torneios")
    
    result = make_request("/leagues")
    
    if not result:
        logger.error("Falha ao coletar ligas/torneios")
        return []
    
    # Salvar todas as ligas
    with open(f"{OUTPUT_DIR}/all_leagues.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Filtrar ligas tier 1 e 2
    tier_leagues = [league for league in result if league.get("tier") in [1, 2]]
    
    # Salvar ligas tier 1 e 2
    with open(f"{OUTPUT_DIR}/tier1_tier2_leagues.json", "w") as f:
        json.dump(tier_leagues, f, indent=2)
    
    # Salvar cada liga individualmente
    for league in result:
        league_id = league.get("leagueid")
        with open(f"{OUTPUT_DIR}/leagues/{league_id}.json", "w") as f:
            json.dump(league, f, indent=2)
    
    logger.info(f"Total de {len(result)} ligas coletadas, {len(tier_leagues)} são tier 1 ou 2")
    return result

def get_pro_players():
    """Coleta informações sobre jogadores profissionais."""
    logger.info("Coletando informações sobre jogadores profissionais")
    
    result = make_request("/proPlayers")
    
    if not result:
        logger.error("Falha ao coletar jogadores profissionais")
        return []
    
    # Salvar todos os jogadores
    with open(f"{OUTPUT_DIR}/all_pro_players.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Salvar cada jogador individualmente
    for player in result:
        account_id = player.get("account_id")
        with open(f"{OUTPUT_DIR}/players/{account_id}.json", "w") as f:
            json.dump(player, f, indent=2)
    
    logger.info(f"Total de {len(result)} jogadores profissionais coletados")
    return result

def get_heroes():
    """Coleta informações sobre heróis."""
    logger.info("Coletando informações sobre heróis")
    
    result = make_request("/heroes")
    
    if not result:
        logger.error("Falha ao coletar heróis")
        return []
    
    # Salvar todos os heróis
    with open(f"{OUTPUT_DIR}/all_heroes.json", "w") as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Total de {len(result)} heróis coletados")
    
    # Coletar estatísticas de heróis
    hero_stats = make_request("/heroStats")
    
    if hero_stats:
        with open(f"{OUTPUT_DIR}/hero_stats.json", "w") as f:
            json.dump(hero_stats, f, indent=2)
        
        logger.info(f"Estatísticas de {len(hero_stats)} heróis coletadas")
    
    return result

def run_explorer_queries():
    """Executa consultas SQL personalizadas via endpoint Explorer."""
    logger.info("Executando consultas SQL personalizadas via Explorer")
    
    # Consultas SQL para análises específicas
    queries = {
        "patch_738_pro_matches": """
            SELECT * FROM matches 
            WHERE patch = 138 AND game_mode = 2 
            ORDER BY start_time DESC LIMIT 1000
        """,
        "hero_picks_patch_738": """
            SELECT hero_id, count(*) as pick_count, 
                   sum(case when ((radiant_win = true AND is_radiant = true) OR 
                                  (radiant_win = false AND is_radiant = false)) 
                       then 1 else 0 end) as win_count,
                   sum(case when ((radiant_win = true AND is_radiant = true) OR 
                                  (radiant_win = false AND is_radiant = false)) 
                       then 1 else 0 end)::float / count(*) as win_rate
            FROM player_matches pm
            JOIN matches m ON pm.match_id = m.match_id
            WHERE m.patch = 138
            GROUP BY hero_id
            ORDER BY pick_count DESC
        """,
        "tier1_tier2_matches_patch_738": """
            SELECT m.* 
            FROM matches m
            JOIN leagues l ON m.leagueid = l.leagueid
            WHERE m.patch = 138 AND l.tier IN (1, 2)
            ORDER BY m.start_time DESC
            LIMIT 500
        """,
        "match_duration_by_patch": """
            SELECT patch, 
                   count(*) as match_count, 
                   avg(duration) as avg_duration,
                   min(duration) as min_duration,
                   max(duration) as max_duration
            FROM matches
            WHERE patch >= 130
            GROUP BY patch
            ORDER BY patch DESC
        """,
        "hero_pairs_patch_738": """
            WITH hero_pairs AS (
                SELECT pm1.hero_id as hero_1, pm2.hero_id as hero_2,
                       count(*) as games_together,
                       sum(case when ((m.radiant_win = true AND pm1.is_radiant = true) OR
                                      (m.radiant_win = false AND pm1.is_radiant = false))
                           then 1 else 0 end) as wins_together
                FROM matches m
                JOIN player_matches pm1 ON pm1.match_id = m.match_id
                JOIN player_matches pm2 ON pm2.match_id = m.match_id
                WHERE m.patch = 138
                AND pm1.hero_id < pm2.hero_id
                AND pm1.is_radiant = pm2.is_radiant
                GROUP BY pm1.hero_id, pm2.hero_id
                HAVING count(*) >= 10
            )
            SELECT hero_1, hero_2, games_together, 
                   wins_together::float / games_together as win_rate
            FROM hero_pairs
            ORDER BY win_rate DESC, games_together DESC
            LIMIT 100
        """
    }
    
    for query_name, sql in queries.items():
        logger.info(f"Executando consulta: {query_name}")
        
        # Codificar a consulta SQL
        params = {"sql": sql}
        
        result = make_request("/explorer", params)
        
        if result:
            with open(f"{OUTPUT_DIR}/explorer/{query_name}.json", "w") as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Consulta {query_name} executada com sucesso")
        else:
            logger.error(f"Falha ao executar consulta {query_name}")
        
        time.sleep(2)  # Respeitar rate limit (consultas SQL são mais pesadas)
    
    logger.info(f"Total de {len(queries)} consultas SQL executadas")

def main():
    """Função principal para coleta de dados."""
    start_time = datetime.now()
    logger.info(f"Iniciando coleta de dados da OpenDota em {start_time}")
    
    # 1. Coletar ligas/torneios
    leagues = get_leagues()
    
    # 2. Coletar partidas profissionais recentes
    pro_matches = get_pro_matches(limit=500)
    
    # 3. Coletar detalhes das partidas (limitando para não exceder rate limit)
    match_ids = [match.get("match_id") for match in pro_matches[:100]]
    match_details = get_match_details(match_ids)
    
    # 4. Coletar informações sobre jogadores profissionais
    pro_players = get_pro_players()
    
    # 5. Coletar informações sobre heróis
    heroes = get_heroes()
    
    # 6. Executar consultas SQL personalizadas
    run_explorer_queries()
    
    # Resumo da coleta
    end_time = datetime.now()
    duration = end_time - start_time
    
    summary = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration.total_seconds(),
        "leagues_count": len(leagues),
        "pro_matches_count": len(pro_matches),
        "match_details_count": len(match_details),
        "pro_players_count": len(pro_players),
        "heroes_count": len(heroes)
    }
    
    with open(f"{OUTPUT_DIR}/collection_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Coleta de dados concluída em {duration.total_seconds()} segundos")
    logger.info(f"Resumo: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    main()
