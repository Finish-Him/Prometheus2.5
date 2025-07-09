import requests
import json
import time
import os

api_key = "91fdee34-226f-4681-8f72-ee87bd85abcf"
input_json_file = "/home/ubuntu/pgl_wallachia_s4_matches.json" # File with list of match IDs
output_full_json_file = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"

# --- Main script ---
print(f"Lendo lista de partidas de {input_json_file}...")
try:
    with open(input_json_file, 'r', encoding='utf-8') as f:
        matches_summary = json.load(f)
except FileNotFoundError:
    print(f"Erro: Arquivo de resumo de partidas não encontrado: {input_json_file}")
    exit()
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar JSON do arquivo: {input_json_file}")
    exit()

if not isinstance(matches_summary, list) or not matches_summary:
    print("Arquivo de resumo de partidas está vazio ou em formato inválido.")
    exit()

match_ids = [match.get('match_id') for match in matches_summary if match.get('match_id')]
print(f"Encontrados {len(match_ids)} IDs de partidas. Buscando detalhes completos (incluindo itens)...")

all_matches_full_details = []
processed_count = 0
fetch_errors = 0

for match_id in match_ids:
    print(f"Buscando detalhes completos da partida {match_id} ({processed_count + 1}/{len(match_ids)})...", end='')
    url = f"https://api.opendota.com/api/matches/{match_id}"
    params = {"api_key": api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        match_full_details = response.json()
        
        # Append the entire JSON response for the match
        all_matches_full_details.append(match_full_details)
        print(" OK")
        processed_count += 1
        
    except requests.exceptions.RequestException as e:
        print(f" Erro de requisição: {e}")
        fetch_errors += 1
    except json.JSONDecodeError:
        print(" Erro de decodificação JSON")
        fetch_errors += 1
    except Exception as e:
        print(f" Erro inesperado: {e}")
        fetch_errors += 1
        
    # Pausa para evitar rate limit
    time.sleep(1.1) # OpenDota free tier limit is roughly 60 calls/minute

print(f"\nBusca concluída. {processed_count} partidas processadas com sucesso, {fetch_errors} falhas.")

if all_matches_full_details:
    print(f"Salvando {len(all_matches_full_details)} partidas com detalhes completos em {output_full_json_file}...")
    try:
        with open(output_full_json_file, 'w', encoding='utf-8') as f:
            json.dump(all_matches_full_details, f, ensure_ascii=False, indent=2) # Using indent=2 for potentially large file
        print("Dados completos salvos em JSON com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON completo: {e}")
else:
    print("Nenhum dado completo de partida foi coletado.")


