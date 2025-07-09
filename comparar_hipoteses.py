import json
import os
import re

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'
licoes_dir = '/home/ubuntu/dota2_knowledge_base/licoes_validadas'

# Criar diretório para resultados da validação
os.makedirs(licoes_dir, exist_ok=True)

# Carregar as hipóteses extraídas
with open(os.path.join(output_dir, 'hipoteses_extraidas.json'), 'r', encoding='utf-8') as f:
    hipoteses = json.load(f)
    print(f"Carregadas {len(hipoteses)} hipóteses extraídas")

# Carregar o texto completo das lições aprendidas para extrair mais hipóteses
with open(os.path.join(output_dir, 'licoes_aprendidas_texto.txt'), 'r', encoding='utf-8') as f:
    texto_licoes = f.read()
    print(f"Carregado texto completo das lições aprendidas ({len(texto_licoes)} caracteres)")

# Carregar a base de conhecimento
with open(os.path.join(output_dir, 'dota2_knowledge_base_final.json'), 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)
    print(f"Carregada base de conhecimento com {knowledge_base['metadata']['total_information_count']} informações")

# Extrair mais hipóteses do texto completo
print("\nExtraindo mais hipóteses do texto completo...")

# Procurar por padrões de tópicos e descrições no formato JSON
topicos_pattern = r'"topico":\s*"([^"]+)",\s*"descricao":\s*"([^"]+)"'
topicos_matches = re.findall(topicos_pattern, texto_licoes)

# Adicionar as novas hipóteses encontradas
for topico, descricao in topicos_matches:
    nova_hipotese = {
        "text": descricao,
        "source": "topico_json",
        "category": topico,
        "is_validated": False,
        "validation_result": None,
        "confidence": None,
        "supporting_evidence": [],
        "contradicting_evidence": []
    }
    
    # Verificar se esta hipótese já existe
    if not any(h.get('text', '') == descricao for h in hipoteses):
        hipoteses.append(nova_hipotese)

# Procurar por padrões de lições aprendidas no texto
licoes_patterns = [
    r'(?i)lição\s+aprendida[:\s]+(.+?)(?:\n|$)',
    r'(?i)aprendemos\s+que[:\s]+(.+?)(?:\n|$)',
    r'(?i)descobrimos\s+que[:\s]+(.+?)(?:\n|$)',
    r'(?i)verificamos\s+que[:\s]+(.+?)(?:\n|$)',
    r'(?i)constatamos\s+que[:\s]+(.+?)(?:\n|$)',
    r'(?i)observamos\s+que[:\s]+(.+?)(?:\n|$)',
    r'(?i)tendência[:\s]+(.+?)(?:\n|$)',
    r'(?i)padrão[:\s]+(.+?)(?:\n|$)'
]

for pattern in licoes_patterns:
    matches = re.findall(pattern, texto_licoes)
    for match in matches:
        licao = match.strip()
        if len(licao) > 20:  # Ignorar lições muito curtas
            nova_hipotese = {
                "text": licao,
                "source": "padrao_texto",
                "pattern_used": pattern,
                "is_validated": False,
                "validation_result": None,
                "confidence": None,
                "supporting_evidence": [],
                "contradicting_evidence": []
            }
            
            # Verificar se esta hipótese já existe
            if not any(h.get('text', '') == licao for h in hipoteses):
                hipoteses.append(nova_hipotese)

print(f"Total de hipóteses após extração adicional: {len(hipoteses)}")

# Categorizar as hipóteses
categorias = {
    "apostas": ["aposta", "odd", "valor esperado", "favorito", "underdog", "handicap", "over", "under", "green", "red"],
    "meta_jogo": ["meta", "patch", "tendência", "popular", "pick rate", "ban rate", "win rate"],
    "herois": ["herói", "heroi", "hero", "campeão", "carry", "suporte", "mid", "offlane"],
    "equipes": ["equipe", "time", "team", "organização", "jogador", "player"],
    "partidas": ["partida", "jogo", "match", "game", "duração", "kills", "first blood", "roshan", "teamfight"],
    "economia": ["net worth", "gold", "farm", "item", "equipamento", "compra"],
    "estrategia": ["estratégia", "tática", "push", "gank", "pickoff", "engage", "scaling"]
}

for hipotese in hipoteses:
    if "category" not in hipotese:
        hipotese["category"] = "não_categorizada"
        
        # Categorizar com base nas palavras-chave
        for categoria, keywords in categorias.items():
            if any(keyword.lower() in hipotese["text"].lower() for keyword in keywords):
                hipotese["category"] = categoria
                break

# Contar hipóteses por categoria
contagem_categorias = {}
for hipotese in hipoteses:
    categoria = hipotese["category"]
    contagem_categorias[categoria] = contagem_categorias.get(categoria, 0) + 1

print("\nDistribuição de hipóteses por categoria:")
for categoria, contagem in contagem_categorias.items():
    print(f"{categoria}: {contagem} hipóteses")

# Comparar as hipóteses com a base de conhecimento
print("\nComparando hipóteses com a base de conhecimento...")

