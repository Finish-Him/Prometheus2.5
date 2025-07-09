#!/usr/bin/env python3
"""
Script para coleta de dados da API PandaScore para Dota 2.
Foco em partidas profissionais do patch 7.38 (após 19/02/2025) em torneios Tier 1 e 2.
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
        logging.FileHandler("pandascore_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pandascore_collector")

# Configurações
API_KEY = "efEXDM0DC_oKaesfsy3RBQ4MdXvnjGEfLTZNeZEOs4W5FMjoKbc"
BASE_URL = "https://api.pandascore.co"
PATCH_738_DATE = "2025-02-19T00:00:00Z"  # Data de lançamento do patch 7.38
OUTPUT_DIR = "collected_data/pandascore"

# Criar diretórios de saída
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/tournaments", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/matches", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/teams", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/players", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/heroes", exist_ok=True)

def make_request(endpoint, params=None):
    """Faz uma requisição à API PandaScore com tratamento de rate limit."""
    if params is None:
        params = {}
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        # Verificar rate limit
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limit atingido. Aguardando {retry_after} segundos.")
            time.sleep(retry_after)
            return make_request(endpoint, params)
        
        # Verificar outros erros
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {e}")
        return None

def get_tournaments(tier=None):
    """Coleta torneios de Dota 2 após o lançamento do patch 7.38."""
    logger.info(f"Coletando torneios de Dota 2 após {PATCH_738_DATE}")
    
    params = {
        "filter[videogame]": "dota-2",
        "filter[begin_at]": PATCH_738_DATE,
        "sort": "-begin_at",
        "page[size]": 100
    }
    
    if tier:
        params["filter[tier]"] = tier
    
    tournaments = []
    page = 1
    
    while True:
        params["page[number]"] = page
        result = make_request("/dota2/tournaments", params)
        
        if not result or len(result) == 0:
            break
        
        tournaments.extend(result)
        logger.info(f"Coletados {len(result)} torneios da página {page}")
        
        # Salvar cada torneio individualmente
        for tournament in result:
            tournament_id = tournament.get("id")
            with open(f"{OUTPUT_DIR}/tournaments/{tournament_id}.json", "w") as f:
                json.dump(tournament, f, indent=2)
        
        # Verificar se há mais páginas
        if len(result) < params["page[size]"]:
            break
        
        page += 1
        time.sleep(1)  # Respeitar rate limit
    
    # Salvar todos os torneios em um único arquivo
    with open(f"{OUTPUT_DIR}/all_tournaments.json", "w") as f:
        json.dump(tournaments, f, indent=2)
    
    logger.info(f"Total de {len(tournaments)} torneios coletados")
    return tournaments

def get_matches_by_tournament(tournament_id):
    """Coleta partidas de um torneio específico."""
    logger.info(f"Coletando partidas do torneio {tournament_id}")
    
    params = {
        "filter[tournament_id]": tournament_id,
        "sort": "-begin_at",
        "page[size]": 100
    }
    
    matches = []
    page = 1
    
    while True:
        params["page[number]"] = page
        result = make_request("/dota2/matches", params)
        
        if not result or len(result) == 0:
            break
        
        matches.extend(result)
        logger.info(f"Coletadas {len(result)} partidas da página {page} do torneio {tournament_id}")
        
        # Salvar cada partida individualmente
        for match in result:
            match_id = match.get("id")
            with open(f"{OUTPUT_DIR}/matches/{match_id}.json", "w") as f:
                json.dump(match, f, indent=2)
        
        # Verificar se há mais páginas
        if len(result) < params["page[size]"]:
            break
        
        page += 1
        time.sleep(1)  # Respeitar rate limit
    
    logger.info(f"Total de {len(matches)} partidas coletadas do torneio {tournament_id}")
    return matches

def get_all_matches_since_patch():
    """Coleta todas as partidas desde o lançamento do patch 7.38."""
    logger.info(f"Coletando todas as partidas desde {PATCH_738_DATE}")
    
    params = {
        "filter[begin_at]": PATCH_738_DATE,
        "sort": "-begin_at",
        "page[size]": 100
    }
    
    matches = []
    page = 1
    
    while True:
        params["page[number]"] = page
        result = make_request("/dota2/matches", params)
        
        if not result or len(result) == 0:
            break
        
        matches.extend(result)
        logger.info(f"Coletadas {len(result)} partidas da página {page}")
        
        # Verificar se há mais páginas
        if len(result) < params["page[size]"]:
            break
        
        page += 1
        time.sleep(1)  # Respeitar rate limit
    
    # Salvar todas as partidas em um único arquivo
    with open(f"{OUTPUT_DIR}/all_matches.json", "w") as f:
        json.dump(matches, f, indent=2)
    
    logger.info(f"Total de {len(matches)} partidas coletadas")
    return matches

def get_teams():
    """Coleta informações de equipes de Dota 2."""
    logger.info("Coletando equipes de Dota 2")
    
    params = {
        "page[size]": 100
    }
    
    teams = []
    page = 1
    
    while True:
        params["page[number]"] = page
        result = make_request("/dota2/teams", params)
        
        if not result or len(result) == 0:
            break
        
        teams.extend(result)
        logger.info(f"Coletadas {len(result)} equipes da página {page}")
        
        # Salvar cada equipe individualmente
        for team in result:
            team_id = team.get("id")
            with open(f"{OUTPUT_DIR}/teams/{team_id}.json", "w") as f:
                json.dump(team, f, indent=2)
        
        # Verificar se há mais páginas
        if len(result) < params["page[size]"]:
            break
        
        page += 1
        time.sleep(1)  # Respeitar rate limit
    
    # Salvar todas as equipes em um único arquivo
    with open(f"{OUTPUT_DIR}/all_teams.json", "w") as f:
        json.dump(teams, f, indent=2)
    
    logger.info(f"Total de {len(teams)} equipes coletadas")
    return teams

def get_players():
    """Coleta informações de jogadores de Dota 2."""
    logger.info("Coletando jogadores de Dota 2")
    
    params = {
        "page[size]": 100
    }
    
    players = []
    page = 1
    
    while True:
        params["page[number]"] = page
        result = make_request("/dota2/players", params)
        
        if not result or len(result) == 0:
            break
        
        players.extend(result)
        logger.info(f"Coletados {len(result)} jogadores da página {page}")
        
        # Salvar cada jogador individualmente
        for player in result:
            player_id = player.get("id")
            with open(f"{OUTPUT_DIR}/players/{player_id}.json", "w") as f:
                json.dump(player, f, indent=2)
        
        # Verificar se há mais páginas
        if len(result) < params["page[size]"]:
            break
        
        page += 1
        time.sleep(1)  # Respeitar rate limit
    
    # Salvar todos os jogadores em um único arquivo
    with open(f"{OUTPUT_DIR}/all_players.json", "w") as f:
        json.dump(players, f, indent=2)
    
    logger.info(f"Total de {len(players)} jogadores coletados")
    return players

def get_heroes():
    """Coleta informações de heróis de Dota 2."""
    logger.info("Coletando heróis de Dota 2")
    
    result = make_request("/dota2/heroes")
    
    if not result:
        logger.error("Falha ao coletar heróis")
        return []
    
    # Salvar todos os heróis em um único arquivo
    with open(f"{OUTPUT_DIR}/all_heroes.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Salvar cada herói individualmente
    for hero in result:
        hero_id = hero.get("id")
        with open(f"{OUTPUT_DIR}/heroes/{hero_id}.json", "w") as f:
            json.dump(hero, f, indent=2)
    
    logger.info(f"Total de {len(result)} heróis coletados")
    return result

def main():
    """Função principal para coleta de dados."""
    start_time = datetime.now()
    logger.info(f"Iniciando coleta de dados da PandaScore em {start_time}")
    
    # 1. Coletar torneios Tier 1 e 2 após o patch 7.38
    tier1_tournaments = get_tournaments(tier=1)
    tier2_tournaments = get_tournaments(tier=2)
    
    # 2. Coletar partidas de cada torneio Tier 1 e 2
    all_tournament_matches = []
    
    for tournament in tier1_tournaments + tier2_tournaments:
        tournament_id = tournament.get("id")
        matches = get_matches_by_tournament(tournament_id)
        all_tournament_matches.extend(matches)
    
    # 3. Coletar todas as partidas desde o patch 7.38 (para garantir cobertura completa)
    all_matches = get_all_matches_since_patch()
    
    # 4. Coletar informações de equipes
    teams = get_teams()
    
    # 5. Coletar informações de jogadores
    players = get_players()
    
    # 6. Coletar informações de heróis
    heroes = get_heroes()
    
    # Resumo da coleta
    end_time = datetime.now()
    duration = end_time - start_time
    
    summary = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration.total_seconds(),
        "tier1_tournaments_count": len(tier1_tournaments),
        "tier2_tournaments_count": len(tier2_tournaments),
        "tournament_matches_count": len(all_tournament_matches),
        "all_matches_count": len(all_matches),
        "teams_count": len(teams),
        "players_count": len(players),
        "heroes_count": len(heroes)
    }
    
    with open(f"{OUTPUT_DIR}/collection_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Coleta de dados concluída em {duration.total_seconds()} segundos")
    logger.info(f"Resumo: {json.dumps(summary, indent=2)}")

if __name__ == "__main__":
    main()
