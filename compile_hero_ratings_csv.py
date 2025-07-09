import json
import sys
import pandas as pd

input_file = "/home/ubuntu/hero_stats_with_all_ratings.json"
output_csv_file = "/home/ubuntu/pgl_wallachia_s4_hero_stats_with_ratings.csv"

# Carregar dados finais dos heróis com notas
print(f"Carregando dados finais dos heróis: {input_file}")
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        hero_stats = json.load(f)
    print(f"Dados de {len(hero_stats)} heróis carregados.")
except Exception as e:
    print(f"Erro ao carregar dados dos heróis: {e}")
    sys.exit(1)

# Preparar lista de dicionários para o DataFrame
hero_data_list = []
for hero_id_str, stats in hero_stats.items():
    picks = stats.get('picks', 0)
    if picks > 0:
        wins = stats.get('wins', 0)
        win_rate = (wins / picks) * 100 if picks > 0 else 0
        avg_duration_min = (stats.get('total_duration', 0) / picks) / 60 if picks > 0 else 0
        
        hero_data_list.append({
            'Hero ID': int(hero_id_str),
            'Hero Name': stats.get('name', 'Unknown'),
            'Picks': picks,
            'Wins': wins,
            'Win Rate (%)': round(win_rate, 1),
            'Avg Duration (min)': round(avg_duration_min, 1),
            'Avg Kills': round(stats.get('avg_kills', 0), 1),
            'Avg Deaths': round(stats.get('avg_deaths', 0), 1),
            'Avg Assists': round(stats.get('avg_assists', 0), 1),
            'KDA Ratio': round(stats.get('kda_ratio', 0), 2),
            'Avg GPM': round(stats.get('avg_gpm', 0), 1),
            'Avg XPM': round(stats.get('avg_xpm', 0), 1),
            'Primary Attribute': stats.get('primary_attr', 'N/A'),
            'STR Gain': stats.get('str_gain', 0),
            'AGI Gain': stats.get('agi_gain', 0),
            'INT Gain': stats.get('int_gain', 0),
            'Game Phase (Heuristic)': stats.get('game_phase_heuristic', 'N/A'),
            'Early Game Rating (1-5)': stats.get('early_game_rating', 'N/A'),
            'Mid Game Rating (1-5)': stats.get('mid_game_rating', 'N/A'),
            'Late Game Rating (1-5)': stats.get('late_game_rating', 'N/A')
        })

if not hero_data_list:
    print("Nenhum dado de herói encontrado para criar o CSV.")
    sys.exit(1)

# Criar DataFrame e ordenar por nome
df = pd.DataFrame(hero_data_list)
df = df.sort_values(by='Hero Name')

# Salvar em CSV
print(f"Salvando dados compilados com notas em CSV: {output_csv_file}")
try:
    df.to_csv(output_csv_file, index=False, encoding='utf-8')
    print("Arquivo CSV com notas criado com sucesso.")
except Exception as e:
    print(f"Erro ao salvar arquivo CSV: {e}")
    sys.exit(1)

