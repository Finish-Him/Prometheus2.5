import os
import re
import json
from collections import defaultdict

# Diretório onde os arquivos markdown estão localizados
upload_dir = '/home/ubuntu/upload'
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Lista para armazenar todas as informações extraídas
all_md_data = []

# Função para extrair informações de um arquivo markdown
def extract_md_info(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin1') as f:
                content = f.read()
        except Exception as e:
            print(f"Erro ao ler {file_path}: {e}")
            return []
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return []
    
    # Nome do arquivo sem caminho e extensão
    file_name = os.path.basename(file_path).replace('.md', '')
    
    # Lista para armazenar informações deste markdown
    md_info = []
    
    # Adicionar metadados do arquivo
    md_info.append({
        "type": "markdown_metadata",
        "file": file_name,
        "length": len(content),
        "source": "upload_directory"
    })
    
    # Extrair cabeçalhos (títulos e subtítulos)
    headers = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
    for level, header in headers:
        header_info = {
            "type": "markdown_header",
            "file": file_name,
            "level": len(level),
            "text": header.strip()
        }
        md_info.append(header_info)
    
    # Extrair listas
    list_items = re.findall(r'^(\s*[-*+]\s+)(.+)$', content, re.MULTILINE)
    for indent, item in list_items:
        list_info = {
            "type": "markdown_list_item",
            "file": file_name,
            "indent": len(indent) - 1,
            "text": item.strip()
        }
        md_info.append(list_info)
    
    # Extrair tabelas
    tables = re.findall(r'(\|[^\n]+\|\n\|[-:| ]+\|\n(?:\|[^\n]+\|\n)+)', content)
    for i, table in enumerate(tables):
        rows = table.strip().split('\n')
        headers = [cell.strip() for cell in rows[0].split('|')[1:-1]]
        
        # Ignorar a linha de formatação (|----|----|----|)
        data_rows = rows[2:]
        
        table_info = {
            "type": "markdown_table",
            "file": file_name,
            "table_index": i,
            "headers": headers,
            "row_count": len(data_rows)
        }
        md_info.append(table_info)
        
        # Extrair dados das linhas da tabela (limitado a 20 linhas por tabela)
        for j, row in enumerate(data_rows[:20]):
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            row_data = {}
            for k, header in enumerate(headers):
                if k < len(cells):
                    row_data[header] = cells[k]
            
            table_row_info = {
                "type": "markdown_table_row",
                "file": file_name,
                "table_index": i,
                "row_index": j,
                "data": row_data
            }
            md_info.append(table_row_info)
    
    # Extrair parágrafos (texto entre linhas em branco, excluindo cabeçalhos, listas e tabelas)
    paragraphs = re.findall(r'(?<!\n#)(?<!\n[-*+])(?<!\n\|)(?<!\n```)\n\n([^#\n][^\n]+(?:\n[^#\n][^\n]+)*)', content)
    for i, para in enumerate(paragraphs):
        if len(para.strip()) > 10:  # Ignorar parágrafos muito curtos
            para_info = {
                "type": "markdown_paragraph",
                "file": file_name,
                "paragraph_index": i,
                "text": para.strip()[:500]  # Limitar tamanho do texto
            }
            md_info.append(para_info)
    
    # Extrair blocos de código
    code_blocks = re.findall(r'```(\w*)\n([\s\S]*?)```', content)
    for i, (language, code) in enumerate(code_blocks):
        code_info = {
            "type": "markdown_code_block",
            "file": file_name,
            "block_index": i,
            "language": language,
            "code": code[:500]  # Limitar tamanho do código
        }
        md_info.append(code_info)
    
    # Extrair informações específicas com base no nome do arquivo
    if "apostas" in file_name.lower() or "betting" in file_name.lower():
        # Extrair informações sobre apostas
        betting_patterns = [
            (r'odds\s+(\d+\.\d+)', "odds_value"),
            (r'probabilidade\s+(\d+\.?\d*%?)', "probability"),
            (r'valor esperado\s+(\d+\.?\d*)', "expected_value"),
            (r'(over|under)\s+(\d+\.?\d*)', "over_under"),
            (r'handicap\s+([+-]?\d+\.?\d*)', "handicap"),
            (r'(team\s+\w+|equipe\s+\w+)', "team_name")
        ]
        
        for pattern, key in betting_patterns:
            matches = re.findall(pattern, content.lower())
            for match in matches:
                betting_info = {
                    "type": "betting_data",
                    "file": file_name,
                    "data_type": key,
                    "value": match
                }
                md_info.append(betting_info)
    
    elif "meta" in file_name.lower() or "patch" in file_name.lower():
        # Extrair informações sobre o meta do jogo
        meta_patterns = [
            (r'(hero|herói)\s+(\w+)', "hero_name"),
            (r'winrate\s+(\d+\.?\d*%?)', "winrate"),
            (r'pick\s+rate\s+(\d+\.?\d*%?)', "pick_rate"),
            (r'ban\s+rate\s+(\d+\.?\d*%?)', "ban_rate"),
            (r'patch\s+(\d+\.\d+\w?)', "patch_version")
        ]
        
        for pattern, key in meta_patterns:
            matches = re.findall(pattern, content.lower())
            for match in matches:
                meta_info = {
                    "type": "meta_data",
                    "file": file_name,
                    "data_type": key,
                    "value": match
                }
                md_info.append(meta_info)
    
    elif "team" in file_name.lower() or "equipe" in file_name.lower() or "spirit" in file_name.lower() or "tidebound" in file_name.lower():
        # Extrair informações sobre equipes
        team_patterns = [
            (r'(team\s+\w+|equipe\s+\w+)', "team_name"),
            (r'winrate\s+(\d+\.?\d*%?)', "team_winrate"),
            (r'(vitórias|victories|wins)\s+(\d+)', "team_wins"),
            (r'(derrotas|losses)\s+(\d+)', "team_losses")
        ]
        
        for pattern, key in team_patterns:
            matches = re.findall(pattern, content.lower())
            for match in matches:
                team_info = {
                    "type": "team_data",
                    "file": file_name,
                    "data_type": key,
                    "value": match
                }
                md_info.append(team_info)
    
    # Limitar a quantidade de informações para arquivos muito grandes
    if len(md_info) > 1000:
        print(f"Limitando informações de {file_path} para 1000 itens")
        return md_info[:1000]
    
    return md_info

# Processar todos os arquivos markdown
md_files = [f for f in os.listdir(upload_dir) if f.endswith('.md')]
for md_file in md_files:
    file_path = os.path.join(upload_dir, md_file)
    print(f"Processando {file_path}...")
    md_info = extract_md_info(file_path)
    all_md_data.extend(md_info)
    print(f"Extraídas {len(md_info)} informações de {file_path}")

# Salvar os dados extraídos em um arquivo JSON
output_file = os.path.join(output_dir, 'markdown_extracted_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_md_data, f, ensure_ascii=False, indent=2)

print(f"Total de {len(all_md_data)} informações extraídas dos arquivos markdown")
print(f"Dados salvos em {output_file}")
