import json
import pandas as pd
import numpy as np
import sys

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_file = "/home/ubuntu/first_objective_times_analysis.txt"

# Carregar dados das partidas
print(f"Carregando dados das partidas: {json_file_path}")
try:
    # Corrected file open mode
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    print(f"Dados de {len(matches_data)} partidas carregados.")
except Exception as e:
    print(f"Erro ao carregar dados das partidas: {e}")
    sys.exit(1)

# Listas para armazenar tempos
first_tower_times = []
first_rax_times = []

# Processar cada partida
for match in matches_data:
    # Corrected key access
    match_id = match.get('match_id')
    objectives = match.get('objectives')

    current_match_first_tower_time = None
    current_match_first_rax_time = None

    if objectives:
        # Corrected key access
        objectives.sort(key=lambda x: x.get('time', 0)) # Ordenar por tempo
        
        for obj in objectives:
            # Corrected key access
            obj_time = obj.get('time')
            obj_type = obj.get('type')
            
            # First Tower
            # Corrected type string
            if current_match_first_tower_time is None and obj_type == 'CHAT_MESSAGE_TOWER_KILL':
                if obj_time is not None and obj_time > 0:
                    current_match_first_tower_time = obj_time
                    first_tower_times.append(current_match_first_tower_time)
            
            # First Barracks
            # Corrected type string
            if current_match_first_rax_time is None and obj_type == 'CHAT_MESSAGE_BARRACKS_KILL':
                if obj_time is not None and obj_time > 0:
                    current_match_first_rax_time = obj_time
                    first_rax_times.append(current_match_first_rax_time)
            
            # Otimização: parar se ambos foram encontrados
            if current_match_first_tower_time is not None and current_match_first_rax_time is not None:
                break

# Calcular estatísticas
def format_time(seconds):
    if seconds is None or np.isnan(seconds):
        return "N/A"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

results_text = f"# Análise do Tempo Médio da Primeira Torre e Primeira Barraca - PGL Wallachia Season 4\n\n"
results_text += f"Total de Partidas Analisadas: {len(matches_data)}\n\n"

results_text += "## Primeira Torre\n"
if first_tower_times:
    count_tower = len(first_tower_times)
    avg_time_tower = np.mean(first_tower_times)
    median_time_tower = np.median(first_tower_times)
    std_time_tower = np.std(first_tower_times)
    results_text += f"Partidas com Primeira Torre registrada: {count_tower} ({count_tower/len(matches_data)*100:.1f}%)\n"
    results_text += f"Tempo Médio da Primeira Torre: {format_time(avg_time_tower)}\n"
    results_text += f"Tempo Mediano da Primeira Torre: {format_time(median_time_tower)}\n"
    results_text += f"Desvio Padrão do Tempo: {format_time(std_time_tower)}\n"
else:
    results_text += "Nenhuma Primeira Torre registrada nos dados.\n"

results_text += "\n## Primeira Barraca\n"
if first_rax_times:
    count_rax = len(first_rax_times)
    avg_time_rax = np.mean(first_rax_times)
    median_time_rax = np.median(first_rax_times)
    std_time_rax = np.std(first_rax_times)
    results_text += f"Partidas com Primeira Barraca registrada: {count_rax} ({count_rax/len(matches_data)*100:.1f}%)\n"
    results_text += f"Tempo Médio da Primeira Barraca: {format_time(avg_time_rax)}\n"
    results_text += f"Tempo Mediano da Primeira Barraca: {format_time(median_time_rax)}\n"
    results_text += f"Desvio Padrão do Tempo: {format_time(std_time_rax)}\n"
else:
    results_text += "Nenhuma Primeira Barraca registrada nos dados.\n"

results_text += "\n**Nota Importante sobre Limitações:** Estes tempos referem-se ao momento em que a *primeira* torre ou barraca de *qualquer* time foi destruída na partida, conforme registrado nos logs de objetivos. Os dados da API OpenDota não permitem identificar de forma confiável qual time realizou a destruição, apenas qual time perdeu a estrutura. Portanto, esta análise não pode determinar qual time foi mais rápido em destruir objetivos ou correlacionar esses tempos com a vitória."

# Salvar resultados
print(f"Salvando resultados em {output_file}")
# Corrected file open mode
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(results_text)

print("Análise de tempo médio de objetivos concluída.")

