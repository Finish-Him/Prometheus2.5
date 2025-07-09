import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from openpyxl import load_workbook

# Configurações para visualização
plt.style.use('ggplot')
sns.set(style="whitegrid")

# Diretório para salvar os gráficos e resultados
output_dir = '/home/ubuntu/dota_analysis/output'
os.makedirs(output_dir, exist_ok=True)

# Carregar o arquivo Excel
excel_path = '/home/ubuntu/upload/Database Oráculo 3.0.xlsx'
print(f"Analisando o arquivo: {excel_path}")

# Função para salvar resultados da análise
def save_analysis_results(filename, content):
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Resultados salvos em: {os.path.join(output_dir, filename)}")

# Função para processar a aba Dataset Previsor que contém dados mais estruturados
def analyze_dataset_previsor():
    try:
        # Tentar carregar a aba Dataset Previsor
        df = pd.read_excel(excel_path, sheet_name='Dataset Previsor')
        
        # Verificar se temos uma única coluna com valores separados por vírgula
        if df.shape[1] == 1 and isinstance(df.iloc[0, 0], str) and ',' in df.iloc[0, 0]:
            # Extrair cabeçalhos da primeira linha
            headers = df.iloc[0, 0].split(',')
            
            # Criar um novo DataFrame com esses cabeçalhos
            new_df = pd.DataFrame(columns=headers)
            
            # Processar cada linha
            for i in range(1, len(df)):
                if isinstance(df.iloc[i, 0], str):
                    values = df.iloc[i, 0].split(',')
                    # Garantir que temos o número correto de valores
                    if len(values) == len(headers):
                        new_df.loc[i-1] = values
            
            df = new_df
        
        print(f"Dimensões do DataFrame: {df.shape}")
        print(f"Colunas disponíveis: {df.columns.tolist()}")
        
        # Converter colunas numéricas
        numeric_cols = ['duration_min', 'total_kills', 'first_blood_time', 'radiant_score', 'dire_score']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calcular diferença de kills
        if 'radiant_score' in df.columns and 'dire_score' in df.columns:
            df['kill_difference'] = abs(df['radiant_score'] - df['dire_score'])
        
        # Análise de cenários específicos
        scenarios = []
        
        # Cenário 1: Jogos rápidos com alta diferença de kills
        if 'duration_min' in df.columns and 'kill_difference' in df.columns:
            fast_games_high_diff = df[(df['duration_min'] < 30) & (df['kill_difference'] > 14.5)]
            if len(fast_games_high_diff) > 0:
                scenario = {
                    'nome': 'Jogos rápidos com alta diferença de kills',
                    'descricao': 'Partidas que terminam em menos de 30 minutos e têm diferença de kills superior a 14.5',
                    'frequencia': len(fast_games_high_diff),
                    'porcentagem': (len(fast_games_high_diff) / len(df)) * 100,
                    'kills_medio': fast_games_high_diff['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'duracao_media': fast_games_high_diff['duration_min'].mean(),
                    'diferenca_media': fast_games_high_diff['kill_difference'].mean()
                }
                scenarios.append(scenario)
        
        # Cenário 2: Jogos com composições de pushers e alta diferença de kills
        if 'dominancia_pushers' in df.columns and 'kill_difference' in df.columns:
            pusher_games_high_diff = df[(df['dominancia_pushers'] == '1') & (df['kill_difference'] > 14.5)]
            if len(pusher_games_high_diff) > 0:
                scenario = {
                    'nome': 'Composições com dominância de pushers e alta diferença de kills',
                    'descricao': 'Partidas com dominância de heróis pushers e diferença de kills superior a 14.5',
                    'frequencia': len(pusher_games_high_diff),
                    'porcentagem': (len(pusher_games_high_diff) / len(df)) * 100,
                    'kills_medio': pusher_games_high_diff['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'duracao_media': pusher_games_high_diff['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'diferenca_media': pusher_games_high_diff['kill_difference'].mean()
                }
                scenarios.append(scenario)
        
        # Cenário 3: Jogos com composições espelhadas
        if 'composicao_espelhada' in df.columns and 'kill_difference' in df.columns:
            mirror_comp_games = df[df['composicao_espelhada'] == '1']
            if len(mirror_comp_games) > 0:
                scenario = {
                    'nome': 'Jogos com composições espelhadas',
                    'descricao': 'Partidas onde ambos os times têm composições similares',
                    'frequencia': len(mirror_comp_games),
                    'porcentagem': (len(mirror_comp_games) / len(df)) * 100,
                    'kills_medio': mirror_comp_games['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'duracao_media': mirror_comp_games['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'diferenca_media': mirror_comp_games['kill_difference'].mean(),
                    'high_diff_percentage': (mirror_comp_games['kill_difference'] > 14.5).mean() * 100
                }
                scenarios.append(scenario)
        
        # Cenário 4: Jogos com stomps (dominância clara de um time)
        if 'stomp' in df.columns and 'kill_difference' in df.columns:
            stomp_games = df[df['stomp'] == '1']
            if len(stomp_games) > 0:
                scenario = {
                    'nome': 'Jogos com stomp (dominância clara)',
                    'descricao': 'Partidas onde um time domina claramente o outro',
                    'frequencia': len(stomp_games),
                    'porcentagem': (len(stomp_games) / len(df)) * 100,
                    'kills_medio': stomp_games['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'duracao_media': stomp_games['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'diferenca_media': stomp_games['kill_difference'].mean(),
                    'high_diff_percentage': (stomp_games['kill_difference'] > 14.5).mean() * 100
                }
                scenarios.append(scenario)
        
        # Cenário 5: Jogos com muitas kills
        if 'muito_kill' in df.columns and 'kill_difference' in df.columns:
            high_kill_games = df[df['muito_kill'] == '1']
            if len(high_kill_games) > 0:
                scenario = {
                    'nome': 'Jogos com muitas kills',
                    'descricao': 'Partidas com número total de kills acima da média',
                    'frequencia': len(high_kill_games),
                    'porcentagem': (len(high_kill_games) / len(df)) * 100,
                    'kills_medio': high_kill_games['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'duracao_media': high_kill_games['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'diferenca_media': high_kill_games['kill_difference'].mean(),
                    'high_diff_percentage': (high_kill_games['kill_difference'] > 14.5).mean() * 100
                }
                scenarios.append(scenario)
        
        # Análise de composições de times
        team_comps = []
        
        # Composição 1: Times com muitos Pushers
        if 'radiant_Pusher' in df.columns and 'dire_Pusher' in df.columns:
            df['radiant_Pusher'] = pd.to_numeric(df['radiant_Pusher'], errors='coerce')
            df['dire_Pusher'] = pd.to_numeric(df['dire_Pusher'], errors='coerce')
            
            radiant_high_pusher = df[df['radiant_Pusher'] >= 2]
            dire_high_pusher = df[df['dire_Pusher'] >= 2]
            
            if len(radiant_high_pusher) > 0:
                comp = {
                    'nome': 'Radiant com 2+ Pushers',
                    'frequencia': len(radiant_high_pusher),
                    'win_rate': (radiant_high_pusher['radiant_win'] == '1').mean() * 100 if 'radiant_win' in df.columns else None,
                    'duracao_media': radiant_high_pusher['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': radiant_high_pusher['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': radiant_high_pusher['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
            
            if len(dire_high_pusher) > 0:
                comp = {
                    'nome': 'Dire com 2+ Pushers',
                    'frequencia': len(dire_high_pusher),
                    'win_rate': 100 - ((dire_high_pusher['radiant_win'] == '1').mean() * 100) if 'radiant_win' in df.columns else None,
                    'duracao_media': dire_high_pusher['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': dire_high_pusher['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': dire_high_pusher['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
        
        # Composição 2: Times com muitos Scalers (late game)
        if 'radiant_Scaler' in df.columns and 'dire_Scaler' in df.columns:
            df['radiant_Scaler'] = pd.to_numeric(df['radiant_Scaler'], errors='coerce')
            df['dire_Scaler'] = pd.to_numeric(df['dire_Scaler'], errors='coerce')
            
            radiant_high_scaler = df[df['radiant_Scaler'] >= 2]
            dire_high_scaler = df[df['dire_Scaler'] >= 2]
            
            if len(radiant_high_scaler) > 0:
                comp = {
                    'nome': 'Radiant com 2+ Scalers (late game)',
                    'frequencia': len(radiant_high_scaler),
                    'win_rate': (radiant_high_scaler['radiant_win'] == '1').mean() * 100 if 'radiant_win' in df.columns else None,
                    'duracao_media': radiant_high_scaler['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': radiant_high_scaler['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': radiant_high_scaler['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
            
            if len(dire_high_scaler) > 0:
                comp = {
                    'nome': 'Dire com 2+ Scalers (late game)',
                    'frequencia': len(dire_high_scaler),
                    'win_rate': 100 - ((dire_high_scaler['radiant_win'] == '1').mean() * 100) if 'radiant_win' in df.columns else None,
                    'duracao_media': dire_high_scaler['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': dire_high_scaler['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': dire_high_scaler['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
        
        # Composição 3: Times com muitos heróis de Pickoff
        if 'radiant_Pickoff' in df.columns and 'dire_Pickoff' in df.columns:
            df['radiant_Pickoff'] = pd.to_numeric(df['radiant_Pickoff'], errors='coerce')
            df['dire_Pickoff'] = pd.to_numeric(df['dire_Pickoff'], errors='coerce')
            
            radiant_high_pickoff = df[df['radiant_Pickoff'] >= 2]
            dire_high_pickoff = df[df['dire_Pickoff'] >= 2]
            
            if len(radiant_high_pickoff) > 0:
                comp = {
                    'nome': 'Radiant com 2+ heróis de Pickoff',
                    'frequencia': len(radiant_high_pickoff),
                    'win_rate': (radiant_high_pickoff['radiant_win'] == '1').mean() * 100 if 'radiant_win' in df.columns else None,
                    'duracao_media': radiant_high_pickoff['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': radiant_high_pickoff['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': radiant_high_pickoff['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
            
            if len(dire_high_pickoff) > 0:
                comp = {
                    'nome': 'Dire com 2+ heróis de Pickoff',
                    'frequencia': len(dire_high_pickoff),
                    'win_rate': 100 - ((dire_high_pickoff['radiant_win'] == '1').mean() * 100) if 'radiant_win' in df.columns else None,
                    'duracao_media': dire_high_pickoff['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': dire_high_pickoff['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': dire_high_pickoff['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
        
        # Composição 4: Times com muitos heróis de Engage
        if 'radiant_Engage' in df.columns and 'dire_Engage' in df.columns:
            df['radiant_Engage'] = pd.to_numeric(df['radiant_Engage'], errors='coerce')
            df['dire_Engage'] = pd.to_numeric(df['dire_Engage'], errors='coerce')
            
            radiant_high_engage = df[df['radiant_Engage'] >= 2]
            dire_high_engage = df[df['dire_Engage'] >= 2]
            
            if len(radiant_high_engage) > 0:
                comp = {
                    'nome': 'Radiant com 2+ heróis de Engage',
                    'frequencia': len(radiant_high_engage),
                    'win_rate': (radiant_high_engage['radiant_win'] == '1').mean() * 100 if 'radiant_win' in df.columns else None,
                    'duracao_media': radiant_high_engage['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': radiant_high_engage['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': radiant_high_engage['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
            
            if len(dire_high_engage) > 0:
                comp = {
                    'nome': 'Dire com 2+ heróis de Engage',
                    'frequencia': len(dire_high_engage),
                    'win_rate': 100 - ((dire_high_engage['radiant_win'] == '1').mean() * 100) if 'radiant_win' in df.columns else None,
                    'duracao_media': dire_high_engage['duration_min'].mean() if 'duration_min' in df.columns else None,
                    'kills_medio': dire_high_engage['total_kills'].mean() if 'total_kills' in df.columns else None,
                    'diferenca_media': dire_high_engage['kill_difference'].mean() if 'kill_difference' in df.columns else None
                }
                team_comps.append(comp)
        
        # Gerar relatório de cenários
        scenarios_report = "# Cenários de Jogo e Tendências no Dota 2\n\n"
        scenarios_report += "## Cenários Específicos com Impacto em Handicap de Kills\n\n"
        
        for i, scenario in enumerate(scenarios, 1):
            scenarios_report += f"### {i}. {scenario['nome']}\n\n"
            scenarios_report += f
(Content truncated due to size limit. Use line ranges to read in chunks)