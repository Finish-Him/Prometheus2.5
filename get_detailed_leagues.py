import requests
import json
import time

# Carregar os dados básicos das ligas do arquivo JSON existente
input_file = '/home/ubuntu/leagues_data.json'
output_file = '/home/ubuntu/leagues_detailed_data.json'

leagues_detailed_data = []

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        basic_leagues_data = json.load(f)

    print(f"Carregados {len(basic_leagues_data)} ligas básicas de {input_file}")

    # Iterar sobre cada liga básica para obter detalhes
    for league in basic_leagues_data:
        league_id = league.get('leagueid')
        if not league_id:
            print(f"Aviso: Liga sem leagueid encontrada: {league}")
            continue

        # URL da API para detalhes da liga específica
        detail_url = f"https://api.opendota.com/api/leagues/{league_id}"

        try:
            print(f"Obtendo detalhes para league_id: {league_id}...")
            response = requests.get(detail_url)
            response.raise_for_status()  # Levanta erro para status HTTP ruins

            detailed_info = response.json()
            leagues_detailed_data.append(detailed_info)

            # Adicionar um pequeno delay para respeitar os limites da API (60 reqs/min)
            time.sleep(1.1) # Espera um pouco mais de 1 segundo

        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter detalhes para league_id {league_id}: {e}")
            # Adicionar a informação básica mesmo se a detalhada falhar?
            # Por agora, vamos apenas registar o erro e continuar.
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON para league_id {league_id}.")
        except Exception as e:
            print(f"Erro inesperado ao processar league_id {league_id}: {e}")

    # Salvar os dados detalhados das ligas em um novo arquivo JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(leagues_detailed_data, f, ensure_ascii=False, indent=4)

    print(f"Dados detalhados de {len(leagues_detailed_data)} ligas salvas em {output_file}")

except FileNotFoundError:
    print(f"Erro: Arquivo de entrada {input_file} não encontrado.")
except json.JSONDecodeError:
    print(f"Erro ao decodificar o arquivo JSON de entrada {input_file}.")
except Exception as e:
    print(f"Ocorreu um erro inesperado no script principal: {e}")


