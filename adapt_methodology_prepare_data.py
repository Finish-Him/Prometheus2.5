# -*- coding: utf-8 -*-
"""
Adapta a metodologia de classificação por fase devido à falta de dados específicos (ouro/xp @ 10min).

Nova Metodologia Proposta (Baseada em Métricas Disponíveis):
1.  **Métricas por Fase (Alternativas):**
    *   **Early Game:** Média de Kills (`avg_kills`), Média de Assists (`avg_assists`). (Proxy para impacto inicial)
    *   **Mid Game:** GPM Médio (`avg_gpm`), KDA Ratio (`kda_ratio`). (Reflete farm e eficiência em lutas no meio do jogo)
    *   **Late Game:** Ganho do Atributo Primário (`primary_gain`), XPM Médio (`avg_xpm`). (Reflete potencial de scaling)
2.  **Cálculo do Score por Fase:** (Será feito nos próximos scripts)
    *   Normalizar cada métrica relevante para a fase (escala 0-1, Min-Max).
    *   Calcular a média simples dos scores normalizados para obter um score combinado para a fase.
3.  **Atribuição da Nota (1-5):** (Será feito nos próximos scripts)
    *   Ordenar os heróis pelo score combinado da fase.
    *   Dividir em 5 quantis e atribuir notas de 1 a 5.

Este script recalcula/verifica as métricas alternativas necessárias (`primary_gain`, `avg_xpm`) e salva os dados prontos para o cálculo das notas.
"""

import json
import sys

input_file = "/home/ubuntu/hero_stats_with_kda_gpm.json" # Arquivo da etapa anterior
output_file = "/home/ubuntu/hero_stats_for_revised_rating.json"

# Carregar estatísticas de heróis pré-calculadas
print(f"Carregando estatísticas de heróis: {input_file}")
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        hero_stats = json.load(f)
    print(f"Estatísticas de {len(hero_stats)} heróis carregadas.")
except Exception as e:
    print(f"Erro ao carregar estatísticas de heróis: {e}")
    sys.exit(1)

print("Calculando/Verificando métricas alternativas (primary_gain, avg_xpm)...")

missing_metrics_heroes = []

for hero_id_str, stats in hero_stats.items():
    picks = stats.get('picks', 0)
    if picks > 0:
        # Calcular Ganho do Atributo Primário
        primary_attr = stats.get('primary_attr')
        primary_gain = 0
        str_gain = stats.get('str_gain')
        agi_gain = stats.get('agi_gain')
        int_gain = stats.get('int_gain')
        
        if primary_attr == 'str' and str_gain is not None:
            primary_gain = str_gain
        elif primary_attr == 'agi' and agi_gain is not None:
            primary_gain = agi_gain
        elif primary_attr == 'int' and int_gain is not None:
            primary_gain = int_gain
        elif primary_attr:
             missing_metrics_heroes.append(f"{stats.get('name', hero_id_str)} (missing gain for {primary_attr})")
        
        stats['primary_gain'] = primary_gain

        # Calcular XPM Médio (se não existir ou precisar recalcular)
        if 'avg_xpm' not in stats:
            total_xpm = stats.get('total_xpm', 0)
            stats['avg_xpm'] = (total_xpm / picks) if picks > 0 else 0
        elif stats['avg_xpm'] is None: # Handle potential None from previous steps
             total_xpm = stats.get('total_xpm', 0)
             stats['avg_xpm'] = (total_xpm / picks) if picks > 0 else 0
             
        # Verificar se métricas necessárias para as próximas etapas existem
        required_metrics = ['avg_kills', 'avg_assists', 'avg_gpm', 'kda_ratio', 'primary_gain', 'avg_xpm']
        for metric in required_metrics:
            if stats.get(metric) is None:
                 if f"{stats.get('name', hero_id_str)} (missing {metric})" not in missing_metrics_heroes:
                      missing_metrics_heroes.append(f"{stats.get('name', hero_id_str)} (missing {metric})")

if missing_metrics_heroes:
    print("\nAviso: Alguns heróis possuem métricas ausentes que podem afetar a classificação:")
    for item in missing_metrics_heroes:
        print(f"- {item}")

# Salvar dados preparados para cálculo de notas
print(f"\nSalvando dados preparados em {output_file}")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hero_stats, f, indent=4)
    print("Metodologia adaptada e dados preparados salvos com sucesso.")
except Exception as e:
    print(f"Erro ao salvar dados preparados: {e}")
    sys.exit(1)

