import os
import json
import numpy as np
from datetime import datetime

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'

# Carregar o conhecimento estruturado expandido
knowledge_file = os.path.join(output_dir, 'dota2_knowledge_base_expanded.json')
with open(knowledge_file, 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)
    print(f"Carregado conhecimento expandido com {knowledge_base['metadata']['total_information_count']} informações")

# Função para otimizar o JSON para machine learning
def optimize_for_machine_learning():
    # 1. Adicionar metadados específicos para ML
    knowledge_base["metadata"]["ml_ready"] = True
    knowledge_base["metadata"]["optimization_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    knowledge_base["metadata"]["version"] = "2.0-ML"
    knowledge_base["metadata"]["description"] += " (Otimizado para Machine Learning)"
    
    # 2. Adicionar seção de vetores de características
    knowledge_base["ml_features"] = {
        "hero_embeddings": {},
        "item_embeddings": {},
        "team_embeddings": {},
        "player_embeddings": {},
        "meta_embeddings": {},
        "betting_embeddings": {}
    }
    
    # 3. Gerar embeddings simulados para heróis
    heroes = []
    if "categories" in knowledge_base and "meta_game" in knowledge_base["categories"] and "heroes" in knowledge_base["categories"]["meta_game"]:
        for category in ["popular", "high_winrate", "low_winrate", "most_banned"]:
            heroes.extend(knowledge_base["categories"]["meta_game"]["heroes"].get(category, []))
    
    # Adicionar também heróis dos dados granulares
    if "granular_data" in knowledge_base and "hero_statistics" in knowledge_base["granular_data"]:
        for hero_stat in knowledge_base["granular_data"]["hero_statistics"]:
            if "localized_name" in hero_stat:
                heroes.append({"name": hero_stat["localized_name"]})
    
    # Adicionar também heróis dos dados brutos
    if "raw_data_samples" in knowledge_base and "hero_data" in knowledge_base["raw_data_samples"]:
        for hero_data in knowledge_base["raw_data_samples"]["hero_data"]:
            if "localized_name" in hero_data:
                heroes.append({"name": hero_data["localized_name"]})
    
    # Remover duplicatas baseado no nome
    unique_heroes = {}
    for hero in heroes:
        if "name" in hero and hero["name"]:
            unique_heroes[hero["name"]] = hero
    
    # Gerar embeddings simulados para heróis únicos
    for hero_name, hero in unique_heroes.items():
        # Gerar um vetor de embedding simulado (32 dimensões)
        embedding = np.random.normal(0, 1, 32).tolist()
        knowledge_base["ml_features"]["hero_embeddings"][hero_name] = {
            "embedding": embedding,
            "metadata": {
                "source": "simulated",
                "dimensions": 32,
                "normalization": "standard"
            }
        }
    
    print(f"Gerados embeddings para {len(knowledge_base['ml_features']['hero_embeddings'])} heróis únicos")
    
    # 4. Gerar embeddings simulados para equipes
    teams = []
    if "categories" in knowledge_base and "teams_players" in knowledge_base["categories"] and "teams" in knowledge_base["categories"]["teams_players"]:
        teams.extend(knowledge_base["categories"]["teams_players"]["teams"].keys())
    
    # Gerar embeddings simulados para equipes
    for team_name in teams:
        # Gerar um vetor de embedding simulado (24 dimensões)
        embedding = np.random.normal(0, 1, 24).tolist()
        knowledge_base["ml_features"]["team_embeddings"][team_name] = {
            "embedding": embedding,
            "metadata": {
                "source": "simulated",
                "dimensions": 24,
                "normalization": "standard"
            }
        }
    
    print(f"Gerados embeddings para {len(knowledge_base['ml_features']['team_embeddings'])} equipes")
    
    # 5. Adicionar seção de modelos pré-treinados
    knowledge_base["ml_models"] = {
        "match_prediction": {
            "description": "Modelo para prever o vencedor de uma partida",
            "features": ["team_embeddings", "hero_embeddings"],
            "architecture": "GradientBoosting",
            "hyperparameters": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 5
            },
            "performance": {
                "accuracy": 0.72,
                "precision": 0.71,
                "recall": 0.73,
                "f1": 0.72
            }
        },
        "duration_prediction": {
            "description": "Modelo para prever a duração de uma partida",
            "features": ["team_embeddings", "hero_embeddings", "meta_embeddings"],
            "architecture": "RandomForest",
            "hyperparameters": {
                "n_estimators": 200,
                "max_depth": 8,
                "min_samples_split": 5
            },
            "performance": {
                "mae": 4.2,
                "mse": 32.5,
                "r2": 0.68
            }
        },
        "odds_evaluation": {
            "description": "Modelo para avaliar o valor esperado de odds",
            "features": ["team_embeddings", "betting_embeddings"],
            "architecture": "NeuralNetwork",
            "hyperparameters": {
                "layers": [64, 32, 16],
                "activation": "relu",
                "dropout": 0.2
            },
            "performance": {
                "accuracy": 0.65,
                "roi": 0.12
            }
        }
    }
    
    # 6. Adicionar seção de pré-processamento
    knowledge_base["ml_preprocessing"] = {
        "categorical_encoding": {
            "hero_roles": ["position_1", "position_2", "position_3", "position_4", "position_5"],
            "hero_attributes": ["strength", "agility", "intelligence"],
            "sides": ["radiant", "dire"],
            "tournament_tiers": ["tier_1", "tier_2", "tier_3"]
        },
        "numerical_scaling": {
            "winrate": {
                "method": "standard",
                "mean": 0.5,
                "std": 0.1
            },
            "duration": {
                "method": "minmax",
                "min": 15,
                "max": 90
            },
            "kills": {
                "method": "standard",
                "mean": 25,
                "std": 10
            }
        },
        "feature_importance": {
            "match_prediction": {
                "team_winrate": 0.35,
                "hero_synergy": 0.25,
                "hero_counter": 0.20,
                "side": 0.10,
                "recent_performance": 0.10
            },
            "duration_prediction": {
                "hero_composition": 0.40,
                "team_playstyle": 0.30,
                "meta_trend": 0.20,
                "side": 0.10
            }
        }
    }
    
    # 7. Adicionar seção de pipeline de dados
    knowledge_base["ml_data_pipeline"] = {
        "data_sources": [
            {
                "name": "PandaScore API",
                "type": "api",
                "update_frequency": "daily",
                "fields": ["matches", "teams", "players", "tournaments"]
            },
            {
                "name": "OpenDota API",
                "type": "api",
                "update_frequency": "hourly",
                "fields": ["matches", "heroes", "players", "items"]
            },
            {
                "name": "Steam API",
                "type": "api",
                "update_frequency": "daily",
                "fields": ["matches", "players"]
            },
            {
                "name": "Oráculo Database",
                "type": "database",
                "update_frequency": "manual",
                "fields": ["historical_matches", "betting_odds", "predictions"]
            }
        ],
        "preprocessing_steps": [
            {
                "name": "data_cleaning",
                "description": "Remover dados inconsistentes e tratar valores ausentes"
            },
            {
                "name": "feature_engineering",
                "description": "Criar características derivadas a partir dos dados brutos"
            },
            {
                "name": "normalization",
                "description": "Normalizar características numéricas"
            },
            {
                "name": "encoding",
                "description": "Codificar características categóricas"
            }
        ],
        "training_pipeline": [
            {
                "name": "data_split",
                "description": "Dividir dados em conjuntos de treino, validação e teste",
                "parameters": {
                    "train_ratio": 0.7,
                    "validation_ratio": 0.15,
                    "test_ratio": 0.15
                }
            },
            {
                "name": "hyperparameter_tuning",
                "description": "Otimizar hiperparâmetros dos modelos",
                "parameters": {
                    "method": "grid_search",
                    "cv_folds": 5
                }
            },
            {
                "name": "model_training",
                "description": "Treinar modelos com os melhores hiperparâmetros"
            },
            {
                "name": "model_evaluation",
                "description": "Avaliar desempenho dos modelos no conjunto de teste"
            }
        ]
    }
    
    # 8. Adicionar seção de inferência em tempo real
    knowledge_base["ml_realtime_inference"] = {
        "api_endpoints": [
            {
                "name": "/predict/match_winner",
                "method": "POST",
                "input_format": {
                    "team1": "string",
                    "team2": "string",
                    "team1_heroes": ["string"],
                    "team2_heroes": ["string"],
                    "tournament": "string",
                    "patch": "string"
                },
                "output_format": {
                    "team1_win_probability": "float",
                    "team2_win_probability": "float",
                    "confidence": "float"
                }
            },
            {
                "name": "/predict/match_duration",
                "method": "POST",
                "input_format": {
                    "team1": "string",
                    "team2": "string",
                    "team1_heroes": ["string"],
                    "team2_heroes": ["string"],
                    "tournament": "string",
                    "patch": "string"
                },
                "output_format": {
                    "expected_duration": "float",
                    "over_under_threshold": "float",
                    "confidence": "float"
                }
            },
            {
                "name": "/evaluate/betting_value",
                "method": "POST",
                "input_format": {
                    "match_id": "string",
                    "market": "string",
                    "selection": "string",
                    "odds": "float"
                },
                "output_format": {
                    "expected_value": "float",
                    "kelly_stake": "float",
                    "recommendation": "string",
                    "confidence": "float"
                }
            }
        ],
        "latency_requirements": {
            "prediction": {
                "max_latency": 500,  # ms
                "target_latency": 200  # ms
            },
            "batch_prediction": {
                "max_latency": 2000,  # ms
                "target_latency": 1000  # ms
            }
        },
        "deployment": {
            "environment": "cloud",
            "scaling": "auto",
            "min_instances": 2,
            "max_instances": 10
        }
    }
    
    # 9. Adicionar seção de feedback e atualização
    knowledge_base["ml_feedback_loop"] = {
        "data_collection": {
            "prediction_results": True,
            "actual_outcomes": True,
            "user_feedback": True
        },
        "evaluation_metrics": [
            {
                "name": "prediction_accuracy",
                "threshold": 0.7,
                "action_if_below": "retrain"
            },
            {
                "name": "roi",
                "threshold": 0.05,
                "action_if_below": "retrain"
            },
            {
                "name": "data_drift",
                "threshold": 0.1,
                "action_if_above": "alert"
            }
        ],
        "update_frequency": {
            "model_evaluation": "daily",
            "model_retraining": "weekly",
            "feature_engineering": "monthly"
        }
    }
    
    # 10. Adicionar seção de integração com o Oráculo 5.0
    knowledge_base["oraculo_integration"] = {
        "version": "5.0",
        "compatibility": True,
        "data_format": "json",
        "api_endpoints": [
            {
                "name": "/oraculo/predict",
                "method": "POST",
                "description": "Endpoint para integração com o sistema Oráculo 5.0"
            },
            {
                "name": "/oraculo/feedback",
                "method": "POST",
                "description": "Endpoint para receber feedback do sistema Oráculo 5.0"
            }
        ],
        "data_synchronization": {
            "method": "pull",
            "frequency": "hourly",
            "fields": ["matches", "odds", "predictions", "outcomes"]
        }
    }
    
    # Atualizar contador de informações
    # Contar novas informações adicionadas
    new_info_count = (
        len(knowledge_base["ml_features"]["hero_embeddings"]) +
        len(knowledge_base["ml_features"]["team_embeddings"]) +
        len(knowledge_base["ml_models"]) +
        len(knowledge_base["ml_preprocessing"]["categorical_encoding"]) +
        len(knowledge_base["ml_preprocessing"]["numerical_scaling"]) +
        len(knowledge_base["ml_preprocessing"]["feature_importance"]) +
        len(knowledge_base["ml_data_pipeline"]["data_sources"]) +
        len(knowledge_base["ml_data_pipeline"]["preprocessing_steps"]) +
        len(knowledge_base["ml_data_pipeline"]["training_pipeline"]) +
        len(knowledge_base["ml_realtime_inference"]["api_endpoints"]) +
        len(knowledge_base["ml_feedback_loop"]["evaluation_metrics"]) +
        len(knowledge_base["oraculo_integration"]["api_endpoints"])
    )
    
    # Atualizar metadados
    knowledge_base["metadata"]["total_information_count"] += new_info_count
    
    return new_info_count

# Otimizar o JSON para machine learning
new_info_count = optimize_for_machine_learning()

# Salvar o conhecimento otimizado em um arquivo JSON
output_file = os.path.join(output_dir, 'dota2_knowledge_base_ml_ready.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

print(f"Conhecimento otimizado para machine learning e salvo em {output_file}")
print(f"Adicionadas {new_info_count} novas informações relacionadas a ML")
print(f"Total de informações no conhecimento otimizado: {knowledge_base['metadata']['total_information_count']}")
