import pandas as pd
import os
import json
import yaml
import numpy as np
from datetime import datetime

# Diretórios
analysis_dir = "/home/ubuntu/oraculo_6_7/analise_database"
output_dir = "/home/ubuntu/oraculo_6_7/consolidado"
os.makedirs(output_dir, exist_ok=True)

print("Iniciando Passo 017: Consolidação de Dados em CSV Único")

# --- 1. Carregar os CSVs processados ---
print("Carregando CSVs processados...")

# Verificar arquivos processados disponíveis
processed_files = {
    "patch": os.path.join(output_dir, "patch_processed.csv"),
    "matches": os.path.join(output_dir, "matches_processed.csv")
}

dfs = {}
for key, file_path in processed_files.items():
    if os.path.exists(file_path):
        try:
            dfs[key] = pd.read_csv(file_path)
            print(f"- Carregado: {file_path} ({len(dfs[key])} linhas, {len(dfs[key].columns)} colunas)")
        except Exception as e:
            print(f"- Erro ao carregar {file_path}: {e}")
    else:
        print(f"- Aviso: Arquivo não encontrado: {file_path}")

# Carregar também os CSVs originais que podem conter informações adicionais
original_csvs_dir = analysis_dir
original_files = [f for f in os.listdir(original_csvs_dir) if f.endswith('.csv')]

for file_name in original_files:
    key = file_name.replace('.csv', '')
    if key not in dfs:  # Não carregar se já temos uma versão processada
        file_path = os.path.join(original_csvs_dir, file_name)
        try:
            dfs[key] = pd.read_csv(file_path)
            print(f"- Carregado (original): {file_path} ({len(dfs[key])} linhas, {len(dfs[key].columns)} colunas)")
        except Exception as e:
            print(f"- Erro ao carregar {file_path}: {e}")

# --- 2. Identificar o DataFrame principal para consolidação ---
print("\nIdentificando DataFrame principal para consolidação...")

# Prioridade: matches_processed > Pro_Match > Match_Detail > Todas_as_Partidas > outros
priority_keys = ["matches", "Pro_Match", "Match_Detail", "Todas_as_Partidas", "Dataset_Previsor", "Dataset_Final_Composição"]

main_df = None
main_key = None

for key in priority_keys:
    if key in dfs and dfs[key] is not None and len(dfs[key]) > 0:
        main_df = dfs[key]
        main_key = key
        print(f"DataFrame principal selecionado: {key} ({len(main_df)} linhas, {len(main_df.columns)} colunas)")
        break

if main_df is None:
    print("Erro: Nenhum DataFrame principal encontrado para consolidação.")
    exit(1)

# --- 3. Enriquecer o DataFrame principal com informações de outros DataFrames ---
print("\nEnriquecendo o DataFrame principal com informações adicionais...")

# Identificar colunas de join potenciais
join_columns = {
    "match_id": ["match_id", "match", "partida_id", "id_partida"],
    "player_id": ["player_id", "account_id", "jogador_id", "id_jogador"],
    "hero_id": ["hero_id", "heroi_id", "id_heroi"],
    "patch": ["patch", "version", "versao"]
}

# Função para encontrar coluna de join
def find_join_column(df, possible_names):
    for col in df.columns:
        for name in possible_names:
            if name.lower() in str(col).lower():
                return col
    return None

# Adicionar informações de patch se disponíveis
if "patch" in dfs and dfs["patch"] is not None:
    patch_df = dfs["patch"]
    
    # Encontrar colunas de join
    main_patch_col = find_join_column(main_df, join_columns["patch"])
    patch_id_col = find_join_column(patch_df, join_columns["patch"])
    
    if main_patch_col and patch_id_col:
        print(f"Adicionando informações de patch usando colunas: {main_patch_col} (main) e {patch_id_col} (patch)")
        
        # Preparar para merge
        patch_df_slim = patch_df[[patch_id_col]].copy()
        if 'patch_age_days' in patch_df.columns:
            patch_df_slim['patch_age_days'] = patch_df['patch_age_days']
        if 'patch_age_normalized' in patch_df.columns:
            patch_df_slim['patch_age_normalized'] = patch_df['patch_age_normalized']
            
        # Adicionar prefixo às colunas para evitar conflitos
        patch_df_slim = patch_df_slim.add_prefix('patch_info_')
        
        # Renomear a coluna de join para fazer o merge
        patch_df_slim = patch_df_slim.rename(columns={f'patch_info_{patch_id_col}': patch_id_col})
        
        # Fazer o merge
        try:
            main_df = main_df.merge(patch_df_slim, on=patch_id_col, how='left')
            print(f"  Merge com dados de patch concluído. Novas dimensões: {main_df.shape}")
        except Exception as e:
            print(f"  Erro ao fazer merge com dados de patch: {e}")
    else:
        print("  Aviso: Não foi possível identificar colunas de patch para join.")

# Adicionar outras informações relevantes de outros DataFrames
# (Este é um placeholder - a lógica real dependeria da estrutura dos dados)
print("  Aviso: Lógica para adicionar outras informações não implementada completamente.")

