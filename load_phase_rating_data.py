import json
import sys

match_details_file = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
hero_stats_file = "/home/ubuntu/hero_stats_with_kda_gpm.json"

matches_data = None
hero_stats = None

# Carregar dados detalhados das partidas
print(f"Carregando dados detalhados das partidas: {match_details_file}")
try:
    with open(match_details_file, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    print(f"Dados de {len(matches_data)} partidas carregados.")
except Exception as e:
    print(f"Erro ao carregar dados das partidas: {e}")
    sys.exit(1)

# Carregar estatísticas de heróis pré-calculadas
print(f"Carregando estatísticas de heróis: {hero_stats_file}")
try:
    with open(hero_stats_file, 'r', encoding='utf-8') as f:
        hero_stats = json.load(f)
    print(f"Estatísticas de {len(hero_stats)} heróis carregadas.")
except Exception as e:
    print(f"Erro ao carregar estatísticas de heróis: {e}")
    sys.exit(1)

if matches_data and hero_stats:
    print("Dados carregados com sucesso e prontos para a análise de notas por fase.")
else:
    print("Falha ao carregar um ou ambos os arquivos de dados.")
    sys.exit(1)

# Este script apenas carrega os dados para verificar se estão acessíveis.
# O próximo script definirá a metodologia e calculará as notas.

