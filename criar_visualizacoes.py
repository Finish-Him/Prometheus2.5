#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar visualizações adicionais para análise de apostas
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
import matplotlib.patches as mpatches

# Diretórios
INPUT_DIR = '/home/ubuntu/upload'
OUTPUT_DIR = '/home/ubuntu/pgl_wallachia_analysis'

# Arquivos de entrada
PARTIDAS_FILE = os.path.join(INPUT_DIR, 'Todas as Partidas.csv')

# Diretório para visualizações
VISUALIZACOES_DIR = os.path.join(OUTPUT_DIR, 'visualizacoes')

# Arquivo de saída para o relatório de visualizações
VISUALIZACOES_REPORT_FILE = os.path.join(OUTPUT_DIR, 'relatorio_visualizacoes.md')

# Configurações
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Criar diretório para visualizações se não existir
os.makedirs(VISUALIZACOES_DIR, exist_ok=True)

# Definir estilo para os gráficos
plt.style.use('seaborn-v0_8-darkgrid')
cores = {
    'Team Spirit': '#3498db',  # Azul
    'Team Tidebound': '#e74c3c',  # Vermelho
    'Outros': '#95a5a6'  # Cinza
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

def visualizar_desempenho_por_lado(df):
    """Cria visualização do desempenho por lado (Radiant/Dire)"""
    print("Criando visualização de desempenho por lado...")
    
    # Filtrar dados para cada equipe
    spirit_df = df[df['team_name'] == 'Team Spirit'].copy()
    tidebound_df = df[df['team_name'] == 'Team Tidebound'].copy()
    
    # Calcular vitórias por lado
    spirit_df['victory'] = (spirit_df['radiant'] == spirit_df['radiant_win'])
    tidebound_df['victory'] = (tidebound_df['radiant'] == tidebound_df['radiant_win'])
    
    # Calcular taxa de vitória por lado para Team Spirit
    spirit_vitorias_por_lado = spirit_df.groupby(['radiant', 'victory']).size().unstack(fill_value=0)
    
    if True in spirit_vitorias_por_lado.columns and False in spirit_vitorias_por_lado.columns:
        spirit_vitorias_por_lado['total'] = spirit_vitorias_por_lado[True] + spirit_vitorias_por_lado[False]
        spirit_vitorias_por_lado['winrate'] = spirit_vitorias_por_lado[True] / spirit_vitorias_por_lado['total']
    
    # Calcular taxa de vitória por lado para Team Tidebound
    tidebound_vitorias_por_lado = tidebound_df.groupby(['radiant', 'victory']).size().unstack(fill_value=0)
    
    if True in tidebound_vitorias_por_lado.columns and False in tidebound_vitorias_por_lado.columns:
        tidebound_vitorias_por_lado['total'] = tidebound_vitorias_por_lado[True] + tidebound_vitorias_por_lado[False]
        tidebound_vitorias_por_lado['winrate'] = tidebound_vitorias_por_lado[True] / tidebound_vitorias_por_lado['total']
    
    # Criar gráfico de barras para taxa de vitória por lado
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Preparar dados para o gráfico
    lados = ['Radiant', 'Dire']
    spirit_winrates = []
    tidebound_winrates = []
    
    if True in spirit_vitorias_por_lado.columns and False in spirit_vitorias_por_lado.columns:
        spirit_winrates = [spirit_vitorias_por_lado.loc[True, 'winrate'] if True in spirit_vitorias_por_lado.index else 0,
                          spirit_vitorias_por_lado.loc[False, 'winrate'] if False in spirit_vitorias_por_lado.index else 0]
    
    if True in tidebound_vitorias_por_lado.columns and False in tidebound_vitorias_por_lado.columns:
        tidebound_winrates = [tidebound_vitorias_por_lado.loc[True, 'winrate'] if True in tidebound_vitorias_por_lado.index else 0,
                             tidebound_vitorias_por_lado.loc[False, 'winrate'] if False in tidebound_vitorias_por_lado.index else 0]
    
    x = np.arange(len(lados))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, spirit_winrates, width, label='Team Spirit', color=cores['Team Spirit'])
    rects2 = ax.bar(x + width/2, tidebound_winrates, width, label='Team Tidebound', color=cores['Team Tidebound'])
    
    # Adicionar linha horizontal em 50%
    ax.axhline(y=0.5, color='black', linestyle='--', alpha=0.5, label='50% (Equilíbrio)')
    
    ax.set_ylabel('Taxa de Vitória', fontsize=14)
    ax.set_title('Taxa de Vitória por Lado (Radiant/Dire)', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(lados, fontsize=12)
    ax.legend(fontsize=12)
    
    # Adicionar rótulos nas barras
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2%}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=12)
    
    autolabel(rects1)
    autolabel(rects2)
    
    # Adicionar anotação destacando a vantagem do Team Spirit como Radiant
    if spirit_winrates[0] > 0.75:
        ax.annotate('Vantagem significativa\ndo Team Spirit como Radiant',
                   xy=(0, spirit_winrates[0]),
                   xytext=(0, spirit_winrates[0] + 0.1),
                   arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                   ha='center', va='bottom',
                   bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
                   fontsize=12)
    
    plt.tight_layout()
    output_file = os.path.join(VISUALIZACOES_DIR, 'desempenho_por_lado_detalhado.png')
    plt.savefig(output_file)
    plt.close()
    
    print(f"Visualização salva em {output_file}")
    return output_file

