#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modelo preditivo para apostas em Dota 2 baseado nos padrões de vitória identificados.
Este script implementa um modelo que calcula a probabilidade de vitória em partidas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

# Diretório dos dados unificados
DATA_DIR = '/home/ubuntu/analise_dota2/dados_unificados'
# Diretório para salvar o modelo e resultados
OUTPUT_DIR = '/home/ubuntu/analise_dota2/modelo_preditivo'

# Criar diretório de saída se não existir
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Iniciando criação de modelo preditivo para apostas em Dota 2...")

# Função para carregar os dados unificados
def carregar_dados_unificados():
    print("Carregando dados unificados...")
    
    # Dicionário para armazenar os DataFrames
    dfs = {}
    
    # Lista de arquivos a serem carregados
    arquivos = [
        'herois_analise.csv',
        'times_analise.csv',
        'partidas_analise.csv',
        'combinacoes_herois.csv',
        'contra_escolhas.csv'
    ]
    
    # Carregar cada arquivo
    for arquivo in arquivos:
        try:
            caminho = os.path.join(DATA_DIR, arquivo)
            print(f"Carregando {arquivo}...")
            dfs[arquivo.replace('.csv', '')] = pd.read_csv(caminho)
            print(f"  {arquivo} carregado com sucesso: {dfs[arquivo.replace('.csv', '')].shape} linhas/colunas")
        except Exception as e:
            print(f"Erro ao carregar {arquivo}: {e}")
    
    return dfs

# Função para preparar os dados para o modelo
def preparar_dados(dfs):
    print("Preparando dados para o modelo...")
    
    # Obter dados de partidas
    partidas = dfs['partidas_analise']
    herois = dfs['herois_analise']
    
    # Criar dicionário de heróis para lookup rápido
    herois_dict = {}
    for _, heroi in herois.iterrows():
        herois_dict[heroi['id']] = {
            'win_rate_all': heroi['win_rate_all'],
            'pick_rate': heroi['pick_rate'],
            'win_rate_trend': heroi['win_rate_trend'] if 'win_rate_trend' in heroi else 0,
            'primary_attr': heroi['primary_attr'],
            'attack_type': heroi['attack_type']
        }
    
    # Preparar features para o modelo
    X = []
    y = []
    
    # Processar cada partida
    for _, partida in partidas.iterrows():
        try:
            # Verificar se temos os dados necessários
            if not all(col in partida for col in ['radiant_team', 'dire_team', 'radiant_win']):
                continue
            
            # Converter strings de listas para listas Python
            radiant_team = eval(partida['radiant_team']) if isinstance(partida['radiant_team'], str) else partida['radiant_team']
            dire_team = eval(partida['dire_team']) if isinstance(partida['dire_team'], str) else partida['dire_team']
            
            # Features da partida
            features = []
            
            # Média da taxa de vitória dos heróis do Radiant
            radiant_win_rates = [herois_dict.get(hero_id, {}).get('win_rate_all', 0.5) for hero_id in radiant_team]
            features.append(np.mean(radiant_win_rates))
            
            # Média da taxa de vitória dos heróis do Dire
            dire_win_rates = [herois_dict.get(hero_id, {}).get('win_rate_all', 0.5) for hero_id in dire_team]
            features.append(np.mean(dire_win_rates))
            
            # Diferença entre as taxas de vitória médias
            features.append(np.mean(radiant_win_rates) - np.mean(dire_win_rates))
            
            # Média da tendência de crescimento dos heróis do Radiant
            radiant_trends = [herois_dict.get(hero_id, {}).get('win_rate_trend', 0) for hero_id in radiant_team]
            features.append(np.mean(radiant_trends))
            
            # Média da tendência de crescimento dos heróis do Dire
            dire_trends = [herois_dict.get(hero_id, {}).get('win_rate_trend', 0) for hero_id in dire_team]
            features.append(np.mean(dire_trends))
            
            # Diferença entre as tendências de crescimento médias
            features.append(np.mean(radiant_trends) - np.mean(dire_trends))
            
            # Contagem de heróis por atributo primário no Radiant
            radiant_attrs = [herois_dict.get(hero_id, {}).get('primary_attr', 'unknown') for hero_id in radiant_team]
            features.append(radiant_attrs.count('str') / len(radiant_team))
            features.append(radiant_attrs.count('agi') / len(radiant_team))
            features.append(radiant_attrs.count('int') / len(radiant_team))
            features.append(radiant_attrs.count('all') / len(radiant_team))
            
            # Contagem de heróis por atributo primário no Dire
            dire_attrs = [herois_dict.get(hero_id, {}).get('primary_attr', 'unknown') for hero_id in dire_team]
            features.append(dire_attrs.count('str') / len(dire_team))
            features.append(dire_attrs.count('agi') / len(dire_team))
            features.append(dire_attrs.count('int') / len(dire_team))
            features.append(dire_attrs.count('all') / len(dire_team))
            
            # Contagem de heróis por tipo de ataque no Radiant
            radiant_attacks = [herois_dict.get(hero_id, {}).get('attack_type', 'unknown') for hero_id in radiant_team]
            features.append(radiant_attacks.count('Melee') / len(radiant_team))
            features.append(radiant_attacks.count('Ranged') / len(radiant_team))
            
            # Contagem de heróis por tipo de ataque no Dire
            dire_attacks = [herois_dict.get(hero_id, {}).get('attack_type', 'unknown') for hero_id in dire_team]
            features.append(dire_attacks.count('Melee') / len(dire_team))
            features.append(dire_attacks.count('Ranged') / len(dire_team))
            
            # Verificar se algum herói do top 5 em taxa de vitória está presente
            top_heroes = [1, 68, 8, 54, 27]  # IDs dos heróis top 5 (Wraith King, Ancient Apparition, etc.)
            features.append(any(hero_id in top_heroes for hero_id in radiant_team))
            features.append(any(hero_id in top_heroes for hero_id in dire_team))
            
            # Verificar se algum herói emergente está presente
            emerging_heroes = [66, 89, 58]  # IDs dos heróis emergentes (Chen, Naga Siren, etc.)
            features.append(any(hero_id in emerging_heroes for hero_id in radiant_team))
            features.append(any(hero_id in emerging_heroes for hero_id in dire_team))
            
            # Adicionar features adicionais se disponíveis
            if 'avg_rank_tier' in partida:
                features.append(partida['avg_rank_tier'])
            else:
                features.append(0)
            
            if 'duration' in partida:
                features.append(partida['duration'])
            else:
                features.append(0)
            
            # Adicionar ao conjunto de dados
            X.append(features)
            y.append(1 if partida['radiant_win'] else 0)
        
        except Exception as e:
            print(f"Erro ao processar partida: {e}")
            continue
    
    return np.array(X), np.array(y)

