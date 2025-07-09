import json
import pandas as pd

# Caminhos dos arquivos
json_input_file = '/home/ubuntu/leagues_detailed_data.json'
csv_output_file = '/home/ubuntu/leagues_detailed_data.csv'

try:
    # Carregar os dados JSON detalhados
    with open(json_input_file, 'r', encoding='utf-8') as f:
        leagues_data = json.load(f)

    if not leagues_data:
        print(f"Aviso: O arquivo JSON {json_input_file} está vazio ou não contém dados válidos.")
        # Criar um arquivo CSV vazio ou com cabeçalhos se necessário
        # Por agora, vamos apenas sair se não houver dados.
    else:
        # Converter os dados JSON (lista de dicionários) para um DataFrame do Pandas
        # Usar json_normalize pode ajudar a achatar estruturas aninhadas, se houver.
        # No entanto, se a estrutura for uma lista simples de objetos, pd.DataFrame é suficiente.
        # Vamos tentar com pd.DataFrame primeiro.
        df = pd.DataFrame(leagues_data)

        # Salvar o DataFrame em um arquivo CSV
        df.to_csv(csv_output_file, index=False, encoding='utf-8')

        print(f"Dados convertidos de JSON para CSV e salvos em {csv_output_file}")

except FileNotFoundError:
    print(f"Erro: Arquivo de entrada {json_input_file} não encontrado.")
except json.JSONDecodeError:
    print(f"Erro ao decodificar o arquivo JSON {json_input_file}.")
except Exception as e:
    print(f"Ocorreu um erro inesperado durante a conversão para CSV: {e}")


