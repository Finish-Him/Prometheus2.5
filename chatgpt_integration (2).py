"""
Módulo para integração do Oráculo 4.0 com ChatGPT
"""

import json
import requests
import base64
from typing import Dict, Any, List, Optional, Union

# Configuração da API
API_BASE_URL = "http://localhost:8000"  # Altere para o URL público quando disponível
API_KEY = "oraculo_v4_api_key_manus_integration_2025_04_24_8f7d3e1a9b2c5d6e"

# Headers para requisições
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def process_text(text: str) -> Dict[str, Any]:
    """
    Processa texto através da API do Oráculo 4.0
    
    Args:
        text: Texto contendo informações da partida
        
    Returns:
        Dicionário com dados da partida e previsões
    """
    url = f"{API_BASE_URL}/process/text"
    payload = {"text": text}
    
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    
    return response.json()

def process_image(image_path: str) -> Dict[str, Any]:
    """
    Processa imagem através da API do Oráculo 4.0
    
    Args:
        image_path: Caminho para o arquivo de imagem
        
    Returns:
        Dicionário com dados da partida e previsões
    """
    url = f"{API_BASE_URL}/process/image"
    
    # Ler imagem e converter para base64
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    payload = {"image_base64": image_data}
    
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    
    return response.json()

def process_form(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa dados de formulário através da API do Oráculo 4.0
    
    Args:
        form_data: Dados do formulário
        
    Returns:
        Dicionário com dados da partida e previsões
    """
    url = f"{API_BASE_URL}/process/form"
    
    response = requests.post(url, headers=HEADERS, json=form_data)
    response.raise_for_status()
    
    return response.json()

def save_to_history(match_data: Dict[str, Any], predictions: Dict[str, Any]) -> str:
    """
    Salva previsão no histórico
    
    Args:
        match_data: Dados da partida
        predictions: Previsões geradas
        
    Returns:
        ID do registro salvo
    """
    url = f"{API_BASE_URL}/history/save"
    payload = {
        "match_data": match_data,
        "predictions": predictions
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    
    return response.json()["record_id"]

def get_history_list(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Obtém lista de registros do histórico
    
    Args:
        limit: Número máximo de registros a retornar
        
    Returns:
        Lista de registros do histórico
    """
    url = f"{API_BASE_URL}/history/list?limit={limit}"
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    return response.json()["records"]

def get_history_item(record_id: str) -> Dict[str, Any]:
    """
    Obtém um registro específico do histórico
    
    Args:
        record_id: ID do registro
        
    Returns:
        Registro do histórico
    """
    url = f"{API_BASE_URL}/history/{record_id}"
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    return response.json()

def format_prediction_for_chatgpt(prediction_data: Dict[str, Any]) -> str:
    """
    Formata os dados de previsão para exibição no ChatGPT
    
    Args:
        prediction_data: Dados da previsão
        
    Returns:
        Texto formatado para exibição
    """
    match_data = prediction_data["match_data"]
    predictions = prediction_data["predictions"]
    
    # Formatar cabeçalho
    header = f"# Previsão: {match_data['time_radiant']} vs {match_data['time_dire']}\n"
    header += f"## {match_data['torneio']}\n\n"
    header += f"Odds: {match_data['time_radiant']} ({match_data['odds']['vitoria_radiant']}) vs "
    header += f"{match_data['time_dire']} ({match_data['odds']['vitoria_dire']})\n\n"
    
    # Formatar previsões
    prev_section = "## Previsões\n\n"
    
    # Duração
    duracao = predictions["previsoes"]["duracao_partida"]
    prev_section += f"### Duração da Partida\n"
    prev_section += f"- **Previsão**: {duracao['valor']} minutos\n"
    prev_section += f"- **Range**: {duracao['range'][0]} - {duracao['range'][1]} minutos\n"
    prev_section += f"- **Confiança**: {int(duracao['confianca']*100)}%\n\n"
    
    # Total de kills
    kills = predictions["previsoes"]["total_kills"]
    prev_section += f"### Total de Abates\n"
    prev_section += f"- **Previsão**: {kills['valor']} kills\n"
    prev_section += f"- **Range**: {kills['range'][0]} - {kills['range'][1]} kills\n"
    prev_section += f"- **Confiança**: {int(kills['confianca']*100)}%\n\n"
    
    # Diferença de kills
    diff = predictions["previsoes"]["diferenca_kills"]
    prev_section += f"### Diferença de Abates\n"
    prev_section += f"- **Previsão**: {diff['valor']} kills\n"
    prev_section += f"- **Range**: {diff['range'][0]} - {diff['range'][1]} kills\n"
    prev_section += f"- **Confiança**: {int(diff['confianca']*100)}%\n\n"
    
    # Formatar valuebets
    vb_section = "## Valuebets Recomendadas\n\n"
    
    if not predictions["valuebets"]:
        vb_section += "Nenhuma valuebet identificada para esta partida.\n\n"
    else:
        for i, vb in enumerate(predictions["valuebets"], 1):
            vb_section += f"### Valuebet {i}: {vb['mercado']}\n"
            vb_section += f"- **Recomendação**: {vb['recomendacao']}\n"
            vb_section += f"- **Odds**: {vb['odds']}\n"
            vb_section += f"- **Valor Esperado**: +{(vb['valor_esperado']*100):.1f}%\n"
            vb_section += f"- **Confiança**: {int(vb['confianca']*100)}%\n\n"
    
    # Formatar explicações
    exp_section = "## Explicações\n\n"
    
    for exp in predictions["explicacao"]["fatores_chave"]:
        exp_section += f"- {exp}\n"
    
    # Combinar tudo
    return header + prev_section + vb_section + exp_section

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo de processamento de texto
    text_data = """
    Team Spirit vs NaVi Junior
    PGL Wallachia Season 4
    
    Odds Team Spirit: 1.16
    Odds NaVi Junior: 4.88
    
    Handicap de kills: 8.5
    Odds over: 1.90
    Odds under: 1.80
    
    Duração da partida: 32.5
    Odds over: 1.85
    Odds under: 1.85
    
    Total de kills: 48.5
    Odds over: 1.90
    Odds under: 1.80
    """
    
    result = process_text(text_data)
    formatted_result = format_prediction_for_chatgpt(result)
    print(formatted_result)
