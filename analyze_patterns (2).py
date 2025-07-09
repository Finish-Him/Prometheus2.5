import json
import pandas as pd
import numpy as np
import sys
from collections import defaultdict

json_file_path = "/home/ubuntu/analysis_data/pgl_wallachia/pgl_wallachia_s4_matches_full_details.json"
output_summary_file = "/home/ubuntu/analysis_results/analysis_patterns_summary.txt"

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Analisando padrões e tendências...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# Initialize counters and lists
radiant_wins = 0
dire_wins = 0
fb_winner_wins = 0
fb_loser_wins = 0
matches_with_fb = 0
first_tower_winners = defaultdict(int) # Key: team (2 or 3), Value: count of wins
matches_with_first_tower = 0
first_roshan_winners = defaultdict(int) # Key: team (2 or 3), Value: count of wins
matches_with_first_roshan = 0
first_rax_winners = defaultdict(int) # Key: team (2 or 3), Value: count of wins
matches_with_first_rax = 0

# Process each match
for match in matches_data:
    match_id = match.get('match_id')
    radiant_win = match.get('radiant_win')
    players = match.get('players')
    objectives = match.get('objectives')
    fb_time = match.get('first_blood_time')

    if radiant_win is None:
        print(f"Aviso: Partida {match_id} sem informação de vencedor. Pulando.")
        continue

    # 1. Side Win Rate
    if radiant_win:
        radiant_wins += 1
        winner_side = 2 # Radiant
    else:
        dire_wins += 1
        winner_side = 3 # Dire

    # 2. First Blood Correlation
    fb_killer_player = None
    if fb_time is not None and fb_time > 0 and players:
        matches_with_fb += 1
        for p in players:
            if p.get('firstblood_claimed') == 1:
                fb_killer_player = p
                break
        
        if fb_killer_player:
            # Determine killer team (Radiant: player_slot < 128, Dire: player_slot >= 128)
            fb_killer_team = 2 if fb_killer_player.get('player_slot', 0) < 128 else 3
            if fb_killer_team == winner_side:
                fb_winner_wins += 1
            else:
                fb_loser_wins += 1

    # 3. Objective Correlations (First Tower, Roshan, Rax)
    first_tower_killer_team = None
    first_roshan_killer_team = None
    first_rax_killer_team = None
    
    if objectives:
        objectives.sort(key=lambda x: x.get('time', 0))
        
        for obj in objectives:
            obj_time = obj.get('time')
            obj_type = obj.get('type')
            obj_team = obj.get('team') # Team whose structure died / Roshan killer team (sometimes)
            obj_player_slot = obj.get('player_slot') # For Roshan kill / Aegis pickup

            # First Tower
            if first_tower_killer_team is None and obj_type == 'CHAT_MESSAGE_TOWER_KILL':
                # Killer team is the opposite of the team whose tower died
                killer_team = 3 if obj_team == 2 else (2 if obj_team == 3 else None)
                if killer_team:
                    first_tower_killer_team = killer_team
                    matches_with_first_tower += 1
                    if killer_team == winner_side:
                        first_tower_winners[killer_team] += 1
            
            # First Roshan - Attempt to identify killer team
            if first_roshan_killer_team is None and obj_type == 'CHAT_MESSAGE_ROSHAN_KILL':
                killer_team = None
                # Try using player_slot if available in the Roshan kill event itself
                if obj_player_slot is not None:
                     killer_team = 2 if obj_player_slot < 128 else 3
                # Fallback: Check aegis pickup shortly after (less reliable)
                # else: 
                #    pass # More complex logic needed, skip for now
                
                if killer_team:
                    first_roshan_killer_team = killer_team
                    matches_with_first_roshan += 1
                    if killer_team == winner_side:
                        first_roshan_winners[killer_team] += 1

            # First Barracks
            if first_rax_killer_team is None and obj_type == 'CHAT_MESSAGE_BARRACKS_KILL':
                # Killer team is the opposite of the team whose rax died
                killer_team = 3 if obj_team == 2 else (2 if obj_team == 3 else None)
                if killer_team:
                    first_rax_killer_team = killer_team
                    matches_with_first_rax += 1
                    if killer_team == winner_side:
                        first_rax_winners[killer_team] += 1

# Calculate Percentages
total_matches = len(matches_data)
radiant_win_pct = (radiant_wins / total_matches * 100) if total_matches else 0
dire_win_pct = (dire_wins / total_matches * 100) if total_matches else 0
fb_win_pct = (fb_winner_wins / matches_with_fb * 100) if matches_with_fb else 0
first_tower_win_pct = (sum(first_tower_winners.values()) / matches_with_first_tower * 100) if matches_with_first_tower else 0
first_roshan_win_pct = (sum(first_roshan_winners.values()) / matches_with_first_roshan * 100) if matches_with_first_roshan else 0
first_rax_win_pct = (sum(first_rax_winners.values()) / matches_with_first_rax * 100) if matches_with_first_rax else 0

# Create Summary
summary = f"Análise de Padrões e Tendências - PGL Wallachia Season 4 ({total_matches} partidas)\n\n"
summary += "--- Taxa de Vitória por Lado ---\n"
summary += f"Radiant: {radiant_wins} vitórias ({radiant_win_pct:.1f}%)\n"
summary += f"Dire:    {dire_wins} vitórias ({dire_win_pct:.1f}%)\n\n"

summary += "--- Correlação com First Blood ---\n"
summary += f"Partidas com First Blood registrado: {matches_with_fb}\n"
summary += f"Vitórias do time que conseguiu First Blood: {fb_winner_wins} ({fb_win_pct:.1f}%)\n\n"

summary += "--- Correlação com Primeira Torre ---\n"
summary += f"Partidas com Primeira Torre registrada: {matches_with_first_tower}\n"
summary += f"Vitórias do time que destruiu a Primeira Torre: {sum(first_tower_winners.values())} ({first_tower_win_pct:.1f}%)\n"
summary += f"  - Radiant destruiu primeiro e venceu: {first_tower_winners[2]}\n"
summary += f"  - Dire destruiu primeiro e venceu: {first_tower_winners[3]}\n\n"

summary += "--- Correlação com Primeiro Roshan ---\n"
summary += f"Partidas com Primeiro Roshan registrado (com time identificado): {matches_with_first_roshan}\n"
summary += f"Vitórias do time que matou o Primeiro Roshan: {sum(first_roshan_winners.values())} ({first_roshan_win_pct:.1f}%)\n"
summary += f"  - Radiant matou primeiro e venceu: {first_roshan_winners[2]}\n"
summary += f"  - Dire matou primeiro e venceu: {first_roshan_winners[3]}\n\n"

summary += "--- Correlação com Primeira Barraca ---\n"
summary += f"Partidas com Primeira Barraca registrada: {matches_with_first_rax}\n"
summary += f"Vitórias do time que destruiu a Primeira Barraca: {sum(first_rax_winners.values())} ({first_rax_win_pct:.1f}%)\n"
summary += f"  - Radiant destruiu primeiro e venceu: {first_rax_winners[2]}\n"
summary += f"  - Dire destruiu primeiro e venceu: {first_rax_winners[3]}\n"

print("--- Resumo da Análise de Padrões ---")
print(summary)

# Salvar resumo no arquivo
try:
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Resumo da análise de padrões salvo em: {output_summary_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de resumo de padrões: {e}")

