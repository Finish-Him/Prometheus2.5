import requests
import json

api_key = "91fdee34-226f-4681-8f72-ee87bd85abcf"
league_id = 18058 # ID correto para PGL Wallachia 2025 Season 4
output_json_file = "/home/ubuntu/pgl_wallachia_s4_matches.json"

url = f"https://api.opendota.com/api/leagues/{league_id}/matches"
params = {"api_key": api_key}

print(f"Buscando dados da liga {league_id} (PGL Wallachia 2025 Season 4)...")
try:
    response = requests.get(url, params=params)
    response.raise_for_status()  # Lança exceção para códigos de erro HTTP (4xx ou 5xx)

    matches_data = response.json()

    if not matches_data:
        print(f"Nenhuma partida encontrada para a liga {league_id} ou ocorreu um erro na API.")
    else:
        print(f"Total de {len(matches_data)} partidas encontradas.")
        # Salvar os dados em JSON
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(matches_data, f, ensure_ascii=False, indent=4)
        print(f"Dados das partidas salvos em {output_json_file}")

except requests.exceptions.RequestException as e:
    print(f"Erro ao buscar dados da API OpenDota: {e}")
except json.JSONDecodeError:
    print("Erro ao decodificar a resposta JSON da API.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")

