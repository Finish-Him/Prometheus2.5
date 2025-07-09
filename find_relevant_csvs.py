
import os
import pandas as pd
import json

# Diretório base da estrutura organizada
base_dir = "/home/ubuntu/oraculo_6_7/organizado/Tabelas_CSV"
output_dir = "/home/ubuntu/oraculo_6_7/analise_database"
os.makedirs(output_dir, exist_ok=True)

# Palavras-chave para identificar CSVs relevantes
keywords = [
    'patch', '7.38', 'roshan', 'tower', 'tormentor', 'torre', 'objective',
    'match', 'player', 'hero', 'item', 'detail', 'pro', 'team', 'tournament',
    'detalhado', 'partida', 'jogador', 'heroi', 'item', 'detalhe', 'time', 'torneio'
]

# Função para verificar se um arquivo CSV é relevante
def is_relevant_csv(file_path, keywords):
    # Verificar nome do arquivo
    file_name = os.path.basename(file_path).lower()
    for keyword in keywords:
        if keyword.lower() in file_name:
            return True, f"Nome contém '{keyword}'"
    
    # Verificar conteúdo do arquivo (primeiras linhas)
    try:
        df = pd.read_csv(file_path, nrows=5)
        
        # Verificar nomes das colunas
        for col in df.columns:
            for keyword in keywords:
                if keyword.lower() in str(col).lower():
                    return True, f"Coluna '{col}' contém '{keyword}'"
        
        # Verificar valores nas primeiras linhas
        for keyword in keywords:
            for col in df.columns:
                if df[col].astype(str).str.contains(keyword.lower()).any():
                    return True, f"Valores na coluna '{col}' contêm '{keyword}'"
    
    except Exception as e:
        return False, f"Erro ao analisar: {str(e)}"
    
    return False, "Não relevante"

# Encontrar todos os CSVs na estrutura organizada
relevant_csvs = []
all_csvs = []

for importance in ['Alta_Importancia', 'Media_Importancia', 'Baixa_Importancia']:
    importance_dir = os.path.join(base_dir, importance)
    
    for root, dirs, files in os.walk(importance_dir):
        for file in files:
            if file.lower().endswith('.csv'):
                file_path = os.path.join(root, file)
                
                # Verificar relevância
                is_relevant, reason = is_relevant_csv(file_path, keywords)
                
                csv_info = {
                    'path': file_path,
                    'importance': importance,
                    'relative_path': os.path.relpath(file_path, base_dir),
                    'is_relevant': is_relevant,
                    'reason': reason
                }
                
                all_csvs.append(csv_info)
                
                if is_relevant:
                    relevant_csvs.append(csv_info)
                    print(f"CSV relevante: {file_path} - {reason}")

# Salvar resultados
with open(os.path.join(output_dir, 'relevant_csvs.json'), 'w', encoding='utf-8') as f:
    json.dump(relevant_csvs, f, indent=2, ensure_ascii=False)

with open(os.path.join(output_dir, 'all_csvs.json'), 'w', encoding='utf-8') as f:
    json.dump(all_csvs, f, indent=2, ensure_ascii=False)

# Criar relatório em Markdown
with open(os.path.join(output_dir, 'relevant_csvs.md'), 'w', encoding='utf-8') as f:
    f.write("# CSVs Relevantes para Consolidação

")

    f.write(f"Total de CSVs relevantes encontrados: {len(relevant_csvs)}

")

    f.write("## Lista de CSVs Relevantes

")
    f.write("| Arquivo | Importância | Razão |
")
    f.write("|---------|-------------|-------|
")

    for csv in relevant_csvs:
        f.write(f"| {csv['relative_path']} | {csv['importance']} | {csv['reason']} |
")

print(f"Encontrados {len(relevant_csvs)} CSVs relevantes de um total de {len(all_csvs)} CSVs.")
print(f"Resultados salvos em {output_dir}/relevant_csvs.json e {output_dir}/relevant_csvs.md")
