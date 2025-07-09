import json
import pandas as pd
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list):
        print("Erro: O arquivo JSON não contém uma lista de partidas.")
        sys.exit(1)
        
    if not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados com sucesso.")

    # Opcional: Tentar carregar em DataFrame para visualização inicial
    # try:
    #     df = pd.json_normalize(matches_data, max_level=1)
    #     print(f"DataFrame criado com {df.shape[0]} linhas e {df.shape[1]} colunas (nível 1 de normalização).")
    #     # print("Primeiras 5 linhas do DataFrame:")
    #     # print(df.head())
    #     # print("\nColunas do DataFrame:")
    #     # print(df.columns.tolist())
    # except Exception as e:
    #     print(f"Não foi possível converter para DataFrame com json_normalize: {e}")
    #     print("Prosseguindo com os dados como lista de dicionários.")

    # Para os próximos passos, os dados estão na variável 'matches_data' (lista de dicionários)
    print("Os dados estão prontos para análise como uma lista de dicionários.")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

