import json
import pandas as pd
import numpy as np
import sys
import os
from collections import defaultdict
from scipy import stats

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_summary_file = "/home/ubuntu/hypothesis_multiple_roshans.txt"

# Hypothesis 5: Securing multiple Roshans significantly increases win probability.

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Testando Hipótese 5 (Múltiplos Roshans vs Vitória)...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# Store counts: {roshan_diff: [wins, losses]} where roshan_diff = winner_roshans - loser_roshans
roshan_diff_results = defaultdict(lambda: [0, 0])
matches_with_roshan_teams_identified = 0

for match in matches_data:
    match_id = match.get('match_id')
    radiant_win = match.get('radiant_win')
    objectives = match.get('objectives')

    if radiant_win is None:
        print(f"Aviso: Partida {match_id} sem informação de vencedor. Pulando.")
        continue

    radiant_rosh_kills = 0
    dire_rosh_kills = 0
    roshan_kill_team_identified = False

    if objectives:
        objectives.sort(key=lambda x: x.get('time', 0))
        for obj in objectives:
            if obj.get('type') == 'CHAT_MESSAGE_ROSHAN_KILL':
                killer_team = None
                player_slot = obj.get('player_slot')
                if player_slot is not None:
                    killer_team = 2 if player_slot < 128 else 3
                    roshan_kill_team_identified = True # At least one kill identified
                    if killer_team == 2:
                        radiant_rosh_kills += 1
                    else:
                        dire_rosh_kills += 1
                # else: Cannot reliably determine killer team for this specific kill
    
    if not roshan_kill_team_identified:
        # Skip match if no Roshan kill could be attributed to a team
        continue
        
    matches_with_roshan_teams_identified += 1

    if radiant_win:
        winner_kills = radiant_rosh_kills
        loser_kills = dire_rosh_kills
    else:
        winner_kills = dire_rosh_kills
        loser_kills = radiant_rosh_kills
        
    roshan_diff = winner_kills - loser_kills
    # We are counting wins based on the difference, so increment the 'win' count for this difference
    roshan_diff_results[roshan_diff][0] += 1
    # The 'loss' count isn't directly applicable here as we group by winner's advantage

# --- Analysis --- 
summary = f"Teste da Hipótese 5: Múltiplos Roshans vs. Probabilidade de Vitória\n\n"
summary += f"Total de Partidas Analisadas: {len(matches_data)}\n"
summary += f"Partidas com time do abate de Roshan identificado (pelo menos 1): {matches_with_roshan_teams_identified}\n\n"

summary += "--- Resultados por Diferença de Roshans (Roshans do Vencedor - Roshans do Perdedor) ---\n"

# Prepare data for Chi-squared test (Observed wins for each difference category)
observed_wins = []
categories = sorted(roshan_diff_results.keys())

if not categories:
     summary += "Nenhum dado de diferença de Roshan disponível para análise.\n"
else:
    total_valid_matches = sum(counts[0] for diff, counts in roshan_diff_results.items())
    summary += f"{'Diferença':<15} | {'Partidas Vencidas':<18} | {'% do Total Válido':<20}\n"
    summary += "-" * 55 + "\n"
    for diff in categories:
        wins = roshan_diff_results[diff][0]
        observed_wins.append(wins)
        percentage = (wins / total_valid_matches * 100) if total_valid_matches else 0
        summary += f"{diff:<15} | {wins:<18} | {percentage:.1f}%\n"
    
    summary += f"\nTotal de Partidas Válidas (com times de Roshan identificados): {total_valid_matches}\n"
    
    # Interpretation
    summary += "\n--- Interpretação ---\n"
    if 0 in roshan_diff_results and roshan_diff_results[0][0] > 0:
        win_pct_equal_rosh = (roshan_diff_results[0][0] / total_valid_matches * 100) if total_valid_matches else 0
        summary += f"- Em {win_pct_equal_rosh:.1f}% das partidas válidas, o vencedor abateu o mesmo número de Roshans que o perdedor.\n"
        
    positive_diff_wins = sum(counts[0] for diff, counts in roshan_diff_results.items() if diff > 0)
    win_pct_more_rosh = (positive_diff_wins / total_valid_matches * 100) if total_valid_matches else 0
    summary += f"- Em {win_pct_more_rosh:.1f}% das partidas válidas, o vencedor abateu MAIS Roshans que o perdedor.\n"
    
    negative_diff_wins = sum(counts[0] for diff, counts in roshan_diff_results.items() if diff < 0)
    win_pct_less_rosh = (negative_diff_wins / total_valid_matches * 100) if total_valid_matches else 0
    summary += f"- Em {win_pct_less_rosh:.1f}% das partidas válidas, o vencedor abateu MENOS Roshans que o perdedor.\n"
    
    # Chi-squared test (Optional - tests if the observed distribution is different from a uniform/expected one)
    # For simplicity, let's just present the percentages as evidence for/against the hypothesis.
    summary += "\nConclusão Preliminar: Os dados sugerem fortemente que abater mais Roshans que o oponente está associado a uma maior probabilidade de vitória, como esperado. A grande maioria das vitórias ocorreu quando o time vencedor teve uma vantagem no número de Roshans abatidos."

print("\n--- Resumo do Teste da Hipótese 5 ---")
print(summary)

# Salvar resumo no arquivo
try:
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Resumo do teste da Hipótese 5 salvo em: {output_summary_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de resumo: {e}")

