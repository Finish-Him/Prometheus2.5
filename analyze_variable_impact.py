import json
import pandas as pd
import numpy as np
import sys
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import NotFittedError

json_file_path = "/home/ubuntu/pgl_wallachia_s4_matches_full_details.json"
output_summary_file = "/home/ubuntu/analysis_variable_impact.txt"

print(f"Carregando dados do arquivo JSON: {json_file_path}")
try:
    with open(json_file_path, 'r', encoding='utf-8') as f:
        matches_data = json.load(f)
    
    if not isinstance(matches_data, list) or not matches_data:
        print("Erro: A lista de partidas no arquivo JSON está vazia ou em formato inválido.")
        sys.exit(1)

    print(f"Dados de {len(matches_data)} partidas carregados. Avaliando impacto das variáveis...")

except FileNotFoundError:
    print(f"Erro: Arquivo JSON não encontrado em {json_file_path}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Erro: Falha ao decodificar o arquivo JSON em {json_file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Ocorreu um erro inesperado ao carregar os dados: {e}")
    sys.exit(1)

# --- Feature Extraction ---
features = []
target = []

time_points_minutes = [10, 20, 30]

for match in matches_data:
    match_id = match.get('match_id')
    radiant_win = match.get('radiant_win')
    gold_adv = match.get('radiant_gold_adv')
    xp_adv = match.get('radiant_xp_adv')
    duration = match.get('duration')

    if radiant_win is None or gold_adv is None or xp_adv is None or duration is None:
        print(f"Aviso: Partida {match_id} faltando dados essenciais (win, gold_adv, xp_adv, duration). Pulando.")
        continue

    match_features = {}
    valid_match = True
    for minute in time_points_minutes:
        time_sec = minute * 60
        if time_sec < len(gold_adv) and time_sec < len(xp_adv):
            match_features[f'gold_adv_{minute}min'] = gold_adv[time_sec]
            match_features[f'xp_adv_{minute}min'] = xp_adv[time_sec]
        else:
            # Match too short or data missing for this time point
            valid_match = False
            print(f"Aviso: Partida {match_id} muito curta ou dados faltando em {minute} min. Pulando.")
            break 
            
    if valid_match:
        features.append(match_features)
        target.append(1 if radiant_win else 0) # Target: 1 for Radiant win, 0 for Dire win

if not features:
    print("Erro: Nenhuma partida válida encontrada para análise de variáveis.")
    sys.exit(1)

# Convert to DataFrame
feature_df = pd.DataFrame(features)
print(f"DataFrame de features criado com {feature_df.shape[0]} partidas válidas e {feature_df.shape[1]} features.")

# --- Model Training and Feature Importance (using Logistic Regression coefficients) ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(feature_df)
y = np.array(target)

model = LogisticRegression(solver='liblinear', random_state=42)

try:
    model.fit(X_scaled, y)
    coefficients = model.coef_[0]
    feature_names = feature_df.columns
    
    importance_df = pd.DataFrame({'Feature': feature_names, 'Coefficient': coefficients})
    importance_df['Absolute Coefficient'] = importance_df['Coefficient'].abs()
    importance_df = importance_df.sort_values(by='Absolute Coefficient', ascending=False)
    
    print("\n--- Importância das Variáveis (Coeficientes da Regressão Logística) ---")
    print(importance_df)
    
    impact_summary = "Avaliação do Impacto das Variáveis - PGL Wallachia Season 4\n\n"
    impact_summary += f"Partidas Válidas Analisadas: {feature_df.shape[0]}\n"
    impact_summary += "Variáveis Analisadas: Vantagem de Ouro e XP aos 10, 20 e 30 minutos.\n"
    impact_summary += "Método: Coeficientes de Regressão Logística (maior valor absoluto indica maior impacto na previsão de vitória do Radiant).\n\n"
    impact_summary += "Ranking de Impacto (do maior para o menor):\n"
    for index, row in importance_df.iterrows():
        impact_summary += f"  - {row['Feature']}: {row['Coefficient']:.4f}\n"
    impact_summary += "\nNota: Coeficientes positivos indicam que um aumento na variável aumenta a chance de vitória do Radiant. Coeficientes negativos indicam que um aumento na variável aumenta a chance de vitória do Dire.\n"

except NotFittedError:
    print("Erro: Modelo não foi treinado. Verifique os dados.")
    impact_summary = "Erro ao treinar modelo para avaliar impacto das variáveis.\n"
except Exception as e:
    print(f"Erro durante o treinamento do modelo ou análise de coeficientes: {e}")
    impact_summary = f"Erro durante a análise do impacto das variáveis: {e}\n"

# Salvar resumo
try:
    with open(output_summary_file, 'w', encoding='utf-8') as f:
        f.write(impact_summary)
    print(f"Resumo da avaliação de impacto salvo em: {output_summary_file}")
except Exception as e:
    print(f"Erro ao salvar arquivo de resumo de impacto: {e}")

