import json
import pandas as pd
import numpy as np
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_comebacks_file = "/home/ubuntu/analysis_comebacks.json"
output_summary_file = "/home/ubuntu/analysis_comebacks_summary.txt"

COMEBACK_THRESHOLD_GOLD = 10000
COMEBACK_TIME_START_SECONDS = 20 * 60 # 20 minutes

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Analisando viradas...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

comeback_matches = []

for match in matches_data:
    match_id = match.get('match_id')
    radiant_win = match.get('radiant_win')
    gold_adv_ts = match.get('radiant_gold_adv')
    duration = match.get('duration')

    if match_id is None or radiant_win is None or gold_adv_ts is None or duration is None:
        print(f"Aviso: Partida {match_id} faltando dados essenciais (win, gold_adv, duration). Pulando.")
        continue

    # Assume gold_adv_ts is a list where index corresponds to time in seconds
    max_deficit_overcome = 0
    is_comeback = False
    comeback_winner = None

    # Check gold advantage after COMEBACK_TIME_START_SECONDS
    relevant_gold_adv = gold_adv_ts[COMEBACK_TIME_START_SECONDS:]
    if not relevant_gold_adv:
        continue # Match too short or gold data missing after threshold

    if radiant_win:
        # Radiant won, check for lowest gold value (highest Dire advantage)
        min_gold_adv = min(relevant_gold_adv)
        if min_gold_adv <= -COMEBACK_THRESHOLD_GOLD:
            is_comeback = True
            max_deficit_overcome = -min_gold_adv
            comeback_winner = 'Radiant'
    else:
        # Dire won, check for highest gold value (highest Radiant advantage)
        max_gold_adv = max(relevant_gold_adv)
        if max_gold_adv >= COMEBACK_THRESHOLD_GOLD:
            is_comeback = True
            max_deficit_overcome = max_gold_adv
            comeback_winner = 'Dire'

    if is_comeback:
        comeback_matches.append({
            'match_id': match_id,
            'winner': comeback_winner,
            'max_deficit_overcome': max_deficit_overcome,
            'duration_seconds': duration
        })
        print(f"Virada detectada! Partida: {match_id}, Vencedor: {comeback_winner}, Déficit Máximo Superado: {max_deficit_overcome} ouro")

print(f"\nAnálise concluída. Total de {len(comeback_matches)} viradas significativas encontradas (déficit > {COMEBACK_THRESHOLD_GOLD} ouro após {COMEBACK_TIME_START_SECONDS // 60} min).")

# Salvar lista de partidas com virada em JSON
try:
    with open(output_comebacks_file, 'w', encoding='utf-8') as f:
        json.dump(comeback_matches, f, indent=4)
    print(f"Lista de partidas com virada salva em: {output_comebacks_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo JSON de viradas: {e}")

# Criar e salvar um resumo em texto
summary_text = f"Análise de Viradas Significativas - PGL Wallachia Season 4\n"
summary_text += f"Total de Partidas Analisadas: {len(matches_data)}\n"
summary_text += f"Critério de Virada: Superar um déficit de >{COMEBACK_THRESHOLD_GOLD} ouro após {COMEBACK_TIME_START_SECONDS // 60} minutos.\n"
summary_text += f"Total de Viradas Encontradas: {len(comeback_matches)}\n\n"

if comeback_matches:
    summary_text += "Partidas com Virada:\n"
    for cb in comeback_matches:
        duration_str = f"{cb['duration_seconds'] // 60}:{cb['duration_seconds'] % 60:02d}"
        summary_text += f"  - Partida ID: {cb['match_id']}, Vencedor: {cb['winner']}, Déficit Máx. Superado: {cb['max_deficit_overcome']}, Duração: {duration_str}\n"
else:
    summary_text += "Nenhuma partida atendeu aos critérios de virada significativa.\n"

try:
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    print(f"Resumo da análise de viradas salvo em: {output_summary_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de resumo de viradas: {e}")


