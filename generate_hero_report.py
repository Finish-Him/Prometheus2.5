import json
import sys
import pandas as pd

input_file = "/home/ubuntu/hero_stats_with_kda_gpm.json"
output_report_file = "/home/ubuntu/detailed_hero_report.md"
TOP_N = 10 # Number of heroes for top lists in the report
MIN_PICKS_THRESHOLD = 5 # Consistent with previous analyses

# Carregar dados finais dos heróis
print(f"Carregando dados finais dos heróis: {input_file}")
try:
    # Corrected file open mode
    with open(input_file, 'r', encoding='utf-8') as f:
        hero_stats_dict = json.load(f)
    print(f"Dados de {len(hero_stats_dict)} heróis carregados.")
except Exception as e:
    print(f"Erro ao carregar dados dos heróis: {e}")
    sys.exit(1)

# Converter para lista e depois DataFrame para facilitar ordenação
hero_data_list = []
for hero_id_str, stats in hero_stats_dict.items():
    # Corrected key access
    picks = stats.get('picks', 0)
    if picks > 0:
        wins = stats.get('wins', 0)
        win_rate = (wins / picks) * 100 if picks > 0 else 0
        # Corrected key access
        avg_duration_min = (stats.get('total_duration', 0) / picks) / 60 if picks > 0 else 0
        
        # Corrected key access
        stats['hero_id'] = int(hero_id_str)
        stats['win_rate'] = win_rate
        stats['avg_duration_min'] = avg_duration_min
        hero_data_list.append(stats)

if not hero_data_list:
    print("Nenhum dado de herói encontrado para gerar o relatório.")
    sys.exit(1)

df = pd.DataFrame(hero_data_list)

# Filtrar por mínimo de picks para rankings principais
# Corrected key access
df_filtered = df[df['picks'] >= MIN_PICKS_THRESHOLD].copy()

# --- Preparar Conteúdo do Relatório --- 
report_content = f"# Relatório Detalhado dos Heróis - PGL Wallachia Season 4\n\n"
report_content += f"Este relatório resume as estatísticas detalhadas para os {len(df)} heróis jogados nas 115 partidas analisadas do PGL Wallachia Season 4. O arquivo CSV complementar (`pgl_wallachia_s4_hero_stats.csv`) contém a tabela completa com todos os dados.\n\n"
report_content += f"**Nota:** Rankings principais consideram apenas heróis com {MIN_PICKS_THRESHOLD} ou mais escolhas.\n\n"

# 1. Win Rate
# Corrected column name
df_sorted_win_rate = df_filtered.sort_values(by='win_rate', ascending=False)
report_content += f"## Top {TOP_N} Heróis por Taxa de Vitória (Win Rate)\n\n"
report_content += "| Rank | Herói | Escolhas | Taxa de Vitória |\n"
report_content += "|------|-------|----------|-----------------|\n"
df_sorted_win_rate['rank'] = df_sorted_win_rate['win_rate'].rank(method='min', ascending=False)
for i, row in df_sorted_win_rate.head(TOP_N).iterrows():
    # Corrected key access
    report_content += f"| {int(row['rank'])} | {row['name']} | {row['picks']} | {row['win_rate']:.1f}% |\n"
report_content += "\n"

# 2. KDA Ratio
# Corrected column name
df_sorted_kda = df_filtered.sort_values(by='kda_ratio', ascending=False)
report_content += f"## Top {TOP_N} Heróis por KDA Ratio\n\n"
report_content += "| Rank | Herói | Escolhas | KDA Ratio |\n"
report_content += "|------|-------|----------|-----------|\n"
df_sorted_kda['rank'] = df_sorted_kda['kda_ratio'].rank(method='min', ascending=False)
for i, row in df_sorted_kda.head(TOP_N).iterrows():
    # Corrected key access
    report_content += f"| {int(row['rank'])} | {row['name']} | {row['picks']} | {row['kda_ratio']:.2f} |\n"
report_content += "\n"

# 3. GPM Médio
# Corrected column name
df_sorted_gpm = df_filtered.sort_values(by='avg_gpm', ascending=False)
report_content += f"## Top {TOP_N} Heróis por GPM Médio\n\n"
report_content += "| Rank | Herói | Escolhas | GPM Médio |\n"
report_content += "|------|-------|----------|-----------|\n"
df_sorted_gpm['rank'] = df_sorted_gpm['avg_gpm'].rank(method='min', ascending=False)
for i, row in df_sorted_gpm.head(TOP_N).iterrows():
    # Corrected key access
    report_content += f"| {int(row['rank'])} | {row['name']} | {row['picks']} | {row['avg_gpm']:.1f} |\n"
report_content += "\n"

# 4. Duração Média da Partida
# Corrected column name
df_sorted_duration = df_filtered.sort_values(by='avg_duration_min', ascending=False)
report_content += f"## Top {TOP_N} Heróis por Duração Média da Partida (Mais Longa)\n\n"
report_content += "| Rank | Herói | Escolhas | Duração Média (min) |\n"
report_content += "|------|-------|----------|---------------------|\n"
df_sorted_duration['rank'] = df_sorted_duration['avg_duration_min'].rank(method='min', ascending=False)
for i, row in df_sorted_duration.head(TOP_N).iterrows():
    # Corrected key access
    report_content += f"| {int(row['rank'])} | {row['name']} | {row['picks']} | {row['avg_duration_min']:.1f} |\n"
report_content += "\n"

# 5. Classificação por Fase de Jogo (Distribuição)
# Corrected column name
phase_counts = df['game_phase_heuristic'].value_counts()
report_content += f"## Distribuição por Fase de Jogo (Heurística)\n\n"
report_content += "| Fase        | Contagem de Heróis |\n"
report_content += "|-------------|--------------------|\n"
for phase, count in phase_counts.items():
    report_content += f"| {phase:<11} | {count:<18} |\n"
report_content += "\n"

# 6. Ganho de Atributos (Top por Ganho Total)
# Corrected calculation and column names
df['total_gain'] = df['str_gain'] + df['agi_gain'] + df['int_gain']
df_sorted_total_gain = df.sort_values(by='total_gain', ascending=False)
report_content += f"## Top {TOP_N} Heróis por Ganho Total de Atributos por Nível\n\n"
report_content += "| Rank | Herói | Ganho Total | STR Gain | AGI Gain | INT Gain |\n"
report_content += "|------|-------|-------------|----------|----------|----------|\n"
df_sorted_total_gain['rank'] = df_sorted_total_gain['total_gain'].rank(method='min', ascending=False)
for i, row in df_sorted_total_gain.head(TOP_N).iterrows():
    # Corrected key access
    report_content += f"| {int(row['rank'])} | {row['name']} | {row['total_gain']:.2f} | {row['str_gain']:.2f} | {row['agi_gain']:.2f} | {row['int_gain']:.2f} |\n"
report_content += "\n"

# Salvar Relatório
print(f"Salvando relatório detalhado em {output_report_file}")
try:
    # Corrected file open mode
    with open(output_report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print("Relatório detalhado dos heróis gerado com sucesso.")
except Exception as e:
    print(f"Erro ao salvar relatório: {e}")
    sys.exit(1)

