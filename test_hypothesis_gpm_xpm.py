import json
import pandas as pd
import numpy as np
import sys
import os
from scipy import stats

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_summary_file = "/home/ubuntu/hypothesis_gpm_xpm_diff.txt"

# Hypothesis: The average difference in GPM and XPM between the winning and losing teams at the end of the match is significantly positive.

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Testando Hipótese (Diferença GPM/XPM Vencedor vs Perdedor)...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# Lists to store differences for each match
gpm_diffs = [] # Winner Avg GPM - Loser Avg GPM
xpm_diffs = [] # Winner Avg XPM - Loser Avg XPM
valid_matches_count = 0

for match in matches_data:
    match_id = match.get('match_id')
    radiant_win = match.get('radiant_win')
    players = match.get('players')

    if radiant_win is None or not players or len(players) != 10:
        print(f"Aviso: Partida {match_id} sem informação de vencedor ou dados de jogadores inválidos. Pulando.")
        continue

    winner_gpm = []
    loser_gpm = []
    winner_xpm = []
    loser_xpm = []

    for p in players:
        gpm = p.get('gold_per_min')
        xpm = p.get('xp_per_min')
        player_slot = p.get('player_slot')

        if gpm is None or xpm is None or player_slot is None:
            print(f"Aviso: Jogador na partida {match_id} com dados GPM/XPM/Slot ausentes. Pulando partida.")
            winner_gpm, loser_gpm, winner_xpm, loser_xpm = [], [], [], [] # Clear lists for this match
            break # Skip to next match

        is_radiant = player_slot < 128
        
        if (radiant_win and is_radiant) or (not radiant_win and not is_radiant):
            # Player is on the winning team
            winner_gpm.append(gpm)
            winner_xpm.append(xpm)
        else:
            # Player is on the losing team
            loser_gpm.append(gpm)
            loser_xpm.append(xpm)
            
    # Check if we successfully processed all players for the match
    if len(winner_gpm) == 5 and len(loser_gpm) == 5:
        avg_winner_gpm = np.mean(winner_gpm)
        avg_loser_gpm = np.mean(loser_gpm)
        avg_winner_xpm = np.mean(winner_xpm)
        avg_loser_xpm = np.mean(loser_xpm)
        
        gpm_diffs.append(avg_winner_gpm - avg_loser_gpm)
        xpm_diffs.append(avg_winner_xpm - avg_loser_xpm)
        valid_matches_count += 1
    elif winner_gpm or loser_gpm: # Only print if we started processing but failed
         print(f"Aviso: Partida {match_id} não teve 5 jogadores em cada time após processamento. Pulando.")


# --- Analysis --- 
summary = f"Teste da Hipótese: Diferença de GPM/XPM entre Vencedores e Perdedores\n\n"
summary += f"Total de Partidas Analisadas: {len(matches_data)}\n"
summary += f"Partidas Válidas para Análise (com dados completos de GPM/XPM para 10 jogadores): {valid_matches_count}\n\n"

if valid_matches_count > 0:
    # GPM Analysis
    mean_gpm_diff = np.mean(gpm_diffs)
    std_gpm_diff = np.std(gpm_diffs)
    # One-sample t-test: Is the mean difference significantly greater than 0?
    gpm_t_stat, gpm_p_value = stats.ttest_1samp(gpm_diffs, 0, alternative='greater') 
    
    summary += "--- Análise da Diferença de GPM (Ouro Por Minuto) ---\n"
    summary += f"Diferença Média (GPM Vencedor - GPM Perdedor): {mean_gpm_diff:.2f}\n"
    summary += f"Desvio Padrão da Diferença: {std_gpm_diff:.2f}\n"
    summary += f"Teste t ( unilateral, H1: diff > 0 ): t = {gpm_t_stat:.2f}, p = {gpm_p_value:.4f}\n"
    if gpm_p_value < 0.05:
        summary += "Conclusão GPM: A diferença média de GPM entre vencedores e perdedores é estatisticamente significativa e positiva (p < 0.05).\n"
    else:
        summary += "Conclusão GPM: Não há evidência estatística suficiente para afirmar que a diferença média de GPM seja significativamente positiva (p >= 0.05).\n"

    # XPM Analysis
    mean_xpm_diff = np.mean(xpm_diffs)
    std_xpm_diff = np.std(xpm_diffs)
    # One-sample t-test: Is the mean difference significantly greater than 0?
    xpm_t_stat, xpm_p_value = stats.ttest_1samp(xpm_diffs, 0, alternative='greater')
    
    summary += "\n--- Análise da Diferença de XPM (Experiência Por Minuto) ---\n"
    summary += f"Diferença Média (XPM Vencedor - XPM Perdedor): {mean_xpm_diff:.2f}\n"
    summary += f"Desvio Padrão da Diferença: {std_xpm_diff:.2f}\n"
    summary += f"Teste t ( unilateral, H1: diff > 0 ): t = {xpm_t_stat:.2f}, p = {xpm_p_value:.4f}\n"
    if xpm_p_value < 0.05:
        summary += "Conclusão XPM: A diferença média de XPM entre vencedores e perdedores é estatisticamente significativa e positiva (p < 0.05).\n"
    else:
        summary += "Conclusão XPM: Não há evidência estatística suficiente para afirmar que a diferença média de XPM seja significativamente positiva (p >= 0.05).\n"
else:
    summary += "Nenhuma partida válida encontrada para realizar a análise de GPM/XPM.\n"

print("\n--- Resumo do Teste da Hipótese GPM/XPM ---")
print(summary)

# Salvar resumo no arquivo
try:
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Resumo do teste da hipótese GPM/XPM salvo em: {output_summary_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de resumo: {e}")