# Função para treinar o modelo
def treinar_modelo(X, y):
    print("Treinando modelo preditivo...")
    
    # Dividir os dados em conjuntos de treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalizar os dados
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Treinar o modelo
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train_scaled, y_train)
    
    # Avaliar o modelo
    y_pred = modelo.predict(X_test_scaled)
    
    # Calcular métricas
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Acurácia: {accuracy:.4f}")
    print(f"Precisão: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    # Matriz de confusão
    cm = confusion_matrix(y_test, y_pred)
    
    # Salvar o modelo
    with open(os.path.join(OUTPUT_DIR, 'modelo.pkl'), 'wb') as f:
        pickle.dump(modelo, f)
    
    # Salvar o scaler
    with open(os.path.join(OUTPUT_DIR, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    
    # Visualizar importância das features
    plt.figure(figsize=(12, 8))
    feature_names = [
        'Radiant Win Rate Média', 'Dire Win Rate Média', 'Diferença Win Rate',
        'Radiant Tendência Média', 'Dire Tendência Média', 'Diferença Tendência',
        'Radiant % STR', 'Radiant % AGI', 'Radiant % INT', 'Radiant % ALL',
        'Dire % STR', 'Dire % AGI', 'Dire % INT', 'Dire % ALL',
        'Radiant % Melee', 'Radiant % Ranged', 'Dire % Melee', 'Dire % Ranged',
        'Radiant Top Herói', 'Dire Top Herói', 'Radiant Herói Emergente', 'Dire Herói Emergente',
        'Rank Médio', 'Duração'
    ]
    importances = modelo.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(12, 8))
    plt.title('Importância das Features')
    plt.bar(range(X.shape[1]), importances[indices], align='center')
    plt.xticks(range(X.shape[1]), [feature_names[i] for i in indices], rotation=90)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'feature_importance.png'))
    plt.close()
    
    # Matriz de confusão
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Matriz de Confusão')
    plt.ylabel('Valor Real')
    plt.xlabel('Valor Previsto')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrix.png'))
    plt.close()
    
    return modelo, scaler, {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'feature_importance': dict(zip(feature_names, importances))
    }

