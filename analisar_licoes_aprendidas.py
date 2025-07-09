import docx2txt
import json
import os
import re

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'
lessons_file = '/home/ubuntu/upload/Lições Aprendidas.docx'

# Extrair texto do arquivo DOCX
try:
    lessons_text = docx2txt.process(lessons_file)
    print(f"Texto extraído com sucesso do arquivo {lessons_file}")
    
    # Salvar o texto extraído para referência
    with open(os.path.join(output_dir, 'licoes_aprendidas_texto.txt'), 'w', encoding='utf-8') as f:
        f.write(lessons_text)
    print(f"Texto salvo em {os.path.join(output_dir, 'licoes_aprendidas_texto.txt')}")
    
except Exception as e:
    print(f"Erro ao extrair texto do arquivo {lessons_file}: {e}")
    exit(1)

# Analisar o conteúdo do texto extraído
print("\nAnalisando conteúdo do arquivo de lições aprendidas...")

# Dividir o texto em parágrafos
paragraphs = re.split(r'\n\s*\n', lessons_text)
print(f"Encontrados {len(paragraphs)} parágrafos no texto")

# Identificar possíveis hipóteses no texto
# Procurar por padrões como "hipótese", "teoria", "observação", "conclusão", etc.
hypothesis_patterns = [
    r'(?i)hipótese[:\s]+(.+?)(?:\n|$)',
    r'(?i)teoria[:\s]+(.+?)(?:\n|$)',
    r'(?i)observa[çc][ãa]o[:\s]+(.+?)(?:\n|$)',
    r'(?i)conclus[ãa]o[:\s]+(.+?)(?:\n|$)',
    r'(?i)descobr[ií][:\s]+(.+?)(?:\n|$)',
    r'(?i)aprend[ií][:\s]+(.+?)(?:\n|$)',
    r'(?i)verific[ao][:\s]+(.+?)(?:\n|$)',
    r'(?i)constata[:\s]+(.+?)(?:\n|$)',
    r'(?i)se\s+([^,]+?),\s+ent[aã]o\s+(.+?)(?:\n|$)',
    r'(?i)quando\s+([^,]+?),\s+([^,]+?)(?:\n|$)'
]

# Estrutura para armazenar as hipóteses encontradas
hypotheses = []

# Procurar por hipóteses em cada parágrafo
for i, paragraph in enumerate(paragraphs):
    paragraph = paragraph.strip()
    if len(paragraph) < 10:  # Ignorar parágrafos muito curtos
        continue
    
    # Verificar se o parágrafo contém algum dos padrões de hipótese
    for pattern in hypothesis_patterns:
        matches = re.findall(pattern, paragraph)
        if matches:
            for match in matches:
                if isinstance(match, tuple):  # Para padrões com múltiplos grupos
                    condition = match[0].strip()
                    result = match[1].strip()
                    hypothesis_text = f"Se {condition}, então {result}"
                else:
                    hypothesis_text = match.strip()
                
                if len(hypothesis_text) > 10:  # Ignorar hipóteses muito curtas
                    hypotheses.append({
                        "text": hypothesis_text,
                        "source_paragraph": paragraph,
                        "paragraph_index": i,
                        "pattern_used": pattern
                    })
    
    # Verificar se o parágrafo inteiro parece ser uma hipótese
    # (começa com palavras-chave ou tem estrutura de hipótese)
    hypothesis_keywords = ['se ', 'quando ', 'sempre que ', 'caso ', 'para ', 'a fim de ']
    if any(paragraph.lower().startswith(keyword) for keyword in hypothesis_keywords):
        if not any(h['source_paragraph'] == paragraph for h in hypotheses):  # Evitar duplicatas
            hypotheses.append({
                "text": paragraph,
                "source_paragraph": paragraph,
                "paragraph_index": i,
                "pattern_used": "paragraph_structure"
            })

print(f"Encontradas {len(hypotheses)} possíveis hipóteses no texto")

# Salvar as hipóteses encontradas
with open(os.path.join(output_dir, 'hipoteses_extraidas.json'), 'w', encoding='utf-8') as f:
    json.dump(hypotheses, f, ensure_ascii=False, indent=2)
print(f"Hipóteses salvas em {os.path.join(output_dir, 'hipoteses_extraidas.json')}")

# Exibir as primeiras 10 hipóteses encontradas (ou todas, se houver menos de 10)
print("\nPrimeiras hipóteses encontradas:")
for i, hypothesis in enumerate(hypotheses[:10]):
    print(f"{i+1}. {hypothesis['text'][:100]}...")

# Análise adicional do conteúdo
# Identificar temas principais
themes = {
    "meta": 0,
    "heroes": 0,
    "teams": 0,
    "players": 0,
    "matches": 0,
    "betting": 0,
    "strategies": 0,
    "patch": 0,
    "items": 0,
    "api": 0
}

theme_keywords = {
    "meta": ["meta", "tendência", "popular", "atual"],
    "heroes": ["herói", "heroi", "hero", "campeão"],
    "teams": ["equipe", "time", "team", "organização"],
    "players": ["jogador", "player", "pro", "profissional"],
    "matches": ["partida", "jogo", "match", "game"],
    "betting": ["aposta", "bet", "odd", "probabilidade", "valor esperado"],
    "strategies": ["estratégia", "tática", "strategy", "tactic"],
    "patch": ["patch", "versão", "atualização", "update"],
    "items": ["item", "equipamento", "artefato", "objeto"],
    "api": ["api", "endpoint", "dados", "coleta", "data"]
}

for paragraph in paragraphs:
    for theme, keywords in theme_keywords.items():
        if any(keyword in paragraph.lower() for keyword in keywords):
            themes[theme] += 1

print("\nDistribuição de temas no documento:")
for theme, count in themes.items():
    print(f"{theme}: {count} ocorrências")

# Identificar possíveis contradições ou confirmações com a base de conhecimento
print("\nAnálise concluída. Os resultados foram salvos para comparação com a base de conhecimento.")
