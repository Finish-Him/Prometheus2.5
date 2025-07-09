import json
import os

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'
licoes_dir = '/home/ubuntu/dota2_knowledge_base/licoes_validadas'
resultados_dir = '/home/ubuntu/dota2_knowledge_base/resultados_analise'

# Carregar as hipóteses validadas para incorporação
with open(os.path.join(resultados_dir, 'hipoteses_para_incorporacao.json'), 'r', encoding='utf-8') as f:
    hipoteses_para_incorporacao = json.load(f)
    print(f"Carregadas {len(hipoteses_para_incorporacao)} hipóteses para incorporação")

# Carregar a base de conhecimento
with open(os.path.join(output_dir, 'dota2_knowledge_base_final.json'), 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)
    print(f"Carregada base de conhecimento com {knowledge_base['metadata']['total_information_count']} informações")

# Função para incorporar as hipóteses validadas na base de conhecimento
def incorporar_hipoteses_validadas():
    print("\nIncorporando hipóteses validadas na base de conhecimento...")
    
    # Contador de hipóteses incorporadas
    contador_incorporadas = 0
    
    # Incorporar apenas as hipóteses recomendadas para incorporação
    for hipotese in hipoteses_para_incorporacao:
        if hipotese.get("incorporation_recommended", False):
            categoria = hipotese.get("category", "betting")
            
            # Mapear categorias para as categorias da base de conhecimento
            categoria_mapeada = {
                "apostas": "betting",
                "herois": "meta_game",
                "equipes": "teams_players",
                "partidas": "matches",
                "Impacto de partidas disputadas": "betting"
            }.get(categoria, "betting")
            
            # Adicionar a hipótese à categoria apropriada
            if categoria_mapeada == "betting":
                if "categories" not in knowledge_base:
                    knowledge_base["categories"] = {}
                if "betting" not in knowledge_base["categories"]:
                    knowledge_base["categories"]["betting"] = {}
                if "validated_patterns" not in knowledge_base["categories"]["betting"]:
                    knowledge_base["categories"]["betting"]["validated_patterns"] = []
                
                knowledge_base["categories"]["betting"]["validated_patterns"].append({
                    "description": hipotese["text"],
                    "confidence": hipotese["confidence"],
                    "validation_date": hipotese["validation_date"],
                    "source": "licoes_aprendidas_validadas"
                })
                contador_incorporadas += 1
            
            elif categoria_mapeada == "meta_game":
                if "categories" not in knowledge_base:
                    knowledge_base["categories"] = {}
                if "meta_game" not in knowledge_base["categories"]:
                    knowledge_base["categories"]["meta_game"] = {}
                if "validated_patterns" not in knowledge_base["categories"]["meta_game"]:
                    knowledge_base["categories"]["meta_game"]["validated_patterns"] = []
                
                knowledge_base["categories"]["meta_game"]["validated_patterns"].append({
                    "description": hipotese["text"],
                    "confidence": hipotese["confidence"],
                    "validation_date": hipotese["validation_date"],
                    "source": "licoes_aprendidas_validadas"
                })
                contador_incorporadas += 1
            
            elif categoria_mapeada == "teams_players":
                if "categories" not in knowledge_base:
                    knowledge_base["categories"] = {}
                if "teams_players" not in knowledge_base["categories"]:
                    knowledge_base["categories"]["teams_players"] = {}
                if "validated_patterns" not in knowledge_base["categories"]["teams_players"]:
                    knowledge_base["categories"]["teams_players"]["validated_patterns"] = []
                
                knowledge_base["categories"]["teams_players"]["validated_patterns"].append({
                    "description": hipotese["text"],
                    "confidence": hipotese["confidence"],
                    "validation_date": hipotese["validation_date"],
                    "source": "licoes_aprendidas_validadas"
                })
                contador_incorporadas += 1
    
    # Atualizar o contador de informações na base de conhecimento
    knowledge_base["metadata"]["total_information_count"] += contador_incorporadas
    knowledge_base["metadata"]["last_updated"] = hipoteses_para_incorporacao[0]["validation_date"] if hipoteses_para_incorporacao else "2025-04-26"
    
    print(f"Incorporadas {contador_incorporadas} hipóteses validadas na base de conhecimento")
    
    # Salvar a base de conhecimento atualizada
    with open(os.path.join(output_dir, 'dota2_knowledge_base_updated.json'), 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    print(f"Base de conhecimento atualizada salva em {os.path.join(output_dir, 'dota2_knowledge_base_updated.json')}")

# Incorporar as hipóteses validadas na base de conhecimento
incorporar_hipoteses_validadas()

print("\nIncorporação de hipóteses validadas concluída com sucesso!")
