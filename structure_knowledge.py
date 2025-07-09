import os
import json
import re
from collections import defaultdict

# Diretórios onde os dados consolidados estão localizados
consolidated_dir = '/home/ubuntu/dota2_knowledge_base/consolidated'
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Carregar todos os dados consolidados
consolidated_files = {
    'meta': os.path.join(consolidated_dir, 'meta_info.json'),
    'teams_players': os.path.join(consolidated_dir, 'teams_players_info.json'),
    'betting': os.path.join(consolidated_dir, 'betting_strategies_info.json'),
    'api': os.path.join(consolidated_dir, 'api_data_collection_info.json')
}

all_consolidated_data = {}
for data_type, file_path in consolidated_files.items():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_consolidated_data[data_type] = json.load(f)
            print(f"Carregados dados consolidados de {data_type}")
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        all_consolidated_data[data_type] = {}

# Carregar dados brutos para complementar
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
            print(f"Carregados dados brutos de {data_type}")
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        raw_data[data_type] = []

# Função para estruturar todo o conhecimento em formato JSON
def structure_all_knowledge():
    # Estrutura principal do conhecimento
    knowledge_base = {
        "metadata": {
            "version": "1.0",
            "date": "2025-04-26",
            "description": "Base de conhecimento abrangente sobre Dota 2 para análise preditiva e apostas",
            "source_files_count": 0,
            "total_information_count": 0
        },
        "categories": {
            "meta_game": {
                "patch_info": [],
                "heroes": {
                    "popular": [],
                    "high_winrate": [],
                    "low_winrate": [],
                    "most_banned": [],
                    "by_position": {},
                    "by_attribute": {}
                },
                "items": {
                    "popular": [],
                    "high_winrate": []
                },
                "strategies": [],
                "meta_trends": []
            },
            "teams_players": {
                "teams": {},
                "players": {},
                "tournaments": {},
                "matchups": [],
                "team_stats": {}
            },
            "betting": {
                "general_strategies": [],
                "market_specific": {},
                "odds_analysis": [],
                "value_betting": [],
                "live_betting": [],
                "bankroll_management": [],
                "risk_assessment": [],
                "team_specific": {},
                "tournament_specific": {}
            },
            "data_collection": {
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
                "strategies": [],
                "best_practices": [],
                "filtering": [],
                "processing": [],
                "storage": []
            },
            "lessons_learned": []
        },
        "raw_data_samples": {
            "csv": [],
            "markdown": [],
            "python": [],
            "text": [],
            "docx": []
        }
    }
    
    # Contador de informações
    info_count = 0
    source_files = set()
    
    # Incorporar informações sobre o meta atual
    if 'meta' in all_consolidated_data:
        meta_data = all_consolidated_data['meta']
        
        # Patch info
        knowledge_base["categories"]["meta_game"]["patch_info"] = meta_data.get("patch_info", [])
        info_count += len(meta_data.get("patch_info", []))
        
        # Heroes
        for category in ["popular", "high_winrate", "low_winrate", "most_banned"]:
            knowledge_base["categories"]["meta_game"]["heroes"][category] = meta_data.get("heroes", {}).get(category, [])
            info_count += len(meta_data.get("heroes", {}).get(category, []))
        
        # Heroes by position and attribute
        knowledge_base["categories"]["meta_game"]["heroes"]["by_position"] = meta_data.get("heroes", {}).get("by_position", {})
        knowledge_base["categories"]["meta_game"]["heroes"]["by_attribute"] = meta_data.get("heroes", {}).get("by_attribute", {})
        
        for position in meta_data.get("heroes", {}).get("by_position", {}):
            info_count += len(meta_data.get("heroes", {}).get("by_position", {}).get(position, []))
        
        for attribute in meta_data.get("heroes", {}).get("by_attribute", {}):
            info_count += len(meta_data.get("heroes", {}).get("by_attribute", {}).get(attribute, []))
        
        # Items
        knowledge_base["categories"]["meta_game"]["items"]["popular"] = meta_data.get("items", {}).get("popular", [])
        knowledge_base["categories"]["meta_game"]["items"]["high_winrate"] = meta_data.get("items", {}).get("high_winrate", [])
        info_count += len(meta_data.get("items", {}).get("popular", []))
        info_count += len(meta_data.get("items", {}).get("high_winrate", []))
        
        # Strategies and trends
        knowledge_base["categories"]["meta_game"]["strategies"] = meta_data.get("strategies", [])
        knowledge_base["categories"]["meta_game"]["meta_trends"] = meta_data.get("meta_trends", [])
        info_count += len(meta_data.get("strategies", []))
        info_count += len(meta_data.get("meta_trends", []))
        
        # Source files
        for file in meta_data.get("source_files", []):
            source_files.add(file)
    
    # Incorporar informações sobre equipes e jogadores
    if 'teams_players' in all_consolidated_data:
        teams_players_data = all_consolidated_data['teams_players']
        
        # Teams
        knowledge_base["categories"]["teams_players"]["teams"] = teams_players_data.get("teams", {})
        info_count += len(teams_players_data.get("teams", {}))
        
        # Players
        knowledge_base["categories"]["teams_players"]["players"] = teams_players_data.get("players", {})
        info_count += len(teams_players_data.get("players", {}))
        
        # Tournaments
        knowledge_base["categories"]["teams_players"]["tournaments"] = teams_players_data.get("tournaments", {})
        info_count += len(teams_players_data.get("tournaments", {}))
        
        # Matchups
        knowledge_base["categories"]["teams_players"]["matchups"] = teams_players_data.get("matchups", [])
        info_count += len(teams_players_data.get("matchups", []))
        
        # Team stats
        knowledge_base["categories"]["teams_players"]["team_stats"] = teams_players_data.get("team_stats", {})
        info_count += len(teams_players_data.get("team_stats", {}))
        
        # Source files
        for file in teams_players_data.get("source_files", []):
            source_files.add(file)
    
    # Incorporar informações sobre estratégias de apostas
    if 'betting' in all_consolidated_data:
        betting_data = all_consolidated_data['betting']
        
        # General strategies
        knowledge_base["categories"]["betting"]["general_strategies"] = betting_data.get("general_strategies", [])
        info_count += len(betting_data.get("general_strategies", []))
        
        # Market specific
        knowledge_base["categories"]["betting"]["market_specific"] = betting_data.get("market_specific", {})
        for market in betting_data.get("market_specific", {}):
            info_count += len(betting_data.get("market_specific", {}).get(market, []))
        
        # Odds analysis
        knowledge_base["categories"]["betting"]["odds_analysis"] = betting_data.get("odds_analysis", [])
        info_count += len(betting_data.get("odds_analysis", []))
        
        # Value betting
        knowledge_base["categories"]["betting"]["value_betting"] = betting_data.get("value_betting", [])
        info_count += len(betting_data.get("value_betting", []))
        
        # Live betting
        knowledge_base["categories"]["betting"]["live_betting"] = betting_data.get("live_betting", [])
        info_count += len(betting_data.get("live_betting", []))
        
        # Bankroll management
        knowledge_base["categories"]["betting"]["bankroll_management"] = betting_data.get("bankroll_management", [])
        info_count += len(betting_data.get("bankroll_management", []))
        
        # Risk assessment
        knowledge_base["categories"]["betting"]["risk_assessment"] = betting_data.get("risk_assessment", [])
        info_count += len(betting_data.get("risk_assessment", []))
        
        # Team specific
        knowledge_base["categories"]["betting"]["team_specific"] = betting_data.get("team_specific", {})
        for team in betting_data.get("team_specific", {}):
            info_count += len(betting_data.get("team_specific", {}).get(team, []))
        
        # Tournament specific
        knowledge_base["categories"]["betting"]["tournament_specific"] = betting_data.get("tournament_specific", {})
        for tournament in betting_data.get("tournament_specific", {}):
            info_count += len(betting_data.get("tournament_specific", {}).get(tournament, []))
        
        # Source files
        for file in betting_data.get("source_files", []):
            source_files.add(file)
    
    # Incorporar informações sobre APIs e coleta de dados
    if 'api' in all_consolidated_data:
        api_data = all_consolidated_data['api']
        
        # APIs
        for api_name in ["pandascore", "opendota", "steam"]:
            # Endpoints
            knowledge_base["categories"]["data_collection"]["apis"][api_name]["endpoints"] = api_data.get("apis", {}).get(api_name, {}).get("endpoints", [])
            info_count += len(api_data.get("apis", {}).get(api_name, {}).get("endpoints", []))
            
            # Parameters
            knowledge_base["categories"]["data_collection"]["apis"][api_name]["parameters"] = api_data.get("apis", {}).get(api_name, {}).get("parameters", [])
            info_count += len(api_data.get("apis", {}).get(api_name, {}).get("parameters", []))
            
            # Authentication
            knowledge_base["categories"]["data_collection"]["apis"][api_name]["authentication"] = api_data.get("apis", {}).get(api_name, {}).get("authentication", {})
            if api_data.get("apis", {}).get(api_name, {}).get("authentication", {}):
                info_count += 1
            
            # Rate limits
            knowledge_base["categories"]["data_collection"]["apis"][api_name]["rate_limits"] = api_data.get("apis", {}).get(api_name, {}).get("rate_limits", [])
            info_count += len(api_data.get("apis", {}).get(api_name, {}).get("rate_limits", []))
            
            # Examples
            knowledge_base["categories"]["data_collection"]["apis"][api_name]["examples"] = api_data.get("apis", {}).get(api_name, {}).get("examples", [])
            info_count += len(api_data.get("apis", {}).get(api_name, {}).get("examples", []))
        
        # Data collection
        knowledge_base["categories"]["data_collection"]["strategies"] = api_data.get("data_collection", {}).get("strategies", [])
        info_count += len(api_data.get("data_collection", {}).get("strategies", []))
        
        knowledge_base["categories"]["data_collection"]["best_practices"] = api_data.get("data_collection", {}).get("best_practices", [])
        info_count += len(api_data.get("data_collection", {}).get("best_practices", []))
        
        knowledge_base["categories"]["data_collection"]["filtering"] = api_data.get("data_collection", {}).get("filtering", [])
        info_count += len(api_data.get("data_collection", {}).get("filtering", []))
        
        knowledge_base["categories"]["data_collection"]["processing"] = api_data.get("data_collection", {}).get("processing", [])
        info_count += len(api_data.get("data_collection", {}).get("processing", []))
        
        knowledge_base["categories"]["data_collection"]["storage"] = api_data.get("data_collection", {}).get("storage", [])
        info_count += len(api_data.get("data_collection", {}).get("storage", []))
        
        # Source files
        for file in api_data.get("source_files", []):
            source_files.add(file)
    
    # Adicionar lições aprendidas do arquivo específico
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
        
        # Limitar para evitar duplicações
        knowledge_base["categories"]["lessons_learned"] = lessons[:500]
        info_count += len(lessons[:500])
    
    # Adicionar amostras de dados brutos para cada tipo
    for data_type in raw_data:
        samples = []
        for i, item in enumerate(raw_data[data_type]):
            if i >= 1000:  # Limitar a 1000 amostras por tipo
                break
            samples.append(item)
        
        knowledge_base["raw_data_samples"][data_type] = samples
        info_count += len(samples)
    
    # Atualizar metadados
    knowledge_base["metadata"]["source_files_count"] = len(source_files)
    knowledge_base["metadata"]["total_information_count"] = info_count
    
    return knowledge_base, info_count

# Estruturar todo o conhecimento em formato JSON
knowledge_base, info_count = structure_all_knowledge()

# Salvar o conhecimento estruturado em um arquivo JSON
output_file = os.path.join(output_dir, 'dota2_knowledge_base.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

print(f"Conhecimento estruturado em formato JSON e salvo em {output_file}")
print(f"Total de informações no conhecimento estruturado: {info_count}")
print(f"Total de arquivos de origem: {knowledge_base['metadata']['source_files_count']}")
