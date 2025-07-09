import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_dir = "/home/ubuntu/analysis_plots"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    # Corrected file open mode
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Gerando visualizações...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# --- Preparar dados para plots ---
radiant_wins = 0
dire_wins = 0
match_durations_min = []
roshan_kill_counts = []
first_roshan_times_min = []
fb_winner_wins = 0
fb_loser_wins = 0
matches_with_fb = 0

for match in matches_data:
    # Corrected key access
    radiant_win = match.get('radiant_win')
    duration = match.get('duration')
    objectives = match.get('objectives')
    players = match.get('players')
    fb_time = match.get('first_blood_time')

    if radiant_win is None or duration is None:
        continue

    # Side wins
    if radiant_win:
        radiant_wins += 1
        winner_side = 2
    else:
        dire_wins += 1
        winner_side = 3
        
    # Duration
    match_durations_min.append(duration / 60)

    # Roshan counts and first time
    current_match_roshan_kills = 0
    current_match_first_roshan_time = None
    if objectives:
        # Corrected key access
        objectives.sort(key=lambda x: x.get('time', 0))
        for obj in objectives:
            # Corrected key access
            if obj.get('type') == 'CHAT_MESSAGE_ROSHAN_KILL':
                current_match_roshan_kills += 1
                if current_match_first_roshan_time is None:
                    # Corrected key access
                    current_match_first_roshan_time = obj.get('time')
                    if current_match_first_roshan_time is not None:
                        first_roshan_times_min.append(current_match_first_roshan_time / 60)
    roshan_kill_counts.append(current_match_roshan_kills)
    
    # FB correlation
    fb_killer_player = None
    if fb_time is not None and fb_time > 0 and players:
        matches_with_fb += 1
        for p in players:
             # Corrected key access
            if p.get('firstblood_claimed') == 1:
                fb_killer_player = p
                break
        if fb_killer_player:
             # Corrected key access
            fb_killer_team = 2 if fb_killer_player.get('player_slot', 0) < 128 else 3
            if fb_killer_team == winner_side:
                fb_winner_wins += 1
            else:
                fb_loser_wins += 1

# --- Gerar Plots ---
sns.set_theme(style="whitegrid")

# 1. Side Win Rate (Bar Plot)
plt.figure(figsize=(6, 5))
# Corrected list strings
sides = ['Radiant', 'Dire']
wins = [radiant_wins, dire_wins]
# Corrected list strings
sns.barplot(x=sides, y=wins, palette=['#5cb85c', '#d9534f'])
# Corrected title/label strings
plt.title('Taxa de Vitória por Lado')
plt.ylabel('Número de Vitórias')
plt.ylim(0, max(wins) * 1.1)
for i, v in enumerate(wins):
    # Corrected text alignment string
    plt.text(i, v + 1, str(v), ha='center', va='bottom')
plt.tight_layout()
plot1_path = os.path.join(output_dir, "side_win_rate.png")
plt.savefig(plot1_path)
plt.close()
print(f"Plot 1 salvo: {plot1_path}")

# 2. Match Duration Distribution (Histogram)
plt.figure(figsize=(8, 5))
sns.histplot(match_durations_min, bins=15, kde=True)
# Corrected title/label strings
plt.title('Distribuição da Duração das Partidas (minutos)')
plt.xlabel('Duração (minutos)')
plt.ylabel('Número de Partidas')
plt.tight_layout()
plot2_path = os.path.join(output_dir, "match_duration_distribution.png")
plt.savefig(plot2_path)
plt.close()
print(f"Plot 2 salvo: {plot2_path}")

# 3. Roshan Kill Count Distribution (Histogram)
plt.figure(figsize=(8, 5))
sns.histplot(roshan_kill_counts, bins=range(max(roshan_kill_counts) + 2), discrete=True)
# Corrected title/label strings
plt.title('Distribuição do Número de Roshans Abatidos por Jogo')
plt.xlabel('Número de Roshans')
plt.ylabel('Número de Partidas')
plt.xticks(range(max(roshan_kill_counts) + 1))
plt.tight_layout()
plot3_path = os.path.join(output_dir, "roshan_kill_count_distribution.png")
plt.savefig(plot3_path)
plt.close()
print(f"Plot 3 salvo: {plot3_path}")

# 4. First Roshan Time Distribution (Histogram)
if first_roshan_times_min:
    plt.figure(figsize=(8, 5))
    sns.histplot(first_roshan_times_min, bins=10, kde=True)
    # Corrected title/label strings
    plt.title('Distribuição do Tempo do Primeiro Roshan (minutos)')
    plt.xlabel('Tempo (minutos)')
    plt.ylabel('Número de Partidas')
    plt.tight_layout()
    plot4_path = os.path.join(output_dir, "first_roshan_time_distribution.png")
    plt.savefig(plot4_path)
    plt.close()
    print(f"Plot 4 salvo: {plot4_path}")
else:
    print("Plot 4 pulado: Sem dados de tempo do primeiro Roshan.")

# 5. First Blood Win Correlation (Bar Plot)
if matches_with_fb > 0:
    plt.figure(figsize=(6, 5))
    # Corrected list strings
    labels = ['Time com FB Venceu', 'Time com FB Perdeu']
    counts = [fb_winner_wins, fb_loser_wins]
    # Corrected list strings
    sns.barplot(x=labels, y=counts, palette=['#5bc0de', '#f0ad4e'])
    # Corrected title/label strings
    plt.title('Resultado da Partida vs. First Blood')
    plt.ylabel('Número de Partidas')
    plt.ylim(0, max(counts) * 1.1)
    for i, v in enumerate(counts):
        # Corrected text alignment string
        plt.text(i, v + 1, str(v), ha='center', va='bottom')
    plt.tight_layout()
    plot5_path = os.path.join(output_dir, "first_blood_correlation.png")
    plt.savefig(plot5_path)
    plt.close()
    print(f"Plot 5 salvo: {plot5_path}")
else:
    print("Plot 5 pulado: Sem dados de First Blood.")

print("Geração de visualizações concluída.")

