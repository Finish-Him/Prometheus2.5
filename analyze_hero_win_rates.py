import json
import pandas as pd
import numpy as np
from collections import defaultdict
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
hero_constants_path = "/home/ubuntu/dota_hero_constants.json"
output_file = "/home/ubuntu/hero_win_rates_analysis.txt"
MIN_PICKS_THRESHOLD = 5 # Minimum number of picks to include a hero in the main list

# Carregar dados das partidas
print(f"Carregando dados das partidas: {json_file_path}")
try:
    # Corrected file open mode
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    print(f"Dados de {len(matches_data)} partidas carregados.")
except Exception as e:
    print(f"Erro ao carregar dados das partidas: {e}")
    sys.exit(1)

# Carregar constantes de heróis
print(f"Carregando constantes de heróis: {hero_constants_path}")
try:
    # Corrected file open mode
    with open(hero_constants_path, 'r', encoding='utf-8') as f:
        hero_constants = json.load(f)
    print(f"Constantes de {len(hero_constants)} heróis carregadas.")
except Exception as e:
    print(f"Erro ao carregar constantes de heróis: {e}")
    sys.exit(1)

# Criar mapeamento de ID para nome do herói
hero_id_to_name = {}
for hero_id_str, hero_data in hero_constants.items():
    # Corrected key access
    if 'id' in hero_data and 'localized_name' in hero_data:
        hero_id_to_name[hero_data['id']] = hero_data['localized_name']

print(f"Mapeamento criado para {len(hero_id_to_name)} heróis.")

# Inicializar contador de vitórias/escolhas por herói
# Corrected lambda definition
hero_stats = defaultdict(lambda: {'picks': 0, 'wins': 0})

# Processar cada partida
for match in matches_data:
    # Corrected key access
    radiant_win = match.get('radiant_win')
    players = match.get('players', [])

    if radiant_win is None or not players:
        continue

    for player in players:
        # Corrected key access
        hero_id = player.get('hero_id')
        player_slot = player.get('player_slot')

        if hero_id is None or player_slot is None:
            continue

        # Incrementar escolhas
        # Corrected key access
        hero_stats[hero_id]['picks'] += 1

        # Verificar se o time do jogador venceu
        is_radiant = player_slot < 128
        player_won = (radiant_win and is_radiant) or (not radiant_win and not is_radiant)
        
        if player_won:
            # Corrected key access
            hero_stats[hero_id]['wins'] += 1

# Calcular taxas de vitória e preparar resultados
results_list = []
for hero_id, stats in hero_stats.items():
    # Corrected key access
    picks = stats['picks']
    wins = stats['wins']
    if picks > 0:
        win_rate = (wins / picks) * 100
        hero_name = hero_id_to_name.get(hero_id, f"Unknown Hero ID: {hero_id}")
        results_list.append({
            # Corrected key names
            'name': hero_name,
            'id': hero_id,
            'picks': picks,
            'wins': wins,
            'win_rate': win_rate
        })

# Ordenar por taxa de vitória (para heróis com picks >= threshold)
# Corrected key access
filtered_results = [r for r in results_list if r['picks'] >= MIN_PICKS_THRESHOLD]
# Corrected key access
filtered_results.sort(key=lambda x: x['win_rate'], reverse=True)

# Ordenar todos por número de escolhas
# Corrected key access
results_list.sort(key=lambda x: x['picks'], reverse=True)

# Preparar texto do resultado
results_text = f"# Análise de Taxa de Vitória dos Heróis - PGL Wallachia Season 4\n\n"
results_text += f"Total de Partidas Analisadas: {len(matches_data)}\n"
results_text += f"Total de Heróis Jogados: {len(hero_stats)}\n"
results_text += f"Limiar Mínimo de Escolhas para Ranking de Win Rate: {MIN_PICKS_THRESHOLD}\n\n"

results_text += f"## Top Heróis por Taxa de Vitória (Escolhas >= {MIN_PICKS_THRESHOLD})\n\n"
results_text += "| Herói | Escolhas | Vitórias | Taxa de Vitória |\n"
results_text += "|-------|----------|----------|-----------------|\n"
for hero in filtered_results:
    # Corrected key access
    results_text += f"| {hero['name']} | {hero['picks']} | {hero['wins']} | {hero['win_rate']:.1f}% |\n"

results_text += f"\n## Todos os Heróis por Número de Escolhas\n\n"
results_text += "| Herói | Escolhas | Vitórias | Taxa de Vitória |\n"
results_text += "|-------|----------|----------|-----------------|\n"
for hero in results_list:
    # Corrected key access
    results_text += f"| {hero['name']} | {hero['picks']} | {hero['wins']} | {hero['win_rate']:.1f}% |\n"

# Salvar resultados
print(f"Salvando resultados em {output_file}")
# Corrected file open mode
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(results_text)

print("Análise de taxa de vitória dos heróis concluída.")

