import json
import pandas as pd
import numpy as np
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_stats_file = "/home/ubuntu/analysis_event_stats.txt"

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Calculando estatísticas...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# Listas para armazenar dados dos eventos
first_blood_times = []
match_durations = []
first_tower_times = []
first_tower_teams = [] # 2 for Radiant, 3 for Dire
roshan_kill_counts = []
first_roshan_times = []
first_rax_times = []
first_rax_teams = [] # 2 for Radiant, 3 for Dire

# Processar cada partida
for match in matches_data:
    # First Blood
    fb_time = match.get('first_blood_time')
    if fb_time is not None and fb_time > 0:
        first_blood_times.append(fb_time)
        
    # Match Duration
    duration = match.get('duration')
    if duration is not None:
        match_durations.append(duration)
        
    objectives = match.get('objectives')
    current_match_roshan_kills = 0
    current_match_first_roshan_time = None
    current_match_first_tower_time = None
    current_match_first_tower_team = None
    current_match_first_rax_time = None
    current_match_first_rax_team = None
    
    if objectives:
        objectives.sort(key=lambda x: x.get('time', 0)) # Ordenar por tempo
        
        for obj in objectives:
            obj_time = obj.get('time')
            obj_type = obj.get('type')
            obj_team = obj.get('team') # Whose structure was destroyed
            
            # First Tower
            if current_match_first_tower_time is None and obj_type == 'CHAT_MESSAGE_TOWER_KILL':
                current_match_first_tower_time = obj_time
                # Killer team is the opposite of the team whose tower died
                current_match_first_tower_team = 3 if obj_team == 2 else (2 if obj_team == 3 else None)
                if current_match_first_tower_team:
                    first_tower_teams.append(current_match_first_tower_team)
                if current_match_first_tower_time is not None:
                     first_tower_times.append(current_match_first_tower_time)
            
            # Roshan Kills
            if obj_type == 'CHAT_MESSAGE_ROSHAN_KILL':
                current_match_roshan_kills += 1
                if current_match_first_roshan_time is None:
                    current_match_first_roshan_time = obj_time
                    if current_match_first_roshan_time is not None:
                        first_roshan_times.append(current_match_first_roshan_time)

            # First Barracks
            if current_match_first_rax_time is None and obj_type == 'CHAT_MESSAGE_BARRACKS_KILL':
                current_match_first_rax_time = obj_time
                # Killer team is the opposite of the team whose rax died
                current_match_first_rax_team = 3 if obj_team == 2 else (2 if obj_team == 3 else None)
                if current_match_first_rax_team:
                    first_rax_teams.append(current_match_first_rax_team)
                if current_match_first_rax_time is not None:
                    first_rax_times.append(current_match_first_rax_time)
                    
    roshan_kill_counts.append(current_match_roshan_kills)

# Calcular estatísticas (usando numpy para médias e desvios padrão)
def format_time(seconds):
    if seconds is None or np.isnan(seconds):
        return "N/A"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

stats_summary = """Estatísticas dos Eventos - PGL Wallachia Season 4 ({num_matches} partidas)

--- Duração e First Blood ---
Duração Média da Partida: {avg_duration}
Tempo Médio do First Blood: {avg_fb_time}

--- Torres ---
Tempo Médio da Primeira Torre: {avg_first_tower_time}
Distribuição da Primeira Torre:
  - Radiant: {radiant_first_tower_pct:.1f}%
  - Dire: {dire_first_tower_pct:.1f}%

--- Roshan ---
Número Médio de Roshans por Jogo: {avg_roshan_kills:.2f}
Tempo Médio do Primeiro Roshan (em jogos com Roshan): {avg_first_roshan_time}
Jogos com pelo menos 1 Roshan: {roshan_games_pct:.1f}%

--- Barracas ---
Tempo Médio da Primeira Barraca Destruída (em jogos com barraca destruída): {avg_first_rax_time}
Distribuição da Primeira Barraca Destruída:
  - Radiant Destruiu Primeiro: {radiant_first_rax_pct:.1f}%
  - Dire Destruiu Primeiro: {dire_first_rax_pct:.1f}%
Jogos com pelo menos 1 Barraca Destruída: {rax_games_pct:.1f}%
""".format(
    num_matches=len(matches_data),
    avg_duration=format_time(np.mean(match_durations) if match_durations else None),
    avg_fb_time=format_time(np.mean(first_blood_times) if first_blood_times else None),
    avg_first_tower_time=format_time(np.mean(first_tower_times) if first_tower_times else None),
    radiant_first_tower_pct=(first_tower_teams.count(2) / len(first_tower_teams) * 100) if first_tower_teams else 0,
    dire_first_tower_pct=(first_tower_teams.count(3) / len(first_tower_teams) * 100) if first_tower_teams else 0,
    avg_roshan_kills=np.mean(roshan_kill_counts) if roshan_kill_counts else 0,
    avg_first_roshan_time=format_time(np.mean(first_roshan_times) if first_roshan_times else None),
    roshan_games_pct=(len(first_roshan_times) / len(matches_data) * 100) if matches_data else 0,
    avg_first_rax_time=format_time(np.mean(first_rax_times) if first_rax_times else None),
    radiant_first_rax_pct=(first_rax_teams.count(2) / len(first_rax_teams) * 100) if first_rax_teams else 0,
    dire_first_rax_pct=(first_rax_teams.count(3) / len(first_rax_teams) * 100) if first_rax_teams else 0,
    rax_games_pct=(len(first_rax_times) / len(matches_data) * 100) if matches_data else 0
)

print("\n--- Resumo das Estatísticas ---")
print(stats_summary)

# Salvar estatísticas no arquivo
try:
    with open(output_stats_file, 'w', encoding='utf-8') as f:
        f.write(stats_summary)
    print(f"Estatísticas salvas em: {output_stats_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de estatísticas: {e}")

