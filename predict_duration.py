import pandas as pd
import joblib
import os

def predict_match_duration(features_dict):
    """
    Prevê a duração de uma partida de Dota 2 com base nas features fornecidas.
    
    Args:
        features_dict: Dicionário com as seguintes chaves:
            - total_kills: Total de kills na partida
            - radiant_score: Score do time Radiant
            - dire_score: Score do time Dire
            - first_blood_time: Tempo do first blood (em segundos)
            - tower_status_radiant: Status das torres do Radiant
            - tower_status_dire: Status das torres do Dire
            - barracks_status_radiant: Status dos barracks do Radiant
            - barracks_status_dire: Status dos barracks do Dire
            
    Returns:
        Duração prevista da partida em minutos
    """
    # Definir o caminho base para os modelos
    base_path = os.path.dirname(os.path.abspath(__file__))
    models_path = os.path.join(base_path, 'models')
    
    # Carregar o modelo e o scaler
    model = joblib.load(os.path.join(models_path, 'best_model_optimized.pkl'))
    scaler = joblib.load(os.path.join(models_path, 'scaler_optimized.pkl'))
    
    # Criar um DataFrame com as features na ordem correta
    features = pd.DataFrame([features_dict])
    
    # Normalizar as features
    features_scaled = scaler.transform(features)
    
    # Fazer a previsão
    duration_pred = model.predict(features_scaled)[0]
    
    return duration_pred

if __name__ == '__main__':
    # Exemplo de uso
    example_match = {
        'total_kills': 50,
        'radiant_score': 30,
        'dire_score': 20,
        'first_blood_time': 120,
        'tower_status_radiant': 1500,
        'tower_status_dire': 500,
        'barracks_status_radiant': 60,
        'barracks_status_dire': 10
    }
    
    predicted_duration = predict_match_duration(example_match)
    print(f'Duração prevista: {predicted_duration:.2f} minutos')
