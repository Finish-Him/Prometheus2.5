#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para análise específica do confronto Team Spirit vs Team Tidebound
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
ANALISE_CONFRONTO_FILE = os.path.join(OUTPUT_DIR, 'analise_spirit_vs_tidebound.md')
VISUALIZACOES_DIR = os.path.join(OUTPUT_DIR, 'visualizacoes')

# Configurações
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Criar diretório para visualizações se não existir
os.makedirs(VISUALIZACOES_DIR, exist_ok=True)

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

def analisar_confronto_direto(df):
    """Analisa os confrontos diretos entre Team Spirit e Team Tidebound"""
    resultados = []
    resultados.append("# Análise Detalhada: Team Spirit vs Team Tidebound\n")
    
    # Identificar partidas onde as duas equipes se enfrentaram
    partidas_spirit = set(df[df['team_name'] == 'Team Spirit']['match_id'])
    partidas_tidebound = set(df[df['team_name'] == 'Team Tidebound']['match_id'])
    confrontos_diretos = partidas_spirit.intersection(partidas_tidebound)
    
    if not confrontos_diretos:
        resultados.append("Não foram encontrados confrontos diretos entre Team Spirit e Team Tidebound nos dados analisados.")
        return "\n".join(resultados)
    
    resultados.append(f"## Histórico de Confrontos Diretos\n")
    resultados.append(f"Foram encontrados {len(confrontos_diretos)} confrontos diretos entre Team Spirit e Team Tidebound.\n")
    
    # Analisar cada confronto direto
    confrontos_detalhes = []
    for match_id in confrontos_diretos:
        partida_df = df[df['match_id'] == match_id]
        
        # Obter informações básicas da partida
        data = datetime.fromtimestamp(partida_df['start_time'].iloc[0]).strftime('%d/%m/%Y')
        duracao = partida_df['duration_sec'].iloc[0] / 60
        
        # Determinar vencedor
        spirit_radiant = partida_df[partida_df['team_name'] == 'Team Spirit']['radiant'].iloc[0]
        radiant_win = partida_df['radiant_win'].iloc[0]
        
        if spirit_radiant == radiant_win:
            vencedor = "Team Spirit"
        else:
            vencedor = "Team Tidebound"
        
        # Obter placar
        radiant_score = partida_df['radiant_score'].iloc[0]
        dire_score = partida_df['dire_score'].iloc[0]
        
        if spirit_radiant:
            spirit_score = radiant_score
            tidebound_score = dire_score
        else:
            spirit_score = dire_score
            tidebound_score = radiant_score
        
        # Obter heróis escolhidos
        spirit_heroes = partida_df[partida_df['team_name'] == 'Team Spirit']['hero_id'].tolist()
        tidebound_heroes = partida_df[partida_df['team_name'] == 'Team Tidebound']['hero_id'].tolist()
        
        # Obter estatísticas de jogadores
        spirit_players = partida_df[partida_df['team_name'] == 'Team Spirit'][['player_id', 'player_kills', 'player_deaths', 'player_assists', 'gpm', 'xpm']]
        tidebound_players = partida_df[partida_df['team_name'] == 'Team Tidebound'][['player_id', 'player_kills', 'player_deaths', 'player_assists', 'gpm', 'xpm']]
        
        # Adicionar informações ao resultado
        resultados.append(f"### Partida {match_id} - {data}\n")
        resultados.append(f"- **Vencedor:** {vencedor}")
        resultados.append(f"- **Placar:** Team Spirit {spirit_score} - {tidebound_score} Team Tidebound")
        resultados.append(f"- **Duração:** {duracao:.2f} minutos")
        resultados.append(f"- **Lado Team Spirit:** {'Radiant' if spirit_radiant else 'Dire'}")
        resultados.append(f"- **Heróis Team Spirit:** {', '.join(map(str, spirit_heroes))}")
        resultados.append(f"- **Heróis Team Tidebound:** {', '.join(map(str, tidebound_heroes))}")
        
        # Estatísticas de jogadores Team Spirit
        resultados.append("\n#### Estatísticas de Jogadores Team Spirit\n")
        resultados.append("| Player ID | Kills | Deaths | Assists | GPM | XPM |")
        resultados.append("|-----------|-------|--------|---------|-----|-----|")
        for _, player in spirit_players.iterrows():
            resultados.append(f"| {player['player_id']} | {player['player_kills']} | {player['player_deaths']} | {player['player_assists']} | {player['gpm']} | {player['xpm']} |")
        
        # Estatísticas de jogadores Team Tidebound
        resultados.append("\n#### Estatísticas de Jogadores Team Tidebound\n")
        resultados.append("| Player ID | Kills | Deaths | Assists | GPM | XPM |")
        resultados.append("|-----------|-------|--------|---------|-----|-----|")
        for _, player in tidebound_players.iterrows():
            resultados.append(f"| {player['player_id']} | {player['player_kills']} | {player['player_deaths']} | {player['player_assists']} | {player['gpm']} | {player['xpm']} |")
        
        resultados.append("\n")
        
        # Armazenar detalhes para análise agregada
        confrontos_detalhes.append({
            'match_id': match_id,
            'data': data,
            'duracao': duracao,
            'vencedor': vencedor,
            'spirit_score': spirit_score,
            'tidebound_score': tidebound_score,
            'spirit_radiant': spirit_radiant,
            'spirit_heroes': spirit_heroes,
            'tidebound_heroes': tidebound_heroes,
            'spirit_players': spirit_players,
            'tidebound_players': tidebound_players
        })
    
    # Estatísticas gerais dos confrontos diretos
    spirit_vitorias = sum(1 for detalhe in confrontos_detalhes if detalhe['vencedor'] == 'Team Spirit')
    tidebound_vitorias = len(confrontos_diretos) - spirit_vitorias
    
    resultados.append("## Estatísticas Agregadas dos Confrontos Diretos\n")
    resultados.append(f"- **Total de confrontos:** {len(confrontos_diretos)}")
    resultados.append(f"- **Vitórias Team Spirit:** {spirit_vitorias} ({spirit_vitorias/len(confrontos_diretos):.2%})")
    resultados.append(f"- **Vitórias Team Tidebound:** {tidebound_vitorias} ({tidebound_vitorias/len(confrontos_diretos):.2%})")
    
    # Calcular duração média dos confrontos diretos
    duracao_media = sum(detalhe['duracao'] for detalhe in confrontos_detalhes) / len(confrontos_detalhes)
    resultados.append(f"- **Duração média:** {duracao_media:.2f} minutos")
    
    # Calcular diferença média de kills
    diferenca_kills = sum(detalhe['spirit_score'] - detalhe['tidebound_score'] for detalhe in confrontos_detalhes) / len(confrontos_detalhes)
    resultados.append(f"- **Diferença média de kills:** {diferenca_kills:.2f} a favor de {'Team Spirit' if diferenca_kills > 0 else 'Team Tidebound'}")
    
    # Calcular média de kills por equipe
    spirit_kills_media = sum(detalhe['spirit_score'] for detalhe in confrontos_detalhes) / len(confrontos_detalhes)
    tidebound_kills_media = sum(detalhe['tidebound_score'] for detalhe in confrontos_detalhes) / len(confrontos_detalhes)
    resultados.append(f"- **Média de kills Team Spirit:** {spirit_kills_media:.2f}")
    resultados.append(f"- **Média de kills Team Tidebound:** {tidebound_kills_media:.2f}")
    
    # Analisar lados
    spirit_radiant_count = sum(1 for detalhe in confrontos_detalhes if detalhe['spirit_radiant'])
    spirit_dire_count = len(confrontos_detalhes) - spirit_radiant_count
    resultados.append(f"- **Team Spirit como Radiant:** {spirit_radiant_count} vezes ({spirit_radiant_count/len(confrontos_detalhes):.2%})")
    resultados.append(f"- **Team Spirit como Dire:** {spirit_dire_count} vezes ({spirit_dire_count/len(confrontos_detalhes):.2%})")
    
    # Analisar vitórias por lado
    if spirit_radiant_count > 0:
        spirit_radiant_vitorias = sum(1 for detalhe in confrontos_detalhes if detalhe['spirit_radiant'] and detalhe['vencedor'] == 'Team Spirit')
        resultados.append(f"- **Taxa de vitória Team Spirit como Radiant:** {spirit_radiant_vitorias}/{spirit_radiant_count} ({spirit_radiant_vitorias/spirit_radiant_count:.2%})")
    
    if spirit_dire_count > 0:
        spirit_dire_vitorias = sum(1 for detalhe in confrontos_detalhes if not detalhe['spirit_radiant'] and detalhe['vencedor'] == 'Team Spirit')
        resultados.append(f"- **Taxa de vitória Team Spirit como Dire:** {spirit_dire_vitorias}/{spirit_dire_count} ({spirit_dire_vitorias/spirit_dire_count:.2%})")
    
    return "\n".join(resultados)

