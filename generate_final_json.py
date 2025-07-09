import os
import json
import hashlib
from datetime import datetime

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Carregar o conhecimento otimizado para ML
knowledge_file = os.path.join(output_dir, 'dota2_knowledge_base_ml_ready.json')
with open(knowledge_file, 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)
    print(f"Carregado conhecimento otimizado com {knowledge_base['metadata']['total_information_count']} informações")

# Função para gerar o documento JSON final
def generate_final_json():
    # 1. Atualizar metadados finais
    knowledge_base["metadata"]["version"] = "3.0-Final"
    knowledge_base["metadata"]["generation_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    knowledge_base["metadata"]["description"] = "Base de conhecimento completa sobre Dota 2 para o Oráculo 5.0, otimizada para análise preditiva, apostas e machine learning"
    
    # 2. Adicionar informações de validação
    # Calcular hash do conteúdo para verificação de integridade
    content_str = json.dumps(knowledge_base, ensure_ascii=False, sort_keys=True)
    content_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    knowledge_base["validation"] = {
        "hash": content_hash,
        "information_count": knowledge_base["metadata"]["total_information_count"],
        "validation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "schema_version": "3.0"
    }
    
    # 3. Adicionar informações de uso
    knowledge_base["usage_guidelines"] = {
        "recommended_applications": [
            "Análise preditiva de partidas de Dota 2",
            "Avaliação de valor em apostas esportivas",
            "Análise de meta e tendências do jogo",
            "Treinamento de modelos de machine learning",
            "Integração com o sistema Oráculo 5.0"
        ],
        "update_frequency": {
            "meta_data": "após cada patch",
            "team_data": "semanal",
            "match_data": "diário",
            "betting_data": "em tempo real"
        },
        "compatibility": {
            "python_version": ">=3.8",
            "frameworks": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"],
            "storage": ["JSON", "CSV", "SQLite", "PostgreSQL"]
        },
        "performance_considerations": {
            "file_size": os.path.getsize(knowledge_file) / (1024 * 1024),  # Tamanho em MB
            "loading_time": "Depende do hardware, tipicamente <5s",
            "memory_usage": "~500MB em uso típico"
        }
    }
    
    # 4. Adicionar informações de expansão futura
    knowledge_base["future_expansion"] = {
        "planned_features": [
            {
                "name": "Suporte a CS2",
                "description": "Expansão da base de conhecimento para incluir dados de Counter-Strike 2",
                "estimated_release": "2025-Q3"
            },
            {
                "name": "Análise de vídeo em tempo real",
                "description": "Integração com sistemas de análise de vídeo para extrair dados em tempo real das transmissões",
                "estimated_release": "2025-Q4"
            },
            {
                "name": "Modelos de deep learning avançados",
                "description": "Implementação de arquiteturas de deep learning mais avançadas para melhorar a precisão das previsões",
                "estimated_release": "2025-Q4"
            }
        ],
        "data_sources_to_add": [
            "API de transmissão ao vivo",
            "Dados de redes sociais dos jogadores",
            "Análise de sentimento da comunidade"
        ],
        "integration_opportunities": [
            "Plataformas de apostas",
            "Aplicativos móveis",
            "Assistentes virtuais",
            "Dashboards de análise"
        ]
    }
    
    # 5. Adicionar resumo executivo
    knowledge_base["executive_summary"] = {
        "title": "Base de Conhecimento Dota 2 para o Oráculo 5.0",
        "purpose": "Fornecer uma base de conhecimento abrangente e estruturada para análise preditiva de partidas de Dota 2, com foco em apostas esportivas e machine learning",
        "key_features": [
            "Mais de 14.000 informações estruturadas sobre Dota 2",
            "Dados sobre meta, equipes, jogadores, estratégias de apostas e APIs",
            "Otimizado para machine learning com embeddings, modelos e pipelines",
            "Compatível com o sistema Oráculo 5.0",
            "Pronto para expansão futura para outros jogos"
        ],
        "information_breakdown": {
            "meta_game": f"{len(knowledge_base['categories']['meta_game']['strategies']) + len(knowledge_base['categories']['meta_game']['meta_trends'])} informações",
            "teams_players": f"{len(knowledge_base['categories']['teams_players']['teams']) + len(knowledge_base['categories']['teams_players']['players']) + len(knowledge_base['categories']['teams_players']['tournaments']) + len(knowledge_base['categories']['teams_players']['matchups'])} informações",
            "betting": f"{len(knowledge_base['categories']['betting']['general_strategies']) + sum(len(v) for v in knowledge_base['categories']['betting']['market_specific'].values()) + len(knowledge_base['categories']['betting']['odds_analysis']) + len(knowledge_base['categories']['betting']['value_betting'])} informações",
            "data_collection": f"{sum(len(v['endpoints']) for k, v in knowledge_base['categories']['data_collection']['apis'].items()) + len(knowledge_base['categories']['data_collection']['strategies'])} informações",
            "raw_data": f"{sum(len(v) for k, v in knowledge_base['raw_data_samples'].items())} informações",
            "ml_features": f"{len(knowledge_base['ml_features']['hero_embeddings']) + len(knowledge_base['ml_features']['team_embeddings'])} embeddings"
        },
        "recommended_next_steps": [
            "Integrar com o sistema Oráculo 5.0",
            "Treinar modelos de machine learning usando os dados fornecidos",
            "Configurar pipelines de atualização automática de dados",
            "Implementar APIs de inferência em tempo real"
        ]
    }
    
    return knowledge_base

# Gerar o documento JSON final
final_knowledge_base = generate_final_json()

# Salvar o documento JSON final
output_file = os.path.join(output_dir, 'dota2_knowledge_base_final.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_knowledge_base, f, ensure_ascii=False, indent=2)

# Criar uma versão compactada para distribuição
output_file_compact = os.path.join(output_dir, 'dota2_knowledge_base_final_compact.json')
with open(output_file_compact, 'w', encoding='utf-8') as f:
    json.dump(final_knowledge_base, f, ensure_ascii=False)

print(f"Documento JSON final gerado e salvo em {output_file}")
print(f"Versão compactada salva em {output_file_compact}")
print(f"Tamanho do arquivo final: {os.path.getsize(output_file) / (1024 * 1024):.2f} MB")
print(f"Tamanho do arquivo compactado: {os.path.getsize(output_file_compact) / (1024 * 1024):.2f} MB")
print(f"Total de informações no documento final: {final_knowledge_base['metadata']['total_information_count']}")
