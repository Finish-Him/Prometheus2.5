#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para identificar padrões e tendências nos dados do PGL Wallachia
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
PADROES_FILE = os.path.join(OUTPUT_DIR, 'padroes_identificados.md')

# Configurações
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

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

def identificar_padroes_duracao(df):
    """Identifica padrões relacionados à duração das partidas"""
    resultados = []
    resultados.append("# Padrões e Tendências Identificados nos Dados do PGL Wallachia\n")
    
    resultados.append("## Padrões de Duração das Partidas\n")
    
    # Converter duração para minutos
    df['duration_min'] = df['duration_sec'] / 60
    
    # Distribuição de duração por equipe
    resultados.append("### Duração Média por Equipe\n")
    duracao_por_equipe = df.groupby('team_name')['duration_min'].agg(['mean', 'median', 'min', 'max', 'count']).sort_values('mean')
    
    # Formatar para markdown
    resultados.append("| Equipe | Média (min) | Mediana (min) | Mínimo (min) | Máximo (min) | Partidas |")
    resultados.append("|--------|-------------|---------------|--------------|--------------|----------|")
    for equipe, stats in duracao_por_equipe.iterrows():
        resultados.append(f"| {equipe} | {stats['mean']:.2f} | {stats['median']:.2f} | {stats['min']:.2f} | {stats['max']:.2f} | {stats['count']:.0f} |")
    
    # Análise de duração por resultado (vitória/derrota)
    resultados.append("\n### Duração por Resultado (Vitória/Derrota)\n")
    
    # Determinar vitória/derrota
    df['victory'] = (df['radiant'] == df['radiant_win'])
    
    duracao_por_resultado = df.groupby(['team_name', 'victory'])['duration_min'].mean().unstack()
    if True in duracao_por_resultado.columns and False in duracao_por_resultado.columns:
        duracao_por_resultado.columns = ['Derrota', 'Vitória']
        duracao_por_resultado['Diferença'] = duracao_por_resultado['Vitória'] - duracao_por_resultado['Derrota']
        duracao_por_resultado = duracao_por_resultado.sort_values('Diferença')
        
        # Formatar para markdown
        resultados.append("| Equipe | Duração Média Vitórias (min) | Duração Média Derrotas (min) | Diferença (min) |")
        resultados.append("|--------|-------------------------------|-------------------------------|----------------|")
        for equipe, stats in duracao_por_resultado.iterrows():
            if not np.isnan(stats['Vitória']) and not np.isnan(stats['Derrota']):
                resultados.append(f"| {equipe} | {stats['Vitória']:.2f} | {stats['Derrota']:.2f} | {stats['Diferença']:.2f} |")
    
    # Análise de duração por lado (Radiant/Dire)
    resultados.append("\n### Duração por Lado (Radiant/Dire)\n")
    duracao_por_lado = df.groupby(['team_name', 'radiant'])['duration_min'].mean().unstack()
    if True in duracao_por_lado.columns and False in duracao_por_lado.columns:
        duracao_por_lado.columns = ['Dire', 'Radiant']
        duracao_por_lado['Diferença'] = duracao_por_lado['Radiant'] - duracao_por_lado['Dire']
        duracao_por_lado = duracao_por_lado.sort_values('Diferença')
        
        # Formatar para markdown
        resultados.append("| Equipe | Duração Média Radiant (min) | Duração Média Dire (min) | Diferença (min) |")
        resultados.append("|--------|------------------------------|---------------------------|----------------|")
        for equipe, stats in duracao_por_lado.iterrows():
            if not np.isnan(stats['Radiant']) and not np.isnan(stats['Dire']):
                resultados.append(f"| {equipe} | {stats['Radiant']:.2f} | {stats['Dire']:.2f} | {stats['Diferença']:.2f} |")
    
    # Análise específica para Team Spirit e Team Tidebound
    resultados.append("\n### Análise de Duração para Team Spirit e Team Tidebound\n")
    
    # Filtrar apenas as partidas dessas equipes
    spirit_df = df[df['team_name'] == 'Team Spirit']
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    
    # Estatísticas de duração para Team Spirit
    resultados.append("#### Team Spirit\n")
    spirit_duracao_stats = spirit_df['duration_min'].describe()
    resultados.append(f"- Duração média: {spirit_duracao_stats['mean']:.2f} minutos")
    resultados.append(f"- Duração mediana: {spirit_duracao_stats['50%']:.2f} minutos")
    resultados.append(f"- Duração mínima: {spirit_duracao_stats['min']:.2f} minutos")
    resultados.append(f"- Duração máxima: {spirit_duracao_stats['max']:.2f} minutos")
    
    # Duração por resultado para Team Spirit
    spirit_duracao_por_resultado = spirit_df.groupby('victory')['duration_min'].mean()
    if True in spirit_duracao_por_resultado.index and False in spirit_duracao_por_resultado.index:
        resultados.append(f"- Duração média em vitórias: {spirit_duracao_por_resultado[True]:.2f} minutos")
        resultados.append(f"- Duração média em derrotas: {spirit_duracao_por_resultado[False]:.2f} minutos")
        resultados.append(f"- Diferença: {spirit_duracao_por_resultado[True] - spirit_duracao_por_resultado[False]:.2f} minutos")
    
    # Estatísticas de duração para Team Tidebound
    resultados.append("\n#### Team Tidebound\n")
    tidebound_duracao_stats = tidebound_df['duration_min'].describe()
    resultados.append(f"- Duração média: {tidebound_duracao_stats['mean']:.2f} minutos")
    resultados.append(f"- Duração mediana: {tidebound_duracao_stats['50%']:.2f} minutos")
    resultados.append(f"- Duração mínima: {tidebound_duracao_stats['min']:.2f} minutos")
    resultados.append(f"- Duração máxima: {tidebound_duracao_stats['max']:.2f} minutos")
    
    # Duração por resultado para Team Tidebound
    tidebound_duracao_por_resultado = tidebound_df.groupby('victory')['duration_min'].mean()
    if True in tidebound_duracao_por_resultado.index and False in tidebound_duracao_por_resultado.index:
        resultados.append(f"- Duração média em vitórias: {tidebound_duracao_por_resultado[True]:.2f} minutos")
        resultados.append(f"- Duração média em derrotas: {tidebound_duracao_por_resultado[False]:.2f} minutos")
        resultados.append(f"- Diferença: {tidebound_duracao_por_resultado[True] - tidebound_duracao_por_resultado[False]:.2f} minutos")
    
    return resultados

