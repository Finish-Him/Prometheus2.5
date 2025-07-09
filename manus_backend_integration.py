"""
Módulo para integração direta com o backend do Manus para processamento de dados de partidas
"""

import json
import requests
import base64
from typing import Dict, Any, List, Optional, Union

# Configuração da API
API_BASE_URL = "http://localhost:8000"  # URL do backend do Manus
API_KEY = "oraculo_v4_api_key_manus_integration_2025_04_24_8f7d3e1a9b2c5d6e"

# Headers para requisições
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def processar_texto(texto: str) -> Dict[str, Any]:
    """
    Processa texto através da API do Manus
    
    Args:
        texto: Texto contendo informações da partida
        
    Returns:
        Dicionário com dados da partida e previsões
    """
    url = f"{API_BASE_URL}/process/text"
    payload = {"text": texto}
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao processar texto: {str(e)}")
        # Simulação de resposta para desenvolvimento
        return simular_resposta_backend(texto)

def formatar_previsao(prediction_data: Dict[str, Any]) -> str:
    """
    Formata os dados de previsão para exibição
    
    Args:
        prediction_data: Dados da previsão
        
    Returns:
        Texto formatado para exibição
    """
    match_data = prediction_data.get("match_data", {})
    predictions = prediction_data.get("predictions", {})
    
    # Formatar cabeçalho
    header = f"# Análise: {match_data.get('time_radiant', 'Time A')} vs {match_data.get('time_dire', 'Time B')}\n\n"
    
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
    exp_section = "## Análise Detalhada\n\n"
    
    explicacao = predictions.get("explicacao", {})
    fatores_chave = explicacao.get("fatores_chave", [])
    if not fatores_chave:
        exp_section += "Sem análise detalhada disponível para esta partida.\n"
    else:
        for exp in fatores_chave:
            exp_section += f"- {exp}\n"
    
    # Combinar tudo
    return header + prev_section + vb_section + exp_section

def simular_resposta_backend(texto: str) -> Dict[str, Any]:
    """
    Simula uma resposta do backend para desenvolvimento
    
    Args:
        texto: Texto contendo informações da partida
        
    Returns:
        Dicionário simulando dados da partida e previsões
    """
    # Extrair times do texto
    lines = texto.strip().split('\n')
    times = lines[0].split(' vs ')
    time_radiant = times[0].strip()
    time_dire = times[1].strip() if len(times) > 1 else "Time B"
    
    # Extrair odds de vitória se disponíveis
    odds_vitoria_radiant = 2.35  # Valor padrão
    odds_vitoria_dire = 1.52  # Valor padrão
    
    for line in lines:
        if "Odds vencedor" in line or "Odds Vencedor" in line:
            try:
                odds_line_index = lines.index(line)
                odds_radiant_line = lines[odds_line_index + 1]
                odds_dire_line = lines[odds_line_index + 2]
                
                odds_vitoria_radiant = float(odds_radiant_line.split(':')[1].strip())
                odds_vitoria_dire = float(odds_dire_line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
    
    # Criar resposta simulada
    return {
        "match_data": {
            "time_radiant": time_radiant,
            "time_dire": time_dire,
            "torneio": "Torneio não especificado",
            "odds": {
                "vitoria_radiant": odds_vitoria_radiant,
                "vitoria_dire": odds_vitoria_dire
            },
            "mercados": [
                {
                    "tipo": "total_kills",
                    "valor": 46.5,
                    "odds_over": 1.80,
                    "odds_under": 1.80
                },
                {
                    "tipo": "duracao",
                    "valor": 39.0,
                    "odds_over": 1.80,
                    "odds_under": 1.80
                },
                {
                    "tipo": "handicap_kills",
                    "valor": 7.5,
                    "odds_over": 1.85,
                    "odds_under": 1.78
                }
            ]
        },
        "predictions": {
            "previsoes": {
                "duracao_partida": {
                    "valor": 38.5,
                    "confianca": 0.75,
                    "range": [36, 41]
                },
                "total_kills": {
                    "valor": 47,
                    "confianca": 0.68,
                    "range": [43, 51]
                },
                "diferenca_kills": {
                    "valor": 8,
                    "confianca": 0.72,
                    "range": [5, 11]
                }
            },
            "valuebets": [
                {
                    "mercado": "Total de kills",
                    "handicap": 46.5,
                    "recomendacao": "Over",
                    "odds": 1.80,
                    "valor_esperado": 0.12,
                    "confianca": 0.68
                },
                {
                    "mercado": "First Blood",
                    "handicap": 0,
                    "recomendacao": "Team Liquid",
                    "odds": 1.78,
                    "valor_esperado": 0.15,
                    "confianca": 0.73
                },
                {
                    "mercado": "Race to 10 kills",
                    "handicap": 0,
                    "recomendacao": "Team Liquid",
                    "odds": 1.65,
                    "valor_esperado": 0.18,
                    "confianca": 0.78
                }
            ],
            "explicacao": {
                "fatores_chave": [
                    "Team Liquid tem demonstrado um early game mais agressivo nas últimas partidas, favorecendo apostas em First Blood e Race to Kills.",
                    "A média de kills nos últimos 5 jogos entre estas equipes é de 48.2, ligeiramente acima da linha de 46.5.",
                    "Tundra tende a jogar de forma mais defensiva, mas costuma ceder objetivos no early game.",
                    "Team Liquid tem vantagem estatística em duração média de partidas (37.8 minutos vs 40.2 minutos da Tundra).",
                    "O handicap de kills de 7.5 favorecendo a Tundra parece excessivo considerando o histórico recente entre as equipes.",
                    "Team Liquid tem conseguido o primeiro Aegis em 68% de suas partidas recentes, tornando a odd de 1.65 potencialmente valiosa."
                ]
            }
        }
    }
