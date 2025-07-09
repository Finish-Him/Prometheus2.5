import pandas as pd
import os
import json
from datetime import datetime

# Caminho para o arquivo Excel
xlsx_path = "/home/ubuntu/upload/Database Oráculo 3.0.xlsx"
output_dir = "/home/ubuntu/oraculo_6_7/analise_database"

# Criar diretório de saída se não existir
os.makedirs(output_dir, exist_ok=True)

# Função para salvar informações sobre as abas
def analyze_excel_file(file_path):
    print(f"Analisando arquivo: {file_path}")
    
    # Ler todas as abas do arquivo Excel
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    
    print(f"Total de abas encontradas: {len(sheet_names)}")
    
    sheets_info = []
    
    # Analisar cada aba
    for sheet_name in sheet_names:
        print(f"Analisando aba: {sheet_name}")
        
        try:
            # Ler a aba como DataFrame
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Informações básicas
            row_count = len(df)
            col_count = len(df.columns)
            
            # Verificar se há dados
            if row_count == 0:
                print(f"  Aba {sheet_name} está vazia.")
                sheets_info.append({
                    "sheet_name": sheet_name,
                    "row_count": 0,
                    "col_count": 0,
                    "columns": [],
                    "has_data": False,
                    "sample_rows": []
                })
                continue
            
            # Coletar nomes das colunas
            columns = df.columns.tolist()
            
            # Verificar tipos de dados
            dtypes = df.dtypes.astype(str).to_dict()
            
            # Verificar valores nulos
            null_counts = df.isnull().sum().to_dict()
            
            # Verificar menções a patch, especialmente 7.38
            patch_mentions = {}
            for col in columns:
                if 'patch' in str(col).lower():
                    patch_mentions[str(col)] = True
                    
                    # Verificar valores específicos na coluna
                    if df[col].dtype == object or df[col].dtype == str:
                        patch_values = df[col].astype(str).str.contains('7.38').sum()
                        patch_mentions[f"{col}_7.38_count"] = int(patch_values)
            
            # Verificar menções a eventos importantes
            event_keywords = ['roshan', 'tower', 'tormentor', 'torre', 'objective']
            event_mentions = {}
            
            for keyword in event_keywords:
                for col in columns:
                    if keyword in str(col).lower():
                        event_mentions[f"{col}_{keyword}"] = True
            
            # Obter amostra de linhas (primeiras 5)
            sample_rows = df.head(5).to_dict(orient='records')
            
            # Salvar CSV da aba para análise posterior
            csv_path = os.path.join(output_dir, f"{sheet_name.replace(' ', '_')}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"  Salvo CSV para aba {sheet_name}: {csv_path}")
            
            # Adicionar informações à lista
            sheets_info.append({
                "sheet_name": sheet_name,
                "row_count": row_count,
                "col_count": col_count,
                "columns": columns,
                "dtypes": {str(k): v for k, v in dtypes.items()},
                "null_counts": {str(k): int(v) for k, v in null_counts.items()},
                "has_data": True,
                "patch_mentions": patch_mentions,
                "event_mentions": event_mentions,
                "csv_path": csv_path,
                "sample_rows_count": min(5, row_count)
            })
            
            print(f"  Aba {sheet_name}: {row_count} linhas, {col_count} colunas")
            
        except Exception as e:
            print(f"  Erro ao processar aba {sheet_name}: {str(e)}")
            sheets_info.append({
                "sheet_name": sheet_name,
                "error": str(e),
                "has_data": False
            })
    
    return sheets_info

# Analisar o arquivo Excel
sheets_info = analyze_excel_file(xlsx_path)

# Salvar informações em formato JSON
json_path = os.path.join(output_dir, "database_analysis.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(sheets_info, f, indent=2, ensure_ascii=False)

print(f"Análise completa salva em: {json_path}")

# Criar relatório em formato Markdown
md_path = os.path.join(output_dir, "database_analysis.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f"# Análise do Database Oráculo 3.0\n\n")
    f.write(f"Data da análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"## Resumo\n\n")
    f.write(f"Total de abas analisadas: {len(sheets_info)}\n\n")
    
    # Tabela de resumo
    f.write("| Aba | Linhas | Colunas | Tem dados | Menções a Patch 7.38 | Eventos importantes |\n")
    f.write("|-----|--------|---------|-----------|----------------------|--------------------|\n")
    
    for sheet in sheets_info:
        sheet_name = sheet["sheet_name"]
        row_count = sheet.get("row_count", 0)
        col_count = sheet.get("col_count", 0)
        has_data = "Sim" if sheet.get("has_data", False) else "Não"
        
        # Verificar menções a patch 7.38
        patch_mentions = "Não"
        if "patch_mentions" in sheet:
            for key, value in sheet["patch_mentions"].items():
                if "7.38" in key and value > 0:
                    patch_mentions = f"Sim ({value})"
        
        # Verificar menções a eventos importantes
        events = []
        if "event_mentions" in sheet:
            for key in sheet["event_mentions"]:
                for event in ['roshan', 'tower', 'tormentor', 'torre', 'objective']:
                    if event in key.lower():
                        events.append(event)
        
        events_str = ", ".join(events) if events else "Não"
        
        f.write(f"| {sheet_name} | {row_count} | {col_count} | {has_data} | {patch_mentions} | {events_str} |\n")
    
    # Detalhes de cada aba
    f.write("\n## Detalhes por Aba\n\n")
    
    for sheet in sheets_info:
        sheet_name = sheet["sheet_name"]
        f.write(f"### {sheet_name}\n\n")
        
        if not sheet.get("has_data", False):
            if "error" in sheet:
                f.write(f"**Erro:** {sheet['error']}\n\n")
            else:
                f.write("**Aba sem dados**\n\n")
            continue
        
        f.write(f"- **Linhas:** {sheet['row_count']}\n")
        f.write(f"- **Colunas:** {sheet['col_count']}\n")
        
        # Listar colunas
        f.write("\n**Colunas:**\n\n")
        for col in sheet["columns"]:
            dtype = sheet["dtypes"].get(str(col), "")
            null_count = sheet["null_counts"].get(str(col), 0)
            null_percent = (null_count / sheet['row_count']) * 100 if sheet['row_count'] > 0 else 0
            
            f.write(f"- `{col}` (Tipo: {dtype}, Nulos: {null_count} - {null_percent:.1f}%)\n")
        
        # Menções a patch
        if "patch_mentions" in sheet and sheet["patch_mentions"]:
            f.write("\n**Menções a Patch:**\n\n")
            for key, value in sheet["patch_mentions"].items():
                f.write(f"- {key}: {value}\n")
        
        # Menções a eventos
        if "event_mentions" in sheet and sheet["event_mentions"]:
            f.write("\n**Menções a Eventos:**\n\n")
            for key in sheet["event_mentions"]:
                f.write(f"- {key}\n")
        
        # Caminho do CSV
        f.write(f"\n**CSV exportado:** {sheet.get('csv_path', 'N/A')}\n\n")
        
        # Separador entre abas
        f.write("---\n\n")

print(f"Relatório Markdown salvo em: {md_path}")

# Criar um script para identificar CSVs relevantes na estrutura organizada
find_csvs_script = """
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
    f.write("# CSVs Relevantes para Consolidação\n\n")

    f.write(f"Total de CSVs relevantes encontrados: {len(relevant_csvs)}\n\n")

    f.write("## Lista de CSVs Relevantes\n\n")
    f.write("| Arquivo | Importância | Razão |\n")
    f.write("|---------|-------------|-------|\n")

    for csv in relevant_csvs:
        f.write(f"| {csv['relative_path']} | {csv['importance']} | {csv['reason']} |\n")

print(f"Encontrados {len(relevant_csvs)} CSVs relevantes de um total de {len(all_csvs)} CSVs.")
print(f"Resultados salvos em {output_dir}/relevant_csvs.json e {output_dir}/relevant_csvs.md")
"""

# Salvar o script para identificar CSVs relevantes
find_csvs_path = os.path.join(output_dir, "find_relevant_csvs.py")
with open(find_csvs_path, 'w', encoding='utf-8') as f:
    f.write(find_csvs_script)

print(f"Script para identificar CSVs relevantes salvo em: {find_csvs_path}")
print("Execute este script após a análise do Database Oráculo 3.0.xlsx para identificar CSVs relevantes na estrutura organizada.")