def analisar_desempenho_geral(df):
    """Analisa o desempenho geral de Team Spirit e Team Tidebound"""
    resultados = []
    resultados.append("\n## Análise de Desempenho Geral\n")
    
    # Filtrar dados para cada equipe
    spirit_df = df[df['team_name'] == 'Team Spirit']
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    
    # Estatísticas gerais Team Spirit
    resultados.append("### Team Spirit\n")
    
    # Partidas e vitórias
    partidas_spirit = spirit_df['match_id'].nunique()
    vitorias_spirit = spirit_df[spirit_df['radiant'] == spirit_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_spirit = vitorias_spirit / partidas_spirit if partidas_spirit > 0 else 0
    
    resultados.append(f"- **Partidas jogadas:** {partidas_spirit}")
    resultados.append(f"- **Vitórias:** {vitorias_spirit}")
    resultados.append(f"- **Taxa de vitória:** {taxa_vitoria_spirit:.2%}")
    
    # Duração média das partidas
    duracao_media_spirit = spirit_df['duration_sec'].mean() / 60
    resultados.append(f"- **Duração média das partidas:** {duracao_media_spirit:.2f} minutos")
    
    # Duração por resultado (vitória/derrota)
    spirit_df['victory'] = (spirit_df['radiant'] == spirit_df['radiant_win'])
    duracao_por_resultado_spirit = spirit_df.groupby('victory')['duration_sec'].mean() / 60
    
    if True in duracao_por_resultado_spirit.index and False in duracao_por_resultado_spirit.index:
        resultados.append(f"- **Duração média em vitórias:** {duracao_por_resultado_spirit[True]:.2f} minutos")
        resultados.append(f"- **Duração média em derrotas:** {duracao_por_resultado_spirit[False]:.2f} minutos")
        resultados.append(f"- **Diferença:** {duracao_por_resultado_spirit[True] - duracao_por_resultado_spirit[False]:.2f} minutos")
    
    # Desempenho por lado
    desempenho_por_lado_spirit = spirit_df.groupby(['radiant', 'victory']).size().unstack(fill_value=0)
    
    if True in desempenho_por_lado_spirit.columns and False in desempenho_por_lado_spirit.columns:
        desempenho_por_lado_spirit['total'] = desempenho_por_lado_spirit[True] + desempenho_por_lado_spirit[False]
        desempenho_por_lado_spirit['winrate'] = desempenho_por_lado_spirit[True] / desempenho_por_lado_spirit['total']
        
        resultados.append("\n#### Desempenho por Lado (Team Spirit)\n")
        resultados.append("| Lado | Vitórias | Derrotas | Total | Winrate |")
        resultados.append("|------|----------|----------|-------|---------|")
        for lado, stats in desempenho_por_lado_spirit.iterrows():
            lado_nome = "Radiant" if lado else "Dire"
            resultados.append(f"| {lado_nome} | {stats[True]:.0f} | {stats[False]:.0f} | {stats['total']:.0f} | {stats['winrate']:.2%} |")
    
    # Estatísticas gerais Team Tidebound
    resultados.append("\n### Team Tidebound\n")
    
    # Partidas e vitórias
    partidas_tidebound = tidebound_df['match_id'].nunique()
    vitorias_tidebound = tidebound_df[tidebound_df['radiant'] == tidebound_df['radiant_win']]['match_id'].nunique()
    taxa_vitoria_tidebound = vitorias_tidebound / partidas_tidebound if partidas_tidebound > 0 else 0
    
    resultados.append(f"- **Partidas jogadas:** {partidas_tidebound}")
    resultados.append(f"- **Vitórias:** {vitorias_tidebound}")
    resultados.append(f"- **Taxa de vitória:** {taxa_vitoria_tidebound:.2%}")
    
    # Duração média das partidas
    duracao_media_tidebound = tidebound_df['duration_sec'].mean() / 60
    resultados.append(f"- **Duração média das partidas:** {duracao_media_tidebound:.2f} minutos")
    
    # Duração por resultado (vitória/derrota)
    tidebound_df['victory'] = (tidebound_df['radiant'] == tidebound_df['radiant_win'])
    duracao_por_resultado_tidebound = tidebound_df.groupby('victory')['duration_sec'].mean() / 60
    
    if True in duracao_por_resultado_tidebound.index and False in duracao_por_resultado_tidebound.index:
        resultados.append(f"- **Duração média em vitórias:** {duracao_por_resultado_tidebound[True]:.2f} minutos")
        resultados.append(f"- **Duração média em derrotas:** {duracao_por_resultado_tidebound[False]:.2f} minutos")
        resultados.append(f"- **Diferença:** {duracao_por_resultado_tidebound[True] - duracao_por_resultado_tidebound[False]:.2f} minutos")
    
    # Desempenho por lado
    desempenho_por_lado_tidebound = tidebound_df.groupby(['radiant', 'victory']).size().unstack(fill_value=0)
    
    if True in desempenho_por_lado_tidebound.columns and False in desempenho_por_lado_tidebound.columns:
        desempenho_por_lado_tidebound['total'] = desempenho_por_lado_tidebound[True] + desempenho_por_lado_tidebound[False]
        desempenho_por_lado_tidebound['winrate'] = desempenho_por_lado_tidebound[True] / desempenho_por_lado_tidebound['total']
        
        resultados.append("\n#### Desempenho por Lado (Team Tidebound)\n")
        resultados.append("| Lado | Vitórias | Derrotas | Total | Winrate |")
        resultados.append("|------|----------|----------|-------|---------|")
        for lado, stats in desempenho_por_lado_tidebound.iterrows():
            lado_nome = "Radiant" if lado else "Dire"
            resultados.append(f"| {lado_nome} | {stats[True]:.0f} | {stats[False]:.0f} | {stats['total']:.0f} | {stats['winrate']:.2%} |")
    
    return "\n".join(resultados)

def analisar_herois_e_estrategias(df):
    """Analisa os heróis e estratégias de Team Spirit e Team Tidebound"""
    resultados = []
    resultados.append("\n## Análise de Heróis e Estratégias\n")
    
    # Filtrar dados para cada equipe
    spirit_df = df[df['team_name'] == 'Team Spirit']
    tidebound_df = df[df['team_name'] == 'Team Tidebound']
    
    # Heróis mais escolhidos por Team Spirit
    resultados.append("### Heróis Mais Escolhidos por Team Spirit\n")
    spirit_herois = spirit_df['hero_id'].value_counts().head(10)
    
    resultados.append("| Hero ID | Quantidade | Porcentagem |")
    resultados.append("|---------|------------|-------------|")
    for hero_id, count in spirit_herois.items():
        resultados.append(f"| {hero_id} | {count} | {count/len(spirit_df)*100:.2f}% |")
    
    # Heróis mais escolhidos por Team Tidebound
    resultados.append("\n### Heróis Mais Escolhidos por Team Tidebound\n")
    tidebound_herois = tidebound_df['hero_id'].value_counts().head(10)
    
    resultados.append("| Hero ID | Quantidade | Porcentagem |")
    resultados.append("|---------|------------|-------------|")
    for hero_id, count in tidebound_herois.items():
        resultados.append(f"| {hero_id} | {count} | {count/len(tidebound_df)*100:.2f}% |")
    
    # Heróis com maior taxa de vitória para Team Spirit
    resultados.append("\n### Heróis com Maior Taxa de Vitória para Team Spirit\n")
    spirit_df['victory'] = (spirit_df['radiant'] == spirit_df['radiant_win'])
    spirit_herois_vitorias = spirit_df.groupby(['hero_id', 'victory']).
(Content truncated due to size limit. Use line ranges to read in chunks)