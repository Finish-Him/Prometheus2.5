import os
import json
import docx2txt
import re
from collections import defaultdict

# Diretório onde os arquivos DOCX estão localizados
upload_dir = '/home/ubuntu/upload'
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Lista para armazenar todas as informações extraídas
all_docx_data = []

# Função para extrair informações de um arquivo DOCX
def extract_docx_info(file_path):
    try:
        # Extrair texto do arquivo DOCX
        text = docx2txt.process(file_path)
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return []
    
    # Nome do arquivo sem caminho e extensão
    file_name = os.path.basename(file_path).replace('.docx', '')
    
    # Lista para armazenar informações deste arquivo DOCX
    docx_info = []
    
    # Adicionar metadados do arquivo
    docx_info.append({
        "type": "docx_metadata",
        "file": file_name,
        "length": len(text),
        "source": "upload_directory"
    })
    
    # Dividir o conteúdo em parágrafos (blocos de texto separados por linhas em branco)
    paragraphs = re.split(r'\n\s*\n', text)
    for i, para in enumerate(paragraphs):
        if len(para.strip()) > 20:  # Ignorar parágrafos muito curtos
            para_info = {
                "type": "docx_paragraph",
                "file": file_name,
                "paragraph_index": i,
                "text": para.strip()[:500]  # Limitar tamanho do texto
            }
            docx_info.append(para_info)
    
    # Extrair cabeçalhos (linhas que parecem ser títulos)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        # Identificar linhas que parecem ser cabeçalhos (curtas, terminam sem pontuação, etc.)
        if (len(line) > 3 and len(line) < 100 and 
            not line.endswith('.') and not line.endswith(',') and
            not line.endswith(':') and not line.endswith(';')):
            header_info = {
                "type": "docx_header",
                "file": file_name,
                "line_index": i,
                "text": line
            }
            docx_info.append(header_info)
    
    # Extrair listas (linhas que começam com marcadores ou números)
    list_items = re.findall(r'(?:^|\n)(?:\s*[\*\-•◦▪▫■□●○]\s+|\s*\d+[\.\)]\s+)(.+)', text)
    for i, item in enumerate(list_items):
        if len(item.strip()) > 5:  # Ignorar itens muito curtos
            list_info = {
                "type": "docx_list_item",
                "file": file_name,
                "item_index": i,
                "text": item.strip()
            }
            docx_info.append(list_info)
    
    # Extrair tabelas (linhas que contêm múltiplos separadores de tabela)
    table_lines = [line for line in lines if line.count('|') > 1 or line.count('\t') > 1]
    if table_lines:
        table_info = {
            "type": "docx_table_detected",
            "file": file_name,
            "table_count": len(table_lines),
            "sample_line": table_lines[0][:100] if table_lines else ""
        }
        docx_info.append(table_info)
    
    # Extrair padrões específicos com base no nome do arquivo
    if "oráculo" in file_name.lower() or "oracle" in file_name.lower() or "database" in file_name.lower():
        # Extrair informações sobre a base de dados
        patterns = [
            (r'(?:tabela|table)\s+(\w+)', "table_name"),
            (r'(?:coluna|column)\s+(\w+)', "column_name"),
            (r'(?:campo|field)\s+(\w+)', "field_name"),
            (r'(?:tipo|type)\s+(\w+)', "data_type"),
            (r'(?:versão|version)\s+(\d+\.?\d*)', "version_number")
        ]
        
        for pattern, key in patterns:
            matches = re.findall(pattern, text.lower())
            for j, match in enumerate(matches):
                db_info = {
                    "type": "database_data",
                    "file": file_name,
                    "data_type": key,
                    "match_index": j,
                    "value": match
                }
                docx_info.append(db_info)
    
    elif "aprendizado" in file_name.lower() or "learning" in file_name.lower():
        # Extrair informações sobre aprendizado
        patterns = [
            (r'(?:lição|lesson)\s+(\d+)', "lesson_number"),
            (r'(?:aprendemos|learned)\s+que\s+(.{10,100}?)(?:\.|\n)', "learning_point"),
            (r'(?:conclusão|conclusion):\s+(.{10,100}?)(?:\.|\n)', "conclusion"),
            (r'(?:observação|observation):\s+(.{10,100}?)(?:\.|\n)', "observation")
        ]
        
        for pattern, key in patterns:
            matches = re.findall(pattern, text.lower())
            for j, match in enumerate(matches):
                learning_info = {
                    "type": "learning_data",
                    "file": file_name,
                    "data_type": key,
                    "match_index": j,
                    "value": match
                }
                docx_info.append(learning_info)
    
    elif "análise" in file_name.lower() or "analysis" in file_name.lower() or "liquipédia" in file_name.lower():
        # Extrair informações sobre análises
        patterns = [
            (r'(?:herói|hero)\s+(\w+)', "hero_name"),
            (r'(?:jogador|player)\s+(\w+)', "player_name"),
            (r'(?:equipe|team)\s+(\w+)', "team_name"),
            (r'(?:taxa de vitória|winrate)\s+(\d+\.?\d*%?)', "winrate"),
            (r'(?:patch|versão)\s+(\d+\.?\d*\w?)', "patch_version")
        ]
        
        for pattern, key in patterns:
            matches = re.findall(pattern, text.lower())
            for j, match in enumerate(matches):
                analysis_info = {
                    "type": "analysis_data",
                    "file": file_name,
                    "data_type": key,
                    "match_index": j,
                    "value": match
                }
                docx_info.append(analysis_info)
    
    # Extrair dados numéricos (números, porcentagens, estatísticas)
    numeric_patterns = [
        (r'(\d+\.?\d*%)', "percentage"),
        (r'(\d+\.?\d*)\s*(?:gold|ouro)', "gold_value"),
        (r'(\d+\.?\d*)\s*(?:xp|experience|experiência)', "xp_value"),
        (r'(\d+\.?\d*)\s*(?:kills|abates)', "kills_value"),
        (r'(\d+\.?\d*)\s*(?:deaths|mortes)', "deaths_value"),
        (r'(\d+\.?\d*)\s*(?:assists|assistências)', "assists_value"),
        (r'(\d+\.?\d*)\s*(?:gpm|gold per minute)', "gpm_value"),
        (r'(\d+\.?\d*)\s*(?:xpm|experience per minute)', "xpm_value")
    ]
    
    for pattern, key in numeric_patterns:
        matches = re.findall(pattern, text.lower())
        for j, match in enumerate(matches):
            numeric_info = {
                "type": "numeric_data",
                "file": file_name,
                "data_type": key,
                "match_index": j,
                "value": match
            }
            docx_info.append(numeric_info)
    
    # Limitar a quantidade de informações para arquivos muito grandes
    if len(docx_info) > 1000:
        print(f"Limitando informações de {file_path} para 1000 itens")
        return docx_info[:1000]
    
    return docx_info

# Processar todos os arquivos DOCX
docx_files = [f for f in os.listdir(upload_dir) if f.endswith('.docx')]
for docx_file in docx_files:
    file_path = os.path.join(upload_dir, docx_file)
    print(f"Processando {file_path}...")
    docx_info = extract_docx_info(file_path)
    all_docx_data.extend(docx_info)
    print(f"Extraídas {len(docx_info)} informações de {file_path}")

# Salvar os dados extraídos em um arquivo JSON
output_file = os.path.join(output_dir, 'docx_extracted_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_docx_data, f, ensure_ascii=False, indent=2)

print(f"Total de {len(all_docx_data)} informações extraídas dos arquivos DOCX")
print(f"Dados salvos em {output_file}")