def identificar_padroes_kills(df):
    """Identifica padrões relacionados a kills nas partidas"""
    resultados = []
    resultados.append("\n## Padrões de Kills nas Partidas\n")
    
    # Média de kills por equipe
    resultados.append("### Média de Kills por Equipe\n")
    kills_por_equipe = df.groupby('team_name')['player_kills'].sum() / df.groupby('team_name')['match_id'].nunique()
    kills_por_equipe = kills_por_equipe.sort_values(ascending=False)
    
    # Formatar para markdown
    resultados.append("| Equipe | Média de Kills por Partida |")
    resultados.append("|--------|----------------------------|")
    for equipe, kills in kills_por_equipe.items():
        resultados.append(f"| {equipe} | {kills:.2f} |")
    
    # Análise de kills por resultado (vitória/derrota)
    resultados.append("\n### Kills por Resultado (Vitória/Derrota)\n")
    
    # Calcular média de kills por equipe e resultado
    kills_por_resultado = df.groupby(['team_name', 'victory'])['player_kills'].sum()
    partidas_por_resultado = df.groupby(['team_name', 'victory'])['match_id'].nunique()
    kills_medio_por_resultado = (kills_por_resultado / partidas_por_resultado).unstack()
    
    if True in kills_medio_por_resultado.columns and False in kills_medio_por_resultado.columns:
        kills_medio_por_resultado.columns = ['Derrota', 'Vitória']
        kills_medio_por_resultado['Diferença'] = kills_medio_por_resultado['Vitória'] - kills_medio_por_resultado['Derrota']
        kills_medio_por_resultado = kills_medio_por_resultado.sort_values('Diferença', ascending=False)
        
        # Formatar para markdown
        resultados.append("| Equipe | Kills Médio em Vitórias | Kills Médio em Derrotas | Diferença |")
        resultados.append("|--------|-------------------------|-------------------------|-----------|")
        for equipe, stats in kills_medio_por_resultado.iterrows():
            if not np.isnan(stats['Vitória']) and not np.isnan(stats['Derrota']):
                resultados.append(f"| {equipe} | {stats['Vitória']:.2f} | {stats['Derrota']:.2f} | {stats['Diferença']:.2f} |")
    
    # Análise específica para Team Spirit e Team Tidebound
    resultados.append("\n### Análise de Kills para Team Spirit e Team Tidebound\n")
    
    # Filtrar apenas as partidas dessas equipes
    spirit_df = df[df['team_name'] == 'Team Spirit']
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    
    # Estatísticas de kills para Team Spirit
    resultados.append("#### Team Spirit\n")
    spirit_kills_por_partida = spirit_df.groupby('match_id')['player_kills'].sum() / 5  # Dividir por 5 jogadores
    spirit_kills_stats = spirit_kills_por_partida.describe()
    resultados.append(f"- Média de kills por partida: {spirit_kills_stats['mean']:.2f}")
    resultados.append(f"- Mediana de kills por partida: {spirit_kills_stats['50%']:.2f}")
    resultados.append(f"- Mínimo de kills por partida: {spirit_kills_stats['min']:.2f}")
    resultados.append(f"- Máximo de kills por partida: {spirit_kills_stats['max']:.2f}")
    
    # Kills por resultado para Team Spirit
    spirit_kills_por_resultado = spirit_df.groupby(['match_id', 'victory'])['player_kills'].sum().groupby(level=1).mean() / 5
    if True in spirit_kills_por_resultado.index and False in spirit_kills_por_resultado.index:
        resultados.append(f"- Média de kills em vitórias: {spirit_kills_por_resultado[True]:.2f}")
        resultados.append(f"- Média de kills em derrotas: {spirit_kills_por_resultado[False]:.2f}")
        resultados.append(f"- Diferença: {spirit_kills_por_resultado[True] - spirit_kills_por_resultado[False]:.2f}")
    
    # Estatísticas de kills para Team Tidebound
    resultados.append("\n#### Team Tidebound\n")
    tidebound_kills_por_partida = tidebound_df.groupby('match_id')['player_kills'].sum() / 5  # Dividir por 5 jogadores
    tidebound_kills_stats = tidebound_kills_por_partida.describe()
    resultados.append(f"- Média de kills por partida: {tidebound_kills_stats['mean']:.2f}")
    resultados.append(f"- Mediana de kills por partida: {tidebound_kills_stats['50%']:.2f}")
    resultados.append(f"- Mínimo de kills por partida: {tidebound_kills_stats['min']:.2f}")
    resultados.append(f"- Máximo de kills por partida: {tidebound_kills_stats['max']:.2f}")
    
    # Kills por resultado para Team Tidebound
    tidebound_kills_por_resultado = tidebound_df.groupby(['match_id', 'victory'])['player_kills'].sum().groupby(level=1).mean() / 5
    if True in tidebound_kills_por_resultado.index and False in tidebound_kills_por_resultado.index:
        resultados.append(f"- Média de kills em vitórias: {tidebound_kills_por_resultado[True]:.2f}")
        resultados.append(f"- Média de kills em derrotas: {tidebound_kills_por_resultado[False]:.2f}")
        resultados.append(f"- Diferença: {tidebound_kills_por_resultado[True] - tidebound_kills_por_resultado[False]:.2f}")
    
    return resultados