# Função para buscar evidências na base de conhecimento
def buscar_evidencias(hipotese):
    evidencias_suporte = []
    evidencias_contrarias = []
    
    # Extrair palavras-chave da hipótese
    texto = hipotese["text"].lower()
    palavras = re.findall(r'\b\w+\b', texto)
    palavras = [p for p in palavras if len(p) > 3 and p not in ["quando", "então", "para", "como", "mais", "menos", "entre", "sobre", "ainda", "mesmo", "outro", "outra", "outros", "outras"]]
    
    # Buscar nas categorias relevantes da base de conhecimento
    categorias_busca = {
        "apostas": ["betting"],
        "meta_jogo": ["meta_game"],
        "herois": ["meta_game", "heroes"],
        "equipes": ["teams_players"],
        "partidas": ["teams_players", "matches"],
        "economia": ["meta_game", "items"],
        "estrategia": ["meta_game", "strategies"]
    }
    
    categoria_hipotese = hipotese.get("category", "não_categorizada")
    categorias_alvo = categorias_busca.get(categoria_hipotese, ["betting", "meta_game", "teams_players"])
    
    # Buscar nas categorias da base de conhecimento
    for categoria in categorias_alvo:
        if categoria == "betting" and "categories" in knowledge_base and "betting" in knowledge_base["categories"]:
            # Buscar em estratégias gerais de apostas
            for estrategia in knowledge_base["categories"]["betting"].get("general_strategies", []):
                if isinstance(estrategia, dict) and "description" in estrategia:
                    descricao = estrategia["description"].lower()
                    if any(palavra in descricao for palavra in palavras):
                        evidencias_suporte.append({
                            "source": "betting.general_strategies",
                            "text": estrategia["description"],
                            "relevance": sum(1 for palavra in palavras if palavra in descricao) / len(palavras)
                        })
            
            # Buscar em análises de odds
            for analise in knowledge_base["categories"]["betting"].get("odds_analysis", []):
                if isinstance(analise, dict) and "description" in analise:
                    descricao = analise["description"].lower()
                    if any(palavra in descricao for palavra in palavras):
                        evidencias_suporte.append({
                            "source": "betting.odds_analysis",
                            "text": analise["description"],
                            "relevance": sum(1 for palavra in palavras if palavra in descricao) / len(palavras)
                        })
            
            # Buscar em apostas ao vivo
            for aposta_vivo in knowledge_base["categories"]["betting"].get("live_betting", []):
                if isinstance(aposta_vivo, dict) and "description" in aposta_vivo:
                    descricao = aposta_vivo["description"].lower()
                    if any(palavra in descricao for palavra in palavras):
                        evidencias_suporte.append({
                            "source": "betting.live_betting",
                            "text": aposta_vivo["description"],
                            "relevance": sum(1 for palavra in palavras if palavra in descricao) / len(palavras)
                        })
        
        elif categoria == "meta_game" and "categories" in knowledge_base and "meta_game" in knowledge_base["categories"]:
            # Buscar em tendências do meta
            for tendencia in knowledge_base["categories"]["meta_game"].get("meta_trends", []):
                if isinstance(tendencia, dict) and "description" in tendencia:
                    descricao = tendencia["description"].lower()
                    if any(palavra in descricao for palavra in palavras):
                        evidencias_suporte.append({
                            "source": "meta_game.meta_trends",
                            "text": tendencia["description"],
                            "relevance": sum(1 for palavra in palavras if palavra in descricao) / len(palavras)
                        })
            
            # Buscar em heróis populares
            for heroi in knowledge_base["categories"]["meta_game"]["heroes"].get("popular", []):
                if isinstance(heroi, dict) and "description" in heroi:
                    descricao = heroi["description"].lower()
                    if any(palavra in descricao for palavra in palavras):
                        evidencias_suporte.append({
                            "source": "meta_game.heroes.popular",
                            "text": heroi["description"],
                            "relevance": sum(1 for palavra in palavras if palavra in descricao) / len(palavras)
                        })
        
        elif categoria == "teams_players" and "categories" in knowledge_base and "teams_players" in knowledge_base["categories"]:
            # Buscar em estatísticas de equipes
            for team_name, team_data in knowledge_base["categories"]["teams_players"].get("teams", {}).items():
                if isinstance(team_data, dict):
                    team_text = json.dumps(team_data).lower()
                    if any(palavra in team_text for palavra in palavras):
                        evidencias_suporte.append({
                            "source": f"teams_players.teams.{team_name}",
                            "text": f"Dados da equipe {team_name}",
                            "relevance": sum(1 for palavra in palavras if palavra in team_text) / len(palavras)
                        })
            
            # Buscar em confrontos
            for matchup in knowledge_base["categories"]["teams_players"].get("matchups", []):
                if isinstance(matchup, dict) and "description" in matchup:
                    descricao = matchup["description"].lower()
                    if any(palavra in descricao for palavra in palavras):
                        evidencias_suporte.append({
                            "source": "teams_players.matchups",
                            "text": matchup["description"],
                            "relevance": sum(1 for palavra in palavras if palavra in descricao) / len(palavras)
                        })
    
    # Buscar também em dados brutos
    if "raw_data_samples" in knowledge_base:
        for data_type, samples in knowledge_base["raw_data_samples"].items():
            if data_type in ["text_paragraphs", "docx_paragraphs"]:
                for sample in samples[:100]:  # Limitar a busca para não sobrecarregar
                    if isinstance(sample, dict) and "text" in sample:
                        texto_amostra = sample["text"].lower()
                        if any(palavra in texto_amostra for palavra in palavras):
                            # Verificar se é evidência de suporte ou contrária
                            palavras_negacao = ["não", "nunca", "raramente", "dificilmente", "ao contrário", "oposto"]
                            tem_negacao = any(neg in texto_amostra for neg in palavras_negacao)
                            
                            if tem_negacao:
                                evidencias_contrarias.append({
                                    "source": f"raw_data.{data_type}",
                                    "text": sample["text"],
                                    "relevance": sum(1 for palavra in palavras if palavra in texto_amostra) / len(palavras)
                                })
                            else:
                                evidencias_suporte.append({
                                    "source": f"raw_data.{data_type}",
                                    "text": sample["text"],
                                    "relevance": sum(1 for palavra in palavras if palavra in texto_amostra) / len(palavras)
                                })
    
    # Ordenar evidências por relevância
    evidencias_suporte.sort(key=lambda x: x["relevance"], reverse=True)
    evidencias_contrarias.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Limitar o número de evidências para as mais relevantes
    return evidencias_suporte[:5], evidencias_contrarias[:3]

