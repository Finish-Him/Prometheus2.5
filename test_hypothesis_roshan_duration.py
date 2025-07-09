import json
import pandas as pd
import numpy as np
import sys
import os
from scipy import stats

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_summary_file = "/home/ubuntu/hypothesis_roshan_duration.txt"

# Hypothesis 1: Getting the first Roshan before 20 minutes correlates with shorter game durations.
ROSHAN_TIME_THRESHOLD_SECONDS = 20 * 60
DURATION_THRESHOLD_MINUTES = 35
DURATION_THRESHOLD_SECONDS = DURATION_THRESHOLD_MINUTES * 60

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    # Corrected file open mode
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Testando Hipótese 1 (Roshan < 20min vs Duração)...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# Lists to store durations based on first Roshan time
durations_roshan_early = [] # First Roshan < 20 min
durations_roshan_late_or_none = [] # First Roshan >= 20 min or no Roshan
matches_with_roshan = 0

for match in matches_data:
    # Corrected key access
    match_id = match.get('match_id')
    duration = match.get('duration')
    objectives = match.get('objectives')

    if duration is None:
        print(f"Aviso: Partida {match_id} sem duração. Pulando.")
        continue

    first_roshan_time = None
    if objectives:
        # Corrected key access
        objectives.sort(key=lambda x: x.get('time', 0))
        for obj in objectives:
             # Corrected key access
            if obj.get('type') == 'CHAT_MESSAGE_ROSHAN_KILL':
                 # Corrected key access
                first_roshan_time = obj.get('time')
                break # Found the first Roshan kill
    
    if first_roshan_time is not None:
        matches_with_roshan += 1
        if first_roshan_time < ROSHAN_TIME_THRESHOLD_SECONDS:
            durations_roshan_early.append(duration)
        else:
            durations_roshan_late_or_none.append(duration)
    else:
        # No Roshan killed in this match
        durations_roshan_late_or_none.append(duration)

# --- Analysis --- 
summary = f"Teste da Hipótese 1: Roshan antes de {ROSHAN_TIME_THRESHOLD_SECONDS // 60} min vs. Duração da Partida\n\n"
summary += f"Total de Partidas Analisadas: {len(matches_data)}\n"
summary += f"Partidas com Roshan registrado: {matches_with_roshan}\n\n"

summary += f"--- Grupo 1: Primeiro Roshan ANTES de {ROSHAN_TIME_THRESHOLD_SECONDS // 60} minutos ---\n"
if durations_roshan_early:
    count_early = len(durations_roshan_early)
    avg_duration_early = np.mean(durations_roshan_early)
    median_duration_early = np.median(durations_roshan_early)
    std_duration_early = np.std(durations_roshan_early)
    ended_before_threshold_early = sum(1 for d in durations_roshan_early if d < DURATION_THRESHOLD_SECONDS)
    pct_ended_before_threshold_early = (ended_before_threshold_early / count_early * 100) if count_early else 0
    
    summary += f"Número de Partidas: {count_early}\n"
    summary += f"Duração Média: {avg_duration_early / 60:.1f} min\n"
    summary += f"Duração Mediana: {median_duration_early / 60:.1f} min\n"
    summary += f"Desvio Padrão da Duração: {std_duration_early / 60:.1f} min\n"
    summary += f"Partidas terminadas ANTES de {DURATION_THRESHOLD_MINUTES} min: {ended_before_threshold_early} ({pct_ended_before_threshold_early:.1f}%)\n"
else:
    summary += "Nenhuma partida encontrada neste grupo.\n"

summary += f"\n--- Grupo 2: Primeiro Roshan DEPOIS de {ROSHAN_TIME_THRESHOLD_SECONDS // 60} minutos ou Sem Roshan ---\n"
if durations_roshan_late_or_none:
    count_late = len(durations_roshan_late_or_none)
    avg_duration_late = np.mean(durations_roshan_late_or_none)
    median_duration_late = np.median(durations_roshan_late_or_none)
    std_duration_late = np.std(durations_roshan_late_or_none)
    ended_before_threshold_late = sum(1 for d in durations_roshan_late_or_none if d < DURATION_THRESHOLD_SECONDS)
    pct_ended_before_threshold_late = (ended_before_threshold_late / count_late * 100) if count_late else 0

    summary += f"Número de Partidas: {count_late}\n"
    summary += f"Duração Média: {avg_duration_late / 60:.1f} min\n"
    summary += f"Duração Mediana: {median_duration_late / 60:.1f} min\n"
    summary += f"Desvio Padrão da Duração: {std_duration_late / 60:.1f} min\n"
    summary += f"Partidas terminadas ANTES de {DURATION_THRESHOLD_MINUTES} min: {ended_before_threshold_late} ({pct_ended_before_threshold_late:.1f}%)\n"
else:
    summary += "Nenhuma partida encontrada neste grupo.\n"

# Statistical Test (t-test to compare means, if both groups have data)
summary += "\n--- Teste Estatístico (Comparação das Durações Médias) ---\n"
if durations_roshan_early and durations_roshan_late_or_none:
    # Check for variance equality (Levene's test)
    levene_stat, levene_p = stats.levene(durations_roshan_early, durations_roshan_late_or_none)
    equal_var = levene_p > 0.05 # Assume equal variance if p > 0.05
    summary += f"Teste de Levene para igualdade de variâncias: p = {levene_p:.4f} (Equal var = {equal_var})\n"
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(durations_roshan_early, durations_roshan_late_or_none, equal_var=equal_var)
    summary += f"Teste t para diferença nas durações médias: t = {t_stat:.2f}, p = {p_value:.4f}\n"
    if p_value < 0.05:
        summary += "Conclusão: Há uma diferença estatisticamente significativa na duração média das partidas entre os dois grupos (p < 0.05).\n"
    else:
        summary += "Conclusão: Não há evidência estatística suficiente para afirmar uma diferença significativa na duração média das partidas entre os dois grupos (p >= 0.05).\n"
else:
    summary += "Teste t não realizado (um ou ambos os grupos estão vazios).\n"

print("\n--- Resumo do Teste da Hipótese 1 ---")
print(summary)

# Salvar resumo no arquivo
try:
    # Corrected file open mode
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Resumo do teste da Hipótese 1 salvo em: {output_summary_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de resumo: {e}")

