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

# Processar o novo arquivo de lições aprendidas
try:
    # Verificar se o arquivo existe
    lessons_file = '/home/ubuntu/upload/Lições Aprendidas.docx'
    if os.path.exists(lessons_file):
        import docx2txt
        lessons_text = docx2txt.process(lessons_file)
        
        # Tentar extrair JSON do texto
        json_matches = re.findall(r'\{[\s\S]*\}', lessons_text)
        if json_matches:
            for json_text in json_matches:
                try:
                    lessons_data = json.loads(json_text)
                    print(f"Extraído JSON válido do arquivo de lições aprendidas")
                    
                    # Adicionar aos dados existentes
                    if 'lessons' not in all_data:
                        all_data['lessons'] = []
                    
                    if isinstance(lessons_data, list):
                        all_data['lessons'].extend(lessons_data)
                    elif isinstance(lessons_data, dict):
                        all_data['lessons'].append(lessons_data)
                except json.JSONDecodeError:
                    print(f"Texto encontrado não é um JSON válido, tratando como texto normal")
                    # Se não for um JSON válido, tratar como texto normal
                    if 'lessons_text' not in all_data:
                        all_data['lessons_text'] = []
                    all_data['lessons_text'].append({"text": json_text, "source": "Lições Aprendidas.docx"})
        else:
            # Se não encontrar JSON, processar como texto normal
            print(f"Processando arquivo de lições aprendidas como texto normal")
            paragraphs = re.split(r'\n\s*\n', lessons_text)
            if 'lessons_text' not in all_data:
                all_data['lessons_text'] = []
            for para in paragraphs:
                if len(para.strip()) > 20:
                    all_data['lessons_text'].append({"text": para.strip(), "source": "Lições Aprendidas.docx"})
            print(f"Extraídos {len(paragraphs)} parágrafos do arquivo de lições aprendidas")
except Exception as e:
    print(f"Erro ao processar arquivo de lições aprendidas: {e}")

