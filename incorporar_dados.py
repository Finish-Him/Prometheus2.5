import pandas as pd
import os
import json
import numpy as np
from datetime import datetime

# Diretório de trabalho
work_dir = '/home/ubuntu/pgl_wallachia_analysis'
output_dir = os.path.join(work_dir, 'processed_data')
os.makedirs(output_dir, exist_ok=True)

print("Iniciando incorporação dos dados na base existente...")

# Carregar o arquivo "Todas as Partidas.csv"
print("Carregando Todas as Partidas.csv...")
todas_partidas_df = pd.read_csv(os.path.join(work_dir, 'Todas as Partidas.csv'))
print(f"Carregadas {len(todas_partidas_df)} linhas de Todas as Partidas.csv")

# Extrair informações específicas sobre Team Spirit e Team Tidebound
team_spirit_matches = todas_partidas_df[todas_partidas_df['team_name'] == 'Team Spirit']
team_tidebound_matches = todas_partidas_df[todas_partidas_df['team_name'] == 'Team Tidebound']

print(f"Encontradas {len(team_spirit_matches)} partidas de Team Spirit")
print(f"Encontradas {len(team_tidebound_matches)} partidas de Team Tidebound")

# Salvar os dados filtrados
team_spirit_matches.to_csv(os.path.join(output_dir, 'team_spirit_matches.csv'), index=False)
team_tidebound_matches.to_csv(os.path.join(output_dir, 'team_tidebound_matches.csv'), index=False)

# Tentar carregar uma amostra do arquivo pgl_wallachia_opendota_full.csv
# Este arquivo é muito grande, então vamos carregar apenas as primeiras linhas para análise
print("Carregando amostra de pgl_wallachia_opendota_full.csv...")
try:
    # Tentar carregar apenas as primeiras 1000 linhas para análise
    opendota_sample = pd.read_csv(os.path.join(work_dir, 'pgl_wallachia_opendota_full.csv'), nrows=1000)
    print(f"Carregadas {len(opendota_sample)} linhas de amostra de pgl_wallachia_opendota_full.csv")
    
    # Salvar a amostra para análise
    opendota_sample.to_csv(os.path.join(output_dir, 'opendota_sample.csv'), index=False)
except Exception as e:
    print(f"Erro ao carregar pgl_wallachia_opendota_full.csv: {e}")
    # Tentar uma abordagem alternativa - ler o arquivo em chunks
    print("Tentando abordagem alternativa com chunks...")
    chunk_size = 100
    chunks = []
    
    try:
        for chunk in pd.read_csv(os.path.join(work_dir, 'pgl_wallachia_opendota_full.csv'), chunksize=chunk_size):
            chunks.append(chunk)
            if len(chunks) >= 10:  # Limitar a 10 chunks (1000 linhas)
                break
                
        if chunks:
            opendota_sample = pd.concat(chunks, ignore_index=True)
            print(f"Carregadas {len(opendota_sample)} linhas de amostra de pgl_wallachia_opendota_full.csv usando chunks")
            opendota_sample.to_csv(os.path.join(output_dir, 'opendota_sample.csv'), index=False)
    except Exception as e2:
        print(f"Erro na abordagem alternativa: {e2}")
        print("Não foi possível carregar pgl_wallachia_opendota_full.csv")

# Tentar carregar uma amostra do arquivo pgl_wallachia_players_all.csv
print("Carregando amostra de pgl_wallachia_players_all.csv...")
try:
    # Tentar carregar apenas as primeiras 1000 linhas para análise
    players_sample = pd.read_csv(os.path.join(work_dir, 'pgl_wallachia_players_all.csv'), nrows=1000)
    print(f"Carregadas {len(players_sample)} linhas de amostra de pgl_wallachia_players_all.csv")
    
    # Salvar a amostra para análise
    players_sample.to_csv(os.path.join(output_dir, 'players_sample.csv'), index=False)
except Exception as e:
    print(f"Erro ao carregar pgl_wallachia_players_all.csv: {e}")
    # Tentar uma abordagem alternativa - ler o arquivo em chunks
    print("Tentando abordagem alternativa com chunks...")
    chunk_size = 100
    chunks = []
    
    try:
        for chunk in pd.read_csv(os.path.join(work_dir, 'pgl_wallachia_players_all.csv'), chunksize=chunk_size):
            chunks.append(chunk)
            if len(chunks) >= 10:  # Limitar a 10 chunks (1000 linhas)
                break
                
        if chunks:
            players_sample = pd.concat(chunks, ignore_index=True)
            print(f"Carregadas {len(players_sample)} linhas de amostra de pgl_wallachia_players_all.csv usando chunks")
            players_sample.to_csv(os.path.join(output_dir, 'players_sample.csv'), index=False)
    except Exception as e2:
        print(f"Erro na abordagem alternativa: {e2}")
        print("Não foi possível carregar pgl_wallachia_players_all.csv")

# Criar um arquivo de metadados para rastrear a incorporação
metadata = {
    'data_processamento': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'arquivos_processados': [
        'Todas as Partidas.csv',
        'pgl_wallachia_opendota_full.csv (amostra)',
        'pgl_wallachia_players_all.csv (amostra)'
    ],
    'total_partidas': len(todas_partidas_df),
    'partidas_team_spirit': len(team_spirit_matches),
    'partidas_team_tidebound': len(team_tidebound_matches)
}

with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=4)

print("Incorporação de dados concluída com sucesso!")
print(f"Dados processados salvos em: {output_dir}")
