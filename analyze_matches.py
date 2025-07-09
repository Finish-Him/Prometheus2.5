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
# Vamos focar em 'Match Detail' e 'Pro Match' primeiro
relevant_sheets = ['Match Detail', 'Pro Match']

for sheet_name in relevant_sheets:
    if sheet_name in sheet_names:
        print(f"\nAnalisando a aba: {sheet_name}")
        
        # Ler apenas as primeiras linhas para entender a estrutura
        df_sample = pd.read_excel(excel_path, sheet_name=sheet_name, nrows=5)
        print(f"Colunas na aba {sheet_name}:")
        print(df_sample.columns.tolist())
        
        # Verificar se existem colunas relacionadas a kills
        kill_columns = [col for col in df_sample.columns if 'kill' in str(col).lower()]
        print(f"Colunas relacionadas a kills: {kill_columns}")
        
        # Agora vamos ler a aba completa, mas apenas as colunas que nos interessam
        # Isso economiza memória e processamento
        try:
            # Identificar colunas relevantes para nossa análise
            relevant_columns = []
            
            # Colunas básicas que provavelmente queremos
            basic_columns = ['match_id', 'duration', 'radiant_win', 'radiant_score', 'dire_score']
            for col in basic_columns:
                if col in df_sample.columns:
                    relevant_columns.append(col)
            
            # Adicionar colunas relacionadas a kills
            relevant_columns.extend(kill_columns)
            
            # Adicionar outras colunas potencialmente úteis
            for col in df_sample.columns:
                col_lower = str(col).lower()
                if any(term in col_lower for term in ['team', 'handicap', 'hero', 'win', 'duration']):
                    if col not in relevant_columns:
                        relevant_columns.append(col)
            
            # Remover duplicatas
            relevant_columns = list(set(relevant_columns))
            
            print(f"Lendo apenas as colunas relevantes: {relevant_columns}")
            
            # Ler apenas as colunas relevantes
            if relevant_columns:
                df = pd.read_excel(excel_path, sheet_name=sheet_name, usecols=relevant_columns)
                print(f"Dimensões do DataFrame: {df.shape}")
                
                # Salvar informações básicas sobre os dados
                analysis_text = f"# Análise da aba {sheet_name}\n\n"
                analysis_text += f"## Dimensões: {df.shape}\n\n"
                analysis_text += f"## Colunas analisadas:\n"
                for col in df.columns:
                    analysis_text += f"- {col}\n"
                
                # Análise específica para kills
                if 'radiant_score' in df.columns and 'dire_score' in df.columns:
                    df['total_kills'] = df['radiant_score'] + df['dire_score']
                    df['kill_difference'] = abs(df['radiant_score'] - df['dire_score'])
                    
                    analysis_text += f"\n## Estatísticas de Kills\n\n"
                    analysis_text += f"- Total médio de kills por partida: {df['total_kills'].mean():.2f}\n"
                    analysis_text += f"- Mediana de kills por partida: {df['total_kills'].median():.2f}\n"
                    analysis_text += f"- Máximo de kills em uma partida: {df['total_kills'].max()}\n"
                    analysis_text += f"- Mínimo de kills em uma partida: {df['total_kills'].min()}\n"
                    analysis_text += f"- Diferença média de kills entre times: {df['kill_difference'].mean():.2f}\n"
                    analysis_text += f"- Máxima diferença de kills: {df['kill_difference'].max()}\n"
                
                # Análise de duração vs kills (se disponível)
                if 'duration' in df.columns and 'total_kills' in df.columns:
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
                    }).reset_index()
                    
                    analysis_text += f"\n## Kills por Faixa de Duração\n\n"
                    analysis_text += "| Duração | Partidas | Kills Médio | Kills Mediana | Diferença Média | Kills/Min |\n"
                    analysis_text += "|---------|----------|-------------|---------------|-----------------|----------|\n"
                    
                    for _, row in duration_stats.iterrows():
                        analysis_text += f"| {row['duration_bracket']} | {row[('total_kills', 'count')]} | "
                        analysis_text += f"{row[('total_kills', 'mean')]:.2f} | {row[('total_kills', 'median')]:.2f} | "
                        analysis_text += f"{row[('kill_difference', 'mean')]:.2f} | {row[('kills_per_minute', 'mean')]:.2f} |\n"
                
                # Salvar a análise
                save_analysis_results(f"analise_{sheet_name.replace(' ', '_').lower()}.md", analysis_text)
                
            else:
                print(f"Nenhuma coluna relevante encontrada na aba {sheet_name}")
        
        except Exception as e:
            print(f"Erro ao analisar a aba {sheet_name}: {e}")

print("\nAnálise inicial concluída. Verificando dados para análise de handicap de Kills...")