def visualizar_distribuicao_duracao(df):
    """Cria visualização da distribuição de duração das partidas"""
    print("Criando visualização de distribuição de duração das partidas...")
    
    # Filtrar dados para cada equipe
    spirit_df = df[df['team_name'] == 'Team Spirit'].copy()
    tidebound_df = df[df['team_name'] == 'Team Tidebound'].copy()
    
    # Converter duração para minutos
    spirit_df['duration_min'] = spirit_df['duration_sec'] / 60
    tidebound_df['duration_min'] = tidebound_df['duration_sec'] / 60
    
    # Criar figura com dois subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
    
    # Histograma com KDE para Team Spirit
    sns.histplot(spirit_df['duration_min'], kde=True, ax=ax1, color=cores['Team Spirit'], bins=20)
    ax1.axvline(spirit_df['duration_min'].mean(), color='black', linestyle='--', 
               label=f'Média: {spirit_df["duration_min"].mean():.2f} min')
    ax1.axvline(35.98, color='red', linestyle='-', 
               label=f'Limiar de aposta (35:59): {(spirit_df["duration_min"] < 35.98).mean():.2%} < 35:59')
    ax1.set_title('Distribuição da Duração das Partidas - Team Spirit', fontsize=16, fontweight='bold')
    ax1.set_ylabel('Frequência', fontsize=14)
    ax1.legend(fontsize=12)
    
    # Histograma com KDE para Team Tidebound
    sns.histplot(tidebound_df['duration_min'], kde=True, ax=ax2, color=cores['Team Tidebound'], bins=20)
    ax2.axvline(tidebound_df['duration_min'].mean(), color='black', linestyle='--', 
               label=f'Média: {tidebound_df["duration_min"].mean():.2f} min')
    ax2.axvline(35.98, color='red', linestyle='-', 
               label=f'Limiar de aposta (35:59): {(tidebound_df["duration_min"] < 35.98).mean():.2%} < 35:59')
    ax2.set_title('Distribuição da Duração das Partidas - Team Tidebound', fontsize=16, fontweight='bold')
    ax2.set_xlabel('Duração (minutos)', fontsize=14)
    ax2.set_ylabel('Frequência', fontsize=14)
    ax2.legend(fontsize=12)
    
    # Adicionar anotações com insights para apostas
    if spirit_df['duration_min'].mean() > 35.98:
        ax1.annotate('Favorável para apostas Over 35:59',
                    xy=(35.98, 0),
                    xytext=(35.98 - 10, ax1.get_ylim()[1] * 0.7),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
                    fontsize=12)
    
    if tidebound_df['duration_min'].mean() > 35.98:
        ax2.annotate('Favorável para apostas Over 35:59',
                    xy=(35.98, 0),
                    xytext=(35.98 - 10, ax2.get_ylim()[1] * 0.7),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
                    fontsize=12)
    
    plt.tight_layout()
    output_file = os.path.join(VISUALIZACOES_DIR, 'distribuicao_duracao_detalhada.png')
    plt.savefig(output_file)
    plt.close()
    
    print(f"Visualização salva em {output_file}")
    return output_file

