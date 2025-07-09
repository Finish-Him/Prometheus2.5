import requests
import json
import time
import pandas as pd
import os

api_key = "91fdee34-226f-4681-8f72-ee87bd85abcf"
input_json_file = "/home/ubuntu/pgl_wallachia_s4_matches.json"
output_detailed_json_file = "/home/ubuntu/pgl_wallachia_s4_matches_detailed.json"

# --- Helper function to parse objectives ---
def parse_objectives(objectives):
    parsed = {
        'first_tower_time': None,
        'first_tower_team': None, # 2 for Radiant, 3 for Dire
        'roshan_kills': [],
        'barracks_kills': [],
        'aegis_pickups': [],
        'aegis_denied': None,
        'aegis_stolen': None
    }
    if not objectives:
        return parsed

    first_tower_found = False
    for obj in objectives:
        obj_time = obj.get('time')
        obj_type = obj.get('type')
        obj_team = obj.get('team') # For tower kills
        obj_key = obj.get('key') # For barracks kills, aegis
        obj_player_slot = obj.get('player_slot') # For aegis

        # First Tower (approximated by first tower kill event)
        if not first_tower_found and obj_type == 'CHAT_MESSAGE_TOWER_KILL':
            parsed['first_tower_time'] = obj_time
            # Team is 2 (Radiant) or 3 (Dire) based on which tower was killed
            # The 'team' field in the objective indicates which team's tower was killed.
            # So the killing team is the opposite.
            parsed['first_tower_team'] = 3 if obj_team == 2 else 2 
            first_tower_found = True

        # Roshan Kills
        if obj_type == 'CHAT_MESSAGE_ROSHAN_KILL':
            # Determine killer team if possible (often not directly available, might need complex logic)
            parsed['roshan_kills'].append({'time': obj_time})

        # Barracks Kills
        if obj_type == 'CHAT_MESSAGE_BARRACKS_KILL':
             # Determine killer team (similar logic to towers)
            killer_team = 3 if obj_team == 2 else 2
            parsed['barracks_kills'].append({'time': obj_time, 'key': obj_key, 'killer_team': killer_team})

        # Aegis Pickups
        if obj_type == 'CHAT_MESSAGE_AEGIS':
             parsed['aegis_pickups'].append({'time': obj_time, 'player_slot': obj_player_slot})
        
        # Aegis Denied
        if obj_type == 'CHAT_MESSAGE_AEGIS_DENIED':
            parsed['aegis_denied'] = {'time': obj_time}
            
        # Aegis Stolen
        if obj_type == 'CHAT_MESSAGE_AEGIS_STOLEN':
            parsed['aegis_stolen'] = {'time': obj_time}

    # Sort lists by time
    parsed['roshan_kills'].sort(key=lambda x: x['time'])
    parsed['barracks_kills'].sort(key=lambda x: x['time'])
    parsed['aegis_pickups'].sort(key=lambda x: x['time'])

    return parsed

# --- Main script ---
print(f"Lendo lista de partidas de {input_json_file}...")
try:
    with open(input_json_file, 'r', encoding='utf-8') as f:
        matches_summary = json.load(f)
except FileNotFoundError:
    print(f"Erro: Arquivo de resumo de partidas não encontrado: {input_json_file}")
    exit()
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar JSON do arquivo: {input_json_file}")
    exit()

if not isinstance(matches_summary, list) or not matches_summary:
    print("Arquivo de resumo de partidas está vazio ou em formato inválido.")
    exit()

match_ids = [match.get('match_id') for match in matches_summary if match.get('match_id')]
print(f"Encontrados {len(match_ids)} IDs de partidas. Buscando detalhes...")

all_matches_details = []
processed_count = 0
fetch_errors = 0

for match_id in match_ids:
    print(f"Buscando detalhes da partida {match_id} ({processed_count + 1}/{len(match_ids)})...", end='')
    url = f"https://api.opendota.com/api/matches/{match_id}"
    params = {"api_key": api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        match_details = response.json()
        
        # Extrair informações básicas e objetivos
        basic_info = {
            'match_id': match_details.get('match_id'),
            'leagueid': match_details.get('leagueid'),
            'start_time': match_details.get('start_time'),
            'duration': match_details.get('duration'),
            'radiant_win': match_details.get('radiant_win'),
            'radiant_score': match_details.get('radiant_score'),
            'dire_score': match_details.get('dire_score'),
            'first_blood_time': match_details.get('first_blood_time'),
            # Adicionar mais campos básicos se necessário
        }
        
        # Parse objectives
        objectives_data = parse_objectives(match_details.get('objectives'))
        
        # Combinar informações
        detailed_entry = {**basic_info, **objectives_data}
        all_matches_details.append(detailed_entry)
        print(" OK")
        processed_count += 1
        
    except requests.exceptions.RequestException as e:
        print(f" Erro de requisição: {e}")
        fetch_errors += 1
    except json.JSONDecodeError:
        print(" Erro de decodificação JSON")
        fetch_errors += 1
    except Exception as e:
        print(f" Erro inesperado: {e}")
        fetch_errors += 1
        
    # Pausa para evitar rate limit
    time.sleep(1.1) # OpenDota free tier limit is roughly 60 calls/minute

print(f"\nBusca concluída. {processed_count} partidas processadas com sucesso, {fetch_errors} falhas.")

if all_matches_details:
    print(f"Salvando {len(all_matches_details)} partidas detalhadas em {output_detailed_json_file}...")
    try:
        with open(output_detailed_json_file, 'w', encoding='utf-8') as f:
            json.dump(all_matches_details, f, ensure_ascii=False, indent=4)
        print("Dados detalhados salvos em JSON com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON detalhado: {e}")
else:
    print("Nenhum dado detalhado de partida foi coletado.")