def identificar_padroes_herois(df):
    """Identifica padrões relacionados aos heróis escolhidos"""
    resultados = []
    resultados.append("\n## Padrões de Escolha de Heróis\n")
    
    # Heróis mais escolhidos por equipe
    resultados.append("### Heróis Mais Escolhidos por Equipe\n")
    
    # Obter as 5 equipes com mais partidas
    top_equipes = df.groupby('team_name')['match_id'].nunique().sort_values(ascending=False).head(5).index
    
    for equipe in top_equipes:
        resultados.append(f"#### {equipe}\n")
        herois_equipe = df[df['team_name'] == equipe]['hero_id'].value_counts().head(10)
        
        # Formatar para markdown
        resultados.append("| Hero ID | Quantidade |")
        resultados.append("|---------|------------|")
        for hero_id, count in herois_equipe.items():
            resultados.append(f"| {hero_id} | {count} |")
        
        resultados.append("")
    
    # Análise específica para Team Spirit e Team Tidebound
    resultados.append("### Análise de Heróis para Team Spirit e Team Tidebound\n")
    
    # Heróis mais escolhidos por Team Spirit
    resultados.append("#### Team Spirit - Heróis Mais Escolhidos\n")
    spirit_herois = df[df['team_name'] == 'Team Spirit']['hero_id'].value_counts().head(10)
    
    # Formatar para markdown
    resultados.append("| Hero ID | Quantidade |")
    resultados.append("|---------|------------|")
    for hero_id, count in spirit_herois.items():
        resultados.append(f"| {hero_id} | {count} |")
    
    # Heróis mais escolhidos por Team Tidebound
    resultados.append("\n#### Team Tidebound - Heróis Mais Escolhidos\n")
    tidebound_herois = df[df['team_name'] == 'Team Tidebound']['hero_id'].value_counts().head(10)
    
    # Formatar para markdown
    resultados.append("| Hero ID | Quantidade |")
    resultados.append("|---------|------------|")
    for hero_id, count in tidebound_herois.items():
        resultados.append(f"| {hero_id} | {count} |")
    
    # Heróis com maior taxa de vitória para Team Spirit
    resultados.append("\n#### Team Spirit - Heróis com Maior Taxa de Vitória\n")
    spirit_df = df[df['team_name'] == 'Team Spirit']
    spirit_herois_vitorias = spirit_df.groupby(['hero_id', 'victory']).size().unstack(fill_value=0)
    
    if True in spirit_herois_vitorias.columns and False in spirit_herois_vitorias.columns:
        spirit_herois_vitorias['total'] = spirit_herois_vitorias[True] + spirit_herois_vitorias[False]
        spirit_herois_vitorias['winrate'] = spirit_herois_vitorias[True] / spirit_herois_vitorias['total']
        spirit_herois_vitorias = spirit_herois_vitorias[spirit_herois_vitorias['total'] >= 3]  # Mínimo de 3 jogos
        spirit_herois_vitorias = spirit_herois_vitorias.sort_values('winrate', ascending=False).head(10)
        
        # Formatar para markdown
        resultados.append("| Hero ID | Vitórias | Derrotas | Total | Winrate |")
        resultados.append("|---------|----------|----------|-------|---------|")
        for hero_id, stats in spirit_herois_vitorias.iterrows():
            resultados.append(f"| {hero_id} | {stats[True]:.0f} | {stats[False]:.0f} | {stats['total']:.0f} | {stats['winrate']:.2%} |")
    
    # Heróis com maior taxa de vitória para Team Tidebound
    resultados.append("\n#### Team Tidebound - Heróis com Maior Taxa de Vitória\n")
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    tidebound_herois_vitorias = tidebound_df.groupby(['hero_id', 'victory']).size().unstack(fill_value=0)
    
    if True in tidebound_herois_vitorias.columns and False in tidebound_herois_vitorias.columns:
        tidebound_herois_vitorias['total'] = tidebound_herois_vitorias[True] + tidebound_herois_vitorias[False]
        tidebound_herois_vitorias['winrate'] = tidebound_herois_vitorias[True] / tidebound_herois_vitorias['total']
        tidebound_herois_vitorias = tidebound_herois_vitorias[tidebound_herois_vitorias['total'] >= 3]  # Mínimo de 3 jogos
        tidebound_herois_vitorias = tidebound_herois_vitorias.sort_values('winrate', ascending=Fal
(Content truncated due to size limit. Use line ranges to read in chunks)