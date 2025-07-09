import os
import json
import re
from collections import defaultdict

# Diretórios onde os dados extraídos estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'
consolidated_dir = '/home/ubuntu/dota2_knowledge_base/consolidated'

# Criar diretório para dados consolidados se não existir
os.makedirs(consolidated_dir, exist_ok=True)

# Carregar todos os dados extraídos
data_files = {
    'csv': os.path.join(output_dir, 'csv_extracted_data.json'),
    'markdown': os.path.join(output_dir, 'markdown_extracted_data.json'),
    'python': os.path.join(output_dir, 'python_extracted_data.json'),
    'text': os.path.join(output_dir, 'text_extracted_data.json'),
    'docx': os.path.join(output_dir, 'docx_extracted_data.json')
}

all_data = {}
for data_type, file_path in data_files.items():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_data[data_type] = json.load(f)
            print(f"Carregados {len(all_data[data_type])} itens de {data_type}")
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        all_data[data_type] = []

# Função para consolidar informações sobre APIs e coleta de dados
def consolidate_api_data_collection_info():
    api_info = {
        "apis": {
            "pandascore": {
                "endpoints": [],
                "parameters": [],
                "authentication": {},
                "rate_limits": [],
                "examples": []
            },
            "opendota": {
                "endpoints": [],
                "parameters": [],
                "authentication": {},
                "rate_limits": [],
                "examples": []
            },
            "steam": {
                "endpoints": [],
                "parameters": [],
                "authentication": {},
                "rate_limits": [],
                "examples": []
            }
        },
        "data_collection": {
            "strategies": [],
            "best_practices": [],
            "filtering": [],
            "processing": [],
            "storage": []
        },
        "code_snippets": [],
        "source_files": []
    }
    
    # Palavras-chave para identificar informações sobre APIs e coleta de dados
    api_keywords = [
        'api', 'endpoint', 'request', 'response', 'parameter', 'authentication', 'token',
        'key', 'rate limit', 'pandascore', 'opendota', 'steam', 'http', 'json', 'rest'
    ]
    
    data_collection_keywords = [
        'collect', 'coletar', 'data', 'dados', 'filter', 'filtrar', 'process', 'processar',
        'store', 'armazenar', 'database', 'banco de dados', 'csv', 'json', 'excel'
    ]
    
    # Extrair informações sobre APIs e coleta de dados de todos os tipos de dados
    for data_type, data_list in all_data.items():
        for item in data_list:
            # Rastrear arquivos de origem
            if 'file' in item and item['file'] not in api_info['source_files']:
                if any(keyword in item['file'].lower() for keyword in api_keywords + data_collection_keywords):
                    api_info['source_files'].append(item['file'])
            
            # Extrair informações sobre endpoints de API
            if 'text' in item and 'api' in item.get('text', '').lower():
                text = item.get('text', '')
                
                # Identificar a qual API pertence
                api_name = None
                if 'pandascore' in text.lower():
                    api_name = 'pandascore'
                elif 'opendota' in text.lower():
                    api_name = 'opendota'
                elif 'steam' in text.lower():
                    api_name = 'steam'
                
                if api_name:
                    # Extrair endpoints
                    endpoint_match = re.search(r'(?:endpoint|url|route)\s*[:-]?\s*(?:https?://)?([^\s"\']+)', text.lower())
                    if endpoint_match:
                        endpoint = endpoint_match.group(1).strip()
                        
                        # Verificar se este endpoint já existe
                        exists = False
                        for existing_endpoint in api_info['apis'][api_name]['endpoints']:
                            if endpoint in existing_endpoint['path']:
                                exists = True
                                break
                        
                        if not exists:
                            endpoint_info = {
                                "path": endpoint,
                                "description": text[:300],
                                "source": f"{data_type}:{item.get('file', 'unknown')}"
                            }
                            api_info['apis'][api_name]['endpoints'].append(endpoint_info)
                    
                    # Extrair parâmetros
                    param_match = re.search(r'(?:parameter|param|parâmetro)\s*[:-]?\s*([^\s"\']+)', text.lower())
                    if param_match:
                        param = param_match.group(1).strip()
                        
                        # Verificar se este parâmetro já existe
                        exists = False
                        for existing_param in api_info['apis'][api_name]['parameters']:
                            if param in existing_param['name']:
                                exists = True
                                break
                        
                        if not exists:
                            param_info = {
                                "name": param,
                                "description": text[:300],
                                "source": f"{data_type}:{item.get('file', 'unknown')}"
                            }
                            api_info['apis'][api_name]['parameters'].append(param_info)
                    
                    # Extrair informações de autenticação
                    if 'authentication' in text.lower() or 'token' in text.lower() or 'key' in text.lower() or 'auth' in text.lower():
                        if 'authentication' not in api_info['apis'][api_name] or not api_info['apis'][api_name]['authentication']:
                            api_info['apis'][api_name]['authentication'] = {
                                "method": None,
                                "description": text[:300],
                                "source": f"{data_type}:{item.get('file', 'unknown')}"
                            }
                            
                            # Tentar extrair método de autenticação
                            auth_method_match = re.search(r'(?:authentication|auth)\s+(?:method|método)\s*[:-]?\s*([^\s"\'\.]+)', text.lower())
                            if auth_method_match:
                                api_info['apis'][api_name]['authentication']['method'] = auth_method_match.group(1).strip()
                    
                    # Extrair limites de taxa
                    if 'rate limit' in text.lower() or 'limite de taxa' in text.lower() or 'requests per' in text.lower():
                        rate_limit_info = {
                            "description": text[:300],
                            "source": f"{data_type}:{item.get('file', 'unknown')}"
                        }
                        
                        # Verificar se esta informação já existe
                        exists = False
                        for existing_rate_limit in api_info['apis'][api_name]['rate_limits']:
                            if text[:100] in existing_rate_limit['description']:
                                exists = True
                                break
                        
                        if not exists:
                            api_info['apis'][api_name]['rate_limits'].append(rate_limit_info)
            
            # Extrair exemplos de código para APIs
            if data_type == 'python' and 'api' in str(item).lower():
                api_name = None
                if 'pandascore' in str(item).lower():
                    api_name = 'pandascore'
                elif 'opendota' in str(item).lower():
                    api_name = 'opendota'
                elif 'steam' in str(item).lower():
                    api_name = 'steam'
                
                if api_name and ('code' in item or 'text' in item):
                    code = item.get('code', item.get('text', ''))
                    
                    if len(code) > 20:
                        example_info = {
                            "code": code[:500],
                            "source": f"{data_type}:{item.get('file', 'unknown')}"
                        }
                        
                        # Verificar se este exemplo já existe
                        exists = False
                        for existing_example in api_info['apis'][api_name]['examples']:
                            if code[:100] in existing_example['code']:
                                exists = True
                                break
                        
                        if not exists:
                            api_info['apis'][api_name]['examples'].append(example_info)
            
            # Extrair URLs de API
            if data_type == 'python' and 'type' in item and item.get('type') == 'api_url':
                url = item.get('url', '')
                
                if url:
                    api_name = None
                    if 'pandascore' in url.lower():
                        api_name = 'pandascore'
                    elif 'opendota' in url.lower():
                        api_name = 'opendota'
                    elif 'steamapi' in url.lower() or 'steampowered' in url.lower():
                        api_name = 'steam'
                    
                    if api_name:
                        endpoint_info = {
                            "path": url,
                            "description": f"URL extracted from code",
                            "source": f"{data_type}:{item.get('file', 'unknown')}"
                        }
                        
                        # Verificar se este endpoint já existe
                        exists = False
                        for existing_endpoint in api_info['apis'][api_name]['endpoints']:
                            if url in existing_endpoint['path']:
                                exists = True
                                break
                        
                        if not exists:
                            api_info['apis'][api_name]['endpoints'].append(endpoint_info)
            
            # Extrair chaves de API
            if data_type == 'python' and 'type' in item and item.get('type') == 'api_key':
                key = item.get('key', '')
                
                if key:
                    api_name = None
                    if 'pandascore' in str(item).lower() or 'efEXDM0DC_oKaesfsy3RBQ4MdXvnjGEfLTZNeZEOs4W5FMjoKbc' in key:
                        api_name = 'pandascore'
                    elif 'opendota' in str(item).lower() or '91fdee34-226f-4681-8f72-ee87bd85abcf' in key:
                        api_name = 'opendota'
                    elif 'steam' in str(item).lower() or '116EF013E6A8537842C3436DE9FD7007' in key:
                        api_name = 'steam'
                    
                    if api_name:
                        if 'authentication' not in api_info['apis'][api_name] or not api_info['apis'][api_name]['authentication']:
                            api_info['apis'][api_name]['authentication'] = {
                                "method": "api_key",
                                "key_example": key[:10] + "...",
                                "source": f"{data_type}:{item.get('file', 'unknown')}"
                            }
            
            # Extrair estratégias de coleta de dados
            if 'text' in item and any(keyword in item.get('text', '').lower() for keyword in data_collection_keywords):
                text = item.get('text', '')
                
                if len(text) > 50 and ('collect' in text.lower() or 'coletar' in text.lower() or 'strategy' in text.lower() or 'estratégia' in text.lower()):
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in api_info['data_collection']['strategies']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        api_info['data_collection']['strategies'].append(strategy_info)
            
            # Extrair melhores práticas para coleta de dados
            if 'text' in item and ('best practice' in item.get('text', '').lower() or 'melhor prática' in item.get('text', '').lower() or 'recommendation' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and any(keyword in text.lower() for keyword in data_collection_keywords):
                    practice_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}"
                    }
                    
                    # Verificar se esta prática já existe
                    exists = False
                    for existing_practice in api_info['data_collection']['best_practices']:
                        if text[:100] in existing_practice['description']:
                            exists = True
                            break
                    
                    if not exists:
                        api_info['data_collection']['best_practices'].append(practice_info)
            
            # Extrair informações sobre filtragem de dados
            if 'text' in item and ('filter' in item.get('text', '').lower() or 'filtrar' in item.get('text', '').lower() or 'filtering' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and 'data' in text.lower():
                    filter_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}"
                    }
                    
                    # Verificar se esta informação já existe
                    exists = False
                    for existing_filter in api_info['data_collection']['filtering']:
                        if text[:100] in existing_filter['description']:
                            exists = True
                            break
                    
                    if not exists:
                        api_info['data_collection']['filtering'].append(filter_info)
            
            # Extrair informações sobre processamento de dados
            if 'text' in item and ('process' in item.get('text', '').lower() or 'processar' in item.get('text', '').lower() or 'processing' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and 'data' in text.lower():
                    process_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}"
                    }
                    
                    # Verificar se esta informação já existe
                    exists = False
                    for existing_process in api_info['data_collection']['processing']:
                        if text[:100] in existing_process['description']:
                            exists = True
                            break
                    
                    if not exists:
                        api_info['data_collection']['processing'].append(process_info)
            
            # Extrair informações sobre armazenamento de dados
            if 'text' in item and ('store' in item.get('text', '').lower() or 'armazenar' in item.get('text', '').lower() or 'storage' in item.get('text', '').lower() or 'database' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and 'data' in text.lower():
                    storage_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}"
                    }
                    
                    # Verificar se esta informação já existe
                    exists = False
                    for existing_storage in api_info['data_collection']['storage']:
                        if text[:100] in existing_storage['description']:
                            exists = True
                            break
                    
                    if not exists:
                        api_info['data_collection']['storage'].append(storage_info)
            
            # Extrair snippets de código relevantes
            if data_type == 'python' and ('function' in item.get('type', '') or 'class' in item.get('type', '') or 'code_block' in item.get('type', '')):
                if 'name' in item or 'code' in item or 'text' in item:
                    name = item.get('name', '')
                    code = item.get('code', item.get('text', ''))
                    
                    if len(code) > 20 and any(keyword in (name + code).lower() for keyword in api_keywords + data_collection_keywords):
                        snippet_info = {
                            "name": name,
                            "code": code[:500],
                            "source": f"{data_type}:{item.get('file', 'unknown')}"
                        }
                        
                        # Verificar se este snippet já existe
                        exists = False
                        for existing_snippet in api_info['code_snippets']:
                            if code[:100] in existing_snippet['code']:
                                exists = True
                                break
                        
                        if not exists:
                            api_info['code_snippets'].append(snippet_info)
    
    # Limitar o número de itens em cada categoria para evitar duplicações
    for api_name in api_info['apis']:
        api_info['apis'][api_name]['endpoints'] = api_info['apis'][api_name]['endpoints'][:30]
        api_info['apis'][api_name]['parameters'] = api_info['apis'][api_name]['parameters'][:20]
        api_info['apis'][api_name]['rate_limits'] = api_info['apis'][api_name]['rate_limits'][:5]
        api_info['apis'][api_name]['examples'] = api_info['apis'][api_name]['examples'][:10]
    
    api_info['data_collection']['strategies'] = api_info['data_collection']['strategies'][:20]
    api_info['data_collection']['best_practices'] = api_info['data_collection']['best_practices'][:15]
    api_info['data_collection']['filtering'] = api_info['data_collection']['filtering'][:15]
    api_info['data_collection']['processing'] = api_info['data_collection']['processing'][:15]
    api_info['data_collection']['storage'] = api_info['data_collection']['storage'][:15]
    
    api_info['code_snippets'] = api_info['code_snippets'][:30]
    
    return api_info

# Consolidar informações sobre APIs e coleta de dados
api_info = consolidate_api_data_collection_info()

# Salvar as informações consolidadas sobre APIs e coleta de dados
output_file = os.path.join(consolidated_dir, 'api_data_collection_info.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(api_info, f, ensure_ascii=False, indent=2)

print(f"Informações sobre APIs e coleta de dados consolidadas e salvas em {output_file}")
print(f"Número de endpoints PandaScore: {len(api_info['apis']['pandascore']['endpoints'])}")
print(f"Número de endpoints OpenDota: {len(api_info['apis']['opendota']['endpoints'])}")
print(f"Número de endpoints Steam: {len(api_info['apis']['steam']['endpoints'])}")
print(f"Número de estratégias de coleta de dados: {len(api_info['data_collection']['strategies'])}")
print(f"Número de melhores práticas: {len(api_info['data_collection']['best_practices'])}")
print(f"Número de snippets de código: {len(api_info['code_snippets'])}")
print(f"Número de arquivos de origem: {len(api_info['source_files'])}")
