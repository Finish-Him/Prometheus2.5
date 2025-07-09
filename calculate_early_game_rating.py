import json
import sys
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

input_file = "/home/ubuntu/hero_stats_for_rating.json"
output_file = "/home/ubuntu/hero_stats_with_early_rating.json"

# Carregar dados dos heróis com métricas extraídas
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

# --- Cálculo da Nota Early Game --- 
print("Calculando nota Early Game...")

# Métricas relevantes para Early Game
early_metrics = ['avg_gold_at_10', 'avg_xp_at_10']

# Verificar se as colunas existem e não são todas zero/nulas
if not all(metric in df.columns for metric in early_metrics):
    print(f"Erro: Colunas necessárias para Early Game ({early_metrics}) não encontradas.")
    sys.exit(1)

# Filtrar heróis com dados válidos para as métricas (não zero)
df_early = df[df[early_metrics].notna().all(axis=1) & (df[early_metrics] != 0).all(axis=1)].copy()

if df_early.empty:
    print("Nenhum herói com dados válidos para as métricas de Early Game.")
    # Atribuir nota 0 ou N/A para todos e salvar
    for hero_id_str in hero_stats_dict.keys():
         hero_stats_dict[hero_id_str]['early_game_rating'] = 'N/A'
else:
    print(f"Calculando nota Early Game para {len(df_early)} heróis com dados válidos.")
    # Normalizar as métricas (escala 0-1)
    scaler = MinMaxScaler()
    df_early[early_metrics + '_norm'] = scaler.fit_transform(df_early[early_metrics])

    # Calcular score combinado (média simples das métricas normalizadas)
    df_early['early_game_score'] = df_early[[metric + '_norm' for metric in early_metrics]].mean(axis=1)

    # Atribuir nota (1-5) baseada em quantis do score
    # Usar qcut para dividir em 5 grupos baseados nos quantis
    # labels=False retorna índices (0-4), adicionamos 1 para obter 1-5
    # duplicates='drop' para lidar com scores iguais que podem cair no mesmo limite de quantil
    try:
        df_early['early_game_rating'] = pd.qcut(df_early['early_game_score'], q=5, labels=False, duplicates='drop') + 1
    except ValueError as e:
        print(f"Aviso: Não foi possível dividir em 5 quantis distintos devido a valores duplicados ou poucos dados ({e}). Tentando com menos quantis ou atribuindo nota média.")
        # Fallback: Atribuir nota 3 para todos ou usar menos quantis se possível
        try:
             df_early['early_game_rating'] = pd.qcut(df_early['early_game_score'], q=3, labels=False, duplicates='drop') + 1 # Tenta 3 quantis (notas 1, 2, 3)
             # Mapear para escala 1-5 (aproximado)
             rating_map = {1: 1, 2: 3, 3: 5}
             df_early['early_game_rating'] = df_early['early_game_rating'].map(rating_map)
             print("Usando 3 quantis para Early Game rating.")
        except:
             print("Não foi possível usar qcut. Atribuindo nota 3 para todos os heróis com dados válidos.")
             df_early['early_game_rating'] = 3 # Nota média como fallback extremo

    # Merge das notas de volta ao dicionário original
    ratings_map = df_early.set_index('hero_id')['early_game_rating'].to_dict()
    for hero_id_str, stats in hero_stats_dict.items():
        hero_id_int = int(hero_id_str)
        if hero_id_int in ratings_map:
            stats['early_game_rating'] = int(ratings_map[hero_id_int]) # Garantir que é int
        elif stats.get('picks', 0) > 0: # Heróis com picks mas sem dados válidos
             stats['early_game_rating'] = 'N/A' # Ou uma nota padrão como 1 ou 2
        else:
             stats['early_game_rating'] = 'N/A' # Heróis não escolhidos

# Salvar dados atualizados
print(f"Salvando dados atualizados com nota Early Game em {output_file}")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hero_stats_dict, f, indent=4)
    print("Cálculo da nota Early Game concluído e salvo.")
except Exception as e:
    print(f"Erro ao salvar dados atualizados: {e}")
    sys.exit(1)