# Comparar cada hipótese com a base de conhecimento
for hipotese in hipoteses:
    evidencias_suporte, evidencias_contrarias = buscar_evidencias(hipotese)
    
    hipotese["supporting_evidence"] = evidencias_suporte
    hipotese["contradicting_evidence"] = evidencias_contrarias
    
    # Determinar o resultado da validação com base nas evidências
    if len(evidencias_suporte) > 0 and len(evidencias_contrarias) == 0:
        hipotese["validation_result"] = "confirmada"
        hipotese["confidence"] = min(0.5 + 0.1 * len(evidencias_suporte), 0.9)
        hipotese["is_validated"] = True
    elif len(evidencias_suporte) > len(evidencias_contrarias):
        hipotese["validation_result"] = "parcialmente_confirmada"
        hipotese["confidence"] = 0.5 + 0.1 * (len(evidencias_suporte) - len(evidencias_contrarias)) / (len(evidencias_suporte) + len(evidencias_contrarias))
        hipotese["is_validated"] = True
    elif len(evidencias_contrarias) > len(evidencias_suporte):
        hipotese["validation_result"] = "refutada"
        hipotese["confidence"] = 0.5 + 0.1 * (len(evidencias_contrarias) - len(evidencias_suporte)) / (len(evidencias_suporte) + len(evidencias_contrarias))
        hipotese["is_validated"] = True
    elif len(evidencias_suporte) > 0 and len(evidencias_contrarias) > 0:
        hipotese["validation_result"] = "inconclusiva"
        hipotese["confidence"] = 0.5
        hipotese["is_validated"] = False
    else:
        hipotese["validation_result"] = "sem_evidencias"
        hipotese["confidence"] = 0.0
        hipotese["is_validated"] = False

# Contar resultados da validação
contagem_resultados = {}
for hipotese in hipoteses:
    resultado = hipotese["validation_result"]
    contagem_resultados[resultado] = contagem_resultados.get(resultado, 0) + 1

print("\nResultados da validação:")
for resultado, contagem in contagem_resultados.items():
    print(f"{resultado}: {contagem} hipóteses")

# Salvar os resultados da comparação
with open(os.path.join(licoes_dir, 'hipoteses_validadas.json'), 'w', encoding='utf-8') as f:
    json.dump(hipoteses, f, ensure_ascii=False, indent=2)
print(f"\nResultados da validação salvos em {os.path.join(licoes_dir, 'hipoteses_validadas.json')}")

# Gerar um resumo das hipóteses validadas
resumo = {
    "total_hipoteses": len(hipoteses),
    "distribuicao_categorias": contagem_categorias,
    "resultados_validacao": contagem_resultados,
    "hipoteses_confirmadas": [h for h in hipoteses if h["validation_result"] == "confirmada"],
    "hipoteses_parcialmente_confirmadas": [h for h in hipoteses if h["validation_result"] == "parcialmente_confirmada"],
    "hipoteses_refutadas": [h for h in hipoteses if h["validation_result"] == "refutada"],
    "hipoteses_inconclusivas": [h for h in hipoteses if h["validation_result"] == "inconclusiva"],
    "hipoteses_sem_evidencias": [h for h in hipoteses if h["validation_result"] == "sem_evidencias"]
}

with open(os.path.join(licoes_dir, 'resumo_validacao.json'), 'w', encoding='utf-8') as f:
    json.dump(resumo, f, ensure_ascii=False, indent=2)
print(f"Resumo da validação salvo em {os.path.join(licoes_dir, 'resumo_validacao.json')}")

print("\nComparação concluída com sucesso!")
