import pandas as pd

csv_file_path = "/home/ubuntu/pgl_wallachia_s4_matches.csv"
parquet_file_path = "/home/ubuntu/pgl_wallachia_s4_matches.parquet"

print(f"Lendo o arquivo CSV: {csv_file_path}")
try:
    # Ler o arquivo CSV
    df = pd.read_csv(csv_file_path)

    # Verificar se o DataFrame não está vazio
    if not df.empty:
        # Salvar o DataFrame como Parquet
        # O engine 'pyarrow' é geralmente o padrão, mas pode ser especificado
        df.to_parquet(parquet_file_path, engine='pyarrow', index=False)
        print(f"Arquivo Parquet salvo com sucesso em: {parquet_file_path}")
    else:
        print("O arquivo CSV está vazio. Nenhum arquivo Parquet será gerado.")

except FileNotFoundError:
    print(f"Erro: Arquivo CSV não encontrado em {csv_file_path}")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a conversão para Parquet: {e}")

