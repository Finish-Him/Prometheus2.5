import json
import sys
from collections import defaultdict
import numpy as np

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
hero_constants_path = "/home/ubuntu/dota_hero_constants.json"
output_file = "/home/ubuntu/aggregated_hero_stats.json"

# Carregar dados das partidas
print(f"Carregando dados das partidas: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    print(f"Dados de {len(matches_data)} partidas carregados.")
except Exception as e:
    print(f"Erro ao carregar dados das partidas: {e}")
    sys.exit(1)

# Carregar constantes de heróis
print(f"Carregando constantes de heróis: {hero_constants_path}")
try:
    with open(hero_constants_path, 'r', encoding='utf-8') as f:
        hero_constants_raw = json.load(f)
    print(f"Constantes de {len(hero_constants_raw)} heróis carregadas.")
except Exception as e:
    print(f"Erro ao carregar constantes de heróis: {e}")
    sys.exit(1)

# Estrutura para armazenar estatísticas agregadas e constantes
hero_stats = defaultdict(lambda: {
    'picks': 0,
    'wins': 0,
    'total_duration': 0,
    'total_kills': 0,
    'total_deaths': 0,
    'total_assists': 0,
    'total_gpm': 0,
    'total_xpm': 0,
    # Constantes (serão preenchidas uma vez)
    'name': None,
    'primary_attr': None,
    'base_str': None,
    'base_agi': None,
    'base_int': None,
    'str_gain': None,
    'agi_gain': None,
    'int_gain': None
})

# Preencher constantes dos heróis
hero_id_map = {}
for hero_id_str, data in hero_constants_raw.items():
    hero_id = data.get('id')
    if hero_id:
        hero_id_map[hero_id] = data # Store raw data for easier access
        stats = hero_stats[hero_id] # Get or create entry
        stats['name'] = data.get('localized_name')
        stats['primary_attr'] = data.get('primary_attr')
        stats['base_str'] = data.get('base_str')
        stats['base_agi'] = data.get('base_agi')
        stats['base_int'] = data.get('base_int')
        stats['str_gain'] = data.get('str_gain')
        stats['agi_gain'] = data.get('agi_gain')
        stats['int_gain'] = data.get('int_gain')

print(f"Constantes preenchidas para {len(hero_stats)} heróis.")

# Processar cada partida para agregar estatísticas
print("Agregando estatísticas das partidas...")
for match in matches_data:
    radiant_win = match.get('radiant_win')
    duration = match.get('duration')
    players = match.get('players', [])

    if radiant_win is None or duration is None or not players:
        continue

    for player in players:
        hero_id = player.get('hero_id')
        player_slot = player.get('player_slot')
        kills = player.get('kills')
        deaths = player.get('deaths')
        assists = player.get('assists')
        gpm = player.get('gold_per_min')
        xpm = player.get('xp_per_min')

        # Verificar se temos dados válidos e se o herói existe nas constantes
        # Corrected line continuation: removed space after backslash
        if hero_id is None or hero_id not in hero_stats or player_slot is None or \
           kills is None or deaths is None or assists is None or gpm is None or xpm is None:
            continue
            
        stats = hero_stats[hero_id]
        stats['picks'] += 1
        stats['total_duration'] += duration
        stats['total_kills'] += kills
        stats['total_deaths'] += deaths
        stats['total_assists'] += assists
        stats['total_gpm'] += gpm
        stats['total_xpm'] += xpm

        # Contar vitórias
        is_radiant = player_slot < 128
        player_won = (radiant_win and is_radiant) or (not radiant_win and not is_radiant)
        if player_won:
            stats['wins'] += 1

# Remover heróis que não foram escolhidos (caso existam nas constantes mas não nas partidas)
heroes_to_remove = [hero_id for hero_id, stats in hero_stats.items() if stats['picks'] == 0]
for hero_id in heroes_to_remove:
    del hero_stats[hero_id]

print(f"Estatísticas agregadas para {len(hero_stats)} heróis escolhidos.")

# Salvar dados agregados em JSON
print(f"Salvando dados agregados em {output_file}")
try:
    # Convert defaultdict to dict for JSON serialization
    output_data = dict(hero_stats)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)
    print("Dados agregados salvos com sucesso.")
except Exception as e:
    print(f"Erro ao salvar dados agregados: {e}")
    sys.exit(1)

