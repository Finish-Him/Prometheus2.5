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

# Processar o arquivo de lições aprendidas
try:
    # Verificar se o arquivo existe
    lessons_file = '/home/ubuntu/upload/Lições Aprendidas.docx'
    if os.path.exists(lessons_file):
        import docx2txt
        lessons_text = docx2txt.process(lessons_file)
        
        # Adicionar aos dados existentes como texto normal
        if 'lessons_text' not in all_data:
            all_data['lessons_text'] = []
        
        paragraphs = re.split(r'\n\s*\n', lessons_text)
        for para in paragraphs:
            if len(para.strip()) > 20:
                all_data['lessons_text'].append({"text": para.strip(), "source": "Lições Aprendidas.docx"})
        print(f"Extraídos {len(paragraphs)} parágrafos do arquivo de lições aprendidas")
except Exception as e:
    print(f"Erro ao processar arquivo de lições aprendidas: {e}")

# Função para consolidar informações sobre estratégias de apostas
def consolidate_betting_strategies():
    betting_info = {
        "general_strategies": [],
        "market_specific": {
            "match_winner": [],
            "handicap": [],
            "total_maps": [],
            "map_duration": [],
            "total_kills": [],
            "first_blood": [],
            "first_roshan": [],
            "first_tower": []
        },
        "odds_analysis": [],
        "value_betting": [],
        "live_betting": [],
        "bankroll_management": [],
        "risk_assessment": [],
        "team_specific": {},
        "tournament_specific": {},
        "source_files": []
    }
    
    # Palavras-chave para identificar informações sobre apostas
    betting_keywords = [
        'bet', 'aposta', 'odds', 'probability', 'probabilidade', 'stake', 'value', 'valor',
        'handicap', 'spread', 'over', 'under', 'mais de', 'menos de', 'winner', 'vencedor',
        'duration', 'duração', 'kills', 'abates', 'first blood', 'primeiro sangue',
        'roshan', 'tower', 'torre', 'bankroll', 'risk', 'risco', 'kelly', 'ev', 'roi'
    ]
    
    # Extrair informações sobre estratégias de apostas de todos os tipos de dados
    for data_type, data_list in all_data.items():
        for item in data_list:
            # Rastrear arquivos de origem
            if 'file' in item and item['file'] not in betting_info['source_files']:
                if any(keyword in item['file'].lower() for keyword in betting_keywords):
                    betting_info['source_files'].append(item['file'])
            
            # Extrair estratégias gerais de apostas
            if 'text' in item and any(keyword in item.get('text', '').lower() for keyword in betting_keywords):
                text = item.get('text', '')
                
                # Verificar se o texto é relevante para apostas
                if len(text) > 50 and ('strategy' in text.lower() or 'estratégia' in text.lower() or 'tip' in text.lower() or 'dica' in text.lower()):
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['general_strategies']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        strategy_info = {
                            "description": text[:500],  # Limitar tamanho do texto
                            "source": f"{data_type}:{item.get('file', 'unknown')}",
                            "confidence": "medium"  # Valor padrão
                        }
                        betting_info['general_strategies'].append(strategy_info)
            
            # Extrair estratégias específicas para diferentes mercados
            if 'text' in item:
                text = item.get('text', '').lower()
                
                # Match Winner
                if ('match winner' in text or 'vencedor da partida' in text or 'vencedor do jogo' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['match_winner']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['match_winner'].append(strategy_info)
                
                # Handicap
                if ('handicap' in text or 'spread' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['handicap']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['handicap'].append(strategy_info)
                
                # Total Maps
                if ('total maps' in text or 'total de mapas' in text or 'número de mapas' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['total_maps']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['total_maps'].append(strategy_info)
                
                # Map Duration
                if ('duration' in text or 'duração' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['map_duration']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['map_duration'].append(strategy_info)
                
                # Total Kills
                if ('total kills' in text or 'total de abates' in text or 'número de kills' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['total_kills']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['total_kills'].append(strategy_info)
                
                # First Blood
                if ('first blood' in text or 'primeiro sangue' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['first_blood']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['first_blood'].append(strategy_info)
                
                # First Roshan
                if ('first roshan' in text or 'primeiro roshan' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['first_roshan']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['first_roshan'].append(strategy_info)
                
                # First Tower
                if ('first tower' in text or 'primeira torre' in text) and len(text) > 50:
                    strategy_info = {
                        "description": text[:500],
                        "source": f"{data_type}:{item.get('file', 'unknown')}",
                        "confidence": "medium"
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['market_specific']['first_tower']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['market_specific']['first_tower'].append(strategy_info)
            
            # Extrair análises de odds
            if 'text' in item and ('odds' in item.get('text', '').lower() or 'probabilidade' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and ('analysis' in text.lower() or 'análise' in text.lower() or 'calculation' in text.lower() or 'cálculo' in text.lower()):
                    # Verificar se esta análise já existe
                    exists = False
                    for existing_analysis in betting_info['odds_analysis']:
                        if text[:100] in existing_analysis['description']:
                            exists = True
                            break
                    
                    if not exists:
                        analysis_info = {
                            "description": text[:500],
                            "source": f"{data_type}:{item.get('file', 'unknown')}",
                            "confidence": "medium"
                        }
                        betting_info['odds_analysis'].append(analysis_info)
            
            # Extrair informações sobre value betting
            if 'text' in item and ('value' in item.get('text', '').lower() or 'valor' in item.get('text', '').lower() or 'ev' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and ('bet' in text.lower() or 'aposta' in text.lower() or 'expected value' in text.lower() or 'valor esperado' in text.lower()):
                    # Verificar se esta informação já existe
                    exists = False
                    for existing_info in betting_info['value_betting']:
                        if text[:100] in existing_info['description']:
                            exists = True
                            break
                    
                    if not exists:
                        value_info = {
                            "description": text[:500],
                            "source": f"{data_type}:{item.get('file', 'unknown')}",
                            "confidence": "medium"
                        }
                        betting_info['value_betting'].append(value_info)
            
            # Extrair informações sobre apostas ao vivo
            if 'text' in item and ('live' in item.get('text', '').lower() or 'ao vivo' in item.get('text', '').lower() or 'in-play' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and ('bet' in text.lower() or 'aposta' in text.lower() or 'strategy' in text.lower() or 'estratégia' in text.lower()):
                    # Verificar se esta informação já existe
                    exists = False
                    for existing_info in betting_info['live_betting']:
                        if text[:100] in existing_info['description']:
                            exists = True
                            break
                    
                    if not exists:
                        live_info = {
                            "description": text[:500],
                            "source": f"{data_type}:{item.get('file', 'unknown')}",
                            "confidence": "medium"
                        }
                        betting_info['live_betting'].append(live_info)
            
            # Extrair informações sobre gestão de bankroll
            if 'text' in item and ('bankroll' in item.get('text', '').lower() or 'stake' in item.get('text', '').lower() or 'kelly' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and ('management' in text.lower() or 'gestão' in text.lower() or 'criterion' in text.lower() or 'critério' in text.lower()):
                    # Verificar se esta informação já existe
                    exists = False
                    for existing_info in betting_info['bankroll_management']:
                        if text[:100] in existing_info['description']:
                            exists = True
                            break
                    
                    if not exists:
                        bankroll_info = {
                            "description": text[:500],
                            "source": f"{data_type}:{item.get('file', 'unknown')}",
                            "confidence": "medium"
                        }
                        betting_info['bankroll_management'].append(bankroll_info)
            
            # Extrair informações sobre avaliação de risco
            if 'text' in item and ('risk' in item.get('text', '').lower() or 'risco' in item.get('text', '').lower() or 'volatility' in item.get('text', '').lower() or 'volatilidade' in item.get('text', '').lower()):
                text = item.get('text', '')
                
                if len(text) > 50 and ('assessment' in text.lower() or 'avaliação' in text.lower() or 'analysis' in text.lower() or 'análise' in text.lower()):
                    # Verificar se esta informação já existe
                    exists = False
                    for existing_info in betting_info['risk_assessment']:
                        if text[:100] in existing_info['description']:
                            exists = True
                            break
                    
                    if not exists:
                        risk_info = {
                            "description": text[:500],
                            "source": f"{data_type}:{item.get('file', 'unknown')}",
                            "confidence": "medium"
                        }
                        betting_info['risk_assessment'].append(risk_info)
            
            # Extrair estratégias específicas para equipes
            if 'text' in item and any(team in item.get('text', '').lower() for team in ['team spirit', 'team tidebound', 'aurora gaming', 'betboom team', 'xtreme gaming', 'tundra esports']):
                text = item.get('text', '')
                
                if len(text) > 50 and any(keyword in text.lower() for keyword in betting_keywords):
                    for team in ['team spirit', 'team tidebound', 'aurora gaming', 'betboom team', 'xtreme gaming', 'tundra esports']:
                        if team in text.lower():
                            # Normalizar nome da equipe
                            team_name = team.strip().lower()
                            
                            # Inicializar entrada da equipe se não existir
                            if team_name not in betting_info['team_specific']:
                                betting_info['team_specific'][team_name] = []
                            
                            # Verificar se esta informação já existe
                            exists = False
                            for existing_info in betting_info['team_specific'][team_name]:
                                if text[:100] in existing_info['description']:
                                    exists = True
                                    break
                            
                            if not exists:
                                team_info = {
                                    "description": text[:500],
                                    "source": f"{data_type}:{item.get('file', 'unknown')}",
                                    "confidence": "medium"
                                }
                                betting_info['team_specific'][team_name].append(team_info)
            
            # Extrair estratégias específicas para torneios
            if 'text' in item and any(tournament in item.get('text', '').lower() for tournament in ['pgl wallachia', 'wallachia season 4']):
                text = item.get('text', '')
                
                if len(text) > 50 and any(keyword in text.lower() for keyword in betting_keywords):
                    for tournament in ['pgl wallachia', 'wallachia season 4']:
                        if tournament in text.lower():
                            # Normalizar nome do torneio
                            tournament_name = tournament.strip().lower()
                            
                            # Inicializar entrada do torneio se não existir
                            if tournament_name not in betting_info['tournament_specific']:
                                betting_info['tournament_specific'][tournament_name] = []
                            
                            # Verificar se esta informação já existe
                            exists = False
                            for existing_info in betting_info['tournament_specific'][tournament_name]:
                                if text[:100] in existing_info['description']:
                                    exists = True
                                    break
                            
                            if not exists:
                                tournament_info = {
                                    "description": text[:500],
                                    "source": f"{data_type}:{item.get('file', 'unknown')}",
                                    "confidence": "medium"
                                }
                                betting_info['tournament_specific'][tournament_name].append(tournament_info)
    
    # Processar dados específicos das lições aprendidas
    if 'lessons_text' in all_data:
        for lesson in all_data['lessons_text']:
            if isinstance(lesson, dict) and 'text' in lesson:
                text = lesson.get('text', '')
                
                # Verificar se o texto é relevante para apostas
                if len(text) > 50 and any(keyword in text.lower() for keyword in betting_keywords):
                    # Adicionar como estratégia geral
                    strategy_info = {
                        "description": text[:500],
                        "source": lesson.get('source', 'Lições Aprendidas.docx'),
                        "confidence": "high"  # Maior confiança por ser de lições aprendidas
                    }
                    
                    # Verificar se esta estratégia já existe
                    exists = False
                    for existing_strategy in betting_info['general_strategies']:
                        if text[:100] in existing_strategy['description']:
                            exists = True
                            break
                    
                    if not exists:
                        betting_info['general_strategies'].append(strategy_info)
    
    # Limitar o número de itens em cada categoria para evitar duplicações
    betting_info['general_strategies'] = betting_info['general_strategies'][:50]
    betting_info['odds_analysis'] = betting_info['odds_analysis'][:30]
    betting_info['value_betting'] = betting_info['value_betting'][:30]
    betting_info['live_betting'] = betting_info['live_betting'][:30]
    betting_info['bankroll_management'] = betting_info['bankroll_management'][:20]
    betting_info['risk_assessment'] = betting_info['risk_assessment'][:20]
    
    for market in betting_info['market_specific']:
        betting_info['market_specific'][market] = betting_info['market_specific'][market][:20]
    
    for team in betting_info['team_specific']:
        betting_info['team_specific'][team] = betting_info['team_specific'][team][:15]
    
    for tournament in betting_info['tournament_specific']:
        betting_info['tournament_specific'][tournament] = betting_info['tournament_specific'][tournament][:15]
    
    return betting_info

# Consolidar informações sobre estratégias de apostas
betting_info = consolidate_betting_strategies()

# Salvar as informações consolidadas sobre estratégias de apostas
output_file = os.path.join(consolidated_dir, 'betting_strategies_info.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(betting_info, f, ensure_ascii=False, indent=2)

print(f"Informações sobre estratégias de apostas consolidadas e salvas em {output_file}")
print(f"Número de estratégias gerais: {len(betting_info['general_strategies'])}")
print(f"Número de análises de odds: {len(betting_info['odds_analysis'])}")
print(f"Número de estratégias de value betting: {len(betting_info['value_betting'])}")
print(f"Número de estratégias de apostas ao vivo: {len(betting_info['live_betting'])}")
print(f"Número de estratégias de gestão de bankroll: {len(betting_info['bankroll_management'])}")
print(f"Número de estratégias de avaliação de risco: {len(betting_info['risk_assessment'])}")
print(f"Número de equipes com estratégias específicas: {len(betting_info['team_specific'])}")
print(f"Número de torneios com estratégias específicas: {len(betting_info['tournament_specific'])}")
print(f"Número de arquivos de origem: {len(betting_info['source_files'])}")