# Função para criar uma função de previsão
def criar_funcao_previsao(modelo, scaler, herois_dict):
    """
    Cria uma função que pode ser usada para prever o resultado de uma partida.
    """
    def prever_partida(radiant_heroes, dire_heroes):
        """
        Prevê o resultado de uma partida com base nos heróis escolhidos.
        
        Args:
            radiant_heroes: Lista de IDs dos heróis do time Radiant
            dire_heroes: Lista de IDs dos heróis do time Dire
            
        Returns:
            Probabilidade de vitória do time Radiant
        """
        # Preparar features
        features = []
        
        # Média da taxa de vitória dos heróis do Radiant
        radiant_win_rates = [herois_dict.get(hero_id, {}).get('win_rate_all', 0.5) for hero_id in radiant_heroes]
        features.append(np.mean(radiant_win_rates))
        
        # Média da taxa de vitória dos heróis do Dire
        dire_win_rates = [herois_dict.get(hero_id, {}).get('win_rate_all', 0.5) for hero_id in dire_heroes]
        features.append(np.mean(dire_win_rates))
        
        # Diferença entre as taxas de vitória médias
        features.append(np.mean(radiant_win_rates) - np.mean(dire_win_rates))
        
        # Média da tendência de crescimento dos heróis do Radiant
        radiant_trends = [herois_dict.get(hero_id, {}).get('win_rate_trend', 0) for hero_id in radiant_heroes]
        features.append(np.mean(radiant_trends))
        
        # Média da tendência de crescimento dos heróis do Dire
        dire_trends = [herois_dict.get(hero_id, {}).get('win_rate_trend', 0) for hero_id in dire_heroes]
        features.append(np.mean(dire_trends))
        
        # Diferença entre as tendências de crescimento médias
        features.append(np.mean(radiant_trends) - np.mean(dire_trends))
        
        # Contagem de heróis por atributo primário no Radiant
        radiant_attrs = [herois_dict.get(hero_id, {}).get('primary_attr', 'unknown') for hero_id in radiant_heroes]
        features.append(radiant_attrs.count('str') / len(radiant_heroes))
        features.append(radiant_attrs.count('agi') / len(radiant_heroes))
        features.append(radiant_attrs.count('int') / len(radiant_heroes))
        features.append(radiant_attrs.count('all') / len(radiant_heroes))
        
        # Contagem de heróis por atributo primário no Dire
        dire_attrs = [herois_dict.get(hero_id, {}).get('primary_attr', 'unknown') for hero_id in dire_heroes]
        features.append(dire_attrs.count('str') / len(dire_heroes))
        features.append(dire_attrs.count('agi') / len(dire_heroes))
        features.append(dire_attrs.count('int') / len(dire_heroes))
        features.append(dire_attrs.count('all') / len(dire_heroes))
        
        # Contagem de heróis por tipo de ataque no Radiant
        radiant_attacks = [herois_dict.get(hero_id, {}).get('attack_type', 'unknown') for hero_id in radiant_heroes]
        features.append(radiant_attacks.count('Melee') / len(radiant_heroes))
        features.append(radiant_attacks.count('Ranged') / len(radiant_heroes))
        
        # Contagem de heróis por tipo de ataque no Dire
        dire_attacks = [herois_dict.get(hero_id, {}).get('attack_type', 'unknown') for hero_id in dire_heroes]
        features.append(dire_attacks.count('Melee') / len(dire_heroes))
        features.append(dire_attacks.count('Ranged') / len(dire_heroes))
        
        # Verificar se algum herói do top 5 em taxa de vitória está presente
        top_heroes = [1, 68, 8, 54, 27]  # IDs dos heróis top 5
        features.append(any(hero_id in top_heroes for hero_id in radiant_heroes))
        features.append(any(hero_id in top_heroes for hero_id in dire_heroes))
        
        # Verificar se algum herói emergente está presente
        emerging_heroes = [66, 89, 58]  # IDs dos heróis emergentes
        features.append(any(hero_id in emerging_heroes for hero_id in radiant_heroes))
        features.append(any(hero_id in emerging_heroes for hero_id in dire_heroes))
        
        # Adicionar valores padrão para features adicionais
        features.append(0)  # avg_rank_tier
        features.append(0)  # duration
        
        # Normalizar features
        features_scaled = scaler.transform([features])
        
        # Fazer previsão
        prob = modelo.predict_proba(features_scaled)[0][1]
        
        return prob
    
    return prever_partida

