# -*- coding: utf-8 -*-
"""
Define a metodologia para classificação por fase e extrai métricas adicionais.

Metodologia Proposta:
1.  **Métricas por Fase:**
    *   **Early Game (0-15 min):** Média de Ouro aos 10 min (`avg_gold_at_10`), Média de XP aos 10 min (`avg_xp_at_10`).
    *   **Mid Game (15-35 min):** GPM Médio (`avg_gpm`), KDA Ratio (`kda_ratio`).
    *   **Late Game (35+ min):** Ganho do Atributo Primário (`primary_gain`), Taxa de Vitória em jogos com duração > 40 min (`late_game_win_rate`).
2.  **Cálculo do Score por Fase:**
    *   Normalizar cada métrica relevante para a fase (escala 0-1, Min-Max).
    *   Calcular a média simples dos scores normalizados para obter um score combinado para a fase.
3.  **Atribuição da Nota (1-5):**
    *   Ordenar os heróis pelo score combinado da fase.
    *   Dividir em 5 quantis (0-20%, 20-40%, 40-60%, 60-80%, 80-100%).
    *   Atribuir notas de 1 a 5 com base no quantil (1 para o mais baixo, 5 para o mais alto).

Este script foca na extração das métricas que faltam: `avg_gold_at_10`, `avg_xp_at_10`, e `late_game_win_rate`.
"""

import json
import sys
from collections import defaultdict
import numpy as np

match_details_file = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
hero_stats_file = "/home/ubuntu/hero_stats_with_kda_gpm.json"
output_file = "/home/ubuntu/hero_stats_for_rating.json"

EARLY_GAME_TIMESTAMP_SECONDS = 10 * 60 # 10 minutos
LATE_GAME_DURATION_THRESHOLD_SECONDS = 40 * 60 # 40 minutos

# Carregar dados detalhados das partidas
print(f"Carregando dados detalhados das partidas: {match_details_file}")
try:
    with open(match_details_file, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    print(f"Dados de {len(matches_data)} partidas carregados.")
except Exception as e:
    print(f"Erro ao carregar dados das partidas: {e}")
    sys.exit(1)

# Carregar estatísticas de heróis pré-calculadas
print(f"Carregando estatísticas de heróis: {hero_stats_file}")
try:
    with open(hero_stats_file, 'r', encoding='utf-8') as f:
        hero_stats = json.load(f)
    print(f"Estatísticas de {len(hero_stats)} heróis carregadas.")
except Exception as e:
    print(f"Erro ao carregar estatísticas de heróis: {e}")
    sys.exit(1)

# Estrutura para armazenar métricas adicionais
extra_metrics = defaultdict(lambda: {
    'total_gold_at_10': 0,
    'count_gold_at_10': 0,
    'total_xp_at_10': 0,
    'count_xp_at_10': 0,
    'late_game_picks': 0,
    'late_game_wins': 0
})

print("Processando partidas para extrair métricas adicionais...")
for match in matches_data:
    duration = match.get('duration')
    radiant_win = match.get('radiant_win')
    players = match.get('players', [])

    if duration is None or radiant_win is None or not players:
        continue

    is_late_game = duration > LATE_GAME_DURATION_THRESHOLD_SECONDS

    for player in players:
        hero_id = player.get('hero_id')
        player_slot = player.get('player_slot')
        gold_t = player.get('gold_t')
        xp_t = player.get('xp_t')

        # Garantir que hero_id seja string para consistência com as chaves de hero_stats
        hero_id_str = str(hero_id)

        if hero_id is None or hero_id_str not in hero_stats:
            continue

        # Métricas Early Game (Ouro/XP aos 10 min)
        if gold_t and len(gold_t) > EARLY_GAME_TIMESTAMP_SECONDS:
            gold_at_10 = gold_t[EARLY_GAME_TIMESTAMP_SECONDS]
            extra_metrics[hero_id_str]['total_gold_at_10'] += gold_at_10
            extra_metrics[hero_id_str]['count_gold_at_10'] += 1
        
        if xp_t and len(xp_t) > EARLY_GAME_TIMESTAMP_SECONDS:
            xp_at_10 = xp_t[EARLY_GAME_TIMESTAMP_SECONDS]
            extra_metrics[hero_id_str]['total_xp_at_10'] += xp_at_10
            extra_metrics[hero_id_str]['count_xp_at_10'] += 1

        # Métricas Late Game (Picks/Vitórias em jogos > 40 min)
        if is_late_game:
            extra_metrics[hero_id_str]['late_game_picks'] += 1
            is_radiant = player_slot < 128
            player_won = (radiant_win and is_radiant) or (not radiant_win and not is_radiant)
            if player_won:
                extra_metrics[hero_id_str]['late_game_wins'] += 1

print("Adicionando métricas calculadas às estatísticas dos heróis...")
# Adicionar métricas calculadas ao dicionário principal hero_stats
for hero_id_str, stats in hero_stats.items():
    if hero_id_str in extra_metrics:
        metrics = extra_metrics[hero_id_str]
        count_gold = metrics['count_gold_at_10']
        count_xp = metrics['count_xp_at_10']
        late_picks = metrics['late_game_picks']
        late_wins = metrics['late_game_wins']

        stats['avg_gold_at_10'] = (metrics['total_gold_at_10'] / count_gold) if count_gold > 0 else 0
        stats['avg_xp_at_10'] = (metrics['total_xp_at_10'] / count_xp) if count_xp > 0 else 0
        stats['late_game_win_rate'] = (late_wins / late_picks) * 100 if late_picks > 0 else 0
        # Adicionar contagens para referência, se necessário
        stats['late_game_picks'] = late_picks 
    else:
        # Definir valores padrão se o herói não teve dados extraídos
        stats['avg_gold_at_10'] = 0
        stats['avg_xp_at_10'] = 0
        stats['late_game_win_rate'] = 0
        stats['late_game_picks'] = 0

# Salvar dados combinados
print(f"Salvando dados combinados em {output_file}")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hero_stats, f, indent=4)
    print("Metodologia definida e métricas extraídas salvas com sucesso.")
except Exception as e:
    print(f"Erro ao salvar dados combinados: {e}")
    sys.exit(1)

