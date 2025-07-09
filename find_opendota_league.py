import requests
import json

api_key = "91fdee34-226f-4681-8f72-ee87bd85abcf"
search_term = "PGL Wallachia" # Termo de busca mais amplo

url = "https://api.opendota.com/api/leagues"
params = {"api_key": api_key}

print(f"Buscando ligas na OpenDota...")
try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    leagues = response.json()

    found_leagues = []
    if leagues:
        print(f"Total de {len(leagues)} ligas encontradas. Procurando por 	'{search_term}	'...")
        for league in leagues:
            # Verifica se o nome da liga contém o termo de busca (case-insensitive)
            if search_term.lower() in league.get('name', '').lower():
                found_leagues.append(league)
                print(f"Liga encontrada: ID={league.get('leagueid')}, Nome={league.get('name')}, Tier={league.get('tier')}")
    
    if not found_leagues:
        print(f"Nenhuma liga encontrada contendo 	'{search_term}	'.")
    elif len(found_leagues) > 0:
        print(f"{len(found_leagues)} liga(s) encontrada(s) contendo 	'{search_term}	'. Verifique os IDs listados.")

except requests.exceptions.RequestException as e:
    print(f"Erro ao buscar dados da API OpenDota: {e}")
except json.JSONDecodeError:
    print("Erro ao decodificar a resposta JSON da API.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")

