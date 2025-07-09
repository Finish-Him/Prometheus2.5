import os
import re
import json
from collections import defaultdict

# Diretório onde os arquivos de texto estão localizados
upload_dir = '/home/ubuntu/upload'
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Lista para armazenar todas as informações extraídas
all_txt_data = []

# Função para extrair informações de um arquivo de texto
def extract_txt_info(file_path):
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
    file_name = os.path.basename(file_path).replace('.txt', '')
    
    # Lista para armazenar informações deste arquivo de texto
    txt_info = []
    
    # Adicionar metadados do arquivo
    txt_info.append({
        "type": "text_metadata",
        "file": file_name,
        "length": len(content),
        "source": "upload_directory"
    })
    
    # Dividir o conteúdo em parágrafos (blocos de texto separados por linhas em branco)
    paragraphs = re.split(r'\n\s*\n', content)
    for i, para in enumerate(paragraphs):
        if len(para.strip()) > 20:  # Ignorar parágrafos muito curtos
            para_info = {
                "type": "text_paragraph",
                "file": file_name,
                "paragraph_index": i,
                "text": para.strip()[:500]  # Limitar tamanho do texto
            }
            txt_info.append(para_info)
    
    # Extrair linhas importantes (linhas que começam com palavras-chave relevantes)
    important_prefixes = [
        'hero', 'item', 'player', 'team', 'match', 'game', 'tournament', 'patch',
        'win', 'loss', 'rate', 'odds', 'bet', 'api', 'data', 'stat', 'meta',
        'herói', 'jogador', 'equipe', 'partida', 'jogo', 'torneio', 'vitória',
        'derrota', 'taxa', 'aposta', 'dados', 'estatística'
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) > 10:  # Ignorar linhas muito curtas
            for prefix in important_prefixes:
                if line.lower().startswith(prefix) or f" {prefix} " in line.lower():
                    line_info = {
                        "type": "important_line",
                        "file": file_name,
                        "line_index": i,
                        "keyword": prefix,
                        "text": line[:500]  # Limitar tamanho do texto
                    }
                    txt_info.append(line_info)
                    break
    
    # Extrair padrões específicos com base no nome do arquivo
    if "odds" in file_name.lower() or "aposta" in file_name.lower() or "bet" in file_name.lower():
        # Extrair informações sobre odds e apostas
        patterns = [
            (r'(\d+\.\d+)\s*(?:odds|odd)', "odds_value"),
            (r'(?:probabilidade|probability)\s*(?:de|of)?\s*(\d+\.?\d*%?)', "probability"),
            (r'(?:valor esperado|expected value)\s*(?:de|of)?\s*(\d+\.?\d*)', "expected_value"),
            (r'(?:over|under|mais de|menos de)\s*(\d+\.?\d*)', "over_under_value"),
            (r'(?:handicap|spread)\s*(?:de|of)?\s*([+-]?\d+\.?\d*)', "handicap_value"),
            (r'(?:team|equipe)\s+(\w+)', "team_name")
        ]
        
        for pattern, key in patterns:
            matches = re.findall(pattern, content.lower())
            for j, match in enumerate(matches):
                betting_info = {
                    "type": "betting_data",
                    "file": file_name,
                    "data_type": key,
                    "match_index": j,
                    "value": match
                }
                txt_info.append(betting_info)
    
    elif "comeback" in file_name.lower() or "virada" in file_name.lower():
        # Extrair informações sobre comebacks
        patterns = [
            (r'(?:gold|ouro)\s*(?:difference|diferença|lead|vantagem)\s*(?:of|de)?\s*(\d+[k]?)', "gold_difference"),
            (r'(?:experience|experiência|xp)\s*(?:difference|diferença|lead|vantagem)\s*(?:of|de)?\s*(\d+[k]?)', "xp_difference"),
            (r'(?:minute|minuto)\s*(\d+)', "game_minute"),
            (r'(?:team|equipe)\s+(\w+)', "team_name")
        ]
        
        for pattern, key in patterns:
            matches = re.findall(pattern, content.lower())
            for j, match in enumerate(matches):
                comeback_info = {
                    "type": "comeback_data",
                    "file": file_name,
                    "data_type": key,
                    "match_index": j,
                    "value": match
                }
                txt_info.append(comeback_info)
    
    elif "treinamento" in file_name.lower() or "training" in file_name.lower() or "super" in file_name.lower():
        # Extrair informações sobre treinamento de IA
        patterns = [
            (r'(?:accuracy|precisão)\s*(?:of|de)?\s*(\d+\.?\d*%?)', "accuracy"),
            (r'(?:error|erro)\s*(?:rate|taxa)?\s*(?:of|de)?\s*(\d+\.?\d*%?)', "error_rate"),
            (r'(?:feature|característica|variável)\s*(?:importance|importância)\s*(?:of|de)?\s*(\w+)', "feature_importance"),
            (r'(?:model|modelo)\s*(\w+)', "model_name")
        ]
        
        for pattern, key in patterns:
            matches = re.findall(pattern, content.lower())
            for j, match in enumerate(matches):
                training_info = {
                    "type": "training_data",
                    "file": file_name,
                    "data_type": key,
                    "match_index": j,
                    "value": match
                }
                txt_info.append(training_info)
    
    # Extrair dados numéricos (números, porcentagens, estatísticas)
    numeric_patterns = [
        (r'(\d+\.?\d*%)', "percentage"),
        (r'(\d+\.?\d*)\s*(?:gold|ouro)', "gold_value"),
        (r'(\d+\.?\d*)\s*(?:xp|experience|experiência)', "xp_value"),
        (r'(\d+\.?\d*)\s*(?:kills|abates)', "kills_value"),
        (r'(\d+\.?\d*)\s*(?:deaths|mortes)', "deaths_value"),
        (r'(\d+\.?\d*)\s*(?:assists|assistências)', "assists_value"),
        (r'(\d+\.?\d*)\s*(?:gpm|gold per minute)', "gpm_value"),
        (r'(\d+\.?\d*)\s*(?:xpm|experience per minute)', "xpm_value"),
        (r'(\d+\.?\d*)\s*(?:cs|last hits|last hit)', "cs_value"),
        (r'(\d+\.?\d*)\s*(?:net worth|patrimônio líquido)', "networth_value"),
        (r'(\d+\.?\d*)\s*(?:damage|dano)', "damage_value"),
        (r'(\d+\.?\d*)\s*(?:healing|cura)', "healing_value"),
        (r'(\d+\.?\d*)\s*(?:tower|torre)', "tower_value"),
        (r'(\d+\.?\d*)\s*(?:barracks|quartel)', "barracks_value"),
        (r'(\d+\.?\d*)\s*(?:roshan)', "roshan_value")
    ]
    
    for pattern, key in numeric_patterns:
        matches = re.findall(pattern, content.lower())
        for j, match in enumerate(matches):
            numeric_info = {
                "type": "numeric_data",
                "file": file_name,
                "data_type": key,
                "match_index": j,
                "value": match
            }
            txt_info.append(numeric_info)
    
    # Limitar a quantidade de informações para arquivos muito grandes
    if len(txt_info) > 1000:
        print(f"Limitando informações de {file_path} para 1000 itens")
        return txt_info[:1000]
    
    return txt_info

# Processar todos os arquivos de texto
txt_files = [f for f in os.listdir(upload_dir) if f.endswith('.txt')]
for txt_file in txt_files:
    file_path = os.path.join(upload_dir, txt_file)
    print(f"Processando {file_path}...")
    txt_info = extract_txt_info(file_path)
    all_txt_data.extend(txt_info)
    print(f"Extraídas {len(txt_info)} informações de {file_path}")

# Salvar os dados extraídos em um arquivo JSON
output_file = os.path.join(output_dir, 'text_extracted_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_txt_data, f, ensure_ascii=False, indent=2)

print(f"Total de {len(all_txt_data)} informações extraídas dos arquivos de texto")
print(f"Dados salvos em {output_file}")
