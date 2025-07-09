#!/usr/bin/env python3

import requests
import json
import os
import urllib.parse

# Chave da API do usuário
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
# URL base da API
BASE_URL = "https://api.opendota.com/api"
# Diretório para salvar os arquivos JSON
OUTPUT_DIR = "/home/ubuntu/opendota_data"

# Cria o diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_data(endpoint_name, url):
    """Busca dados de uma URL específica e salva em JSON."""
    print(f"Fetching data from: {endpoint_name}")
    # A URL já inclui a chave da API e parâmetros necessários
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        data = response.json()

        # Salva os dados em um arquivo JSON
        file_path = os.path.join(OUTPUT_DIR, f"{endpoint_name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {file_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        # Tenta ler o corpo da resposta se houver erro
        try:
            error_details = response.json()
            print(f"Error details: {error_details}")
        except Exception:
            print(f"Could not decode error response from {url}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {url}: {e}")
        return False

if __name__ == "__main__":
    all_successful = True

    # 1. Buscar partidas profissionais do Patch 7.38 via /explorer
    print("--- Fetching Pro Matches Patch 7.38 ---")
    sql_query = "SELECT m.match_id, m.start_time, m.duration, m.radiant_team_id, m.dire_team_id, m.leagueid, m.radiant_score, m.dire_score, m.radiant_win FROM matches m JOIN match_patch mp ON m.match_id = mp.match_id WHERE mp.patch = '7.38' AND m.leagueid IN (SELECT leagueid FROM leagues WHERE tier = 'premium' OR tier = 'professional') ORDER BY m.start_time DESC LIMIT 1000"
    encoded_sql = urllib.parse.quote(sql_query)
    explorer_url = f"{BASE_URL}/explorer?sql={encoded_sql}&api_key={API_KEY}"
    if not fetch_data("proMatches_patch738", explorer_url):
        all_successful = False
        print("Failed to fetch pro matches for patch 7.38. Check the SQL query or API limits.")

    # 2. Buscar outros endpoints gerais (já baixados antes, mas podemos re-executar se necessário ou pular)
    print("\n--- Fetching General Endpoints ---")
    general_endpoints = {
        # "proMatches": "/proMatches", # Já temos dados mais específicos
        "proPlayers": "/proPlayers",
        "heroes": "/heroes",
        "heroStats": "/heroStats",
        "leagues": "/leagues",
        "teams": "/teams",
    }
    for name, path in general_endpoints.items():
        endpoint_url = f"{BASE_URL}{path}?api_key={API_KEY}"
        # Verifica se o arquivo já existe para não baixar novamente desnecessariamente
        file_path_check = os.path.join(OUTPUT_DIR, f"{name}.json")
        if os.path.exists(file_path_check):
            print(f"Skipping {name}, file already exists: {file_path_check}")
            continue
        if not fetch_data(name, endpoint_url):
            all_successful = False

    if all_successful:
        print("\nSuccessfully fetched all requested data.")
    else:
        print("\nEncountered errors while fetching some data.")


