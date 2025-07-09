import pandas as pd

csv_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.csv"
parquet_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.parquet"

print(f"Lendo o arquivo CSV completo: {csv_file_path}")
try:
    # Ler o arquivo CSV
    # É importante notar que colunas complexas foram convertidas para string na etapa anterior.
    # O Parquet pode lidar melhor com tipos aninhados, mas aqui estamos lendo do CSV.
    df = pd.read_csv(csv_file_path)

    if not df.empty:
        print(f"Salvando DataFrame como Parquet em: {parquet_file_path}")
        # Salvar o DataFrame como Parquet usando pyarrow
        df.to_parquet(parquet_file_path, engine='pyarrow', index=False)
        print("Arquivo Parquet com detalhes completos salvo com sucesso.")
    else:
        print("O arquivo CSV está vazio. Nenhum arquivo Parquet será gerado.")

except FileNotFoundError:
    print(f"Erro: Arquivo CSV não encontrado em {csv_file_path}")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a conversão para Parquet: {e}")

