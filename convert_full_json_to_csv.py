import pandas as pd
import json

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
csv_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.csv"

print(f"Lendo o arquivo JSON completo: {json_file_path}")
try:
    # Ler o arquivo JSON completo (lista de partidas)
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list) and data:
        print("Normalizando dados JSON para DataFrame...")
        # Usar json_normalize para achatar a estrutura JSON.
        # max_level=1 pode ajudar a controlar a complexidade inicial.
        # Ajustes podem ser necessários dependendo da estrutura exata e profundidade desejada.
        df = pd.json_normalize(data, max_level=1) # Tentar achatar um nível
        
        # Converter colunas que são listas/dicionários para string para salvar em CSV
        # Isso evita erros e mantém a informação, embora não seja ideal para análise direta no CSV
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                print(f"Convertendo coluna complexa '{col}' para string.")
                df[col] = df[col].astype(str)

        print(f"Salvando DataFrame como CSV em: {csv_file_path}")
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print("Arquivo CSV com detalhes completos salvo com sucesso.")
        
    elif isinstance(data, list) and not data:
        print("O arquivo JSON completo está vazio. Nenhum arquivo CSV será gerado.")
    else:
        print("Formato JSON inesperado. Esperava uma lista de partidas.")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a conversão para CSV: {e}")

