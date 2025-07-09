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

# Função para extrair informações sobre o meta atual
def consolidate_meta_info():
    meta_info = {
        "patch_info": [],
        "heroes": {
            "popular": [],
            "high_winrate": [],
            "low_winrate": [],
            "most_banned": [],
            "by_position": {
                "position_1": [],
                "position_2": [],
                "position_3": [],
                "position_4": [],
                "position_5": []
            },
            "by_attribute": {
                "strength": [],
                "agility": [],
                "intelligence": []
            }
        },
        "items": {
            "popular": [],
            "high_winrate": [],
            "by_hero_type": {}
        },
        "strategies": [],
        "meta_trends": [],
        "source_files": []
    }
    
    # Palavras-chave para identificar informações sobre o meta
    meta_keywords = [
        'meta', 'patch', 'version', 'update', 'hero', 'item', 'popular', 'winrate', 
        'pick rate', 'ban rate', 'strategy', 'trend', 'position', 'role', 'lane',
        'carry', 'mid', 'offlane', 'support', 'hard support', 'strength', 'agility', 
        'intelligence', 'attribute', 'counter', 'synergy', 'combo', 'build'
    ]
    
    # Extrair informações sobre o meta de todos os tipos de dados
    for data_type, data_list in all_data.items():
        for item in data_list:
            # Rastrear arquivos de origem
            if 'file' in item and item['file'] not in meta_info['source_files']:
                if any(keyword in item['file'].lower() for keyword in ['meta', 'patch', 'hero', 'item']):
                    meta_info['source_files'].append(item['file'])
            
            # Extrair informações sobre o patch
            if 'patch' in str(item).lower() or 'version' in str(item).lower():
                patch_match = re.search(r'(?:patch|version)\s*(\d+\.\d+\w*)', str(item).lower())
                if patch_match and patch_match.group(1) not in [p.get('version') for p in meta_info['patch_info']]:
                    meta_info['patch_info'].append({
                        "version": patch_match.group(1),
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
            
            # Extrair informações sobre heróis populares
            if 'hero' in str(item).lower() and ('popular' in str(item).lower() or 'pick' in str(item).lower()):
                hero_name = None
                pick_rate = None
                
                # Tentar extrair nome do herói
                if item.get('type') == 'hero_data' and 'localized_name' in item:
                    hero_name = item.get('localized_name')
                elif 'hero_name' in item:
                    hero_name = item.get('hero_name')
                elif 'value' in item and item.get('data_type') == 'hero_name':
                    hero_name = item.get('value')
                
                # Tentar extrair taxa de pick
                if 'pick_rate' in item:
                    pick_rate = item.get('pick_rate')
                elif 'value' in item and item.get('data_type') == 'pick_rate':
                    pick_rate = item.get('value')
                
                if hero_name and hero_name not in [h.get('name') for h in meta_info['heroes']['popular']]:
                    meta_info['heroes']['popular'].append({
                        "name": hero_name,
                        "pick_rate": pick_rate,
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
            
            # Extrair informações sobre heróis com alta taxa de vitória
            if 'hero' in str(item).lower() and 'winrate' in str(item).lower():
                hero_name = None
                winrate = None
                
                # Tentar extrair nome do herói
                if item.get('type') == 'hero_data' and 'localized_name' in item:
                    hero_name = item.get('localized_name')
                elif 'hero_name' in item:
                    hero_name = item.get('hero_name')
                elif 'value' in item and item.get('data_type') == 'hero_name':
                    hero_name = item.get('value')
                
                # Tentar extrair taxa de vitória
                if 'winrate' in item:
                    winrate = item.get('winrate')
                elif 'value' in item and item.get('data_type') == 'winrate':
                    winrate = item.get('value')
                
                if hero_name and winrate:
                    # Converter winrate para float se possível
                    try:
                        winrate_value = float(str(winrate).replace('%', ''))
                        if winrate_value > 50:
                            if hero_name not in [h.get('name') for h in meta_info['heroes']['high_winrate']]:
                                meta_info['heroes']['high_winrate'].append({
                                    "name": hero_name,
                                    "winrate": winrate,
                                    "source": item.get('file', 'unknown'),
                                    "data_type": data_type
                                })
                        elif winrate_value < 45:
                            if hero_name not in [h.get('name') for h in meta_info['heroes']['low_winrate']]:
                                meta_info['heroes']['low_winrate'].append({
                                    "name": hero_name,
                                    "winrate": winrate,
                                    "source": item.get('file', 'unknown'),
                                    "data_type": data_type
                                })
                    except:
                        pass
            
            # Extrair informações sobre heróis mais banidos
            if 'hero' in str(item).lower() and 'ban' in str(item).lower():
                hero_name = None
                ban_rate = None
                
                # Tentar extrair nome do herói
                if item.get('type') == 'hero_data' and 'localized_name' in item:
                    hero_name = item.get('localized_name')
                elif 'hero_name' in item:
                    hero_name = item.get('hero_name')
                elif 'value' in item and item.get('data_type') == 'hero_name':
                    hero_name = item.get('value')
                
                # Tentar extrair taxa de ban
                if 'ban_rate' in item:
                    ban_rate = item.get('ban_rate')
                elif 'value' in item and item.get('data_type') == 'ban_rate':
                    ban_rate = item.get('value')
                
                if hero_name and ban_rate and hero_name not in [h.get('name') for h in meta_info['heroes']['most_banned']]:
                    meta_info['heroes']['most_banned'].append({
                        "name": hero_name,
                        "ban_rate": ban_rate,
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
            
            # Extrair informações sobre heróis por posição
            if 'hero' in str(item).lower() and ('position' in str(item).lower() or 'role' in str(item).lower() or 'lane' in str(item).lower()):
                hero_name = None
                position = None
                
                # Tentar extrair nome do herói
                if item.get('type') == 'hero_data' and 'localized_name' in item:
                    hero_name = item.get('localized_name')
                elif 'hero_name' in item:
                    hero_name = item.get('hero_name')
                elif 'value' in item and item.get('data_type') == 'hero_name':
                    hero_name = item.get('value')
                
                # Tentar extrair posição
                position_match = re.search(r'(?:position|role|lane)\s*(\d)', str(item).lower())
                if position_match:
                    position = f"position_{position_match.group(1)}"
                elif 'carry' in str(item).lower():
                    position = 'position_1'
                elif 'mid' in str(item).lower():
                    position = 'position_2'
                elif 'offlane' in str(item).lower():
                    position = 'position_3'
                elif 'support' in str(item).lower() and 'hard' not in str(item).lower():
                    position = 'position_4'
                elif 'hard support' in str(item).lower() or 'hard_support' in str(item).lower():
                    position = 'position_5'
                
                if hero_name and position and hero_name not in [h.get('name') for h in meta_info['heroes']['by_position'][position]]:
                    meta_info['heroes']['by_position'][position].append({
                        "name": hero_name,
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
            
            # Extrair informações sobre heróis por atributo
            if 'hero' in str(item).lower() and ('attribute' in str(item).lower() or 'strength' in str(item).lower() or 'agility' in str(item).lower() or 'intelligence' in str(item).lower()):
                hero_name = None
                attribute = None
                
                # Tentar extrair nome do herói
                if item.get('type') == 'hero_data' and 'localized_name' in item:
                    hero_name = item.get('localized_name')
                elif 'hero_name' in item:
                    hero_name = item.get('hero_name')
                elif 'value' in item and item.get('data_type') == 'hero_name':
                    hero_name = item.get('value')
                
                # Tentar extrair atributo
                if 'primary_attr' in item:
                    attribute = item.get('primary_attr')
                elif 'strength' in str(item).lower():
                    attribute = 'strength'
                elif 'agility' in str(item).lower():
                    attribute = 'agility'
                elif 'intelligence' in str(item).lower():
                    attribute = 'intelligence'
                
                if hero_name and attribute and attribute in meta_info['heroes']['by_attribute'] and hero_name not in [h.get('name') for h in meta_info['heroes']['by_attribute'][attribute]]:
                    meta_info['heroes']['by_attribute'][attribute].append({
                        "name": hero_name,
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
            
            # Extrair informações sobre itens populares
            if 'item' in str(item).lower() and ('popular' in str(item).lower() or 'common' in str(item).lower()):
                item_name = None
                
                # Tentar extrair nome do item
                if item.get('type') == 'item_data' and 'name' in item:
                    item_name = item.get('name')
                elif 'item_name' in item:
                    item_name = item.get('item_name')
                elif 'value' in item and item.get('data_type') == 'item_name':
                    item_name = item.get('value')
                
                if item_name and item_name not in [i.get('name') for i in meta_info['items']['popular']]:
                    meta_info['items']['popular'].append({
                        "name": item_name,
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
            
            # Extrair informações sobre estratégias
            if 'strategy' in str(item).lower() or 'tactic' in str(item).lower() or 'playstyle' in str(item).lower():
                strategy_text = None
                
                # Tentar extrair texto da estratégia
                if 'text' in item and len(item.get('text', '')) > 20:
                    strategy_text = item.get('text')
                
                if strategy_text and strategy_text not in [s.get('description') for s in meta_info['strategies']]:
                    meta_info['strategies'].append({
                        "description": strategy_text,
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
            
            # Extrair informações sobre tendências do meta
            if 'trend' in str(item).lower() or 'meta' in str(item).lower():
                trend_text = None
                
                # Tentar extrair texto da tendência
                if 'text' in item and len(item.get('text', '')) > 20:
                    trend_text = item.get('text')
                
                if trend_text and trend_text not in [t.get('description') for t in meta_info['meta_trends']]:
                    meta_info['meta_trends'].append({
                        "description": trend_text,
                        "source": item.get('file', 'unknown'),
                        "data_type": data_type
                    })
    
    # Limitar o número de itens em cada categoria para evitar duplicações
    for category in ['popular', 'high_winrate', 'low_winrate', 'most_banned']:
        meta_info['heroes'][category] = meta_info['heroes'][category][:50]
    
    for position in meta_info['heroes']['by_position']:
        meta_info['heroes']['by_position'][position] = meta_info['heroes']['by_position'][position][:20]
    
    for attribute in meta_info['heroes']['by_attribute']:
        meta_info['heroes']['by_attribute'][attribute] = meta_info['heroes']['by_attribute'][attribute][:30]
    
    meta_info['items']['popular'] = meta_info['items']['popular'][:50]
    meta_info['strategies'] = meta_info['strategies'][:30]
    meta_info['meta_trends'] = meta_info['meta_trends'][:30]
    
    return meta_info

# Consolidar informações sobre o meta atual
meta_info = consolidate_meta_info()

# Salvar as informações consolidadas sobre o meta atual
output_file = os.path.join(consolidated_dir, 'meta_info.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(meta_info, f, ensure_ascii=False, indent=2)

print(f"Informações sobre o meta atual consolidadas e salvas em {output_file}")
print(f"Número de heróis populares: {len(meta_info['heroes']['popular'])}")
print(f"Número de heróis com alta taxa de vitória: {len(meta_info['heroes']['high_winrate'])}")
print(f"Número de heróis com baixa taxa de vitória: {len(meta_info['heroes']['low_winrate'])}")
print(f"Número de heróis mais banidos: {len(meta_info['heroes']['most_banned'])}")
print(f"Número de estratégias: {len(meta_info['strategies'])}")
print(f"Número de tendências do meta: {len(meta_info['meta_trends'])}")
print(f"Número de arquivos de origem: {len(meta_info['source_files'])}")