# Função para consolidar informações sobre equipes e jogadores
def consolidate_teams_players_info():
    teams_players_info = {
        "teams": {},
        "players": {},
        "tournaments": {},
        "matchups": [],
        "team_stats": {},
        "player_stats": {},
        "source_files": []
    }
    
    # Palavras-chave para identificar informações sobre equipes e jogadores
    team_keywords = [
        'team', 'equipe', 'squad', 'roster', 'organization', 'org', 
        'spirit', 'tidebound', 'aurora', 'betboom', 'xtreme', 'tundra'
    ]
    
    player_keywords = [
        'player', 'jogador', 'pro', 'professional', 'profissional', 'carry', 
        'mid', 'offlane', 'support', 'captain', 'capitão'
    ]
    
    tournament_keywords = [
        'tournament', 'torneio', 'championship', 'campeonato', 'league', 'liga',
        'wallachia', 'pgl', 'major', 'minor', 'international', 'ti'
    ]
    
    # Extrair informações sobre equipes e jogadores de todos os tipos de dados
    for data_type, data_list in all_data.items():
        for item in data_list:
            # Rastrear arquivos de origem
            if 'file' in item and item['file'] not in teams_players_info['source_files']:
                if any(keyword in item['file'].lower() for keyword in team_keywords + player_keywords + tournament_keywords):
                    teams_players_info['source_files'].append(item['file'])
            
            # Extrair informações sobre equipes
            team_name = None
            
            # Tentar extrair nome da equipe
            if 'team_name' in item:
                team_name = item.get('team_name')
            elif 'value' in item and item.get('data_type') == 'team_name':
                team_name = item.get('value')
            elif 'text' in item and any(team in item.get('text', '').lower() for team in ['team spirit', 'team tidebound', 'aurora gaming', 'betboom team', 'xtreme gaming', 'tundra esports']):
                for team in ['team spirit', 'team tidebound', 'aurora gaming', 'betboom team', 'xtreme gaming', 'tundra esports']:
                    if team in item.get('text', '').lower():
                        team_name = team
                        break
            
            if team_name:
                # Normalizar nome da equipe
                team_name = team_name.strip().lower()
                if team_name.startswith('team '):
                    normalized_name = team_name
                else:
                    normalized_name = team_name
                
                # Inicializar entrada da equipe se não existir
                if normalized_name not in teams_players_info['teams']:
                    teams_players_info['teams'][normalized_name] = {
                        "name": normalized_name,
                        "aliases": [],
                        "players": [],
                        "region": None,
                        "achievements": [],
                        "sources": []
                    }
                
                # Adicionar fonte
                source = f"{data_type}:{item.get('file', 'unknown')}"
                if source not in teams_players_info['teams'][normalized_name]['sources']:
                    teams_players_info['teams'][normalized_name]['sources'].append(source)
                
                # Extrair informações adicionais sobre a equipe
                if 'text' in item:
                    # Região
                    region_match = re.search(r'(?:region|região)\s*[:-]?\s*(\w+)', item.get('text', '').lower())
                    if region_match and not teams_players_info['teams'][normalized_name]['region']:
                        teams_players_info['teams'][normalized_name]['region'] = region_match.group(1)
                    
                    # Conquistas
                    achievement_match = re.search(r'(?:achievement|conquista|won|venceu|champion|campeão)\s*[:-]?\s*(.+?)(?:\.|$)', item.get('text', '').lower())
                    if achievement_match:
                        achievement = achievement_match.group(1).strip()
                        if achievement and achievement not in teams_players_info['teams'][normalized_name]['achievements']:
                            teams_players_info['teams'][normalized_name]['achievements'].append(achievement)
            
            # Extrair informações sobre jogadores
            player_name = None
            
            # Tentar extrair nome do jogador
            if 'player_name' in item:
                player_name = item.get('player_name')
            elif 'value' in item and item.get('data_type') == 'player_name':
                player_name = item.get('value')
            
            if player_name:
                # Normalizar nome do jogador
                player_name = player_name.strip().lower()
                
                # Inicializar entrada do jogador se não existir
                if player_name not in teams_players_info['players']:
                    teams_players_info['players'][player_name] = {
                        "name": player_name,
                        "aliases": [],
                        "team": None,
                        "position": None,
                        "signature_heroes": [],
                        "sources": []
                    }
                
                # Adicionar fonte
                source = f"{data_type}:{item.get('file', 'unknown')}"
                if source not in teams_players_info['players'][player_name]['sources']:
                    teams_players_info['players'][player_name]['sources'].append(source)
                
                # Extrair informações adicionais sobre o jogador
                if 'text' in item:
                    # Equipe
                    team_match = re.search(r'(?:team|equipe)\s*[:-]?\s*(\w+)', item.get('text', '').lower())
                    if team_match and not teams_players_info['players'][player_name]['team']:
                        teams_players_info['players'][player_name]['team'] = team_match.group(1)
                    
                    # Posição
                    position_match = re.search(r'(?:position|posição|role|função)\s*[:-]?\s*(\d|carry|mid|offlane|support|hard support)', item.get('text', '').lower())
                    if position_match and not teams_players_info['players'][player_name]['position']:
                        teams_players_info['players'][player_name]['position'] = position_match.group(1)
                    
                    # Heróis assinatura
                    hero_match = re.search(r'(?:signature|assinatura|best|melhor)\s+(?:hero|herói)\s*[:-]?\s*(\w+)', item.get('text', '').lower())
                    if hero_match:
                        hero = hero_match.group(1).strip()
                        if hero and hero not in teams_players_info['players'][player_name]['signature_heroes']:
                            teams_players_info['players'][player_name]['signature_heroes'].append(hero)
            
            # Extrair informações sobre torneios
            tournament_name = None
            
            # Tentar extrair nome do torneio
            if 'tournament_name' in item:
                tournament_name = item.get('tournament_name')
            elif 'value' in item and item.get('data_type') == 'tournament_name':
                tournament_name = item.get('value')
            elif 'text' in item and any(tournament in item.get('text', '').lower() for tournament in ['pgl wallachia', 'wallachia season 4']):
                for tournament in ['pgl wallachia', 'wallachia season 4']:
                    if tournament in item.get('text', '').lower():
                        tournament_name = tournament
                        break
            
            if tournament_name:
                # Normalizar nome do torneio
                tournament_name = tournament_name.strip().lower()
                
                # Inicializar entrada do torneio se não existir
                if tournament_name not in teams_players_info['tournaments']:
                    teams_players_info['tournaments'][tournament_name] = {
                        "name": tournament_name,
                        "aliases": [],
                        "teams": [],
                        "dates": None,
                        "prize_pool": None,
                        "format": None,
                        "sources": []
                    }
                
                # Adicionar fonte
                source = f"{data_type}:{item.get('file', 'unknown')}"
                if source not in teams_players_info['tournaments'][tournament_name]['sources']:
                    teams_players_info['tournaments'][tournament_name]['sources'].append(source)
                
                # Extrair informações adicionais sobre o torneio
                if 'text' in item:
                    # Datas
                    date_match = re.search(r'(?:date|data|period|período)\s*[:-]?\s*(.+?)(?:\.|$)', item.get('text', '').lower())
                    if date_match and not teams_players_info['tournaments'][tournament_name]['dates']:
                        teams_players_info['tournaments'][tournament_name]['dates'] = date_match.group(1).strip()
                    
                    # Prize pool
                    prize_match = re.search(r'(?:prize|prêmio|pool)\s*[:-]?\s*(.+?)(?:\.|$)', item.get('text', '').lower())
                    if prize_match and not teams_players_info['tournaments'][tournament_name]['prize_pool']:
                        teams_players_info['tournaments'][tournament_name]['prize_pool'] = prize_match.group(1).strip()
                    
                    # Formato
                    format_match = re.search(r'(?:format|formato)\s*[:-]?\s*(.+?)(?:\.|$)', item.get('text', '').lower())
                    if format_match and not teams_players_info['tournaments'][tournament_name]['format']:
                        teams_players_info['tournaments'][tournament_name]['format'] = format_match.group(1).strip()
            
            # Extrair informações sobre confrontos diretos
            if 'text' in item and ('vs' in item.get('text', '').lower() or 'versus' in item.get('text', '').lower()):
                matchup_match = re.search(r'(team\s+\w+|aurora|betboom|xtreme|tundra)\s+(?:vs|versus)\s+(team\s+\w+|aurora|betboom|xtreme|tundra)', item.get('text', '').lower())
                if matchup_match:
                    team1 = matchup_match.group(1).strip()
                    team2 = matchup_match.group(2).strip()
                    
                    # Extrair resultado se disponível
                    result_match = re.search(r'(?:result|resultado|score|placar)\s*[:-]?\s*(\d+)\s*-\s*(\d+)', item.get('text', '').lower())
                    if result_match:
                        team1_score = int(result_match.group(1))
                        team2_score = int(result_match.group(2))
                        
                        matchup_info = {
                            "team1": team1,
                            "team2": team2,
                            "team1_score": team1_score,
                            "team2_score": team2_score,
                            "winner": team1 if team1_score > team2_score else team2,
                            "source": f"{data_type}:{item.get('file', 'unknown')}"
                        }
                        
                        # Verificar se este confronto já existe
                        exists = False
                        for existing_matchup in teams_players_info['matchups']:
                            if (existing_matchup['team1'] == team1 and existing_matchup['team2'] == team2 and
                                existing_matchup['team1_score'] == team1_score and existing_matchup['team2_score'] == team2_score):
                                exists = True
                                break
                        
                        if not exists:
                            teams_players_info['matchups'].append(matchup_info)
            
            # Extrair estatísticas de equipes
            if 'team' in str(item).lower() and ('stat' in str(item).lower() or 'winrate' in str(item).lower() or 'win rate' in str(item).lower()):
                team_name = None
                
                # Tentar extrair nome da equipe
                if 'team_name' in item:
                    team_name = item.get('team_name')
                elif 'value' in item and item.get('data_type') == 'team_name':
                    team_name = item.get('value')
                elif 'text' in item and any(team in item.get('text', '').lower() for team in ['team spirit', 'team tidebound', 'aurora gaming', 'betboom team', 'xtreme gaming', 'tundra esports']):
                    for team in ['team spirit', 'team tidebound', 'aurora gaming', 'betboom team', 'xtreme gaming', 'tundra esports']:
                        if team in item.get('text', '').lower():
                            team_name = team
                            break
                
                if team_name:
                    # Normalizar nome da equipe
                    team_name = team_name.strip().lower()
                    
                    # Inicializar estatísticas da equipe se não existirem
                    if team_name not in teams_players_info['team_stats']:
                        teams_players_info['team_stats'][team_name] = {
                            "team": team_name,
                            "overall_winrate": None,
                            "radiant_winrate": None,
                            "dire_winrate": None,
                            "average_game_duration": None,
                            "favorite_heroes": [],
                            "sources": []
                        }
                    
                    # Adicionar fonte
                    source = f"{data_type}:{item.get('file', 'unknown')}"
                    if source not in teams_players_info['team_stats'][team_name]['sources']:
                        teams_players_info['team_stats'][team_name]['sources'].append(source)
                    
                    # Extrair estatísticas específicas
                    if 'text' in item:
                        # Taxa de vitória geral
                        winrate_match = re.search(r'(?:overall\s+)?(?:winrate|win rate|taxa de vitória)\s*[:-]?\s*(\d+\.?\d*%?)', item.get('text', '').lower())
                        if winrate_match and not teams_players_info['team_stats'][team_name]['overall_winrate']:
                            teams_players_info['team_stats'][team_name]['overall_winrate'] = winrate_match.group(1)
                        
                        # Taxa de vitória como Radiant
                        radiant_match = re.search(r'(?:radiant)\s+(?:winrate|win rate|taxa de vitória)\s*[:-]?\s*(\d+\.?\d*%?)', item.get('text', '').lower())
                        if radiant_match and not teams_players_info['team_stats'][team_name]['radiant_winrate']:
                            teams_players_info['team_stats'][team_name]['radiant_winrate'] = radiant_match.group(1)
                        
                        # Taxa de vitória como Dire
                        dire_match = re.search(r'(?:dire)\s+(?:winrate|win rate|taxa de vitória)\s*[:-]?\s*(\d+\.?\d*%?)', item.get('text', '').lower())
                        if dire_match and not teams_players_info['team_stats'][team_name]['dire_winrate']:
                            teams_players_info['team_stats'][team_name]['dire_winrate'] = dire_match.group(1)
                        
                        # Duração média das partidas
                        duration_match = re.search(r'(?:average|média)\s+(?:game|partida|match)\s+(?:duration|duração)\s*[:-]?\s*(\d+\.?\d*)', item.get('text', '').lower())
                        if duration_match and not teams_players_info['team_stats'][team_name]['average_game_duration']:
                            teams_players_info['team_stats'][team_name]['average_game_duration'] = duration_match.group(1)
                        
                        # Heróis favoritos
                        hero_match = re.search(r'(?:favorite|favorito|preferred|preferido)\s+(?:hero|herói)\s*[:-]?\s*(\w+)', item.get('text', '').lower())
                        if hero_match:
                            hero = hero_match.group(1).strip()
                            if hero and hero not in [h.get('name') for h in teams_players_info['team_stats'][team_name]['favorite_heroes']]:
                                teams_players_info['team_stats'][team_name]['favorite_heroes'].append({
                                    "name": hero,
                                    "picks": None,
                                    "winrate": None
                                })
    
    # Processar dados específicos das lições aprendidas
    if 'lessons' in all_data:
        for lesson in all_data['lessons']:
            if isinstance(lesson, dict):
                # Extrair informações sobre equipes
                if 'team' in lesson:
                    team_name = lesson.get('team', '').strip().lower()
                    if team_name and team_name not in teams_players_info['teams']:
                        teams_players_info['teams'][team_name] = {
                            "name": team_name,
                            "aliases": [],
                            "players": [],
                            "region": lesson.get('region'),
                            "achievements": [],
                            "sources": ["lessons_learned"]
                        }
                
                # Extrair informações sobre jogadores
                if 'player' in lesson:
                    player_name = lesson.get('player', '').strip().lower()
                    if player_name and player_name not in teams_players_info['players']:
                        teams_players_info['players'][player_name] = {
                            "name": player_name,
                            "aliases": [],
                            "team": lesson.get('team'),
                            "position": lesson.get('position'),
                            "signature_heroes": [],
                            "sources": ["lessons_learned"]
                        }
                
                # Extrair estatísticas de equipes
                if 'team_stats' in lesson:
                    team_stats = lesson.get('team_stats', {})
                    if isinstance(team_stats, dict) and 'team' in team_stats:
                        team_name = team_stats.get('team', '').strip().lower()
                        if team_name and team_name not in teams_players_info['team_stats']:
                            teams_players_info['team_stats'][team_name] = {
                                "team": team_name,
                                "overall_winrate": team_stats.get('overall_winrate'),
                                "radiant_winrate": team_stats.get('radiant_winrate'),
                                "dire_winrate": team_stats.get('dire_winrate'),
                                "average_game_duration": team_stats.get('average_game_duration'),
                                "favorite_heroes": team_stats.get('favorite_heroes', []),
                                "sources": ["lessons_learned"]
                            }
    
    # Limitar o número de itens em cada categoria para evitar duplicações
    teams_players_info['matchups'] = teams_players_info['matchups'][:50]
    
    return teams_players_info

# Consolidar informações sobre equipes e jogadores
teams_players_info = consolidate_teams_players_info()

# Salvar as informações consolidadas sobre equipes e jogadores
output_file = os.path.join(consolidated_dir, 'teams_players_info.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(teams_players_info, f, ensure_ascii=False, indent=2)

print(f"Informações sobre equipes e jogadores consolidadas e salvas em {output_file}")
print(f"Número de equipes: {len(teams_players_info['teams'])}")
print(f"Número de jogadores: {len(teams_players_info['players'])}")
print(f"Número de torneios: {len(teams_players_info['tournaments'])}")
print(f"Número de confrontos: {len(teams_players_info['matchups'])}")
print(f"Número de estatísticas de equipes: {len(teams_players_info['team_stats'])}")
print(f"Número de arquivos de origem: {len(teams_players_info['source_files'])}")