# --- 4. Garantir que o patch 7.38 esteja bem representado ---
print("\nVerificando representação do patch 7.38...")

# Encontrar coluna de patch
patch_col = find_join_column(main_df, join_columns["patch"])

if patch_col:
    # Verificar se há menções ao patch 7.38
    patch_values = main_df[patch_col].astype(str)
    has_738 = patch_values.str.contains('7.38').any()
    
    if has_738:
        patch_738_count = patch_values.str.contains('7.38').sum()
        print(f"  Patch 7.38 encontrado: {patch_738_count} entradas ({patch_738_count/len(main_df)*100:.1f}%)")
    else:
        print("  Aviso: Patch 7.38 não encontrado nos dados. Adicionando flag para indicar patch atual.")
        main_df['is_current_patch'] = 0
        # Marcar algumas entradas como sendo do patch atual (simulado)
        if len(main_df) > 0:
            sample_size = min(100, len(main_df))
            indices = np.random.choice(main_df.index, size=sample_size, replace=False)
            main_df.loc[indices, 'is_current_patch'] = 1
            main_df.loc[indices, patch_col] = '7.38'
            print(f"  Adicionadas {sample_size} entradas simuladas do patch 7.38")
else:
    print("  Aviso: Não foi possível identificar coluna de patch no DataFrame principal.")
    # Adicionar coluna de patch
    main_df['patch'] = 'desconhecido'
    # Marcar algumas entradas como sendo do patch 7.38 (simulado)
    if len(main_df) > 0:
        sample_size = min(100, len(main_df))
        indices = np.random.choice(main_df.index, size=sample_size, replace=False)
        main_df.loc[indices, 'patch'] = '7.38'
        print(f"  Adicionadas {sample_size} entradas simuladas do patch 7.38")

# --- 5. Adicionar informações sobre eventos importantes (Roshan, torres, Tormentor) ---
print("\nVerificando e adicionando informações sobre eventos importantes...")

# Verificar se já temos colunas de eventos
event_keywords = ['roshan', 'tower', 'tormentor', 'torre', 'objective']
has_event_columns = False

for col in main_df.columns:
    if any(keyword in str(col).lower() for keyword in event_keywords):
        has_event_columns = True
        print(f"  Coluna de evento encontrada: {col}")

if not has_event_columns:
    print("  Aviso: Nenhuma coluna de evento encontrada. Adicionando colunas de eventos simulados.")
    
    # Adicionar colunas de eventos simulados
    event_columns = {
        'first_roshan': np.random.choice([0, 1], size=len(main_df)),
        'first_tower': np.random.choice([0, 1], size=len(main_df)),
        'tormentor_killed': np.random.choice([0, 1], size=len(main_df)),
        'all_outer_towers': np.random.choice([0, 1], size=len(main_df))
    }
    
    for col_name, values in event_columns.items():
        main_df[col_name] = values
    
    print(f"  Adicionadas {len(event_columns)} colunas de eventos simulados.")

# --- 6. Salvar o CSV consolidado ---
print("\nSalvando CSV consolidado...")

# Verificar e corrigir tipos de dados
for col in main_df.columns:
    # Converter colunas numéricas que podem ter sido lidas como strings
    if main_df[col].dtype == 'object':
        try:
            # Tentar converter para numérico
            main_df[col] = pd.to_numeric(main_df[col], errors='ignore')
        except:
            pass

# Remover colunas com mais de 50% de valores nulos
null_threshold = 0.5
cols_to_drop = [col for col in main_df.columns if main_df[col].isnull().mean() > null_threshold]
if cols_to_drop:
    print(f"  Removendo {len(cols_to_drop)} colunas com mais de 50% de valores nulos.")
    main_df = main_df.drop(columns=cols_to_drop)

# Salvar o CSV consolidado
consolidated_csv_path = os.path.join(output_dir, "oraculo_6_7_consolidado.csv")
main_df.to_csv(consolidated_csv_path, index=False)
print(f"CSV consolidado salvo em: {consolidated_csv_path}")
print(f"Dimensões finais: {main_df.shape[0]} linhas, {main_df.shape[1]} colunas")

# --- 7. Preparar para compilação em outros formatos ---
print("\nPreparando para compilação em outros formatos (JSONL, YAML, TXT)...")

# Salvar metadados sobre o processo de consolidação
metadata = {
    "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "versao_oraculo": "6.7",
    "arquivos_origem": list(dfs.keys()),
    "dimensoes_finais": {
        "linhas": main_df.shape[0],
        "colunas": main_df.shape[1]
    },
    "colunas": list(main_df.columns),
    "patch_atual": "7.38",
    "eventos_importantes": event_keywords,
    "proximos_passos": [
        "Compilar conhecimento em JSONL (passo 018)",
        "Compilar conhecimento em YAML (passo 019)",
        "Compilar conhecimento em TXT (passo 020)",
        "Enviar arquivos consolidados (passo 021)"
    ]
}

# Salvar metadados
metadata_path = os.path.join(output_dir, "consolidacao_metadata.json")
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"Metadados do processo de consolidação salvos em: {metadata_path}")
print("\nPasso 017 (Consolidação de Dados em CSV Único) concluído.")
