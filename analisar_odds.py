#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para cruzar dados de desempenho com odds de apostas
Autor: Manus
Data: 26/04/2025
"""

import pandas as pd
import json
import os
import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Diretórios
INPUT_DIR = '/home/ubuntu/upload'
OUTPUT_DIR = '/home/ubuntu/pgl_wallachia_analysis'

# Arquivos de entrada
PARTIDAS_FILE = os.path.join(INPUT_DIR, 'Todas as Partidas.csv')

# Arquivos de saída
ODDS_ANALISE_FILE = os.path.join(OUTPUT_DIR, 'analise_odds_apostas.md')
VISUALIZACOES_DIR = os.path.join(OUTPUT_DIR, 'visualizacoes')

# Configurações
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Criar diretório para visualizações se não existir
os.makedirs(VISUALIZACOES_DIR, exist_ok=True)

# Definir odds da Rivalry para Team Spirit vs Team Tidebound
# Baseado nas informações disponíveis
ODDS = {
    'vencedor': {
        'Team Spirit': 1.23,
        'Team Tidebound': 3.75
    },
    'handicap_mapas': {
        'Team Spirit -1.5': 2.40,
        'Team Tidebound +1.5': 1.97
    },
    'total_mapas': {
        'Over 2.5': 2.40,
        'Under 2.5': 1.50
    },
    'placar_correto': {
        '2-0': 2.10,
        '2-1': 3.50,
        '1-2': 5.50,
        '0-2': 7.00
    },
    'duracao_mapa1': {
        'Over 35:59': 1.85,
        'Under 35:59': 2.80
    },
    'first_blood': {
        'Team Spirit': 1.80,
        'Team Tidebound': 1.90
    },
    'handicap_kills': {
        'Team Spirit -8.5': 1.90,
        'Team Tidebound +8.5': 1.80
    }
}

def carregar_dados_partidas():
    """Carrega os dados do arquivo 'Todas as Partidas.csv'"""
    print(f"Carregando dados de partidas de {PARTIDAS_FILE}...")
    try:
        df = pd.read_csv(PARTIDAS_FILE)
        print(f"Dados carregados com sucesso. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Erro ao carregar dados de partidas: {e}")
        return None

def calcular_valor_esperado(probabilidade, odd):
    """Calcula o valor esperado de uma aposta"""
    return (probabilidade * odd) - 1

def analisar_odds_vencedor(df):
    """Analisa as odds para o mercado de vencedor"""
    resultados = []
    resultados.append("# Análise de Odds e Oportunidades de Apostas: Team Spirit vs Team Tidebound\n")
    
    # Identificar partidas onde as duas equipes se enfrentaram
    partidas_spirit = set(df[df['team_name'] == 'Team Spirit']['match_id'])
    partidas_tidebound = set(df[df['team_name'] == 'Team Tidebound']['match_id'])
    confrontos_diretos = partidas_spirit.intersection(partidas_tidebound)
    
    # Calcular estatísticas gerais
    spirit_df = df[df['team_name'] == 'Team Spirit']
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    
    # Calcular taxa de vitória geral
    partidas_spirit = spirit_df['match_id'].nunique()
    vitorias_spirit = spirit_df[spirit_df['radiant'] == spirit_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_spirit = vitorias_spirit / partidas_spirit if partidas_spirit > 0 else 0
    
    partidas_tidebound = tidebound_df['match_id'].nunique()
    vitorias_tidebound = tidebound_df[tidebound_df['radiant'] == tidebound_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_tidebound = vitorias_tidebound / partidas_tidebound if partidas_tidebound > 0 else 0
    
    # Calcular taxa de vitória em confrontos diretos
    if confrontos_diretos:
        spirit_vitorias_diretas = sum(1 for match_id in confrontos_diretos if 
                                    (df[(df['match_id'] == match_id) & (df['team_name'] == 'Team Spirit')]['radiant'].iloc[0] == 
                                     df[(df['match_id'] == match_id)]['radiant_win'].iloc[0]))
        
        tidebound_vitorias_diretas = len(confrontos_diretos) - spirit_vitorias_diretas
        
        taxa_vitoria_spirit_diretas = spirit_vitorias_diretas / len(confrontos_diretos)
        taxa_vitoria_tidebound_diretas = tidebound_vitorias_diretas / len(confrontos_diretos)
    else:
        taxa_vitoria_spirit_diretas = 0
        taxa_vitoria_tidebound_diretas = 0
    
    # Calcular probabilidade ajustada (média ponderada entre taxa geral e confrontos diretos)
    # Damos mais peso para confrontos diretos (70%) e menos para taxa geral (30%)
    if confrontos_diretos:
        prob_spirit = (0.3 * taxa_vitoria_spirit) + (0.7 * taxa_vitoria_spirit_diretas)
        prob_tidebound = (0.3 * taxa_vitoria_tidebound) + (0.7 * taxa_vitoria_tidebound_diretas)
    else:
        prob_spirit = taxa_vitoria_spirit
        prob_tidebound = taxa_vitoria_tidebound
    
    # Normalizar probabilidades para somar 1
    soma_probs = prob_spirit + prob_tidebound
    if soma_probs > 0:
        prob_spirit = prob_spirit / soma_probs
        prob_tidebound = prob_tidebound / soma_probs
    
    # Calcular valor esperado
    valor_esperado_spirit = calcular_valor_esperado(prob_spirit, ODDS['vencedor']['Team Spirit'])
    valor_esperado_tidebound = calcular_valor_esperado(prob_tidebound, ODDS['vencedor']['Team Tidebound'])
    
    # Analisar odds para o mercado de vencedor
    resultados.append("## Mercado: Vencedor da Partida\n")
    resultados.append("| Equipe | Odd | Probabilidade Estimada | Valor Esperado | Recomendação |")
    resultados.append("|--------|-----|------------------------|----------------|--------------|")
    resultados.append(f"| Team Spirit | {ODDS['vencedor']['Team Spirit']:.2f} | {prob_spirit:.2%} | {valor_esperado_spirit:.2f} | {'✅ Valor' if valor_esperado_spirit > 0 else '❌ Sem valor'} |")
    resultados.append(f"| Team Tidebound | {ODDS['vencedor']['Team Tidebound']:.2f} | {prob_tidebound:.2%} | {valor_esperado_tidebound:.2f} | {'✅ Valor' if valor_esperado_tidebound > 0 else '❌ Sem valor'} |")
    
    # Adicionar análise detalhada
    resultados.append("\n### Análise Detalhada\n")
    resultados.append(f"- **Taxa de vitória geral Team Spirit:** {taxa_vitoria_spirit:.2%}")
    resultados.append(f"- **Taxa de vitória geral Team Tidebound:** {taxa_vitoria_tidebound:.2%}")
    
    if confrontos_diretos:
        resultados.append(f"- **Confrontos diretos:** {len(confrontos_diretos)}")
        resultados.append(f"- **Vitórias Team Spirit em confrontos diretos:** {spirit_vitorias_diretas} ({taxa_vitoria_spirit_diretas:.2%})")
        resultados.append(f"- **Vitórias Team Tidebound em confrontos diretos:** {tidebound_vitorias_diretas} ({taxa_vitoria_tidebound_diretas:.2%})")
    
    resultados.append(f"- **Probabilidade ajustada Team Spirit:** {prob_spirit:.2%}")
    resultados.append(f"- **Probabilidade ajustada Team Tidebound:** {prob_tidebound:.2%}")
    resultados.append(f"- **Probabilidade implícita na odd Team Spirit:** {1/ODDS['vencedor']['Team Spirit']:.2%}")
    resultados.append(f"- **Probabilidade implícita na odd Team Tidebound:** {1/ODDS['vencedor']['Team Tidebound']:.2%}")
    
    # Adicionar conclusão
    resultados.append("\n**Conclusão:** ")
    if valor_esperado_spirit > valor_esperado_tidebound and valor_esperado_spirit > 0:
        resultados.append(f"Apostar em Team Spirit (odd {ODDS['vencedor']['Team Spirit']:.2f}) oferece o melhor valor esperado ({valor_esperado_spirit:.2f}).")
    elif valor_esperado_tidebound > valor_esperado_spirit and valor_esperado_tidebound > 0:
        resultados.append(f"Apostar em Team Tidebound (odd {ODDS['vencedor']['Team Tidebound']:.2f}) oferece o melhor valor esperado ({valor_esperado_tidebound:.2f}).")
    else:
        resultados.append("Nenhuma das apostas neste mercado oferece valor positivo esperado.")
    
    return "\n".join(resultados)

def analisar_odds_handicap_mapas(df):
    """Analisa as odds para o mercado de handicap de mapas"""
    resultados = []
    resultados.append("\n## Mercado: Handicap de Mapas\n")
    
    # Identificar partidas onde as duas equipes se enfrentaram
    partidas_spirit = set(df[df['team_name'] == 'Team Spirit']['match_id'])
    partidas_tidebound = set(df[df['team_name'] == 'Team Tidebound']['match_id'])
    confrontos_diretos = partidas_spirit.intersection(partidas_tidebound)
    
    # Calcular estatísticas gerais
    spirit_df = df[df['team_name'] == 'Team Spirit']
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    
    # Calcular taxa de vitória geral
    partidas_spirit = spirit_df['match_id'].nunique()
    vitorias_spirit = spirit_df[spirit_df['radiant'] == spirit_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_spirit = vitorias_spirit / partidas_spirit if partidas_spirit > 0 else 0
    
    partidas_tidebound = tidebound_df['match_id'].nunique()
    vitorias_tidebound = tidebound_df[tidebound_df['radiant'] == tidebound_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_tidebound = vitorias_tidebound / partidas_tidebound if partidas_tidebound > 0 else 0
    
    # Calcular taxa de vitória em confrontos diretos
    if confrontos_diretos:
        spirit_vitorias_diretas = sum(1 for match_id in confrontos_diretos if 
                                    (df[(df['match_id'] == match_id) & (df['team_name'] == 'Team Spirit')]['radiant'].iloc[0] == 
                                     df[(df['match_id'] == match_id)]['radiant_win'].iloc[0]))
        
        tidebound_vitorias_diretas = len(confrontos_diretos) - spirit_vitorias_diretas
        
        taxa_vitoria_spirit_diretas = spirit_vitorias_diretas / len(confrontos_diretos)
        taxa_vitoria_tidebound_diretas = tidebound_vitorias_diretas / len(confrontos_diretos)
    else:
        taxa_vitoria_spirit_diretas = 0
        taxa_vitoria_tidebound_diretas = 0
    
    # Calcular probabilidade ajustada (média ponderada entre taxa geral e confrontos diretos)
    if confrontos_diretos:
        prob_spirit = (0.3 * taxa_vitoria_spirit) + (0.7 * taxa_vitoria_spirit_diretas)
        prob_tidebound = (0.3 * taxa_vitoria_tidebound) + (0.7 * taxa_vitoria_tidebound_diretas)
    else:
        prob_spirit = taxa_vitoria_spirit
        prob_tidebound = taxa_vitoria_tidebound
    
    # Normalizar probabilidades para somar 1
    soma_probs = prob_spirit + prob_tidebound
    if soma_probs > 0:
        prob_spirit = prob_spirit / soma_probs
        prob_tidebound = prob_tidebound / soma_probs
    
    # Calcular probabilidades para handicap de mapas
    # Simulação simples de uma série melhor de 3 (Bo3)
    # Probabilidade de Team Spirit vencer 2-0
    prob_spirit_2_0 = prob_spirit * prob_spirit
    # Probabilidade de Team Spirit vencer 2-1
    prob_spirit_2_1 = prob_spirit * prob_tidebound * prob_spirit
    # Probabilidade de Team Tidebound vencer 2-1
    prob_tidebound_2_1 = prob_tidebound * prob_spirit * prob_tidebound
    # Probabilidade de Team Tidebound vencer 2-0
    prob_tidebound_2_0 = prob_tidebound * prob_tidebound
    
    # Normalizar probabilidades para somar 1
    soma_probs = prob_spirit_2_0 + prob_spirit_2_1 + prob_tidebound_2_1 + prob_tidebound_2_0
    if soma_probs > 0:
        prob_spirit_2_0 = prob_spirit_2_0 / soma_probs
        prob_spirit_2_1 = prob_spirit_2_1 / soma_probs
        prob_tidebound_2_1 = prob_tidebound_2_1 / soma_probs
        prob_tidebound_2_0 = prob_tidebound_2_0 / soma_probs
    
    # Probabilidade de Team Spirit -1.5 (vencer 2-0)
    prob_spirit_menos_1_5 = prob_spirit_2_0
    # Probabilidade de Team Tidebound +1.5 (vencer pelo menos 1 mapa)
    prob_tidebound_mais_1_5 = prob_spirit_2_1 + prob_tidebound_2_1 + prob_tidebound_2_0
    
    # Calcular valor esperado
    valor_esperado_spirit_menos_1_5 = calcular_valor_esperado(prob_spirit_menos_1_5, ODDS['handicap_mapas']['Team Spirit -1.5'])
    valor_esperado_tidebound_mais_1_5 = calcular_valor_esperado(prob_tidebound_mais_1_5, ODDS['handicap_mapas']['Team Tidebound +1.5'])
    
    # Analisar odds para o mercado de handicap de mapas
    resultados.append("| Aposta | Odd | Probabilidade Estimada | Valor Esperado | Recomendação |")
    resultados.append("|--------|-----|------------------------|----------------|--------------|")
    resultados.append(f"| Team Spirit -1.5 | {ODDS['handicap_mapas']['Team Spirit -1.5']:.2f} | {prob_spirit_menos_1_5:.2%} | {valor_esperado_spirit_menos_1_5:.2f} | {'✅ Valor' if valor_esperado_spirit_menos_1_5 > 0 else '❌ Sem valor'} |")
    resultados.append(f"| Team Tidebound +1.5 | {ODDS['handicap_mapas']['Team Tidebound +1.5']:.2f} | {prob_tidebound_mais_1_5:.2%} | {valor_esperado_tidebound_mais_1_5:.2f} | {'✅ Valor' if valor_esperado_tidebound_mais_1_5 > 0 else '❌ Sem valor'} |")
    
    # Adicionar análise detalhada
    resultados.append("\n### Análise Detalhada\n")
    resultados.append(f"- **Probabilidade de Team Spirit vencer 2-0:** {prob_spirit_2_0:.2%}")
    resultados.append(f"- **Probabilidade de Team Spirit vencer 2-1:** {prob_spirit_2_1:.2%}")
    resultados.append(f"- **Probabilidade de Team Tidebound vencer 2-1:** {prob_tidebound_2_1:.2%}")
    resultados.append(f"- **Probabilidade de Team Tidebound vencer 2-0:** {prob_tidebound_2_0:.2%}")
    resultados.append(f"- **Probabilidade implícita na odd Team Spirit -1.5:** {1/ODDS['handicap_mapas']['Team Spirit -1.5']:.2%}")
    resultados.append(f"- **Probabilidade implícita na odd Team Tidebound +1.5:** {1/ODDS['handicap_mapas']['Team Tidebound +1.5']:.2%}")
    
    # Adicionar conclusão
    resultados.append("\n**Conclusão:** ")
    if valor_esperado_spirit_menos_1_5 > valor_esperado_tidebound_mais_1_5 and valor_esperado_spirit_menos_1_5 > 0:
        resultados.append(f"Apostar em Team Spirit -1.5 (odd {ODDS['handicap_mapas']['Team Spirit -1.5']:.2f}) oferece o melhor valor esperado ({valor_esperado_spirit_menos_1_5:.2f}).")
    elif valor_esperado_tidebound_mais_1_5 > valor_esperado_spirit_menos_1_5 and valor_esperado_tidebound_mais_1_5 > 0:
        resultados.append(f"Apostar em Team Tidebound +1.5 (odd {ODDS['handicap_mapas']['Team Tidebound +1.5']:.2f}) oferece o melhor valor esperado ({valor_esperado_tidebound_mais_1_5:.2f}).")
    else:
        resultados.append("Nenhuma das apostas neste mercado oferece valor positivo esperado.")
    
    return "\n".join(resultados)

def analisar_odds_total_mapas(df):
    """Analisa as odds para o mercado de total de mapas"""
    resultados = []
    resultados.append("\n## Mercado: Total de Mapas\n")
    
    # Identificar partidas onde as duas equipes se enfrentaram
    partidas_spirit = set(df[df['team_name'] == 'Team Spirit']['match_id'])
    partidas_tidebound = set(df[df['team_name'] == 'Team Tidebound']['match_id'])
    confrontos_diretos = partidas_spirit.intersection(partidas_tidebound)
    
    # Calcular estatísticas gerais
    spirit_df = df[df['team_name'] == 'Team Spirit']
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    
    # Calcular taxa de vitória geral
    partidas_spirit = spirit_df['match_id'].nunique()
    vitorias_spirit = spirit_df[spirit_df['radiant'] == spirit_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_spirit = vitorias_spirit / partidas_spirit if partidas_spirit > 0 else 0
    
    partidas_tidebound = tidebound_df['match_id'].nunique()
    vitorias_tidebound = tidebound_df[tidebound_df['radiant'] == tidebound_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_tidebound = vitorias_tidebound / partidas_tidebound if partidas_tidebound > 0 else 0
    
    # Calcular taxa de vitória em confrontos diretos
    if confrontos_diretos:
        spirit_vitorias_diretas = sum(1 for match_id in confrontos_diretos if 
                                    (df[(df['match_id'] == match_id) & (df['team_name'] == 'Team Spirit')]['radiant'].iloc[0] == 
                                     df[(df['match_id'] == match_id)]['radiant_win'].iloc[0]))
        
        tidebound_vitorias_diretas = len(confrontos_diretos) - spirit_vitorias_diretas
        
        taxa_vitoria_spirit_diretas = spirit_vitorias_diretas / len(confrontos_diretos)
        taxa_vitoria_tidebound_diretas = tidebound_vitorias_diretas / len(confrontos_diretos)
    else:
        taxa_vitoria_spirit_direta
(Content truncated due to size limit. Use line ranges to read in chunks)