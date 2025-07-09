import json
import sys
import numpy as np

input_file = "/home/ubuntu/hero_stats_with_phase.json"
output_file = "/home/ubuntu/hero_stats_with_kda_gpm.json"

# Carregar dados dos heróis com fase
print(f"Carregando dados dos heróis: {input_file}")
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        hero_stats = json.load(f)
    print(f"Dados de {len(hero_stats)} heróis carregados.")
except Exception as e:
    print(f"Erro ao carregar dados dos heróis: {e}")
    sys.exit(1)

# Calcular KDA e GPM médios
print("Calculando KDA e GPM médios...")
for hero_id_str, stats in hero_stats.items():
    picks = stats.get('picks', 0)
    if picks > 0:
        total_kills = stats.get('total_kills', 0)
        total_deaths = stats.get('total_deaths', 0)
        total_assists = stats.get('total_assists', 0)
        total_gpm = stats.get('total_gpm', 0)
        
        # Médias por partida
        stats['avg_kills'] = total_kills / picks
        stats['avg_deaths'] = total_deaths / picks
        stats['avg_assists'] = total_assists / picks
        stats['avg_gpm'] = total_gpm / picks
        
        # KDA Ratio (usando totais para evitar média de razões)
        # Usar max(1, total_deaths) para evitar divisão por zero
        stats['kda_ratio'] = (total_kills + total_assists) / max(1, total_deaths)
    else:
        # Definir valores padrão para heróis não escolhidos (se houver)
        stats['avg_kills'] = 0
        stats['avg_deaths'] = 0
        stats['avg_assists'] = 0
        stats['avg_gpm'] = 0
        stats['kda_ratio'] = 0

# Salvar dados atualizados
print(f"Salvando dados atualizados com KDA e GPM em {output_file}")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hero_stats, f, indent=4)
    print("Cálculo de KDA e GPM concluído e salvo.")
except Exception as e:
    print(f"Erro ao salvar dados atualizados: {e}")
    sys.exit(1)

