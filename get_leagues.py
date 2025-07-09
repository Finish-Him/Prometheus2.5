import requests
import json

# URL da API OpenDota para obter a lista de ligas
url = "https://api.opendota.com/api/leagues"

try:
    response = requests.get(url)
    response.raise_for_status()  # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)

    leagues_data = response.json()

    # Filtrar por ligas profissionais (tier 'professional' ou 'premium')
    # OpenDota usa 'premium' e 'professional' para tiers mais altos.
    professional_leagues = [league for league in leagues_data if league.get('tier') in ['professional', 'premium']]

    # Ordenar as ligas por leagueid em ordem decrescente para obter as mais recentes
    professional_leagues_sorted = sorted(professional_leagues, key=lambda x: x['leagueid'], reverse=True)

    # Obter as últimas 50 ligas profissionais
    last_50_leagues = professional_leagues_sorted[:50]

    # Salvar os dados das últimas 50 ligas em um arquivo JSON
    output_file = '/home/ubuntu/leagues_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(last_50_leagues, f, ensure_ascii=False, indent=4)

    print(f"Dados das últimas {len(last_50_leagues)} ligas profissionais salvas em {output_file}")

except requests.exceptions.RequestException as e:
    print(f"Erro ao fazer a requisição para a API: {e}")
except json.JSONDecodeError:
    print("Erro ao decodificar a resposta JSON da API.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")

