import json
import sys
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

input_file = "/home/ubuntu/hero_stats_for_revised_rating.json"
output_file = "/home/ubuntu/hero_stats_with_all_ratings.json"

# Carregar dados dos heróis com métricas preparadas
print(f"Carregando dados dos heróis: {input_file}")
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        hero_stats_dict = json.load(f)
    print(f"Dados de {len(hero_stats_dict)} heróis carregados.")
except Exception as e:
    print(f"Erro ao carregar dados dos heróis: {e}")
    sys.exit(1)

# Converter para DataFrame para facilitar cálculos e normalização
hero_data_list = []
for hero_id_str, stats in hero_stats_dict.items():
    if stats.get('picks', 0) > 0: # Considerar apenas heróis escolhidos
        stats['hero_id'] = int(hero_id_str) # Adicionar ID para merge posterior
        hero_data_list.append(stats)

if not hero_data_list:
    print("Nenhum herói com picks encontrado para calcular notas.")
    sys.exit(1)

df = pd.DataFrame(hero_data_list)

def calculate_phase_rating(df_input, metrics, phase_name):
    """Calcula a nota (1-5) para uma fase específica do jogo."""
    print(f"\nCalculando nota {phase_name} Game...")
    df_phase = df_input.copy()
    
    # Verificar se as colunas existem
    if not all(metric in df_phase.columns for metric in metrics):
        print(f"Erro: Colunas necessárias para {phase_name} Game ({metrics}) não encontradas.")
        # Atribuir N/A e retornar
        df_phase[f'{phase_name.lower()}_game_rating'] = 'N/A'
        return df_phase[['hero_id', f'{phase_name.lower()}_game_rating']]

    # Filtrar heróis com dados válidos para as métricas (não nulos/NaN)
    # Permitir zero como valor válido para algumas métricas (e.g., kills, assists)
    df_valid = df_phase[df_phase[metrics].notna().all(axis=1)].copy()

    if df_valid.empty:
        print(f"Nenhum herói com dados válidos para as métricas de {phase_name} Game.")
        df_phase[f'{phase_name.lower()}_game_rating'] = 'N/A'
        return df_phase[['hero_id', f'{phase_name.lower()}_game_rating']]
    
    print(f"Calculando nota {phase_name} Game para {len(df_valid)} heróis com dados válidos.")
    
    # Normalizar as métricas (escala 0-1)
    # Lidar com colunas que podem ter variância zero (constantes)
    norm_metrics = []
    for metric in metrics:
        if df_valid[metric].nunique() > 1:
            scaler = MinMaxScaler()
            df_valid[metric + '_norm'] = scaler.fit_transform(df_valid[[metric]])
            norm_metrics.append(metric + '_norm')
        else:
            # Se a coluna for constante, atribuir um valor normalizado médio (0.5)
            df_valid[metric + '_norm'] = 0.5
            norm_metrics.append(metric + '_norm')
            print(f"Aviso: Métrica '{metric}' tem valor constante, usando 0.5 normalizado.")

    # Calcular score combinado (média simples das métricas normalizadas)
    df_valid[f'{phase_name.lower()}_game_score'] = df_valid[norm_metrics].mean(axis=1)

    # Atribuir nota (1-5) baseada em quantis do score
    try:
        df_valid[f'{phase_name.lower()}_game_rating'] = pd.qcut(df_valid[f'{phase_name.lower()}_game_score'], q=5, labels=False, duplicates='drop') + 1
    except ValueError as e:
        print(f"Aviso: Não foi possível dividir em 5 quantis distintos para {phase_name} ({e}). Tentando com 3 quantis.")
        try:
             df_valid[f'{phase_name.lower()}_game_rating'] = pd.qcut(df_valid[f'{phase_name.lower()}_game_score'], q=3, labels=False, duplicates='drop') + 1
             rating_map = {1: 1, 2: 3, 3: 5}
             df_valid[f'{phase_name.lower()}_game_rating'] = df_valid[f'{phase_name.lower()}_game_rating'].map(rating_map)
             print(f"Usando 3 quantis para {phase_name} Game rating.")
        except Exception as e2:
             print(f"Não foi possível usar qcut para {phase_name} ({e2}). Atribuindo nota 3 para todos os heróis válidos.")
             df_valid[f'{phase_name.lower()}_game_rating'] = 3
             
    # Selecionar colunas relevantes para merge
    result_df = df_valid[['hero_id', f'{phase_name.lower()}_game_rating']].copy()
    
    # Adicionar heróis que não tinham dados válidos com N/A
    missing_ids = df_input[~df_input['hero_id'].isin(result_df['hero_id'])]['hero_id']
    missing_df = pd.DataFrame({'hero_id': missing_ids, f'{phase_name.lower()}_game_rating': 'N/A'})
    
    final_result_df = pd.concat([result_df, missing_df], ignore_index=True)
    return final_result_df

# Métricas por Fase (Adaptadas)
early_metrics = ['avg_kills', 'avg_assists']
mid_metrics = ['avg_gpm', 'kda_ratio']
late_metrics = ['primary_gain', 'avg_xpm']

# Calcular notas para cada fase
early_ratings_df = calculate_phase_rating(df, early_metrics, 'Early')
mid_ratings_df = calculate_phase_rating(df, mid_metrics, 'Mid')
late_ratings_df = calculate_phase_rating(df, late_metrics, 'Late')

# Merge das notas de volta ao dicionário original
print("\nCombinando notas calculadas...")

def merge_ratings(hero_dict, ratings_df, rating_col_name):
    ratings_map = ratings_df.set_index('hero_id')[rating_col_name].to_dict()
    for hero_id_str, stats in hero_dict.items():
        hero_id_int = int(hero_id_str)
        if hero_id_int in ratings_map:
            rating = ratings_map[hero_id_int]
            # Converter para int se for numérico, senão manter como string (e.g., 'N/A')
            try:
                stats[rating_col_name] = int(rating)
            except (ValueError, TypeError):
                stats[rating_col_name] = rating
        elif stats.get('picks', 0) > 0:
             stats[rating_col_name] = 'N/A' # Heróis com picks mas sem nota calculada
        else:
             stats[rating_col_name] = 'N/A' # Heróis não escolhidos

merge_ratings(hero_stats_dict, early_ratings_df, 'early_game_rating')
merge_ratings(hero_stats_dict, mid_ratings_df, 'mid_game_rating')
merge_ratings(hero_stats_dict, late_ratings_df, 'late_game_rating')

# Salvar dados finais com todas as notas
print(f"Salvando dados finais com todas as notas em {output_file}")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hero_stats_dict, f, indent=4)
    print("Cálculo de todas as notas de fase concluído e salvo.")
except Exception as e:
    print(f"Erro ao salvar dados finais: {e}")
    sys.exit(1)

