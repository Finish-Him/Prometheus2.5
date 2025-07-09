import os
import pandas as pd
import json
import re
from collections import defaultdict

# Diretório onde os arquivos CSV estão localizados
upload_dir = '/home/ubuntu/upload'
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Lista para armazenar todas as informações extraídas
all_csv_data = []

# Função para extrair informações de um arquivo CSV
def extract_csv_info(file_path):
    try:
        # Carregar o CSV
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        try:
            # Tentar com encoding alternativo
            df = pd.read_csv(file_path, encoding='latin1', low_memory=False)
        except Exception as e:
            print(f"Erro ao ler {file_path}: {e}")
            return []
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return []
    
    # Nome do arquivo sem caminho e extensão
    file_name = os.path.basename(file_path).replace('.csv', '')
    
    # Lista para armazenar informações deste CSV
    csv_info = []
    
    # Adicionar metadados do arquivo
    csv_info.append({
        "type": "csv_metadata",
        "file": file_name,
        "columns": list(df.columns),
        "rows": len(df),
        "source": "upload_directory"
    })
    
    # Extrair estatísticas básicas para colunas numéricas
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            try:
                stats = {
                    "type": "column_statistics",
                    "file": file_name,
                    "column": col,
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "std": float(df[col].std())
                }
                csv_info.append(stats)
            except:
                pass
    
    # Extrair distribuições de valores para colunas categóricas
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].nunique() < 50:
            try:
                value_counts = df[col].value_counts().head(20)
                distribution = {
                    "type": "value_distribution",
                    "file": file_name,
                    "column": col,
                    "unique_values": int(df[col].nunique()),
                    "top_values": {str(k): int(v) for k, v in value_counts.items()}
                }
                csv_info.append(distribution)
            except:
                pass
    
    # Extrair correlações entre colunas numéricas
    try:
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if not numeric_df.empty and len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            for col1 in corr_matrix.columns:
                for col2 in corr_matrix.columns:
                    if col1 < col2:  # Evitar duplicações
                        correlation = {
                            "type": "correlation",
                            "file": file_name,
                            "column1": col1,
                            "column2": col2,
                            "correlation_value": float(corr_matrix.loc[col1, col2])
                        }
                        csv_info.append(correlation)
    except:
        pass
    
    # Extrair informações específicas com base no nome do arquivo
    if "heroes" in file_name.lower():
        # Extrair informações sobre heróis
        for _, row in df.iterrows():
            try:
                hero_info = {
                    "type": "hero_data",
                    "file": file_name
                }
                for col in df.columns:
                    if pd.notna(row[col]):
                        hero_info[col] = row[col]
                csv_info.append(hero_info)
            except:
                pass
    
    elif "matches" in file_name.lower():
        # Extrair informações sobre partidas
        for _, row in df.iterrows():
            try:
                match_info = {
                    "type": "match_data",
                    "file": file_name
                }
                for col in df.columns:
                    if pd.notna(row[col]):
                        match_info[col] = row[col]
                csv_info.append(match_info)
            except:
                pass
    
    elif "players" in file_name.lower():
        # Extrair informações sobre jogadores
        for _, row in df.iterrows():
            try:
                player_info = {
                    "type": "player_data",
                    "file": file_name
                }
                for col in df.columns:
                    if pd.notna(row[col]):
                        player_info[col] = row[col]
                csv_info.append(player_info)
            except:
                pass
    
    elif "items" in file_name.lower():
        # Extrair informações sobre itens
        for _, row in df.iterrows():
            try:
                item_info = {
                    "type": "item_data",
                    "file": file_name
                }
                for col in df.columns:
                    if pd.notna(row[col]):
                        item_info[col] = row[col]
                csv_info.append(item_info)
            except:
                pass
    
    # Limitar a quantidade de informações para arquivos muito grandes
    if len(csv_info) > 1000:
        print(f"Limitando informações de {file_path} para 1000 itens")
        return csv_info[:1000]
    
    return csv_info

# Processar todos os arquivos CSV
csv_files = [f for f in os.listdir(upload_dir) if f.endswith('.csv')]
for csv_file in csv_files:
    file_path = os.path.join(upload_dir, csv_file)
    print(f"Processando {file_path}...")
    csv_info = extract_csv_info(file_path)
    all_csv_data.extend(csv_info)
    print(f"Extraídas {len(csv_info)} informações de {file_path}")

# Salvar os dados extraídos em um arquivo JSON
output_file = os.path.join(output_dir, 'csv_extracted_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_csv_data, f, ensure_ascii=False, indent=2)

print(f"Total de {len(all_csv_data)} informações extraídas dos arquivos CSV")
print(f"Dados salvos em {output_file}")