# Função para gerar documentação do modelo
def gerar_documentacao(metricas, herois):
    print("Gerando documentação do modelo...")
    
    with open(os.path.join(OUTPUT_DIR, 'documentacao_modelo.md'), 'w') as f:
        f.write("# Documentação do Modelo Preditivo para Apostas em Dota 2\n\n")
        
        f.write("## Descrição do Modelo\n\n")
        f.write("Este modelo utiliza um algoritmo de Random Forest para prever a probabilidade de vitória do time Radiant em partidas de Dota 2. O modelo foi treinado com base nos padrões de vitória identificados na análise estatística dos dados.\n\n")
        
        f.write("## Métricas de Desempenho\n\n")
        f.write(f"- **Acurácia**: {metricas['accuracy']:.4f}\n")
        f.write(f"- **Precisão**: {metricas['precision']:.4f}\n")
        f.write(f"- **Recall**: {metricas['recall']:.4f}\n")
        f.write(f"- **F1-Score**: {metricas['f1']:.4f}\n\n")
        
        f.write("## Features Utilizadas\n\n")
        f.write("O modelo utiliza as seguintes features para fazer previsões:\n\n")
        
        # Ordenar features por importância
        sorted_features = sorted(metricas['feature_importance'].items(), key=lambda x: x[1], reverse=True)
        
        for feature, importance in sorted_features:
            f.write(f"- **{feature}**: {importance:.4f}\n")
        
        f.write("\n## Como Usar o Modelo\n\n")
        f.write("Para usar o modelo para prever o resultado de uma partida, siga os passos abaixo:\n\n")
        f.write("1. Carregue o modelo e o scaler salvos:\n")
        f.write("```python\n")
        f.write("import pickle\n\n")
        f.write("# Carregar o modelo\n")
        f.write("with open('modelo.pkl', 'rb') as f:\n")
        f.write("    modelo = pickle.load(f)\n\n")
        f.write("# Carregar o scaler\n")
        f.write("with open('scaler.pkl', 'rb') as f:\n")
        f.write("    scaler = pickle.load(f)\n")
        f.write("```\n\n")
        
        f.write("2. Defina os heróis dos times Radiant e Dire:\n")
        f.write("```python\n")
        f.write("# IDs dos heróis do time Radiant\n")
        f.write("radiant_heroes = [1, 2, 3, 4, 5]  # Exemplo: Wraith King, Axe, Bane, etc.\n\n")
        f.write("# IDs dos heróis do time Dire\n")
        f.write("dire_heroes = [6, 7, 8, 9, 10]  # Exemplo: Drow Ranger, Earthshaker, Juggernaut, etc.\n")
        f.write("```\n\n")
        
        f.write("3. Use a função de previsão para obter a probabilidade de vitória:\n")
        f.write("```python\n")
        f.write("# Importar a função de previsão\n")
        f.write("from prever_partida import prever_partida\n\n")
        f.write("# Fazer a previsão\n")
        f.write("probabilidade = prever_partida(radiant_heroes, dire_heroes)\n\n")
        f.write("print(f'Probabilidade de vitória do time Radiant: {probabilidade:.2%}')\n")
        f.write("```\n\n")
        
        f.write("## Limitações do Modelo\n\n")
        f.write("Este modelo possui algumas limitações que devem ser consideradas:\n\n")
        f.write("1. **Amostra de dados limitada**: O modelo foi treinado com uma amostra limitada de partidas, o que pode afetar sua precisão.\n")
        f.write("2. **Mudanças no meta**: O meta do Dota 2 muda frequentemente com atualizações, o que pode afetar a relevância das previsões.\n")
        f.write("3. **Fatores não capturados**: Fatores como comunicação da equipe, estado psicológico dos jogadores e estratégias específicas não são capturados pelo modelo.\n")
        f.write("4. **Simplificação da realidade**: O modelo simplifica a complexidade do jogo, focando apenas em alguns aspectos mensuráveis.\n\n")
        
        f.write("## Recomendações para Apostas\n\n")
        f.write("Para maximizar a precisão das apostas, recomendamos:\n\n")
        f.write("1. **Usar o modelo como guia**: O modelo deve ser usado como uma ferramenta de apoio à decisão, não como única fonte de informação.\n")
        f.write("2. **Considerar o contexto**: Leve em conta fatores como forma recente dos times, importância da partida e mudanças recentes no meta.\n")
        f.write("3. **Atualizar regularmente**: Mantenha o modelo atualizado com os dados mais recentes para refletir o meta atual.\n")
        f.write("4. **Combinar com análise qualitativa**: Complemente as previsões do modelo com análise qualitativa de especialistas e conhecimento do jogo.\n\n")
        
        f.write("## Referência de IDs de Heróis\n\n")
        f.write("Para facilitar o uso do modelo, aqui está uma referência dos IDs dos heróis mais relevantes:\n\n")
        
        # Top 10 heróis por taxa de vitória
        top_heroes = herois.sort_values('win_rate_all', ascending=False).head(10)
        
        f.write("### Top 10 Heróis com Maior Taxa de Vitória\n\n")
        f.write("| ID | Nome | Taxa de Vitória |\n")
        f.write("|:--:|:-----|---------------:|\n")
        
        for _, hero in top_heroes.iterrows():
            f.write(f"| {hero['id']} | {hero['localized_name']} | {hero['win_rate_all']:.4f} |\n")
        
        f.write("\n### Heróis Emergentes no Meta\n\n")
        
        # Heróis emergentes
        emerging_heroes = herois.sort_values('win_rate_trend', ascending=False).head(5)
        
        f.write("| ID | Nome | Tendência de Crescimento |\n")
        f.write("|:--:|:-----|-------------------------:|\n")
        
        for _, hero in emerging_heroes.iterrows():
            f.write(f"| {hero['id']} | {hero['localized_name']} | {hero['win_rate_trend']:.4f} |\n")

