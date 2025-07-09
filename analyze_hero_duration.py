import json
import pandas as pd
import numpy as np
from collections import defaultdict
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
hero_constants_path = "/home/ubuntu/dota_hero_constants.json"
output_file = "/home/ubuntu/hero_duration_analysis.txt"
MIN_PICKS_THRESHOLD = 5 # Minimum number of picks to include a hero in the list

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
        hero_constants = json.load(f)
    print(f"Constantes de {len(hero_constants)} heróis carregadas.")
except Exception as e:
    print(f"Erro ao carregar constantes de heróis: {e}")
    sys.exit(1)

# Criar mapeamento de ID para nome do herói
hero_id_to_name = {}
for hero_id_str, hero_data in hero_constants.items():
    if 'id' in hero_data and 'localized_name' in hero_data:
        hero_id_to_name[hero_data['id']] = hero_data['localized_name']

print(f"Mapeamento criado para {len(hero_id_to_name)} heróis.")

# Inicializar dicionário para armazenar duração total e contagem de partidas por herói
hero_duration_stats = defaultdict(lambda: {'total_duration': 0, 'match_count': 0})

# Processar cada partida
for match in matches_data:
    duration = match.get('duration')
    players = match.get('players', [])

    if duration is None or not players:
        continue

    # Obter IDs dos heróis presentes na partida
    heroes_in_match = set()
    for player in players:
        hero_id = player.get('hero_id')
        if hero_id:
            heroes_in_match.add(hero_id)
            
    # Adicionar duração e contagem para cada herói na partida
    for hero_id in heroes_in_match:
        hero_duration_stats[hero_id]['total_duration'] += duration
        hero_duration_stats[hero_id]['match_count'] += 1

# Calcular duração média e preparar resultados
results_list = []
for hero_id, stats in hero_duration_stats.items():
    match_count = stats['match_count']
    total_duration = stats['total_duration']
    if match_count > 0:
        avg_duration_seconds = total_duration / match_count
        avg_duration_minutes = avg_duration_seconds / 60
        hero_name = hero_id_to_name.get(hero_id, f"Unknown Hero ID: {hero_id}")
        results_list.append({
            'name': hero_name,
            'id': hero_id,
            'picks': match_count, # Renomeado de match_count para consistência
            'avg_duration_min': avg_duration_minutes
        })

# Filtrar e ordenar por duração média (para heróis com picks >= threshold)
filtered_results = [r for r in results_list if r['picks'] >= MIN_PICKS_THRESHOLD]
filtered_results.sort(key=lambda x: x['avg_duration_min'], reverse=True)

# Preparar texto do resultado
results_text = f"# Análise de Heróis Associados a Partidas Mais Demoradas - PGL Wallachia Season 4\n\n"
results_text += f"Total de Partidas Analisadas: {len(matches_data)}\n"
results_text += f"Total de Heróis Jogados: {len(hero_duration_stats)}\n"
results_text += f"Limiar Mínimo de Escolhas para Ranking: {MIN_PICKS_THRESHOLD}\n\n"

results_text += f"## Heróis por Duração Média da Partida (Escolhas >= {MIN_PICKS_THRESHOLD})\n\n"
results_text += "| Herói | Escolhas | Duração Média (min) |\n"
results_text += "|-------|----------|---------------------|\n"
for hero in filtered_results:
    results_text += f"| {hero['name']} | {hero['picks']} | {hero['avg_duration_min']:.1f} |\n"

# Salvar resultados
print(f"Salvando resultados em {output_file}")
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(results_text)

print("Análise de duração de partida por herói concluída.")

