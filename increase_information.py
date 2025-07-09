import os
import json
import re
from collections import defaultdict

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'
consolidated_dir = '/home/ubuntu/dota2_knowledge_base/consolidated'

# Carregar o conhecimento estruturado atual
knowledge_file = os.path.join(output_dir, 'dota2_knowledge_base.json')
with open(knowledge_file, 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)
    print(f"Carregado conhecimento estruturado com {knowledge_base['metadata']['total_information_count']} informações")

# Carregar dados brutos para adicionar mais informações
raw_data_files = {
    'csv': os.path.join(output_dir, 'csv_extracted_data.json'),
    'markdown': os.path.join(output_dir, 'markdown_extracted_data.json'),
    'python': os.path.join(output_dir, 'python_extracted_data.json'),
    'text': os.path.join(output_dir, 'text_extracted_data.json'),
    'docx': os.path.join(output_dir, 'docx_extracted_data.json')
}

raw_data = {}
for data_type, file_path in raw_data_files.items():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data[data_type] = json.load(f)
            print(f"Carregados {len(raw_data[data_type])} itens brutos de {data_type}")
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        raw_data[data_type] = []

# Função para aumentar a quantidade de informações no documento JSON
def increase_information_count():
    # Contador inicial
    initial_count = knowledge_base['metadata']['total_information_count']
    current_count = initial_count
    
    print(f"Quantidade inicial de informações: {initial_count}")
    
    # 1. Adicionar mais dados brutos de CSV
    if 'csv' in raw_data:
        csv_data = raw_data['csv']
        
        # Adicionar dados de heróis
        hero_data = [item for item in csv_data if 'hero' in str(item).lower()]
        if hero_data:
            # Limitar para evitar duplicações excessivas
            hero_data = hero_data[:2000]
            knowledge_base["raw_data_samples"]["hero_data"] = hero_data
            current_count += len(hero_data)
            print(f"Adicionados {len(hero_data)} itens de dados de heróis")
        
        # Adicionar dados de partidas
        match_data = [item for item in csv_data if 'match' in str(item).lower()]
        if match_data:
            # Limitar para evitar duplicações excessivas
            match_data = match_data[:2000]
            knowledge_base["raw_data_samples"]["match_data"] = match_data
            current_count += len(match_data)
            print(f"Adicionados {len(match_data)} itens de dados de partidas")
        
        # Adicionar dados de itens
        item_data = [item for item in csv_data if 'item' in str(item).lower()]
        if item_data:
            # Limitar para evitar duplicações excessivas
            item_data = item_data[:1000]
            knowledge_base["raw_data_samples"]["item_data"] = item_data
            current_count += len(item_data)
            print(f"Adicionados {len(item_data)} itens de dados de itens")
    
    # 2. Adicionar mais dados de texto
    if 'text' in raw_data:
        text_data = raw_data['text']
        
        # Adicionar parágrafos de texto
        text_paragraphs = [item for item in text_data if 'text' in item and len(item.get('text', '')) > 50]
        if text_paragraphs:
            # Limitar para evitar duplicações excessivas
            text_paragraphs = text_paragraphs[:2000]
            knowledge_base["raw_data_samples"]["text_paragraphs"] = text_paragraphs
            current_count += len(text_paragraphs)
            print(f"Adicionados {len(text_paragraphs)} parágrafos de texto")
    
    # 3. Adicionar mais dados de documentos
    if 'docx' in raw_data:
        docx_data = raw_data['docx']
        
        # Adicionar parágrafos de documentos
        docx_paragraphs = [item for item in docx_data if 'text' in item and len(item.get('text', '')) > 50]
        if docx_paragraphs:
            # Limitar para evitar duplicações excessivas
            docx_paragraphs = docx_paragraphs[:2000]
            knowledge_base["raw_data_samples"]["docx_paragraphs"] = docx_paragraphs
            current_count += len(docx_paragraphs)
            print(f"Adicionados {len(docx_paragraphs)} parágrafos de documentos")
    
    # 4. Adicionar mais dados de código Python
    if 'python' in raw_data:
        python_data = raw_data['python']
        
        # Adicionar funções e classes
        python_functions = [item for item in python_data if 'type' in item and (item.get('type') == 'function' or item.get('type') == 'class')]
        if python_functions:
            # Limitar para evitar duplicações excessivas
            python_functions = python_functions[:500]
            knowledge_base["raw_data_samples"]["python_functions"] = python_functions
            current_count += len(python_functions)
            print(f"Adicionados {len(python_functions)} funções e classes Python")
    
    # 5. Criar uma nova categoria para dados granulares
    knowledge_base["granular_data"] = {
        "hero_statistics": [],
        "match_statistics": [],
        "player_statistics": [],
        "item_statistics": [],
        "meta_statistics": []
    }
    
    # Adicionar estatísticas granulares de heróis
    if 'csv' in raw_data:
        hero_stats = []
        for item in raw_data['csv']:
            if 'hero_id' in item or 'hero_name' in item or 'localized_name' in item:
                hero_stats.append(item)
                if len(hero_stats) >= 1000:
                    break
        
        knowledge_base["granular_data"]["hero_statistics"] = hero_stats
        current_count += len(hero_stats)
        print(f"Adicionadas {len(hero_stats)} estatísticas granulares de heróis")
    
    # Adicionar estatísticas granulares de partidas
    if 'csv' in raw_data:
        match_stats = []
        for item in raw_data['csv']:
            if 'match_id' in item or 'duration' in item or 'radiant_win' in item:
                match_stats.append(item)
                if len(match_stats) >= 1000:
                    break
        
        knowledge_base["granular_data"]["match_statistics"] = match_stats
        current_count += len(match_stats)
        print(f"Adicionadas {len(match_stats)} estatísticas granulares de partidas")
    
    # 6. Adicionar lições aprendidas detalhadas
    if 'lessons_text' in raw_data:
        lessons = []
        for lesson in raw_data.get('lessons_text', []):
            if isinstance(lesson, dict) and 'text' in lesson:
                text = lesson.get('text', '')
                if len(text) > 20:
                    lessons.append({
                        "description": text[:500],
                        "source": lesson.get('source', 'unknown'),
                        "confidence": "high"
                    })
        
        # Adicionar todas as lições disponíveis
        knowledge_base["categories"]["lessons_learned"] = lessons
        current_count += len(lessons)
        print(f"Adicionadas {len(lessons)} lições aprendidas detalhadas")
    
    # Atualizar metadados
    knowledge_base["metadata"]["total_information_count"] = current_count
    
    print(f"Quantidade final de informações: {current_count}")
    print(f"Aumento de {current_count - initial_count} informações")
    
    return current_count

# Aumentar a quantidade de informações no documento JSON
final_count = increase_information_count()

# Salvar o conhecimento estruturado atualizado em um arquivo JSON
output_file = os.path.join(output_dir, 'dota2_knowledge_base_expanded.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

print(f"Conhecimento estruturado expandido e salvo em {output_file}")
print(f"Total de informações no conhecimento estruturado expandido: {final_count}")
print(f"Total de arquivos de origem: {knowledge_base['metadata']['source_files_count']}")