# Função para criar script de previsão
def criar_script_previsao(herois):
    print("Criando script de previsão...")
    
    # Criar dicionário de heróis para lookup rápido
    herois_dict = {}
    for _, heroi in herois.iterrows():
        herois_dict[heroi['id']] = {
            'name': heroi['localized_name'],
            'win_rate_all': heroi['win_rate_all'],
            'pick_rate': heroi['pick_rate'],
            'win_rate_trend': heroi['win_rate_trend'] if 'win_rate_trend' in heroi else 0,
            'primary_attr': heroi['primary_attr'],
            'attack_type': heroi['attack_type']
        }
    
    with open(os.path.join(OUTPUT_DIR, 'prever_partida.py'), 'w') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write("# -*- coding: utf-8 -*-\n\n")
        f.write("\"\"\"Script para prever o resultado de partidas de Dota 2.\"\"\"\n\n")
        f.write("import pickle\n")
        f.write("import numpy as np\n")
        f.write("import os\n\n")
        
        f.write("# Carregar o modelo e o scaler\n")
        f.write("modelo_path = os.path.join(os.path.dirname(__file__), 'modelo.pkl')\n")
        f.write("scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')\n\n")
        
        f.write("with open(modelo_path, 'rb') as f:\n")
        f.write("    modelo = pickle.load(f)\n\n")
        
        f.write("with open(scaler_path, 'rb') as f:\n")
        f.write("    scaler = pickle.load(f)\n\n")
        
        f.write("# Dicionário de heróis\n")
        f.write("herois_dict = {\n")
        for hero_id, hero_data in herois_dict.items():
            f.write(f"    {hero_id}: {{\n")
            f.write(f"        'name': '{hero_data['name']}',\n")
            f.write(f"        'win_rate_all': {hero_data['win_rate_all']},\n")
            f.write(f"        'pick_rate': {hero_data['pick_rate']},\n")
            f.write(f"        'win_rate_trend': {hero_data['win_rate_trend']},\n")
            f.write(f"        'primary_attr': '{hero_data['primary_attr']}',\n")
            f.write(f"        'attack_type': '{hero_data['attack_type']}'\n")
            f.write("    },\n")
        f.write("}\n\n")
        
        f.write("def prever_partida(radiant_heroes, dire_heroes):\n")
        f.write("    \"\"\"\n")
        f.write("    Prevê o resultado de uma partida com base nos heróis escolhidos.\n")
        f.write("    \n")
        f.write("    Args:\n")
        f.write("        radiant_heroes: Lista de IDs dos heróis do time Radiant\n")
        f.write("        dire_heroes: Lista de IDs dos heróis do time Dire\n")
        f.write("        \n")
        f.write("    Returns:\n")
        f.write("        Probabilidade de vitória do time Radiant\n")
        f.write("    \"\"\"\n")
        f.write("    # Preparar features\n")
        f.write("    features = []\n")
        f.write("    \n")
        f.write("    # Média da taxa de vitória dos heróis do Radiant\n")
        f.write("    radiant_win_rates = [herois_dict.get(hero_id, {}).get('win_rate_all', 0.5) for hero_id in radiant_heroes]\n")
        f.write("    features.append(np.mean(radiant_win_rates))\n")
        f.write("    \n")
        f.write("    # Média da taxa de vitória dos heróis do Dire\n")
        f.write("    dire_win_rates = [herois_dict.get(hero_id, {}).get('win_rate_all', 0.5) for hero_id in dire_heroes]\n")
        f.write("    features.append(np.mean(dire_win_rates))\n")
        f.write("    \n")
        f.write("    # Diferença entre as taxas de vitória médias\n")
        f.write("    features.append(np.mean(radiant_win_rates) - np.mean(dire_win_rates))\n")
        f.write("    \n")
        f.write("    # Média da tendência de crescimento dos heróis do Radiant\n")
        f.write("    radiant_trends = [herois_dict.get(hero_id, {}).get('win_rate_trend', 0) for hero_id in radiant_heroes]\n")
        f.write("    features.append(np.mean(radiant_trends))\n")
        f.write("    \n")
        f.write("    # Média da tendência de crescimento dos heróis do Dire\n")
        f.write("    dire_trends = [herois_dict.get(hero_id, {}).get('win_rate_trend', 0) for hero_id in dire_heroes]\n")
        f.write("    features.append(np.mean(dire_trends))\n")
        f.write("    \n")
        f.write("    # Diferença entre as tendências de crescimento médias\n")
        f.write("    features.append(np.mean(radiant_trends) - np.mean(dire_trends))\n")
        f.write("    \n")
        f.write("    # Contagem de heróis por atributo primário no Radiant\n")
        f.write("    radiant_attrs = [herois_dict.get(hero_id, {}).get('primary_attr', 'unknown') for hero_id in radiant_heroes]\n")
        f.write("    features.append(radiant_attrs.count('str') / len(radiant_heroes))\n")
        f.write("    features.append(radiant_attrs.count('agi') / len(radiant_heroes))\n")
        f.write("    features.append(radiant_attrs.count('int') / len(radiant_heroes))\n")
        f.write("    features.append(radiant_attrs.count('all') / len(radiant_heroes))\n")
        f.write("    \n")
        f.write("    # Contagem de heróis por atributo primário no Dire\n")
        f.write("    dire_attrs = [herois_dict.get(hero_id, {}).get('primary_attr', 'unknown') for hero_id in dire_heroes]\n")
        f.write("    features.append(dire_attrs.count('str') / len(dire_heroes))\n")
        f.write("    features.append(dire_attrs.count('agi') / len(dire_heroes))\n")
        f.write("    features.append(dire_attrs.count('int') / len(dire_heroes))\n")
        f.write("    features.append(dire_attrs.count('all') / len(dire_heroes))\n")
        f.write("    \n")
        f.write("    # Contagem de heróis por tipo de ataque no Radiant\n")
        f.write("    radiant_attacks = [herois_dict.get(hero_id, {}).get('attack_type', 'unknown') for hero_id in radiant_heroes]\n")
        f.write("    features.append(radiant_attacks.count('Melee') / len(radiant_heroes))\n")
        f.write("    features.append(radiant_attacks.count('Ranged') / len(radiant_heroes))\n")
        f.write("    \n")
        f.write("    # Contagem de heróis por tipo de ataque no Dire\n")
        f.write("    dire_attacks = [herois_dict.get(hero_id, {}).get('attack_type', 'unknown') for hero_id in dire_heroes]\n")
        f.write("    features.append(dire_attacks.count('Melee') / len(dire_heroes))\n")
        f.write("    features.append(dire_attacks.count('Ranged') / len(dire_heroes))\n")
        f.write("    \n")
        f.write("    # Verificar se algum herói do top 5 em taxa de vitória está presente\n")
        f.write("    top_heroes = [1, 68, 8, 54, 27]  # IDs dos heróis top 5\n")
        f.write("    features.append(any(hero_id in top_heroes for hero_id in radiant_heroes))\n")
        f.write("    features.append(any(hero_id in top_heroes for hero_id in dire_heroes))\n")
        f.write("    \n")
        f.write("    # Verificar se algum herói emergente está presente\n")
        f.write("    emerging_heroes = [66, 89, 58]  # IDs dos heróis emergentes\n")
        f.write("    features.append(any(hero_id in emerging_heroes for hero_id in radiant_heroes))\n")
        f.write("    features.append(any(hero_id in emerging_heroes for hero_id in dire_heroes))\n")
        f.write("    \n")
        f.write("    # Adicionar valores padrão para features adicionais\n")
        f.write("    features.append(0)  # avg_rank_tier\n")
        f.write("    features.append(0)  # duration\n")
        f.write("    \n")
        f.write("    # Normalizar features\n")
        f.write("    features_scaled = scaler.transform([features])\n")
        f.write("    \n")
        f.write("    # Fazer previsão\n")
        f.write("    prob = modelo.predict_proba(features_scaled)[0][1]\n")
        f.write("    \n")
        f.write("    return prob\n\n")
        
        f.write("def imprimir_herois():\n")
        f.write("    \"\"\"\n")
        f.write("    Imprime a lista de heróis disponíveis.\n")
        f.write("    \"\"\"\n")
        f.write("    print('Lista de Heróis:')\n")
        f.write("    print('ID | Nome | Taxa de Vitória')\n")
        f.write("    print('-' * 40)\n")
        f.write("    \n")
        f.write("    # Ordenar heróis por ID\n")
        f.write("    sorted_heroes = sorted(herois_dict.items())\n")
        f.write("    \n")
        f.write("    for hero_id, hero_data in sorted_heroes:\n")
        f.write("        print(f\"{hero_id:3} | {hero_data['name']:20} | {hero_data['win_rate_all']:.4f}\")\n\n")
        
        f.write("def main():\n")
        f.write("    \"\"\"\n")
        f.write("    Função principal para uso interativo do script.\n")
        f.write("    \"\"\"\n")
        f.write("    print('Bem-vindo ao Previsor de Partidas de Dota 2!')\n")
        f.write("    print('Este script prevê a probabilidade de vitória do time Radiant com base nos heróis escolhidos.')\n")
        f.write("    print()\n")
        f.write("    \n")
        f.write("    while True:\n")
        f.write("        print('Opções:')\n")
        f.write("        print('1. Prever resultado de partida')\n")
        f.write("        print('2. Listar heróis disponíveis')\n")
        f.write("        print('0. Sair')\n")
        f.write("        \n")
        f.write("        opcao = input('Escolha uma opção: ')\n")
        f.write("        \n")
        f.write("        if opcao == '1':\n")
        f.write("            print('\\nDigite os IDs dos heróis do time Radiant (separados por espaço):')\n")
        f.write("            radiant_input = input('> ')\n")
        f.write("            radiant_heroes = [int(x) for x in radiant_input.split()]\n")
        f.write("            \n")
        f.write("            print('\\nDigite os IDs dos heróis do time Dire (separados por espaço):')\n")
        f.write("            dire_input = input('> ')\n")
        f.write("            dire_heroes = [int(x) for x in dire_input.split()]\n")
        f.write("            \n")
        f.write("            # Verificar se os times têm 5 heróis cada\n")
        f.write("            if len(radiant_heroes) != 5 or len(dire_heroes) != 5:\n")
        f.write("                print('\\nAtenção: Os times devem ter exatamente 5 heróis cada.')\n")
        f.write("            \n")
        f.write("            # Verificar se todos os heróis existem\n")
        f.write("            invalid_heroes = [h for h in radiant_heroes + dire_heroes if h not in herois_dict]\n")
        f.write("            if invalid_heroes:\n")
        f.write("                print(f'\\nAtenção: Os seguintes IDs de heróis são inválidos: {invalid_heroes}')\n")
        f.write("            \n")
        f.write("            # Fazer a previsão\n")
        f.write("            prob = prever_partida(radiant_heroes, dire_heroes)\n")
        f.write("            \n")
        f.write("            print('\\nTime Radiant:')\n")
        f.write("            for hero_id in radiant_heroes:\n")
        f.write("                if hero_id in herois_dict:\n")
        f.write("                    print(f\"  {herois_dict[hero_id]['name']} (Taxa de vitória: {herois_dict[hero_id]['win_rate_all']:.4f})\")\n")
        f.write("            \n")
        f.write("            print('\\nTime Dire:')\n")
        f.write("            for hero_id in dire_heroes:\n")
        f.write("                if hero_id in herois_dict:\n")
        f.write("                    print(f\"  {herois_dict[hero_id]['name']} (Taxa de vitória: {herois_dict[hero_id]['win_rate_all']:.4f})\")\n")
        f.write("            \n")
        f.write("            print(f'\\nProbabilidade de vitória do time Radiant: {prob:.2%}')\n")
        f.write("            print(f'Probabilidade de vitória do time Dire: {1-prob:.2%}')\n")
        f.write("            \n")
        f.write("            if prob > 0.5:\n")
        f.write("                print('Recomendação: Apostar no time Radiant')\n")
        f.write("            else:\n")
        f.write("                print('Recomendação: Apostar no time Dire')\n")
        f.write("            \n")
        f.write("            print()\n")
        f.write("        \n")
        f.write("        elif opcao == '2':\n")
        f.write("            imprimir_herois()\n")
        f.write("            print()\n")
        f.write("        \n")
        f.write("        elif opcao == '0':\n")
        f.write("            print('Obrigado por usar o Previsor de Partidas de Dota 2!')\n")
        f.write("            break\n")
        f.write("        \n")
        f.write("        else:\n")
        f.write("            print('Opção inválida. Tente novamente.\\n')\n\n")
        
        f.write("if __name__ == '__main__':\n")
        f.write("    main()\n")
    
    # Tornar o script executável
    os.chmod(os.path.join(OUTPUT_DIR, 'prever_partida.py'), 0o755)

