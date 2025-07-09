import os
import re
import json

# Diretório onde os arquivos Python estão localizados
upload_dir = '/home/ubuntu/upload'
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Lista para armazenar todas as informações extraídas
all_py_data = []

# Função para extrair informações de um arquivo Python
def extract_py_info(file_path):
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
    file_name = os.path.basename(file_path).replace('.py', '')
    
    # Lista para armazenar informações deste arquivo Python
    py_info = []
    
    # Adicionar metadados do arquivo
    py_info.append({
        "type": "python_metadata",
        "file": file_name,
        "length": len(content),
        "source": "upload_directory"
    })
    
    # Extrair importações
    imports = re.findall(r'^(?:import|from)\s+([^\n]+)', content, re.MULTILINE)
    for i, imp in enumerate(imports):
        import_info = {
            "type": "python_import",
            "file": file_name,
            "import_index": i,
            "statement": imp.strip()
        }
        py_info.append(import_info)
    
    # Extrair definições de funções
    functions = re.findall(r'^def\s+([^\(]+)\(([^\)]*)\)(?:\s*->\s*([^\:]+))?\s*:', content, re.MULTILINE)
    for i, (name, params, return_type) in enumerate(functions):
        function_info = {
            "type": "python_function",
            "file": file_name,
            "function_index": i,
            "name": name.strip(),
            "parameters": params.strip(),
            "return_type": return_type.strip() if return_type else None
        }
        py_info.append(function_info)
    
    # Extrair definições de classes
    classes = re.findall(r'^class\s+([^\(:\s]+)(?:\(([^\)]*)\))?\s*:', content, re.MULTILINE)
    for i, (name, parents) in enumerate(classes):
        class_info = {
            "type": "python_class",
            "file": file_name,
            "class_index": i,
            "name": name.strip(),
            "parents": parents.strip() if parents else None
        }
        py_info.append(class_info)
    
    # Extrair comentários de documentação (docstrings) - versão simplificada
    docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)
    for i, doc in enumerate(docstrings):
        if len(doc.strip()) > 10:  # Ignorar docstrings muito curtos
            docstring_info = {
                "type": "python_docstring",
                "file": file_name,
                "docstring_index": i,
                "text": doc.strip()[:500]  # Limitar tamanho do texto
            }
            py_info.append(docstring_info)
    
    # Extrair comentários de linha única
    line_comments = re.findall(r'^\s*#\s*(.+)$', content, re.MULTILINE)
    for i, comment in enumerate(line_comments):
        if len(comment.strip()) > 10:  # Ignorar comentários muito curtos
            comment_info = {
                "type": "python_comment",
                "file": file_name,
                "comment_index": i,
                "text": comment.strip()
            }
            py_info.append(comment_info)
    
    # Extrair URLs e endpoints
    urls = re.findall(r'(?:http|https)://[^\s\'"]+', content)
    for i, url in enumerate(urls):
        url_info = {
            "type": "api_url",
            "file": file_name,
            "url_index": i,
            "url": url.strip('"\'')
        }
        py_info.append(url_info)
    
    # Extrair chaves de API
    api_keys = re.findall(r'(?:api_key|key|token|auth)[\s]*=[\s]*[\'"]([^\'"]+)[\'"]', content)
    for i, key in enumerate(api_keys):
        if len(key) > 8:  # Ignorar chaves muito curtas
            key_info = {
                "type": "api_key",
                "file": file_name,
                "key_index": i,
                "key": key
            }
            py_info.append(key_info)
    
    # Limitar a quantidade de informações para arquivos muito grandes
    if len(py_info) > 500:
        print(f"Limitando informações de {file_path} para 500 itens")
        return py_info[:500]
    
    return py_info

# Processar todos os arquivos Python
py_files = [f for f in os.listdir(upload_dir) if f.endswith('.py')]
for py_file in py_files:
    file_path = os.path.join(upload_dir, py_file)
    print(f"Processando {file_path}...")
    py_info = extract_py_info(file_path)
    all_py_data.extend(py_info)
    print(f"Extraídas {len(py_info)} informações de {file_path}")

# Salvar os dados extraídos em um arquivo JSON
output_file = os.path.join(output_dir, 'python_extracted_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_py_data, f, ensure_ascii=False, indent=2)

print(f"Total de {len(all_py_data)} informações extraídas dos arquivos Python")
print(f"Dados salvos em {output_file}")
