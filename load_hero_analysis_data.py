import json
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
hero_constants_path = "/home/ubuntu/dota_hero_constants.json"

matches_data = None
hero_constants = None

# Carregar dados das partidas
print(f"Carregando dados das partidas: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    print(f"Dados de {len(matches_data)} partidas carregados.")
except Exception as e:
    print(f"Erro ao carregar dados das partidas: {e}")
    sys.exit(1)

# Carregar constantes de heróis
print(f"Carregando constantes de heróis: {hero_constants_path}")
try:
    with open(hero_constants_path, 'r', encoding='utf-8') as f:
        hero_constants = json.load(f)
    print(f"Constantes de {len(hero_constants)} heróis carregadas.")
except Exception as e:
    print(f"Erro ao carregar constantes de heróis: {e}")
    sys.exit(1)

if matches_data and hero_constants:
    print("Dados carregados com sucesso e prontos para análise.")
else:
    print("Falha ao carregar um ou ambos os arquivos de dados.")
    sys.exit(1)

# Este script apenas carrega os dados para verificar se estão acessíveis.
# O próximo script fará a análise detalhada.

