import pandas as pd
import os
import numpy as np

# Diretório para salvar os resultados
output_dir = '/home/ubuntu/dota_analysis/output'
os.makedirs(output_dir, exist_ok=True)

# Carregar o arquivo Excel
excel_path = '/home/ubuntu/upload/Database Oráculo 3.0.xlsx'
print(f"Analisando o arquivo: {excel_path}")

# Listar todas as abas do arquivo Excel
xl = pd.ExcelFile(excel_path)
sheet_names = xl.sheet_names
print(f"Abas disponíveis no arquivo: {sheet_names}")

# Função para salvar resultados da análise
def save_analysis_results(filename, content):
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Resultados salvos em: {os.path.join(output_dir, filename)}")

# Analisar apenas as abas mais relevantes para handicap de Kills
relevant_sheets = ['Match Detail', 'Pro Match', 'LOB', 'Treinamento da IA', 'Dataset Previsor']

for sheet_name in relevant_sheets:
    if sheet_name in sheet_names:
        print(f"\nAnalisando a aba: {sheet_name}")
        
        try:
            # Tentar ler a aba com diferentes parâmetros para lidar com formatos variados
            try:
                # Primeira tentativa: formato padrão
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
            except:
                try:
                    # Segunda tentativa: especificar separador
                    df = pd.read_excel(excel_path, sheet_name=sheet_name, sep=',')
                except:
                    # Terceira tentativa: ler como texto e depois processar
                    df_raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
                    # Verificar se temos apenas uma coluna com valores separados por vírgula
                    if df_raw.shape[1] == 1 and isinstance(df_raw.iloc[0, 0], str) and ',' in df_raw.iloc[0, 0]:
                        # Extrair cabeçalhos da primeira linha
                        headers = df_raw.iloc[0, 0].split(',')
                        # Criar DataFrame vazio com esses cabeçalhos
                        df = pd.DataFrame(columns=headers)
                        # Processar cada linha
                        for i in range(1, len(df_raw)):
                            if isinstance(df_raw.iloc[i, 0], str):
                                values = df_raw.iloc[i, 0].split(',')
                                # Garantir que temos o número correto de valores
                                if len(values) == len(headers):
                                    df.loc[i-1] = values
                    else:
                        # Se não conseguirmos processar, usar o DataFrame bruto
                        df = df_raw
            
            print(f"Dimensões do DataFrame: {df.shape}")
            print(f"Colunas na aba {sheet_name}:")
            print(df.columns.tolist())
            
            # Verificar se existem colunas relacionadas a kills
            kill_columns = [col for col in df.columns if 'kill' in str(col).lower() or 'score' in str(col).lower()]
            handicap_columns = [col for col in df.columns if 'handicap' in str(col).lower()]
            
            print(f"Colunas relacionadas a kills/score: {kill_columns}")
            print(f"Colunas relacionadas a handicap: {handicap_columns}")
            
            # Salvar informações básicas sobre os dados
            analysis_text = f"# Análise da aba {sheet_name}\n\n"
            analysis_text += f"## Dimensões: {df.shape}\n\n"
            analysis_text += f"## Colunas disponíveis:\n"
            for col in df.columns:
                analysis_text += f"- {col}\n"
            
            analysis_text += f"\n## Colunas relacionadas a kills/score: {', '.join(kill_columns)}\n"
            analysis_text += f"\n## Colunas relacionadas a handicap: {', '.join(handicap_columns)}\n"
            
            # Análise específica para kills se tivermos as colunas necessárias
            if 'radiant_score' in df.columns and 'dire_score' in df.columns:
                # Converter para numérico se necessário
                if df['radiant_score'].dtype == 'object':
                    df['radiant_score'] = pd.to_numeric(df['radiant_score'], errors='coerce')
                if df['dire_score'].dtype == 'object':
                    df['dire_score'] = pd.to_numeric(df['dire_score'], errors='coerce')
                
                df['total_kills'] = df['radiant_score'] + df['dire_score']
                df['kill_difference'] = abs(df['radiant_score'] - df['dire_score'])
                
                analysis_text += f"\n## Estatísticas de Kills\n\n"
                analysis_text += f"- Total médio de kills por partida: {df['total_kills'].mean():.2f}\n"
                analysis_text += f"- Mediana de kills por partida: {df['total_kills'].median():.2f}\n"
                analysis_text += f"- Máximo de kills em uma partida: {df['total_kills'].max()}\n"
                analysis_text += f"- Mínimo de kills em uma partida: {df['total_kills'].min()}\n"
                analysis_text += f"- Diferença média de kills entre times: {df['kill_difference'].mean():.2f}\n"
                analysis_text += f"- Máxima diferença de kills: {df['kill_difference'].max()}\n"
                
                # Distribuição de diferenças de kills
                kill_diff_counts = df['kill_difference'].value_counts().sort_index()
                analysis_text += f"\n## Distribuição de Diferenças de Kills\n\n"
                analysis_text += "| Diferença | Número de Partidas | Porcentagem |\n"
                analysis_text += "|-----------|-------------------|-------------|\n"
                
                for diff, count in kill_diff_counts.items():
                    percentage = (count / len(df)) * 100
                    analysis_text += f"| {diff} | {count} | {percentage:.2f}% |\n"
                
                # Análise de handicap alto
                analysis_text += f"\n## Análise de Handicap Alto (>14.5 Kills)\n\n"
                high_diff_matches = df[df['kill_difference'] > 14.5]
                analysis_text += f"- Número de partidas com diferença > 14.5 kills: {len(high_diff_matches)}\n"
                analysis_text += f"- Porcentagem do total: {(len(high_diff_matches) / len(df)) * 100:.2f}%\n"
                
                if len(high_diff_matches) > 0 and 'duration' in df.columns:
                    # Converter duração para minutos se necessário
                    if df['duration'].dtype == 'object':
                        df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
                    
                    if df['duration'].max() > 1000:  # provavelmente em segundos
                        df['duration_minutes'] = df['duration'] / 60
                        high_diff_matches['duration_minutes'] = high_diff_matches['duration'] / 60
                    else:
                        df['duration_minutes'] = df['duration']
                        high_diff_matches['duration_minutes'] = high_diff_matches['duration']
                    
                    analysis_text += f"- Duração média de partidas com alta diferença: {high_diff_matches['duration_minutes'].mean():.2f} minutos\n"
                    analysis_text += f"- Duração média de todas as partidas: {df['duration_minutes'].mean():.2f} minutos\n"
                    
                    # Comparar duração de partidas com alta diferença vs. todas as partidas
                    shorter_percentage = (high_diff_matches['duration_minutes'] < df['duration_minutes'].mean()).mean() * 100
                    analysis_text += f"- Porcentagem de partidas com alta diferença que são mais curtas que a média: {shorter_percentage:.2f}%\n"
            
            # Análise de duração vs kills (se disponível)
            if 'duration' in df.columns and ('radiant_score' in df.columns and 'dire_score' in df.columns):
                # Converter para numérico se necessário
                if df['duration'].dtype == 'object':
                    df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
                
                # Converter duração para minutos se estiver em segundos
                if df['duration'].max() > 1000:  # provavelmente em segundos
                    df['duration_minutes'] = df['duration'] / 60
                else:
                    df['duration_minutes'] = df['duration']
                
                # Calcular kills por minuto
                df['kills_per_minute'] = df['total_kills'] / df['duration_minutes']
                
                analysis_text += f"\n## Relação entre Duração e Kills\n\n"
                analysis_text += f"- Duração média das partidas: {df['duration_minutes'].mean():.2f} minutos\n"
                analysis_text += f"- Taxa média de kills por minuto: {df['kills_per_minute'].mean():.2f}\n"
                
                # Agrupar por faixas de duração
                df['duration_bracket'] = pd.cut(df['duration_minutes'], 
                                               bins=[0, 20, 30, 40, 50, 60, float('inf')],
                                               labels=['<20 min', '20-30 min', '30-40 min', '40-50 min', '50-60 min', '>60 min'])
                
                duration_stats = df.groupby('duration_bracket').agg({
                    'total_kills': ['mean', 'median', 'count'],
                    'kill_difference': ['mean', 'median'],
                    'kills_per_minute': ['mean', 'median']
                })
                
                analysis_text += f"\n## Kills por Faixa de Duração\n\n"
                analysis_text += "| Duração | Partidas | Kills Médio | Kills Mediana | Diferença Média | Kills/Min |\n"
                analysis_text += "|---------|----------|-------------|---------------|-----------------|----------|\n"
                
                for idx, row in duration_stats.iterrows():
                    analysis_text += f"| {idx} | {row[('total_kills', 'count')]} | "
                    analysis_text += f"{row[('total_kills', 'mean')]:.2f} | {row[('total_kills', 'median')]:.2f} | "
                    analysis_text += f"{row[('kill_difference', 'mean')]:.2f} | {row[('kills_per_minute', 'mean')]:.2f} |\n"
                
                # Análise de correlação
                analysis_text += f"\n## Correlação entre Duração e Kills\n\n"
                corr_duration_total = df['duration_minutes'].corr(df['total_kills'])
                corr_duration_diff = df['duration_minutes'].corr(df['kill_difference'])
                analysis_text += f"- Correlação entre duração e total de kills: {corr_duration_total:.4f}\n"
                analysis_text += f"- Correlação entre duração e diferença de kills: {corr_duration_diff:.4f}\n"
                
                # Análise de jogos rápidos
                fast_games = df[df['duration_minutes'] < 30]
                if len(fast_games) > 0:
                    analysis_text += f"\n## Análise de Jogos Rápidos (<30 minutos)\n\n"
                    analysis_text += f"- Número de jogos rápidos: {len(fast_games)}\n"
                    analysis_text += f"- Porcentagem do total: {(len(fast_games) / len(df)) * 100:.2f}%\n"
                    analysis_text += f"- Total médio de kills: {fast_games['total_kills'].mean():.2f}\n"
                    analysis_text += f"- Diferença média de kills: {fast_games['kill_difference'].mean():.2f}\n"
                    analysis_text += f"- Porcentagem com diferença > 14.5: {(fast_games['kill_difference'] > 14.5).mean() * 100:.2f}%\n"
            
            # Salvar a análise
            save_analysis_results(f"analise_{sheet_name.replace(' ', '_').lower()}.md", analysis_text)
            
        except Exception as e:
            print(f"Erro ao analisar a aba {sheet_name}: {e}")

print("\nAnálise inicial concluída. Verificando dados para análise de handicap de Kills...")
