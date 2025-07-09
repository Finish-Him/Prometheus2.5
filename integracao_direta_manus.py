"""
Integração direta entre o ChatGPT e o back-end do Manus (API Oráculo 4.0)

Este módulo fornece funções que podem ser chamadas diretamente pelo ChatGPT
para processar dados através da API do Oráculo 4.0 sem a necessidade de um plugin completo.
"""

import json
import requests
import base64
import os
from typing import Dict, Any, List, Optional, Union
from io import BytesIO
from PIL import Image

# Configuração da API
API_BASE_URL = os.environ.get("ORACULO_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("ORACULO_API_KEY", "oraculo_v4_api_key_manus_integration_2025_04_24_8f7d3e1a9b2c5d6e")

# Headers para requisições
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def analisar_partida_texto(texto_partida: str) -> str:
    """
    Analisa texto de partida e retorna previsões formatadas para o ChatGPT.
    
    Esta função pode ser chamada diretamente pelo ChatGPT para processar
    informações de partida em formato de texto.
    
    Args:
        texto_partida: Texto contendo informações da partida
        
    Returns:
        Texto formatado com as previsões
    """
    try:
        # Chamar a API do Oráculo 4.0
        url = f"{API_BASE_URL}/process/text"
        payload = {"text": texto_partida}
        
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        # Formatar o resultado para exibição
        result = response.json()
        return format_prediction_for_chatgpt(result)
    except Exception as e:
        return f"Erro ao processar texto: {str(e)}"

def analisar_partida_imagem(imagem_base64: str) -> str:
    """
    Analisa imagem de partida e retorna previsões formatadas para o ChatGPT.
    
    Esta função pode ser chamada diretamente pelo ChatGPT para processar
    informações de partida em formato de imagem.
    
    Args:
        imagem_base64: Imagem em formato base64
        
    Returns:
        Texto formatado com as previsões
    """
    try:
        # Chamar a API do Oráculo 4.0
        url = f"{API_BASE_URL}/process/image"
        payload = {"image_base64": imagem_base64}
        
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        # Formatar o resultado para exibição
        result = response.json()
        return format_prediction_for_chatgpt(result)
    except Exception as e:
        return f"Erro ao processar imagem: {str(e)}"

def analisar_partida_formulario(dados_formulario: Dict[str, Any]) -> str:
    """
    Analisa dados de formulário e retorna previsões formatadas para o ChatGPT.
    
    Esta função pode ser chamada diretamente pelo ChatGPT para processar
    informações de partida em formato de formulário.
    
    Args:
        dados_formulario: Dicionário com dados do formulário
        
    Returns:
        Texto formatado com as previsões
    """
    try:
        # Chamar a API do Oráculo 4.0
        url = f"{API_BASE_URL}/process/form"
        
        response = requests.post(url, headers=HEADERS, json=dados_formulario)
        response.raise_for_status()
        
        # Formatar o resultado para exibição
        result = response.json()
        return format_prediction_for_chatgpt(result)
    except Exception as e:
        return f"Erro ao processar formulário: {str(e)}"

def obter_historico(limite: int = 5) -> str:
    """
    Obtém o histórico de previsões e retorna formatado para o ChatGPT.
    
    Esta função pode ser chamada diretamente pelo ChatGPT para obter
    o histórico de previsões.
    
    Args:
        limite: Número máximo de registros a retornar
        
    Returns:
        Texto formatado com o histórico
    """
    try:
        # Chamar a API do Oráculo 4.0
        url = f"{API_BASE_URL}/history/list?limit={limite}"
        
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        # Formatar o resultado para exibição
        records = response.json()["records"]
        
        if not records:
            return "Nenhum registro encontrado no histórico."
        
        result = "# Histórico de Previsões\n\n"
        
        for i, record in enumerate(records, 1):
            match_data = record.get("match_data", {})
            result += f"## {i}. {match_data.get('time_radiant', 'Time A')} vs {match_data.get('time_dire', 'Time B')}\n"
            result += f"**Torneio**: {match_data.get('torneio', 'Desconhecido')}\n"
            result += f"**ID**: {record.get('id', 'N/A')}\n"
            result += f"**Data**: {record.get('timestamp', 'N/A')}\n\n"
        
        return result
    except Exception as e:
        return f"Erro ao obter histórico: {str(e)}"

def obter_detalhe_historico(record_id: str) -> str:
    """
    Obtém detalhes de um registro específico do histórico.
    
    Esta função pode ser chamada diretamente pelo ChatGPT para obter
    detalhes de uma previsão específica.
    
    Args:
        record_id: ID do registro
        
    Returns:
        Texto formatado com os detalhes da previsão
    """
    try:
        # Chamar a API do Oráculo 4.0
        url = f"{API_BASE_URL}/history/{record_id}"
        
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        # Formatar o resultado para exibição
        result = response.json()
        return format_prediction_for_chatgpt(result)
    except Exception as e:
        return f"Erro ao obter detalhes do registro: {str(e)}"

def format_prediction_for_chatgpt(prediction_data: Dict[str, Any]) -> str:
    """
    Formata os dados de previsão para exibição no ChatGPT
    
    Args:
        prediction_data: Dados da previsão
        
    Returns:
        Texto formatado para exibição
    """
    try:
        match_data = prediction_data.get("match_data", {})
        predictions = prediction_data.get("predictions", {})
        
        if not match_data or not predictions:
            return "Dados de previsão incompletos ou inválidos."
        
        # Formatar cabeçalho
        header = f"# Previsão: {match_data.get('time_radiant', 'Time A')} vs {match_data.get('time_dire', 'Time B')}\n"
        header += f"## {match_data.get('torneio', 'Torneio não especificado')}\n\n"
        
        odds = match_data.get('odds', {})
        if odds:
            header += f"Odds: {match_data.get('time_radiant', 'Time A')} ({odds.get('vitoria_radiant', 'N/A')}) vs "
            header += f"{match_data.get('time_dire', 'Time B')} ({odds.get('vitoria_dire', 'N/A')})\n\n"
        
        # Formatar previsões
        prev_section = "## Previsões\n\n"
        
        previsoes = predictions.get("previsoes", {})
        if previsoes:
            # Duração
            duracao = previsoes.get("duracao_partida", {})
            if duracao:
                prev_section += f"### Duração da Partida\n"
                prev_section += f"- **Previsão**: {duracao.get('valor', 'N/A')} minutos\n"
                range_val = duracao.get('range', [0, 0])
                prev_section += f"- **Range**: {range_val[0]} - {range_val[1]} minutos\n"
                confianca = duracao.get('confianca', 0)
                prev_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
            
            # Total de kills
            kills = previsoes.get("total_kills", {})
            if kills:
                prev_section += f"### Total de Abates\n"
                prev_section += f"- **Previsão**: {kills.get('valor', 'N/A')} kills\n"
                range_val = kills.get('range', [0, 0])
                prev_section += f"- **Range**: {range_val[0]} - {range_val[1]} kills\n"
                confianca = kills.get('confianca', 0)
                prev_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
            
            # Diferença de kills
            diff = previsoes.get("diferenca_kills", {})
            if diff:
                prev_section += f"### Diferença de Abates\n"
                prev_section += f"- **Previsão**: {diff.get('valor', 'N/A')} kills\n"
                range_val = diff.get('range', [0, 0])
                prev_section += f"- **Range**: {range_val[0]} - {range_val[1]} kills\n"
                confianca = diff.get('confianca', 0)
                prev_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
        
        # Formatar valuebets
        vb_section = "## Valuebets Recomendadas\n\n"
        
        valuebets = predictions.get("valuebets", [])
        if not valuebets:
            vb_section += "Nenhuma valuebet identificada para esta partida.\n\n"
        else:
            for i, vb in enumerate(valuebets, 1):
                vb_section += f"### Valuebet {i}: {vb.get('mercado', 'N/A')}\n"
                vb_section += f"- **Recomendação**: {vb.get('recomendacao', 'N/A')}\n"
                vb_section += f"- **Odds**: {vb.get('odds', 'N/A')}\n"
                valor_esperado = vb.get('valor_esperado', 0)
                vb_section += f"- **Valor Esperado**: +{(valor_esperado*100):.1f}%\n"
                confianca = vb.get('confianca', 0)
                vb_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
        
        # Formatar explicações
        exp_section = "## Explicações\n\n"
        
        explicacao = predictions.get("explicacao", {})
        fatores_chave = explicacao.get("fatores_chave", [])
        if not fatores_chave:
            exp_section += "Nenhuma explicação disponível para esta previsão.\n"
        else:
            for exp in fatores_chave:
                exp_section += f"- {exp}\n"
        
        # Combinar tudo
        return header + prev_section + vb_section + exp_section
    except Exception as e:
        return f"Erro ao formatar previsão: {str(e)}"

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
    
    result = analisar_partida_texto(text_data)
    print(result)
