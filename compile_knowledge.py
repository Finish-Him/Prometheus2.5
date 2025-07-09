import pandas as pd
import json
import os

# Diretórios
consolidated_dir = "/home/ubuntu/oraculo_6_7/consolidado"
output_file_jsonl = os.path.join(consolidated_dir, "oraculo_6_7_conhecimento.jsonl")
consolidated_csv_path = os.path.join(consolidated_dir, "oraculo_6_7_consolidado.csv")
metadata_path = os.path.join(consolidated_dir, "consolidacao_metadata.json")

print("Iniciando Passo 018: Compilação de Conhecimento em JSONL")

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

# --- 3. Compilar em JSONL ---
print(f"Compilando dados em JSONL: {output_file_jsonl}")
lines_written = 0
try:
    with open(output_file_jsonl, 'w', encoding='utf-8') as f_jsonl:
        # Adicionar metadados como primeira linha (opcional, mas pode ser útil)
        if metadata:
             metadata_record = {"type": "metadata", "content": metadata}
             f_jsonl.write(json.dumps(metadata_record, ensure_ascii=False) + '\n')
             lines_written += 1

        # Adicionar cada linha do CSV consolidado como um registro JSON
        if df_consolidated is not None:
            for index, row in df_consolidated.iterrows():
                # Converter a linha para um dicionário, tratando NaNs
                record = row.where(pd.notnull(row), None).to_dict()
                # Adicionar um tipo para diferenciar (opcional)
                record_jsonl = {"type": "match_data", "content": record}
                f_jsonl.write(json.dumps(record_jsonl, ensure_ascii=False) + '\n')
                lines_written += 1
        else:
             print("  Aviso: CSV consolidado não disponível para compilação em JSONL.")

    print(f"  Compilação em JSONL concluída. Total de linhas escritas: {lines_written}")

except Exception as e:
    print(f"Erro durante a compilação em JSONL: {e}")

print("\nPasso 018 (Compilação em JSONL) concluído.")