def visualizar_handicap_kills(df):
    """Cria visualização do handicap de kills"""
    print("Criando visualização de handicap de kills...")
    
    # Identificar partidas onde as duas equipes se enfrentaram
    partidas_spirit = set(df[df['team_name'] == 'Team Spirit']['match_id'])
    partidas_tidebound = set(df[df['team_name'] == 'Team Tidebound']['match_id'])
    confrontos_diretos = partidas_spirit.intersection(partidas_tidebound)
    
    # Calcular diferença de kills em confrontos diretos
    diferencas_kills = []
    datas_confrontos = []
    
    for match_id in confrontos_diretos:
        match_df = df[df['match_id'] == match_id]
        
        # Obter data da partida
        data = datetime.fromtimestamp(match_df['start_time'].iloc[0]).strftime('%d/%m/%Y')
        datas_confrontos.append(data)
        
        # Obter placar
        radiant_score = match_df['radiant_score'].iloc[0]
        dire_score = match_df['dire_score'].iloc[0]
        
        # Determinar qual equipe era Radiant
        spirit_radiant = match_df[match_df['team_name'] == 'Team Spirit']['radiant'].iloc[0]
        
        if spirit_radiant:
            spirit_score = radiant_score
            tidebound_score = dire_score
        else:
            spirit_score = dire_score
            tidebound_score = radiant_score
        
        diferencas_kills.append(spirit_score - tidebound_score)
    
    # Calcular média de kills por equipe
    spirit_df = df[df['team_name'] == 'Team Spirit'].copy()
    tidebound_df = df[df['team_name'] == 'Team Tidebound'].copy()
    
    spirit_kills_por_partida = spirit_df.groupby('match_id')['player_kills'].sum() / 5  # Dividir por 5 jogadores
    tidebound_kills_por_partida = tidebound_df.groupby('match_id')['player_kills'].sum() / 5  # Dividir por 5 jogadores
    
    # Criar figura com dois subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    
    # Gráfico de barras para diferença de kills em confrontos diretos
    if confrontos_diretos:
        x = np.arange(len(confrontos_diretos))
        ax1.bar(x, diferencas_kills, color=[cores['Team Spirit'] if d > 0 else cores['Team Tidebound'] for d in diferencas_kills])
        ax1.axhline(y=8.5, color='red', linestyle='--', label='Handicap de apostas (8.5)')
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.set_title('Diferença de Kills em Confrontos Diretos (Team Spirit - Team Tidebound)', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Diferença de Kills', fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels([f"Partida {i+1}\n{data}" for i, data in enumerate(datas_confrontos)], fontsize=12)
        
        # Adicionar rótulos nas barras
        for i, v in enumerate(diferencas_kills):
            ax1.text(i, v + 0.5 if v > 0 else v - 2, f"{v:+}", ha='center', fontsize=12)
        
        # Adicionar anotação com a média
        media_diferencas = sum(diferencas_kills) / len(diferencas_kills)
        ax1.annotate(f'Média: {media_diferencas:.2f}',
                    xy=(len(diferencas_kills) / 2, media_diferencas),
                    xytext=(len(diferencas_kills) / 2, max(diferencas_kills) * 0.8),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                    ha='center',
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.3),
                    fontsize=12)
        
        # Adicionar legenda para o handicap
        ax1.legend(fontsize=12)
    
    # Boxplot para distribuição de kills por equipe
    data_to_plot = [spirit_kills_por_partida, tidebound_kills_por_partida]
    box = ax2.boxplot(data_to_plot, patch_artist=True, widths=0.6)
    
    # Colorir os boxplots
    colors = [cores['Team Spirit'], cores['Team Tidebound']]
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    
    # Adicionar pontos individuais (swarmplot)
    positions = [1, 2]
    for pos, data, color in zip(positions, data_to_plot, colors):
        # Adicionar jitter para melhor visualização
        x = np.random.normal(pos, 0.04, size=len(data))
        ax2.scatter(x, data, alpha=0.5, s=30, color=color)
    
    ax2.set_title('Distribuição de Kills por Equipe', fontsize=16, fontweight='bold')
    ax2.set_ylabel('Kills por Partida', fontsize=14)
    ax2.set_xticklabels(['Team Spirit', 'Team Tidebound'], fontsize=12)
    
    # Adicionar médias como linhas horizontais
    spirit_mean = spirit_kills_por_partida.mean()
    tidebound_mean = tidebound_kills_por_partida.mean()
    ax2.axhline(y=spirit_mean, xmin=0.25, xmax=0.35, color='black', linestyle='-', linewidth=2)
    ax2.axhline(y=tidebound_mean, xmin=0.65, xmax=0.75, color='black', linestyle='-', linewidth=2)
    
    # Adicionar anotações com as médias
    ax2.annotate(f'Média: {spirit_mean:.2f}',
                xy=(1, spirit_mean),
                xytext=(1.2, spirit_mean),
                fontsize=12)
    ax2.annotate(f'Média: {tidebound_mean:.2f}',
                xy=(2, tidebound_mean),
                xytext=(1.8, tidebound_mean),
                fontsize=12)
    
    plt.tight_layout()
    output_file = os.path.join(VISUALIZACOES_DIR, 'handicap_kills_detalhado.png')
    plt.savefig(output_file)
    plt.close()
    
    print(f"Visualização salva em {output_file}")
    return output_file

