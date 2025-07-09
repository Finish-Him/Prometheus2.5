import json
import pandas as pd
import numpy as np
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_summary_file = "/home/ubuntu/xp_comebacks_analysis.txt"

# Define thresholds for XP comeback analysis
COMEBACK_THRESHOLD_XP = 15000 # Example threshold, can be adjusted
COMEBACK_TIME_START_SECONDS = 20 * 60 # 20 minutes

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Analisando viradas baseadas em déficit de XP...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

xp_comeback_matches = []
valid_matches_for_xp_analysis = 0

for match in matches_data:
    match_id = match.get('match_id')
    radiant_win = match.get('radiant_win')
    xp_adv_ts = match.get('radiant_xp_adv') # XP advantage time series
    duration = match.get('duration')

    if radiant_win is None or xp_adv_ts is None or duration is None:
        # print(f"Aviso: Partida {match_id} faltando dados essenciais (win, xp_adv, duration). Pulando.")
        continue
        
    # Check if data exists beyond the start time threshold
    if duration < COMEBACK_TIME_START_SECONDS or len(xp_adv_ts) <= COMEBACK_TIME_START_SECONDS:
        # print(f"Aviso: Partida {match_id} muito curta ou dados de XP faltando após {COMEBACK_TIME_START_SECONDS // 60} min. Pulando.")
        continue
        
    valid_matches_for_xp_analysis += 1
    relevant_xp_adv = xp_adv_ts[COMEBACK_TIME_START_SECONDS:]
    is_comeback = False
    max_deficit_overcome = 0
    comeback_winner = None

    if radiant_win:
        # Radiant won, check for lowest XP value (highest Dire advantage)
        min_xp_adv = min(relevant_xp_adv)
        if min_xp_adv <= -COMEBACK_THRESHOLD_XP:
            is_comeback = True
            max_deficit_overcome = -min_xp_adv
            comeback_winner = 'Radiant'
    else:
        # Dire won, check for highest XP value (highest Radiant advantage)
        max_xp_adv = max(relevant_xp_adv)
        if max_xp_adv >= COMEBACK_THRESHOLD_XP:
            is_comeback = True
            max_deficit_overcome = max_xp_adv
            comeback_winner = 'Dire'

    if is_comeback:
        xp_comeback_matches.append({
            'match_id': match_id,
            'winner': comeback_winner,
            'max_xp_deficit_overcome': max_deficit_overcome,
            'duration_seconds': duration
        })
        print(f"Virada de XP detectada! Partida: {match_id}, Vencedor: {comeback_winner}, Déficit Máximo Superado: {max_deficit_overcome} XP")

print(f"\nAnálise concluída. Total de {len(xp_comeback_matches)} viradas significativas de XP encontradas (déficit > {COMEBACK_THRESHOLD_XP} XP após {COMEBACK_TIME_START_SECONDS // 60} min) em {valid_matches_for_xp_analysis} partidas válidas.")

# Criar e salvar um resumo em texto
summary_text = f"Análise de Viradas Significativas por Déficit de XP - PGL Wallachia Season 4\n"
summary_text += f"Total de Partidas Analisadas: {len(matches_data)}\n"
summary_text += f"Partidas Válidas para Análise de XP (com dados após {COMEBACK_TIME_START_SECONDS // 60} min): {valid_matches_for_xp_analysis}\n"
summary_text += f"Critério de Virada: Superar um déficit de >{COMEBACK_THRESHOLD_XP} XP após {COMEBACK_TIME_START_SECONDS // 60} minutos.\n"
summary_text += f"Total de Viradas de XP Encontradas: {len(xp_comeback_matches)}\n\n"

if xp_comeback_matches:
    summary_text += "Partidas com Virada de XP:\n"
    for cb in xp_comeback_matches:
        duration_str = f"{cb['duration_seconds'] // 60}:{cb['duration_seconds'] % 60:02d}"
        summary_text += f"  - Partida ID: {cb['match_id']}, Vencedor: {cb['winner']}, Déficit Máx. Superado: {cb['max_xp_deficit_overcome']}, Duração: {duration_str}\n"
else:
    summary_text += "Nenhuma partida atendeu aos critérios de virada significativa por déficit de XP.\n"

try:
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    print(f"Resumo da análise de viradas de XP salvo em: {output_summary_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de resumo de viradas de XP: {e}")

