import json
import sys
import numpy as np
import pandas as pd

input_file = "/home/ubuntu/aggregated_hero_stats.json"
output_file = "/home/ubuntu/hero_stats_with_phase.json"

# Carregar dados agregados dos heróis
print(f"Carregando dados agregados dos heróis: {input_file}")
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        hero_stats = json.load(f)
    print(f"Dados de {len(hero_stats)} heróis carregados.")
except Exception as e:
    print(f"Erro ao carregar dados agregados: {e}")
    sys.exit(1)

# Calcular estatísticas necessárias e preparar para análise
hero_data_list = []
for hero_id, stats in hero_stats.items():
    if stats['picks'] > 0:
        avg_duration_min = (stats['total_duration'] / stats['picks']) / 60
        primary_attr = stats.get('primary_attr')
        primary_gain = 0
        if primary_attr == 'str':
            primary_gain = stats.get('str_gain', 0)
        elif primary_attr == 'agi':
            primary_gain = stats.get('agi_gain', 0)
        elif primary_attr == 'int':
            primary_gain = stats.get('int_gain', 0)
            
        hero_data_list.append({
            'hero_id': hero_id,
            'avg_duration_min': avg_duration_min,
            'primary_gain': primary_gain if primary_gain else 0 # Handle None
        })

if not hero_data_list:
    print("Nenhum herói com picks encontrado para análise de fase.")
    sys.exit(1)

# Converter para DataFrame para facilitar cálculo de quantis
df = pd.DataFrame(hero_data_list)

# Definir quantis para classificação (Exemplo: 33º e 66º percentis)
low_duration_threshold = df['avg_duration_min'].quantile(0.33)
high_duration_threshold = df['avg_duration_min'].quantile(0.66)
low_gain_threshold = df['primary_gain'].quantile(0.33)
high_gain_threshold = df['primary_gain'].quantile(0.66)

print(f"Limiares - Duração (min): Baixo < {low_duration_threshold:.1f}, Alto > {high_duration_threshold:.1f}")
print(f"Limiares - Ganho Primário: Baixo < {low_gain_threshold:.2f}, Alto > {high_gain_threshold:.2f}")

# Classificar heróis
print("Classificando heróis por fase de jogo (heurística)...")
for hero_id_str, stats in hero_stats.items():
    hero_id = int(hero_id_str) # JSON keys are strings
    if stats['picks'] > 0:
        # Encontrar dados correspondentes no DataFrame
        hero_row = df[df['hero_id'] == hero_id_str].iloc[0]
        avg_duration = hero_row['avg_duration_min']
        primary_gain = hero_row['primary_gain']
        
        # Regras heurísticas de classificação
        if primary_gain >= high_gain_threshold and avg_duration >= high_duration_threshold:
            phase = "Late"
        elif primary_gain >= high_gain_threshold:
             phase = "Mid-Late" # Tendência Late
        elif avg_duration >= high_duration_threshold:
             phase = "Mid-Late" # Tendência Late
        elif primary_gain <= low_gain_threshold and avg_duration <= low_duration_threshold:
            phase = "Early"
        elif primary_gain <= low_gain_threshold:
            phase = "Early-Mid" # Tendência Early
        elif avg_duration <= low_duration_threshold:
            phase = "Early-Mid" # Tendência Early
        else:
            phase = "Mid"
            
        stats['game_phase_heuristic'] = phase
    else:
        stats['game_phase_heuristic'] = "N/A"

# Salvar dados atualizados
print(f"Salvando dados atualizados com classificação de fase em {output_file}")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hero_stats, f, indent=4)
    print("Classificação de fase de jogo concluída e salva.")
except Exception as e:
    print(f"Erro ao salvar dados atualizados: {e}")
    sys.exit(1)

