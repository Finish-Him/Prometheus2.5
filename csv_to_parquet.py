import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Caminhos dos arquivos
csv_input_file = '/home/ubuntu/leagues_detailed_data.csv'
parquet_output_file = '/home/ubuntu/leagues_detailed_data.parquet'

try:
    # Ler o arquivo CSV para um DataFrame do Pandas
    df = pd.read_csv(csv_input_file, encoding='utf-8')

    if df.empty:
        print(f"Aviso: O arquivo CSV {csv_input_file} está vazio.")
        # Criar um arquivo Parquet vazio se necessário?
        # Por agora, vamos apenas sair se não houver dados.
    else:
        # Converter o DataFrame do Pandas para uma Tabela do PyArrow
        table = pa.Table.from_pandas(df)

        # Escrever a Tabela do PyArrow em um arquivo Parquet
        pq.write_table(table, parquet_output_file)

        print(f"Dados convertidos de CSV para Parquet e salvos em {parquet_output_file}")

except FileNotFoundError:
    print(f"Erro: Arquivo de entrada {csv_input_file} não encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a conversão para Parquet: {e}")