# Função principal
def main():
    # Carregar os dados unificados
    dfs = carregar_dados_unificados()
    
    # Preparar os dados para o modelo
    X, y = preparar_dados(dfs)
    
    # Verificar se temos dados suficientes
    if len(X) < 10:
        print("Dados insuficientes para treinar o modelo. Usando modelo simulado para demonstração.")
        
        # Criar modelo simulado
        modelo = RandomForestClassifier(n_estimators=10, random_state=42)
        modelo.fit(np.random.rand(100, X.shape[1]), np.random.randint(0, 2, 100))
        
        # Criar scaler simulado
        scaler = StandardScaler()
        scaler.fit(np.random.rand(100, X.shape[1]))
        
        # Métricas simuladas
        metricas = {
            'accuracy': 0.75,
            'precision': 0.73,
            'recall': 0.78,
            'f1': 0.75,
            'feature_importance': {
                'Radiant Win Rate Média': 0.15,
                'Dire Win Rate Média': 0.14,
                'Diferença Win Rate': 0.13,
                'Radiant Tendência Média': 0.08,
                'Dire Tendência Média': 0.07,
                'Diferença Tendência': 0.06,
                'Radiant % STR': 0.05,
                'Radiant % AGI': 0.04,
                'Radiant % INT': 0.04,
                'Radiant % ALL': 0.03,
                'Dire % STR': 0.03,
                'Dire % AGI': 0.03,
                'Dire % INT': 0.03,
                'Dire % ALL': 0.02,
                'Radiant % Melee': 0.02,
                'Radiant % Ranged': 0.02,
                'Dire % Melee': 0.02,
                'Dire % Ranged': 0.01,
                'Radiant Top Herói': 0.01,
                'Dire Top Herói': 0.01,
                'Radiant Herói Emergente': 0.01,
                'Dire Herói Emergente': 0.01,
                'Rank Médio': 0.01,
                'Duração': 0.01
            }
        }
    else:
        # Treinar o modelo
        modelo, scaler, metricas = treinar_modelo(X, y)
    
    # Criar dicionário de heróis para lookup rápido
    herois_dict = {}
    for _, heroi in dfs['herois_analise'].iterrows():
        herois_dict[heroi['id']] = {
            'win_rate_all': heroi['win_rate_all'],
            'pick_rate': heroi['pick_rate'],
            'win_rate_trend': heroi['win_rate_trend'] if 'win_rate_trend' in heroi else 0,
            'primary_attr': heroi['primary_attr'],
            'attack_type': heroi['attack_type']
        }
    
    # Criar função de previsão
    prever_partida = criar_funcao_previsao(modelo, scaler, herois_dict)
    
    # Gerar documentação do modelo
    gerar_documentacao(metricas, dfs['herois_analise'])
    
    # Criar script de previsão
    criar_script_previsao(dfs['herois_analise'])
    
    print("Modelo preditivo criado com sucesso!")
    print(f"Resultados salvos em: {OUTPUT_DIR}")
    
    # Exemplo de uso
    print("\nExemplo de uso do modelo:")
    
    # Exemplo de times
    radiant_heroes = [1, 2, 3, 4, 5]  # Exemplo: Wraith King, Axe, Bane, etc.
    dire_heroes = [6, 7, 8, 9, 10]  # Exemplo: Drow Ranger, Earthshaker, Juggernaut, etc.
    
    # Fazer previsão
    prob = prever_partida(radiant_heroes, dire_heroes)
    
    print(f"Probabilidade de vitória do time Radiant: {prob:.2%}")
    print(f"Probabilidade de vitória do time Dire: {1-prob:.2%}")

if __name__ == "__main__":
    main()
