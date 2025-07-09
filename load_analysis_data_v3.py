import json
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados com sucesso para nova análise.")
    # Os dados estão agora na variável 'matches_data' (lista de dicionários)
    # O próximo script usará esta estrutura de dados.

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# Este script apenas carrega os dados. A análise será feita em outro script.
# Para simplificar, o próximo script irá incluir este carregamento.
print("Dados prontos para serem usados nos scripts de análise.")

