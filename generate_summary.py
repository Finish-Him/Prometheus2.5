import pandas as pd
import json

# Carregar os dados para exibir um resumo
json_file = '/home/ubuntu/leagues_detailed_data.json'
csv_file = '/home/ubuntu/leagues_detailed_data.csv'

try:
    # Carregar dados JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Carregar dados CSV
    df = pd.read_csv(csv_file)
    
    # Criar um resumo dos dados
    print("Resumo dos dados dos campeonatos profissionais do OpenDota:")
    print(f"Total de campeonatos: {len(json_data)}")
    print("\nColunas disponíveis:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nPrimeiros 5 campeonatos:")
    print(df.head().to_string())
    
    # Verificar se há league_id
    if 'league_id' in df.columns:
        league_id_col = 'league_id'
    elif 'leagueid' in df.columns:
        league_id_col = 'leagueid'
    else:
        league_id_col = None
    
    if league_id_col:
        print(f"\nLeague IDs dos 10 campeonatos mais recentes:")
        for idx, row in df.sort_values(by=league_id_col, ascending=False).head(10).iterrows():
            league_name = row.get('name', 'Nome não disponível')
            league_id = row[league_id_col]
            print(f"- {league_name}: {league_id}")
    
except Exception as e:
    print(f"Erro ao gerar resumo: {e}")
