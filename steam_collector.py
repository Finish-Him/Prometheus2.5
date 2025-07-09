#!/usr/bin/env python3
"""
Script para coleta de dados da Steam Web API para Dota 2.
Foco em partidas profissionais do patch 7.38 (após 19/02/2025).
"""

import requests
import json
import os
import time
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("steam_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("steam_collector")

# Configurações
API_KEY = "116EF013E6A8537842C3436DE9FD7007"
BASE_URL = "https://api.steampowered.com"
DOTA2_APP_ID = 570
PATCH_738_TIMESTAMP = 1708300800  # 19 de fevereiro de 2025
OUTPUT_DIR = "collected_data/steam"

# Criar diretórios de saída
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/matches", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/leagues", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/teams", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/heroes", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/live_games", exist_ok=True)

def make_request(interface, method, version, params=None):
    """Faz uma requisição à Steam Web API com tratamento de erros."""
    if params is None:
        params = {}
    
    # Adicionar API key
    params["key"] = API_KEY
    
    url = f"{BASE_URL}/{interface}/{method}/v{version}/"
    
    try:
        response = requests.get(url, params=params)
        
        # Verificar erros
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        return None

def get_match_history(start_at_match_id=None, tournament_games_only=True, limit=500):
    """Coleta histórico de partidas de Dota 2."""
    logger.info(f"Coletando histórico de partidas (tournament_games_only={tournament_games_only})")
    
    interface = f"IDOTA2Match_{DOTA2_APP_ID}"
    method = "GetMatchHistory"
    version = "1"
    
    all_matches = []
    
    while len(all_matches) < limit:
        params = {
            "tournament_games_only": 1 if tournament_games_only else 0,
            "date_min": PATCH_738_TIMESTAMP,  # Filtrar pelo patch 7.38
            "matches_requested": 100  # Máximo permitido pela API
        }
        
        if start_at_match_id:
            params["start_at_match_id"] = start_at_match_id
        
        result = make_request(interface, method, version, params)
        
        if not result or result.get("result", {}).get("status") != 1:
            logger.warning(f"Falha ao obter histórico de partidas: {result}")
            break
        
        matches = result.get("result", {}).get("matches", [])
        
        if not matches:
            logger.info("Não há mais partidas disponíveis")
            break
        
        all_matches.extend(matches)
        logger.info(f"Coletadas {len(matches)} partidas (total: {len(all_matches)})")
        
        # Atualizar start_at_match_id para a próxima página
        start_at_match_id = matches[-1]["match_id"] - 1
        
        # Verificar se atingimos o limite
        if len(all_matches) >= limit:
            break
        
        time.sleep(1)  # Respeitar rate limit
    
    # Filtrar partidas após o lançamento do patch 7.38
    patch_matches = [m for m in all_matches if m.get("start_time", 0) >= PATCH_738_TIMESTAMP]
    
    # Salvar todas as partidas em um único arquivo
    with open(f"{OUTPUT_DIR}/match_history.json", "w") as f:
        json.dump(patch_matches, f, indent=2)
    
    logger.info(f"Total de {len(patch_matches)} partidas do patch 7.38 coletadas")
    return patch_matches

def get_match_details(match_ids):
    """Coleta detalhes completos de partidas específicas."""
    logger.info(f"Coletando detalhes de {len(match_ids)} partidas")
    
    interface = f"IDOTA2Match_{DOTA2_APP_ID}"
    method = "GetMatchDetails"
    version = "1"
    
    match_details = []
    
    for match_id in match_ids:
        params = {"match_id": match_id}
        
        result = make_request(interface, method, version, params)
        
        if not result or not result.get("result"):
            logger.warning(f"Falha ao obter detalhes da partida {match_id}")
            continue
        
        match_data = result.get("result")
        
        # Verificar se é do patch 7.38
        if match_data.get("start_time", 0) >= PATCH_738_TIMESTAMP:
            match_details.append(match_data)
            
            # Salvar detalhes da partida
            with open(f"{OUTPUT_DIR}/matches/{match_id}.json", "w") as f:
                json.dump(match_data, f, indent=2)
            
            logger.info(f"Detalhes da partida {match_id} coletados")
        else:
            logger.info(f"Partida {match_id} não é do patch 7.38")
        
        time.sleep(1)  # Respeitar rate limit
    
    logger.info(f"Detalhes de {len(match_details)} partidas do patch 7.38 coletados")
    return match_details

def get_league_listing():
    """Coleta lista de ligas/torneios."""
    logger.info("Coletando lista de ligas/torneios")
    
    interface = f"IDOTA2Match_{DOTA2_APP_ID}"
    method = "GetLeagueListing"
    version = "1"
    
    result = make_request(interface, method, version)
    
    if not result or not result.get("result"):
        logger.error("Falha ao obter lista de ligas/torneios")
        return []
    
    leagues = result.get("result", {}).get("leagues", [])
    
    # Salvar todas as ligas
    with open(f"{OUTPUT_DIR}/leagues.json", "w") as f:
        json.dump(leagues, f, indent=2)
    
    # Salvar cada liga individualmente
    for league in leagues:
        league_id = league.get("leagueid")
        with open(f"{OUTPUT_DIR}/leagues/{league_id}.json", "w") as f:
            json.dump(league, f, indent=2)
    
    logger.info(f"Total de {len(leagues)} ligas/torneios coletados")
    return leagues

def get_live_league_games():
    """Coleta informações sobre partidas de ligas em andamento."""
    logger.info("Coletando partidas de ligas em andamento")
    
    interface = f"IDOTA2Match_{DOTA2_APP_ID}"
    method = "GetLiveLeagueGames"
    version = "1"
    
    result = make_request(interface, method, version)
    
    if not result or not result.get("result"):
        logger.error("Falha ao obter partidas de ligas em andamento")
        return []
    
    games = result.get("result", {}).get("games", [])
    
    # Salvar todas as partidas em andamento
    timestamp = int(time.time())
    with open(f"{OUTPUT_DIR}/live_games/live_games_{timestamp}.json", "w") as f:
        json.dump(games, f, indent=2)
    
    # Salvar também no arquivo principal
    with open(f"{OUTPUT_DIR}/live_games.json", "w") as f:
        json.dump(games, f, indent=2)
    
    logger.info(f"Total de {len(games)} partidas de ligas em andamento coletadas")
    return games

def get_team_info(start_at_team_id=0, teams_requested=100):
    """Coleta informações sobre equipes."""
    logger.info(f"Coletando informações sobre equipes (start_at_team_id={start_at_team_id})")
    
    interface = f"IDOTA2Match_{DOTA2_APP_ID}"
    method = "GetTeamInfoByTeamID"
    version = "1"
    
    params = {
        "start_at_team_id": start_at_team_id,
        "teams_requested": teams_requested
    }
    
    result = make_request(interface, method, version, params)
    
    if not result or not result.get("result"):
        logger.error("Falha ao obter informações sobre equipes")
        return []
    
    teams = result.get("result", {}).get("teams", [])
    
    # Salvar todas as equipes
    with open(f"{OUTPUT_DIR}/teams_{start_at_team_id}.json", "w") as f:
        json.dump(teams, f, indent=2)
    
    # Salvar cada equipe individualmente
    for team in teams:
        team_id = team.get("team_id")
        with open(f"{OUTPUT_DIR}/teams/{team_id}.json", "w") as f:
            json.dump(team, f, indent=2)
    
    logger.info(f"Total de {len(teams)} equipes coletadas")
    return teams

def get_heroes():
    """Coleta informações sobre heróis."""
    logger.info("Coletando informações sobre heróis")
    
    interface = "IEconDOTA2_570"
    method = "GetHeroes"
    version = "1"
    
    result = make_request(interface, method, version)
    
    if not result or not result.get("result"):
        logger.error("Falha ao obter informações sobre heróis")
        return []
    
    heroes = result.get("result", {}).get("heroes", [])
    
    # Salvar todos os heróis
    with open(f"{OUTPUT_DIR}/heroes.json", "w") as f:
        json.dump(heroes, f, indent=2)
    
    logger.info(f"Total de {len(heroes)} heróis coletados")
    return heroes

def get_game_items():
    """Coleta informações sobre itens do jogo."""
    logger.info("Coletando informações sobre itens do jogo")
    
    interface = "IEconDOTA2_570"
    method = "GetGameItems"
    version = "1"
    
    result = make_request(interface, method, version)
    
    if not result or not result.get("result"):
        logger.error("Falha ao obter informações sobre itens do jogo")
        return []
    
    items = result.get("result", {}).get("items", [])
    
    # Salvar todos os itens
    with open(f"{OUTPUT_DIR}/items.json", "w") as f:
        json.dump(items, f, indent=2)
    
    logger.info(f"Total de {len(items)} itens coletados")
    return items

def main():
    """Função principal para coleta de dados."""
    start_time = datetime.now()
    logger.info(f"Iniciando coleta de dados da Steam Web API em {start_time}")
    
    # 1. Coletar lista de ligas/torneios
    leagues = get_league_listing()
    
    # 2. Coletar histórico de partidas de torneios
    tournament_matches = get_match_history(tournament_games_only=True, limit=200)
    
    # 3. Coletar detalhes das partidas (limitando para não exceder rate limit)
    match_ids = [match.get("match_id") for match in tournament_matches[:50]]
    match_details = get_match_details(match_ids)
    
    # 4. Coletar partidas de ligas em andamento
    live_games = get_live_league_games()
    
    # 5. Coletar informações sobre equipes
    teams = get_team_info()
    
    # 6. Coletar informações sobre heróis
    heroes = get_heroes()
    
    # 7. Coletar informações sobre itens do jogo
    items = get_game_items()
    
    # Resumo da coleta
    end_time = datetime.now()
    duration = end_time - start_time
    
    summary = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration.total_seconds(),
        "leagues_count": len(leagues),
        "tournament_matches_count": len(tournament_matches),
        "match_details_count": len(match_details),
        "live_games_count": len(live_games),
        "teams_count": len(teams),
        "heroes_count": len(heroes),
        "items_count": len(items)
    }
    
    with open(f"{OUTPUT_DIR}/collection_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Coleta de dados concluída em {duration.total_seconds()} segundos")
    logger.info(f"Resumo: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    main()
