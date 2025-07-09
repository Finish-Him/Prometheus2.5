import requests
import json
import os
import time
from datetime import datetime
import pandas as pd
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dota2_data_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dota2_data_collector")

# Configuração das APIs
PANDASCORE_API_KEY = "efEXDM0DC_oKaesfsy3RBQ4MdXvnjGEfLTZNeZEOs4W5FMjoKbc"
OPENDOTA_API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
STEAM_API_KEY = "116EF013E6A8537842C3436DE9FD7007"

# URLs base
PANDASCORE_BASE_URL = "https://api.pandascore.co"
OPENDOTA_BASE_URL = "https://api.opendota.com/api"
STEAM_BASE_URL = "https://api.steampowered.com"

# Headers para PandaScore
PANDASCORE_HEADERS = {
    "Authorization": f"Bearer {PANDASCORE_API_KEY}",
    "Accept": "application/json"
}

# Diretório para salvar os dados
DATA_DIR = "collected_data"
os.makedirs(DATA_DIR, exist_ok=True)

# Função para fazer requisições à API PandaScore
def pandascore_request(endpoint, params=None):
    if params is None:
        params = {}
    
    url = f"{PANDASCORE_BASE_URL}{endpoint}"
    
    try:
        logger.info(f"Fazendo requisição para PandaScore: {url}")
        response = requests.get(url, headers=PANDASCORE_HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para PandaScore: {e}")
        return None

# Função para fazer requisições à API OpenDota
def opendota_request(endpoint, params=None):
    if params is None:
        params = {}
    
    # Adicionar API key aos parâmetros
    if OPENDOTA_API_KEY:
        params['api_key'] = OPENDOTA_API_KEY
    
    url = f"{OPENDOTA_BASE_URL}{endpoint}"
    
    try:
        logger.info(f"Fazendo requisição para OpenDota: {url}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para OpenDota: {e}")
        return None

# Função para fazer requisições à API Steam
def steam_request(interface, method, version, params=None):
    if params is None:
        params = {}
    
    # Adicionar API key aos parâmetros
    params['key'] = STEAM_API_KEY
    
    url = f"{STEAM_BASE_URL}/{interface}/{method}/v{version}/"
    
    try:
        logger.info(f"Fazendo requisição para Steam: {url}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para Steam: {e}")
        return None

# Função para salvar dados em arquivo JSON
def save_to_json(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"Dados salvos em {filepath}")
    return filepath

# Função para salvar dados em arquivo CSV
def save_to_csv(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    logger.info(f"Dados salvos em {filepath}")
    return filepath

# Função para coletar partidas recentes da PandaScore
def collect_pandascore_matches(limit=100):
    logger.info(f"Coletando até {limit} partidas recentes da PandaScore...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    # Coletar partidas passadas
    all_matches = []
    
    for page in range(1, pages_needed + 1):
        params = {
            "page": page,
            "per_page": 100,
            "sort": "-end_at"
        }
        
        matches = pandascore_request("/dota2/matches/past", params)
        
        if not matches:
            break
            
        all_matches.extend(matches)
        
        if len(all_matches) >= limit:
            all_matches = all_matches[:limit]
            break
        
        # Adicionar delay para evitar rate limiting
        time.sleep(1)
    
    logger.info(f"Coletadas {len(all_matches)} partidas da PandaScore")
    save_to_json(all_matches, "pandascore_matches.json")
    
    # Extrair informações relevantes para análise
    simplified_matches = []
    
    for match in all_matches:
        try:
            match_data = {
                "match_id": match.get("id"),
                "tournament_id": match.get("tournament_id"),
                "tournament_name": match.get("tournament", {}).get("name"),
                "league_name": match.get("league", {}).get("name"),
                "begin_at": match.get("begin_at"),
                "end_at": match.get("end_at"),
                "status": match.get("status"),
                "radiant_team": match.get("opponents", [{}])[0].get("opponent", {}).get("name") if len(match.get("opponents", [])) > 0 else None,
                "dire_team": match.get("opponents", [{}])[1].get("opponent", {}).get("name") if len(match.get("opponents", [])) > 1 else None,
                "radiant_score": match.get("results", [{}])[0].get("score") if len(match.get("results", [])) > 0 else None,
                "dire_score": match.get("results", [{}])[1].get("score") if len(match.get("results", [])) > 1 else None,
                "winner": match.get("winner", {}).get("name"),
                "duration": None  # Será preenchido com dados de games se disponíveis
            }
            
            # Adicionar duração se disponível nos games
            if "games" in match and match["games"] and len(match["games"]) > 0:
                durations = [game.get("length") for game in match["games"] if game.get("length")]
                if durations:
                    match_data["duration"] = sum(durations) / len(durations)  # Média das durações
            
            simplified_matches.append(match_data)
        except Exception as e:
            logger.error(f"Erro ao processar partida da PandaScore: {e}")
    
    save_to_csv(simplified_matches, "pandascore_matches_simplified.csv")
    
    return all_matches, simplified_matches

# Função para coletar partidas profissionais da OpenDota
def collect_opendota_pro_matches(limit=100):
    logger.info(f"Coletando até {limit} partidas profissionais da OpenDota...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    all_matches = []
    last_match_id = None
    
    for _ in range(pages_needed):
        params = {"limit": 100}
        
        if last_match_id:
            params["less_than_match_id"] = last_match_id
        
        matches = opendota_request("/proMatches", params)
        
        if not matches or len(matches) == 0:
            break
            
        all_matches.extend(matches)
        
        if len(all_matches) >= limit:
            all_matches = all_matches[:limit]
            break
        
        # Atualizar o último match_id para a próxima requisição
        last_match_id = matches[-1]["match_id"]
        
        # Adicionar delay para evitar rate limiting
        time.sleep(1)
    
    logger.info(f"Coletadas {len(all_matches)} partidas profissionais da OpenDota")
    save_to_json(all_matches, "opendota_pro_matches.json")
    
    # Extrair informações relevantes para análise
    simplified_matches = []
    
    for match in all_matches:
        try:
            match_data = {
                "match_id": match.get("match_id"),
                "league_name": match.get("league_name"),
                "start_time": match.get("start_time"),
                "duration": match.get("duration"),
                "radiant_team": match.get("radiant_name"),
                "dire_team": match.get("dire_name"),
                "radiant_score": match.get("radiant_score"),
                "dire_score": match.get("dire_score"),
                "radiant_win": match.get("radiant_win"),
                "patch": match.get("patch")
            }
            
            simplified_matches.append(match_data)
        except Exception as e:
            logger.error(f"Erro ao processar partida da OpenDota: {e}")
    
    save_to_csv(simplified_matches, "opendota_pro_matches_simplified.csv")
    
    return all_matches, simplified_matches

# Função para coletar detalhes de partidas da OpenDota
def collect_opendota_match_details(match_ids):
    logger.info(f"Coletando detalhes de {len(match_ids)} partidas da OpenDota...")
    
    match_details = {}
    
    for match_id in match_ids:
        logger.info(f"Coletando detalhes da partida {match_id}...")
        
        details = opendota_request(f"/matches/{match_id}")
        
        if details:
            match_details[match_id] = details
        
        # Adicionar delay para evitar rate limiting
        time.sleep(1)
    
    logger.info(f"Coletados detalhes de {len(match_details)} partidas da OpenDota")
    save_to_json(match_details, "opendota_match_details.json")
    
    # Extrair informações relevantes para análise
    simplified_details = []
    
    for match_id, details in match_details.items():
        try:
            match_data = {
                "match_id": match_id,
                "duration": details.get("duration"),
                "start_time": details.get("start_time"),
                "radiant_win": details.get("radiant_win"),
                "radiant_score": details.get("radiant_score"),
                "dire_score": details.get("dire_score"),
                "patch": details.get("patch"),
                "region": details.get("region"),
                "first_blood_time": details.get("first_blood_time"),
                "lobby_type": details.get("lobby_type"),
                "game_mode": details.get("game_mode"),
                "radiant_gold_adv": details.get("radiant_gold_adv", [])[-1] if details.get("radiant_gold_adv") else None,
                "radiant_xp_adv": details.get("radiant_xp_adv", [])[-1] if details.get("radiant_xp_adv") else None,
                "tower_status_radiant": details.get("tower_status_radiant"),
                "tower_status_dire": details.get("tower_status_dire"),
                "barracks_status_radiant": details.get("barracks_status_radiant"),
                "barracks_status_dire": details.get("barracks_status_dire")
            }
            
            simplified_details.append(match_data)
        except Exception as e:
            logger.error(f"Erro ao processar detalhes da partida {match_id} da OpenDota: {e}")
    
    save_to_csv(simplified_details, "opendota_match_details_simplified.csv")
    
    return match_details, simplified_details

# Função para coletar estatísticas de heróis da OpenDota
def collect_opendota_hero_stats():
    logger.info("Coletando estatísticas de heróis da OpenDota...")
    
    hero_stats = opendota_request("/heroStats")
    
    if not hero_stats:
        logger.error("Falha ao coletar estatísticas de heróis da OpenDota")
        return None, None
    
    logger.info(f"Coletadas estatísticas de {len(hero_stats)} heróis da OpenDota")
    save_to_json(hero_stats, "opendota_hero_stats.json")
    
    # Extrair informações relevantes para análise
    simplified_stats = []
    
    for hero in hero_stats:
        try:
            hero_data = {
                "hero_id": hero.get("id"),
                "name": hero.get("localized_name"),
                "primary_attr": hero.get("primary_attr"),
                "attack_type": hero.get("attack_type"),
                "roles": ", ".join(hero.get("roles", [])),
                "base_health": hero.get("base_health"),
                "base_mana": hero.get("base_mana"),
                "base_armor": hero.get("base_armor"),
                "base_attack_min": hero.get("base_attack_min"),
                "base_attack_max": hero.get("base_attack_max"),
                "move_speed": hero.get("move_speed"),
                "pro_pick": hero.get("pro_pick"),
                "pro_win": hero.get("pro_win"),
                "pro_ban": hero.get("pro_ban"),
                "pro_winrate": hero.get("pro_win") / hero.get("pro_pick") if hero.get("pro_pick") else None,
                "1_pick": hero.get("1_pick"),
                "1_win": hero.get("1_win"),
                "2_pick": hero.get("2_pick"),
                "2_win": hero.get("2_win"),
                "3_pick": hero.get("3_pick"),
                "3_win": hero.get("3_win"),
                "4_pick": hero.get("4_pick"),
                "4_win": hero.get("4_win"),
                "5_pick": hero.get("5_pick"),
                "5_win": hero.get("5_win"),
                "6_pick": hero.get("6_pick"),
                "6_win": hero.get("6_win"),
                "7_pick": hero.get("7_pick"),
                "7_win": hero.get("7_win"),
                "8_pick": hero.get("8_pick"),
                "8_win": hero.get("8_win"),
                "turbo_pick": hero.get("turbo_pick"),
                "turbo_win": hero.get("turbo_win")
            }
            
            simplified_stats.append(hero_data)
        except Exception as e:
            logger.error(f"Erro ao processar estatísticas do herói {hero.get('localized_name')} da OpenDota: {e}")
    
    save_to_csv(simplified_stats, "opendota_hero_stats_simplified.csv")
    
    return hero_stats, simplified_stats

# Função para coletar partidas ao vivo da Steam
def collect_steam_live_games():
    logger.info("Coletando partidas ao vivo da Steam...")
    
    live_games = steam_request("IDOTA2Match_570", "GetLiveLeagueGames", "1")
    
    if not live_games or "result" not in live_games or "games" not in live_games["result"]:
        logger.error("Falha ao coletar partidas ao vivo da Steam")
        return None, None
    
    logger.info(f"Coletadas {len(live_games['result']['games'])} partidas ao vivo da Steam")
    save_to_json(live_games, "steam_live_games.json")
    
    # Extrair informações relevantes para análise
    simplified_games = []
    
    for game in live_games["result"]["games"]:
        try:
            game_data = {
                "match_id": game.get("match_id"),
                "league_id": game.get("league_id"),
                "radiant_team": game.get("radiant_team", {}).get("team_name"),
                "dire_team": game.get("dire_team", {}).get("team_name"),
                "spectators": game.get("spectators"),
                "series_type": game.get("series_type"),
                "radiant_series_wins": game.get("radiant_series_wins"),
                "dire_series_wins": game.get("dire_series_wins")
            }
            
            # Adicionar informações do placar se disponíveis
            if "scoreboard" in game:
                scoreboard = game["scoreboard"]
                if "duration" in scoreboard:
                    game_data["duration"] = scoreboard["duration"]
                if "radiant" in scoreboard:
                    game_data["radiant_score"] = scoreboard["radiant"].get("score")
                    game_data["radiant_tower_state"] = scoreboard["radiant"].get("tower_state")
                    game_data["radiant_barracks_state"] = scoreboard["radiant"].get("barracks_state")
                if "dire" in scoreboard:
                    game_data["dire_score"] = scoreboard["dire"].get("score")
                    game_data["dire_tower_state"] = scoreboard["dire"].get("tower_state")
                    game_data["dire_barracks_state"] = scoreboard["dire"].get("barracks_state")
            
            simplified_games.append(game_data)
        except Exception as e:
            logger.error(f"Erro ao processar partida ao vivo da Steam: {e}")
    
    save_to_csv(simplified_games, "steam_live_games_simplified.csv")
    
    return live_games, simplified_games

# Função para colet
(Content truncated due to size limit. Use line ranges to read in chunks)