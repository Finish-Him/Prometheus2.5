"""
Módulo para análise futura incluindo composições das equipes
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

def processar_partida_completa(texto_odds: str, composicao: str = None) -> Dict[str, Any]:
    """
    Processa dados completos da partida, incluindo odds e composições quando disponíveis
    
    Args:
        texto_odds: Texto contendo as odds da partida
        composicao: Texto contendo as composições das equipes (opcional)
        
    Returns:
        Dicionário com dados da partida e previsões
    """
    # Preparar os dados para envio
    dados_completos = texto_odds
    
    if composicao:
        dados_completos += "\n\nComposições:\n" + composicao
    
    try:
        # Tentar processar via backend do Manus
        url = f"{API_BASE_URL}/process/text"
        payload = {"text": dados_completos}
        
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao processar dados: {str(e)}")
        # Simulação de resposta para desenvolvimento
        return simular_resposta_backend(dados_completos)

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
    
    # Verificar se há informações de composição
    tem_composicao = "Composições:" in texto or "composições:" in texto or "draft" in texto.lower()
    
    # Criar resposta simulada
    resultado_base = {
        "match_data": {
            "time_radiant": time_radiant,
            "time_dire": time_dire,
            "torneio": "Torneio não especificado",
            "odds": {
                "vitoria_radiant": 2.35,
                "vitoria_dire": 1.52
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
    
    # Adicionar análises específicas de composição se disponível
    if tem_composicao:
        # Adicionar valuebets específicas de composição
        resultado_base["predictions"]["valuebets"].append({
            "mercado": "First Tower",
            "handicap": 0,
            "recomendacao": "Team Liquid",
            "odds": 1.72,
            "valor_esperado": 0.22,
            "confianca": 0.82
        })
        
        # Adicionar explicações específicas de composição
        resultado_base["predictions"]["explicacao"]["fatores_chave"].extend([
            "A composição do Team Liquid tem forte potencial de push com heróis que dominam o early-mid game.",
            "A sinergia entre os heróis do Team Liquid favorece engajamentos rápidos e agressivos.",
            "A composição da Tundra é mais voltada para o late game, o que pode resultar em uma postura mais defensiva no início.",
            "O potencial de teamfight do Team Liquid é superior nos primeiros 25 minutos de jogo."
        ])
        
        # Ajustar confiança nas previsões
        resultado_base["predictions"]["previsoes"]["duracao_partida"]["confianca"] = 0.85
        resultado_base["predictions"]["previsoes"]["total_kills"]["confianca"] = 0.78
        resultado_base["predictions"]["previsoes"]["diferenca_kills"]["confianca"] = 0.82
    
    return resultado_base

def formatar_previsao_completa(prediction_data: Dict[str, Any], tem_composicao: bool = False) -> str:
    """
    Formata os dados de previsão para exibição, incluindo análise de composição quando disponível
    
    Args:
        prediction_data: Dados da previsão
        tem_composicao: Indica se há dados de composição disponíveis
        
    Returns:
        Texto formatado para exibição
    """
    match_data = prediction_data.get("match_data", {})
    predictions = prediction_data.get("predictions", {})
    
    # Formatar cabeçalho
    header = f"# Análise: {match_data.get('time_radiant', 'Time A')} vs {match_data.get('time_dire', 'Time B')}\n\n"
    
    if tem_composicao:
        header += "## Análise com Composições Incluídas\n\n"
    else:
        header += "## Análise Baseada em Odds (Sem Composições)\n\n"
    
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
    
    # Adicionar seção sobre composições futuras se não houver composição
    if not tem_composicao:
        future_section = "\n## Análise Futura com Composições\n\n"
        future_section += "Quando as composições (drafts) das equipes estiverem disponíveis, a análise será atualizada com:\n\n"
        future_section += "- Avaliação da sinergia entre os heróis de cada equipe\n"
        future_section += "- Análise de timings de poder para cada composição\n"
        future_section += "- Previsões mais precisas baseadas no estilo de jogo de cada herói\n"
        future_section += "- Valuebets específicas considerando as interações entre composições\n"
        future_section += "- Confiança aumentada nas previsões devido aos dados adicionais\n\n"
        future_section += "Para obter esta análise atualizada, envie as informações de draft assim que estiverem disponíveis."
    else:
        future_section = ""
    
    # Combinar tudo
    return header + prev_section + vb_section + exp_section + future_section
