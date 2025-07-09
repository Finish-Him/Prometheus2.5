import json
import pandas as pd
import pyarrow.parquet as pq

# Caminhos dos arquivos
json_file = '/home/ubuntu/leagues_detailed_data.json'
csv_file = '/home/ubuntu/leagues_detailed_data.csv'
parquet_file = '/home/ubuntu/leagues_detailed_data.parquet'

validation_passed = True
error_messages = []

try:
    # Validar JSON
    print(f"Validando {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        json_record_count = len(json_data)
        print(f"JSON: {json_record_count} registos encontrados.")
        if json_record_count != 50:
            validation_passed = False
            error_messages.append(f"Erro JSON: Esperados 50 registos, encontrados {json_record_count}.")

except FileNotFoundError:
    validation_passed = False
    error_messages.append(f"Erro: Arquivo {json_file} não encontrado.")
    print(f"Erro: Arquivo {json_file} não encontrado.")
except json.JSONDecodeError:
    validation_passed = False
    error_messages.append(f"Erro: Falha ao decodificar {json_file}.")
    print(f"Erro: Falha ao decodificar {json_file}.")
except Exception as e:
    validation_passed = False
    error_messages.append(f"Erro inesperado ao validar JSON: {e}")
    print(f"Erro inesperado ao validar JSON: {e}")

try:
    # Validar CSV
    print(f"Validando {csv_file}...")
    df_csv = pd.read_csv(csv_file)
    csv_record_count = len(df_csv)
    csv_column_count = len(df_csv.columns)
    print(f"CSV: {csv_record_count} registos e {csv_column_count} colunas encontrados.")
    if csv_record_count != 50:
        validation_passed = False
        error_messages.append(f"Erro CSV: Esperados 50 registos, encontrados {csv_record_count}.")

except FileNotFoundError:
    validation_passed = False
    error_messages.append(f"Erro: Arquivo {csv_file} não encontrado.")
    print(f"Erro: Arquivo {csv_file} não encontrado.")
except Exception as e:
    validation_passed = False
    error_messages.append(f"Erro inesperado ao validar CSV: {e}")
    print(f"Erro inesperado ao validar CSV: {e}")

try:
    # Validar Parquet
    print(f"Validando {parquet_file}...")
    table_parquet = pq.read_table(parquet_file)
    df_parquet = table_parquet.to_pandas()
    parquet_record_count = len(df_parquet)
    parquet_column_count = len(df_parquet.columns)
    print(f"Parquet: {parquet_record_count} registos e {parquet_column_count} colunas encontrados.")
    if parquet_record_count != 50:
        validation_passed = False
        error_messages.append(f"Erro Parquet: Esperados 50 registos, encontrados {parquet_record_count}.")

    # Comparar colunas CSV e Parquet
    if 'df_csv' in locals() and csv_column_count != parquet_column_count:
        validation_passed = False
        error_messages.append(f"Erro Colunas: CSV ({csv_column_count}) e Parquet ({parquet_column_count}) têm número diferente de colunas.")
        print(f"Erro Colunas: CSV ({csv_column_count}) e Parquet ({parquet_column_count}) têm número diferente de colunas.")
    elif 'df_csv' in locals():
         print("Número de colunas consistente entre CSV e Parquet.")

except FileNotFoundError:
    validation_passed = False
    error_messages.append(f"Erro: Arquivo {parquet_file} não encontrado.")
    print(f"Erro: Arquivo {parquet_file} não encontrado.")
except Exception as e:
    validation_passed = False
    error_messages.append(f"Erro inesperado ao validar Parquet: {e}")
    print(f"Erro inesperado ao validar Parquet: {e}")

# Resultado final da validação
if validation_passed:
    print("\nValidação concluída com sucesso! Todos os arquivos parecem consistentes.")
else:
    print("\nValidação falhou. Erros encontrados:")
    for msg in error_messages:
        print(f"- {msg}")


