import json
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
item_constants_path = "/home/ubuntu/dota_item_constants.json"
output_file = "/home/ubuntu/most_purchased_items_analysis.txt"

# Carregar dados das partidas
print(f"Carregando dados das partidas: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados.")

except Exception as e:
    print(f"Erro ao carregar dados das partidas: {e}")
    sys.exit(1)

# Carregar constantes de itens
print(f"Carregando constantes de itens: {item_constants_path}")
try:
    with open(item_constants_path, 'r', encoding='utf-8') as f:
        item_constants = json.load(f)
    
    print(f"Constantes de {len(item_constants)} itens carregadas.")

except Exception as e:
    print(f"Erro ao carregar constantes de itens: {e}")
    sys.exit(1)

# Criar mapeamento de ID para nome do item
item_id_to_name = {}
for item_id, item_data in item_constants.items():
    if 'dname' in item_data:
        item_id_to_name[item_id] = item_data['dname']

print(f"Mapeamento criado para {len(item_id_to_name)} itens.")

# Inicializar contadores
all_purchased_items = Counter()  # Todos os itens comprados (do purchase_log)
final_items = Counter()          # Itens finais (do inventário final)
early_game_items = Counter()     # Itens comprados antes de 10 minutos
mid_game_items = Counter()       # Itens comprados entre 10-25 minutos
late_game_items = Counter()      # Itens comprados após 25 minutos

# Itens a ignorar (consumíveis comuns, componentes básicos, etc.)
ignore_items = {
    'tpscroll', 'clarity', 'faerie_fire', 'enchanted_mango', 'tango', 
    'flask', 'ward_observer', 'ward_sentry', 'dust', 'smoke_of_deceit',
    'branches', 'gauntlets', 'slippers', 'mantle', 'circlet', 'belt_of_strength',
    'band_of_elvenskin', 'robe', 'crown', 'ogre_axe', 'blade_of_alacrity', 
    'staff_of_wizardry', 'ring_of_protection', 'quelling_blade', 'stout_shield',
    'blades_of_attack', 'chainmail', 'quarterstaff', 'helm_of_iron_will',
    'broadsword', 'claymore', 'javelin', 'mithril_hammer', 'blight_stone',
    'ring_of_regen', 'sobi_mask', 'boots', 'gloves', 'cloak', 'ring_of_health',
    'void_stone', 'gem', 'lifesteal', 'shadow_amulet', 'ghost', 'blink',
    'blitz_knuckles', 'voodoo_mask', 'fluffy_hat', 'infused_raindrop'
}

# Processar cada partida
total_players = 0
for match in matches_data:
    players = match.get('players', [])
    total_players += len(players)
    
    for player in players:
        # Processar purchase_log
        purchase_log = player.get('purchase_log', [])
        for purchase in purchase_log:
            item_name = purchase.get('key')
            time = purchase.get('time')
            
            if item_name and item_name not in ignore_items:
                all_purchased_items[item_name] += 1
                
                if time is not None:
                    if time < 10 * 60:  # Antes de 10 minutos
                        early_game_items[item_name] += 1
                    elif time < 25 * 60:  # Entre 10-25 minutos
                        mid_game_items[item_name] += 1
                    else:  # Após 25 minutos
                        late_game_items[item_name] += 1
        
        # Processar itens finais
        for i in range(6):  # 6 slots de itens
            item_id = player.get(f'item_{i}')
            if item_id and item_id != 0:
                item_name = item_id_to_name.get(str(item_id))
                if item_name:
                    final_items[item_name] += 1

# Calcular estatísticas
avg_players_per_match = total_players / len(matches_data) if matches_data else 0
total_matches = len(matches_data)

# Preparar resultados
results = "# Análise dos Itens Mais Comprados - PGL Wallachia Season 4\n\n"
results += f"Total de Partidas Analisadas: {total_matches}\n"
results += f"Total de Jogadores: {total_players} (média de {avg_players_per_match:.1f} por partida)\n\n"

# Top 20 itens mais comprados (geral)
results += "## Top 20 Itens Mais Comprados (Geral)\n\n"
results += "| Item | Quantidade | Média por Partida |\n"
results += "|------|------------|-------------------|\n"
for item, count in all_purchased_items.most_common(20):
    item_name = item_id_to_name.get(item, item)
    results += f"| {item_name} | {count} | {count/total_matches:.1f} |\n"

# Top 15 itens finais mais comuns
results += "\n## Top 15 Itens Finais Mais Comuns\n\n"
results += "| Item | Quantidade | % dos Jogadores |\n"
results += "|------|------------|------------------|\n"
for item, count in final_items.most_common(15):
    percentage = (count / total_players) * 100
    results += f"| {item} | {count} | {percentage:.1f}% |\n"

# Top 10 itens por fase do jogo
results += "\n## Top 10 Itens por Fase do Jogo\n\n"

results += "### Early Game (0-10 min)\n\n"
results += "| Item | Quantidade | Média por Partida |\n"
results += "|------|------------|-------------------|\n"
for item, count in early_game_items.most_common(10):
    item_name = item_id_to_name.get(item, item)
    results += f"| {item_name} | {count} | {count/total_matches:.1f} |\n"

results += "\n### Mid Game (10-25 min)\n\n"
results += "| Item | Quantidade | Média por Partida |\n"
results += "|------|------------|-------------------|\n"
for item, count in mid_game_items.most_common(10):
    item_name = item_id_to_name.get(item, item)
    results += f"| {item_name} | {count} | {count/total_matches:.1f} |\n"

results += "\n### Late Game (25+ min)\n\n"
results += "| Item | Quantidade | Média por Partida |\n"
results += "|------|------------|-------------------|\n"
for item, count in late_game_items.most_common(10):
    item_name = item_id_to_name.get(item, item)
    results += f"| {item_name} | {count} | {count/total_matches:.1f} |\n"

# Salvar resultados
print(f"Salvando resultados em {output_file}")
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(results)

print("Análise de itens mais comprados concluída.")
