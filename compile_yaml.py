import pandas as pd
import json
import yaml
import os

# Diretórios
consolidated_dir = "/home/ubuntu/oraculo_6_7/consolidado"
output_file_yaml = os.path.join(consolidated_dir, "oraculo_6_7_conhecimento.yaml")
consolidated_csv_path = os.path.join(consolidated_dir, "oraculo_6_7_consolidado.csv")
metadata_path = os.path.join(consolidated_dir, "consolidacao_metadata.json")

print("Iniciando Passo 019: Compilação de Conhecimento em YAML")

# --- 1. Carregar Dados Consolidados ---
print(f"Carregando CSV consolidado: {consolidated_csv_path}")
try:
    df_consolidated = pd.read_csv(consolidated_csv_path)
    print(f"  Carregado com sucesso: {len(df_consolidated)} linhas, {len(df_consolidated.columns)} colunas")
except Exception as e:
    print(f"Erro ao carregar CSV consolidado: {e}")
    df_consolidated = None

# --- 2. Carregar Metadados ---
print(f"Carregando metadados: {metadata_path}")
try:
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    print("  Metadados carregados com sucesso.")
except Exception as e:
    print(f"Erro ao carregar metadados: {e}")
    metadata = None

# --- 3. Compilar em YAML ---
print(f"Compilando dados em YAML: {output_file_yaml}")
try:
    # Preparar estrutura de dados para YAML
    yaml_data = {
        "metadata": metadata,
        "dados": []
    }
    
    # Adicionar dados do CSV
    if df_consolidated is not None:
        for index, row in df_consolidated.iterrows():
            # Converter a linha para um dicionário, tratando NaNs
            record = row.where(pd.notnull(row), None).to_dict()
            yaml_data["dados"].append(record)
    else:
        print("  Aviso: CSV consolidado não disponível para compilação em YAML.")
    
    # Escrever arquivo YAML
    with open(output_file_yaml, 'w', encoding='utf-8') as f_yaml:
        yaml.dump(yaml_data, f_yaml, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"  Compilação em YAML concluída. Estrutura: metadados + {len(yaml_data['dados'])} registros de dados.")

except Exception as e:
    print(f"Erro durante a compilação em YAML: {e}")

print("\nPasso 019 (Compilação em YAML) concluído.")