def visualizar_herois_mais_efetivos(df):
    """Cria visualização dos heróis mais efetivos para cada equipe"""
    print("Criando visualização de heróis mais efetivos...")
    
    # Filtrar dados para cada equipe
    spirit_df = df[df['team_name'] == 'Team Spirit'].copy()
    tidebound_df = df[df['team_name'] == 'Team Tidebound'].copy()
    
    # Calcular vitórias por herói
    spirit_df['victory'] = (spirit_df['radiant'] == spirit_df['radiant_win'])
    tidebound_df['victory'] = (tidebound_df['radiant'] == tidebound_df['radiant_win'])
    
    # Calcular taxa de vitória por herói para Team Spirit
    spirit_herois_vitorias = spirit_df.groupby(['hero_id', 'victory']).size().unstack(fill_value=0)
    
    if True in spirit_herois_vitorias.columns and False in spirit_herois_vitorias.columns:
        spirit_herois_vitorias['total'] = spirit_herois_vitorias[True] + spirit_herois_vitorias[False]
        spirit_herois_vitorias['winrate'] = spirit_herois_vitorias[True] / spirit_herois_vitorias['total']
        spirit_herois_vitorias = spirit_herois_vitorias[spirit_herois_vitorias['total'] >= 3]  # Mínimo de 3 jogos
        spirit_herois_vitorias = spirit_herois_vitorias.sort_values('winrate', ascending=False)
    
    # Calcular taxa de vitória por herói para Team Tidebound
    tidebound_herois_vitorias = tidebound_df.groupby(['hero_id', 'victory']).size().unstack(fill_value=0)
    
    if True in tidebound_herois_vitorias.columns and False in tidebound_herois_vitorias.columns:
        tidebound_herois_vitorias['total
(Content truncated due to size limit. Use line ranges to read in chunks)