import pandas as pd
import json

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches.json"
csv_file_path = "/home/ubuntu/pgl_wallachia_s4_matches.csv"

print(f"Lendo o arquivo JSON: {json_file_path}")
try:
    # Ler o arquivo JSON
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Verificar se os dados são uma lista (esperado pela API)
    if isinstance(data, list) and data:
        # Converter a lista de dicionários JSON para DataFrame do Pandas
        df = pd.json_normalize(data)
        
        # Salvar o DataFrame como CSV
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print(f"Arquivo CSV salvo com sucesso em: {csv_file_path}")
    elif isinstance(data, list) and not data:
        print("O arquivo JSON está vazio. Nenhum arquivo CSV será gerado.")
    else:
        print("Formato JSON inesperado. Esperava uma lista de partidas.")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a conversão para CSV: {e}")

