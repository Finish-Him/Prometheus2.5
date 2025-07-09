#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para preparar a base de dados do Oráculo 5.0
Este script processa os dados brutos e cria estruturas otimizadas para machine learning
"""

import os
import pandas as pd
import numpy as np
import json
from datetime import datetime

# Definir caminhos
BASE_DIR = '/home/ubuntu/oraculov5'
DADOS_BRUTOS_DIR = os.path.join(BASE_DIR, 'dados_brutos')
DADOS_PROCESSADOS_DIR = os.path.join(BASE_DIR, 'dados_processados')
MODELOS_DIR = os.path.join(BASE_DIR, 'modelos')

# Criar diretórios de saída se não existirem
os.makedirs(os.path.join(DADOS_PROCESSADOS_DIR, 'estatisticas'), exist_ok=True)
os.makedirs(os.path.join(DADOS_PROCESSADOS_DIR, 'visualizacoes'), exist_ok=True)
os.makedirs(os.path.join(MODELOS_DIR, 'predicao_duracao', 'datasets'), exist_ok=True)
os.makedirs(os.path.join(MODELOS_DIR, 'predicao_vencedor', 'datasets'), exist_ok=True)
os.makedirs(os.path.join(MODELOS_DIR, 'predicao_kills', 'datasets'), exist_ok=True)

def carregar_dados_apostas():
    """Carrega e processa os datasets de apostas"""
    print("Carregando datasets de apostas...")
    
    # Carregar datasets principais
    try:
        df_apostas = pd.read_csv(os.path.join(DADOS_PROCESSADOS_DIR, 'apostas', 'dataset_previsor_apostas.csv'))
        df_tatica = pd.read_csv(os.path.join(DADOS_PROCESSADOS_DIR, 'apostas', 'dataset_final_com_composicao_tatica.csv'))
        
        print(f"Dataset de apostas: {df_apostas.shape[0]} linhas, {df_apostas.shape[1]} colunas")
        print(f"Dataset de composição tática: {df_tatica.shape[0]} linhas, {df_tatica.shape[1]} colunas")
        
        # Verificar se há valores nulos nas colunas principais
        colunas_importantes = ['match_id', 'duration_min', 'total_kills', 'radiant_win']
        for col in colunas_importantes:
            if col in df_apostas.columns:
                nulos = df_apostas[col].isnull().sum()
                if nulos > 0:
                    print(f"Atenção: {nulos} valores nulos na coluna {col} do dataset de apostas")
            
            if col in df_tatica.columns:
                nulos = df_tatica[col].isnull().sum()
                if nulos > 0:
                    print(f"Atenção: {nulos} valores nulos na coluna {col} do dataset de composição tática")
        
        return df_apostas, df_tatica
    
    except Exception as e:
        print(f"Erro ao carregar datasets de apostas: {str(e)}")
        return None, None

def preparar_dataset_duracao(df_apostas, df_tatica):
    """Prepara dataset específico para predição de duração de partidas"""
    print("Preparando dataset para predição de duração...")
    
    if df_apostas is None or df_tatica is None:
        print("Datasets de entrada não disponíveis")
        return
    
    try:
        # Selecionar colunas relevantes para predição de duração
        colunas_duracao = [
            'match_id', 'duration_min', 'total_kills', 'first_blood_time', 
            'radiant_composicao_tipo', 'dire_composicao_tipo', 'composicao_espelhada',
            'dominancia_pushers', 'radiant_Pusher', 'dire_Pusher', 
            'radiant_Scaler', 'dire_Scaler', 'faixa_tempo'
        ]
        
        # Filtrar colunas que existem no dataset
        colunas_existentes = [col for col in colunas_duracao if col in df_apostas.columns]
        
        # Criar dataset para predição de duração
        df_duracao = df_apostas[colunas_existentes].copy()
        
        # Adicionar informações de composição tática se não estiverem presentes
        for col in colunas_duracao:
            if col not in df_duracao.columns and col in df_tatica.columns:
                df_duracao[col] = df_tatica[col]
        
        # Remover linhas com valores nulos em colunas críticas
        colunas_criticas = ['match_id', 'duration_min']
        df_duracao = df_duracao.dropna(subset=colunas_criticas)
        
        # Salvar dataset
        output_path = os.path.join(MODELOS_DIR, 'predicao_duracao', 'datasets', 'dataset_duracao.csv')
        df_duracao.to_csv(output_path, index=False)
        print(f"Dataset para predição de duração salvo em {output_path}")
        print(f"Dimensões: {df_duracao.shape[0]} linhas, {df_duracao.shape[1]} colunas")
        
        # Criar versão simplificada para referência rápida
        df_duracao_simple = df_duracao[['match_id', 'duration_min', 'faixa_tempo', 'dominancia_pushers']].copy()
        simple_path = os.path.join(DADOS_PROCESSADOS_DIR, 'estatisticas', 'duracao_partidas_resumo.csv')
        df_duracao_simple.to_csv(simple_path, index=False)
        
        return df_duracao
    
    except Exception as e:
        print(f"Erro ao preparar dataset de duração: {str(e)}")
        return None

def preparar_dataset_vencedor(df_apostas, df_tatica):
    """Prepara dataset específico para predição de vencedores"""
    print("Preparando dataset para predição de vencedores...")
    
    if df_apostas is None or df_tatica is None:
        print("Datasets de entrada não disponíveis")
        return
    
    try:
        # Selecionar colunas relevantes para predição de vencedor
        colunas_vencedor = [
            'match_id', 'radiant_win', 'radiant_score', 'dire_score',
            'radiant_composicao_tipo', 'dire_composicao_tipo', 'composicao_espelhada',
            'radiant_Engage', 'radiant_Pickoff', 'radiant_Pusher', 'radiant_Scaler',
            'dire_Engage', 'dire_Pickoff', 'dire_Pusher', 'dire_Scaler'
        ]
        
        # Filtrar colunas que existem no dataset
        colunas_existentes = [col for col in colunas_vencedor if col in df_apostas.columns]
        
        # Criar dataset para predição de vencedor
        df_vencedor = df_apostas[colunas_existentes].copy()
        
        # Adicionar informações de composição tática se não estiverem presentes
        for col in colunas_vencedor:
            if col not in df_vencedor.columns and col in df_tatica.columns:
                df_vencedor[col] = df_tatica[col]
        
        # Remover linhas com valores nulos em colunas críticas
        colunas_criticas = ['match_id', 'radiant_win']
        df_vencedor = df_vencedor.dropna(subset=colunas_criticas)
        
        # Salvar dataset
        output_path = os.path.join(MODELOS_DIR, 'predicao_vencedor', 'datasets', 'dataset_vencedor.csv')
        df_vencedor.to_csv(output_path, index=False)
        print(f"Dataset para predição de vencedor salvo em {output_path}")
        print(f"Dimensões: {df_vencedor.shape[0]} linhas, {df_vencedor.shape[1]} colunas")
        
        return df_vencedor
    
    except Exception as e:
        print(f"Erro ao preparar dataset de vencedor: {str(e)}")
        return None

def preparar_dataset_kills(df_apostas, df_tatica):
    """Prepara dataset específico para predição de total de kills"""
    print("Preparando dataset para predição de total de kills...")
    
    if df_apostas is None or df_tatica is None:
        print("Datasets de entrada não disponíveis")
        return
    
    try:
        # Selecionar colunas relevantes para predição de kills
        colunas_kills = [
            'match_id', 'total_kills', 'duration_min', 'radiant_score', 'dire_score',
            'radiant_composicao_tipo', 'dire_composicao_tipo', 'muito_kill',
            'radiant_Engage', 'radiant_Pickoff', 'dire_Engage', 'dire_Pickoff'
        ]
        
        # Filtrar colunas que existem no dataset
        colunas_existentes = [col for col in colunas_kills if col in df_apostas.columns]
        
        # Criar dataset para predição de kills
        df_kills = df_apostas[colunas_existentes].copy()
        
        # Adicionar informações de composição tática se não estiverem presentes
        for col in colunas_kills:
            if col not in df_kills.columns and col in df_tatica.columns:
                df_kills[col] = df_tatica[col]
        
        # Remover linhas com valores nulos em colunas críticas
        colunas_criticas = ['match_id', 'total_kills']
        df_kills = df_kills.dropna(subset=colunas_criticas)
        
        # Salvar dataset
        output_path = os.path.join(MODELOS_DIR, 'predicao_kills', 'datasets', 'dataset_kills.csv')
        df_kills.to_csv(output_path, index=False)
        print(f"Dataset para predição de kills salvo em {output_path}")
        print(f"Dimensões: {df_kills.shape[0]} linhas, {df_kills.shape[1]} colunas")
        
        return df_kills
    
    except Exception as e:
        print(f"Erro ao preparar dataset de kills: {str(e)}")
        return None

def processar_dados_pgl_wallachia():
    """Processa dados específicos do torneio PGL Wallachia"""
    print("Processando dados do torneio PGL Wallachia...")
    
    try:
        # Carregar dados de jogadores
        players_path = os.path.join(DADOS_BRUTOS_DIR, 'tournaments', 'pgl_wallachia', 'pgl_wallachia_season4_players.csv')
        df_players = pd.read_csv(players_path)
        
        # Calcular estatísticas por herói
        hero_stats = df_players.groupby('hero_name').agg({
            'kills': ['mean', 'sum'],
            'deaths': ['mean', 'sum'],
            'assists': ['mean', 'sum'],
            'last_hits': ['mean'],
            'gold_per_min': ['mean'],
            'xp_per_min': ['mean'],
            'hero_damage': ['mean'],
            'tower_damage': ['mean'],
            'hero_id': 'count'  # Contagem de vezes que o herói foi escolhido
        }).reset_index()
        
        # Renomear colunas
        hero_stats.columns = ['hero_name', 'kills_mean', 'kills_sum', 'deaths_mean', 'deaths_sum', 
                             'assists_mean', 'assists_sum', 'last_hits_mean', 'gold_per_min_mean', 
                             'xp_per_min_mean', 'hero_damage_mean', 'tower_damage_mean', 'pick_count']
        
        # Calcular KDA médio
        hero_stats['kda_ratio'] = (hero_stats['kills_mean'] + hero_stats['assists_mean']) / hero_stats['deaths_mean'].replace(0, 1)
        
        # Ordenar por número de escolhas
        hero_stats = hero_stats.sort_values('pick_count', ascending=False)
        
        # Salvar estatísticas
        output_path = os.path.join(DADOS_PROCESSADOS_DIR, 'estatisticas', 'pgl_wallachia_hero_stats.csv')
        hero_stats.to_csv(output_path, index=False)
        print(f"Estatísticas de heróis do PGL Wallachia salvas em {output_path}")
        
        # Calcular estatísticas por jogador
        player_stats = df_players.groupby('account_id').agg({
            'kills': ['mean', 'sum'],
            'deaths': ['mean', 'sum'],
            'assists': ['mean', 'sum'],
            'last_hits': ['mean'],
            'gold_per_min': ['mean'],
            'xp_per_min': ['mean'],
            'hero_damage': ['mean'],
            'tower_damage': ['mean'],
            'match_id': 'count'  # Contagem de partidas jogadas
        }).reset_index()
        
        # Renomear colunas
        player_stats.columns = ['account_id', 'kills_mean', 'kills_sum', 'deaths_mean', 'deaths_sum', 
                               'assists_mean', 'assists_sum', 'last_hits_mean', 'gold_per_min_mean', 
                               'xp_per_min_mean', 'hero_damage_mean', 'tower_damage_mean', 'matches_played']
        
        # Calcular KDA médio
        player_stats['kda_ratio'] = (player_stats['kills_mean'] + player_stats['assists_mean']) / player_stats['deaths_mean'].replace(0, 1)
        
        # Ordenar por número de partidas
        player_stats = player_stats.sort_values('matches_played', ascending=False)
        
        # Salvar estatísticas
        output_path = os.path.join(DADOS_PROCESSADOS_DIR, 'estatisticas', 'pgl_wallachia_player_stats.csv')
        player_stats.to_csv(output_path, index=False)
        print(f"Estatísticas de jogadores do PGL Wallachia salvas em {output_path}")
        
        return hero_stats, player_stats
    
    except Exception as e:
        print(f"Erro ao processar dados do PGL Wallachia: {str(e)}")
        return None, None

def gerar_metadados():
    """Gera arquivo de metadados para a base de dados"""
    print("Gerando metadados da base de dados...")
    
    try:
        metadata = {
            "nome": "Oráculo 5.0",
            "descricao": "Base de dados para predição de apostas em Dota 2",
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "versao": "5.0.0",
            "patch_principal": "7.38",
            "estrutura": {
                "dados_brutos": {
                    "heroes": "Informações sobre heróis do Dota 2",
                    "matches": "Dados de partidas profissionais",
                    "players": "Estatísticas de jogadores",
                    "tournaments": "Dados específicos de torneios",
                    "items": "Informações sobre itens do jogo",
                    "patches": "Histórico de patches"
                },
                "dados_processados": {
                    "apostas": "Datasets preparados para predição de apostas",
                    "estatisticas": "Estatísticas processadas e agregadas",
                    "analises": "Análises detalhadas de padrões e tendências",
                    "visualizacoes": "Gráficos e visualizações de dados"
                },
                "modelos": {
                    "predicao_duracao": "Modelos para prever duração de partidas",
                    "predicao_vencedor": "Modelos para prever vencedores",
                    "predicao_kills": "Modelos para prever total de kills",
                    "predicao_outros": "Outros modelos (first blood, Roshan kills, etc.)"
                }
            },
            "datasets_principais": [
                {
                    "nome": "dataset_previsor_apostas.csv",
                    "descricao": "Dataset principal para predição de apostas",
                    "colunas_principais": ["match_id", "duration_min", "total_kills", "first_blood_time", "radiant_win"]
                },
                {
                    "nome": "dataset_final_com_composicao_tatica.csv",
                    "descricao": "Dataset com informações sobre composições táticas",
                    "colunas_principais": ["match_id", "radiant_composicao_tipo", "dire_composicao_tipo", "composicao_espelhada"]
                },
                {
                    "nome": "pgl_wallachia_season4_players.csv",
                    "descricao": "Dados de jogadores do torneio PGL Wallachia Season 4",
                    "colunas_principais": ["match_id", "account_id", "hero_id", "kills", "deaths", "assists"]
                }
            ],
            "recomendacoes_apostas": {
                "duracao": {
                    "valor_referencia": 36.0,
                    "aposta_over": 28.0,
                    "aposta_under": 41.0
                },
                "vencedores": {
                    "herois_alta_vitoria": ["Dragon Knight", "Clinkz", "Phoenix", "Spirit Breaker", "Venomancer"],
                    "atributo_melhor": "Força"
                }
            }
        }
        
        # Salvar metadados
        output_path = os.path.join(BASE_DIR, 'documentacao', 'metadados_oraculov5.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        print(f"Metadados gerados e salvos em {output_path}")
        return metadata
    
    except Exception as e:
        print(f"Erro ao gerar metadados: {str(e)}")
        return None

def main():
    """Função principal para preparar a base de dados"""
    print("Iniciando preparação da base de dados do Oráculo 5.0...")
    
    # Carregar datasets de apostas
    df_apostas, df_tatica = carregar_dados_apostas()
    
    # Preparar datasets específicos para cada tipo de predição
    df_duracao = preparar_dataset_duracao(df_apostas, df_tatica)
    df_vencedor = preparar_dataset_vencedor(df_apostas, df_tatica)
    df_kills = preparar_dataset_kills(df_apostas, df_tatica)
    
    # Processar dados do PGL Wal
(Content truncated due to size limit. Use line ranges to read in chunks)