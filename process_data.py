"""
Módulo para processamento de dados de texto e imagens para o Oráculo 4.0
"""

import json
import os
import re
import base64
from datetime import datetime
import numpy as np
from typing import Dict, Any, List, Optional, Union

# Configurações
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history")

# Criar diretório de histórico se não existir
os.makedirs(HISTORY_DIR, exist_ok=True)

# Dicionário de times conhecidos e seus padrões
KNOWN_TEAMS = {
    "Team Spirit": ["spirit", "ts", "team spirit"],
    "NaVi Junior": ["navi junior", "navi jr", "navijr", "navi j"],
    "Natus Vincere": ["navi", "natus vincere", "na'vi"],
    "Tundra Esports": ["tundra", "tundra esports"],
    "Team Liquid": ["liquid", "tl", "team liquid"],
    "PARIVISION": ["parivision", "pari"],
    "Team Tidebound": ["tidebound", "team tidebound", "tide"],
    "BetBoom Team": ["betboom", "bb", "betboom team"],
    "Aurora": ["aurora"],
    "Virtus.pro": ["virtus.pro", "virtus pro", "vp"],
    "PSG.LGD": ["psg.lgd", "lgd", "psg lgd"],
    "Team Aster": ["aster", "team aster"],
    "Gaimin Gladiators": ["gaimin", "gg", "gaimin gladiators"],
    "OG": ["og"],
    "Entity": ["entity"],
    "Falcons": ["falcons"],
    "9Pandas": ["9pandas", "pandas"],
    "Team Secret": ["secret", "team secret"]
}

# Dicionário de torneios conhecidos e seus padrões
KNOWN_TOURNAMENTS = {
    "PGL Wallachia Season 4": ["pgl", "wallachia", "pgl wallachia", "wallachia s4"],
    "ESL One Birmingham 2025": ["esl", "birmingham", "esl one", "esl birmingham"],
    "BTS Pro Series": ["bts", "pro series", "bts pro"],
    "DPC China 2025": ["dpc china", "dpc cn"],
    "DPC WEU 2025": ["dpc weu", "dpc western europe", "dpc eu"],
    "DPC EEU 2025": ["dpc eeu", "dpc eastern europe"],
    "DPC NA 2025": ["dpc na", "dpc north america"],
    "DPC SA 2025": ["dpc sa", "dpc south america"],
    "DPC SEA 2025": ["dpc sea", "dpc southeast asia"]
}

class DataProcessor:
    """Classe para processamento de dados de texto e imagens"""
    
    def __init__(self):
        """Inicializa o processador de dados"""
        self.heroes_data = self._load_heroes_data()
        self.teams_data = self._load_teams_data()
    
    def _load_heroes_data(self) -> Dict[str, Any]:
        """Carrega dados de heróis do JSON"""
        try:
            with open(os.path.join(DATA_DIR, "heroes", "heroes.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Retornar dicionário vazio se o arquivo não existir ou for inválido
            return {}
    
    def _load_teams_data(self) -> Dict[str, Any]:
        """Carrega dados de times do JSON"""
        try:
            with open(os.path.join(DATA_DIR, "teams", "teams.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Retornar dicionário vazio se o arquivo não existir ou for inválido
            return {}
    
    def process_text_data(self, text: str) -> Dict[str, Any]:
        """
        Processa dados de texto para extrair informações da partida
        
        Args:
            text: Texto contendo informações da partida
            
        Returns:
            Dicionário com dados estruturados da partida
        """
        # Normalizar texto
        text = text.lower().strip()
        
        # Extrair times
        teams = self._extract_teams(text)
        
        # Extrair torneio
        tournament = self._extract_tournament(text)
        
        # Extrair odds
        odds = self._extract_odds(text)
        
        # Extrair mercados
        markets = self._extract_markets(text)
        
        # Construir resultado
        result = {
            "time_radiant": teams.get("radiant", "Time A"),
            "time_dire": teams.get("dire", "Time B"),
            "torneio": tournament or "Torneio não especificado",
            "odds": {
                "vitoria_radiant": odds.get("radiant", 2.0),
                "vitoria_dire": odds.get("dire", 1.8)
            },
            "mercados": markets
        }
        
        return result
    
    def process_image_data(self, image_base64: str) -> Dict[str, Any]:
        """
        Processa dados de imagem para extrair informações da partida
        
        Args:
            image_base64: Imagem em formato base64
            
        Returns:
            Dicionário com dados estruturados da partida
        """
        # Em um sistema real, usaríamos OCR para extrair texto da imagem
        # Aqui vamos simular a extração com dados fictícios
        
        # Gerar um hash da imagem para simular diferentes resultados
        image_hash = hash(image_base64[:100]) % 5
        
        if image_hash == 0:
            return {
                "time_radiant": "Team Spirit",
                "time_dire": "NaVi Junior",
                "torneio": "PGL Wallachia Season 4",
                "odds": {
                    "vitoria_radiant": 1.16,
                    "vitoria_dire": 4.88
                },
                "mercados": [
                    {
                        "tipo": "handicap_kills",
                        "valor": 8.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    },
                    {
                        "tipo": "duracao_partida",
                        "valor": 32.5,
                        "odds_over": 1.85,
                        "odds_under": 1.85
                    },
                    {
                        "tipo": "total_kills",
                        "valor": 48.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    }
                ]
            }
        elif image_hash == 1:
            return {
                "time_radiant": "Tundra Esports",
                "time_dire": "Team Liquid",
                "torneio": "PGL Wallachia Season 4",
                "odds": {
                    "vitoria_radiant": 2.35,
                    "vitoria_dire": 1.52
                },
                "mercados": [
                    {
                        "tipo": "handicap_kills",
                        "valor": 5.5,
                        "odds_over": 1.85,
                        "odds_under": 1.85
                    },
                    {
                        "tipo": "duracao_partida",
                        "valor": 35.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    },
                    {
                        "tipo": "total_kills",
                        "valor": 45.5,
                        "odds_over": 1.85,
                        "odds_under": 1.85
                    }
                ]
            }
        elif image_hash == 2:
            return {
                "time_radiant": "PARIVISION",
                "time_dire": "Team Tidebound",
                "torneio": "PGL Wallachia Season 4",
                "odds": {
                    "vitoria_radiant": 1.22,
                    "vitoria_dire": 3.71
                },
                "mercados": [
                    {
                        "tipo": "handicap_kills",
                        "valor": 7.5,
                        "odds_over": 1.85,
                        "odds_under": 1.85
                    },
                    {
                        "tipo": "duracao_partida",
                        "valor": 34.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    },
                    {
                        "tipo": "total_kills",
                        "valor": 46.5,
                        "odds_over": 1.85,
                        "odds_under": 1.85
                    }
                ]
            }
        elif image_hash == 3:
            return {
                "time_radiant": "BetBoom Team",
                "time_dire": "Aurora",
                "torneio": "PGL Wallachia Season 4",
                "odds": {
                    "vitoria_radiant": 1.45,
                    "vitoria_dire": 2.63
                },
                "mercados": [
                    {
                        "tipo": "handicap_kills",
                        "valor": 6.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    },
                    {
                        "tipo": "duracao_partida",
                        "valor": 36.5,
                        "odds_over": 1.85,
                        "odds_under": 1.85
                    },
                    {
                        "tipo": "total_kills",
                        "valor": 47.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    }
                ]
            }
        else:
            return {
                "time_radiant": "Virtus.pro",
                "time_dire": "Team Secret",
                "torneio": "ESL One Birmingham 2025",
                "odds": {
                    "vitoria_radiant": 1.75,
                    "vitoria_dire": 2.05
                },
                "mercados": [
                    {
                        "tipo": "handicap_kills",
                        "valor": 3.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    },
                    {
                        "tipo": "duracao_partida",
                        "valor": 38.5,
                        "odds_over": 1.85,
                        "odds_under": 1.85
                    },
                    {
                        "tipo": "total_kills",
                        "valor": 49.5,
                        "odds_over": 1.90,
                        "odds_under": 1.80
                    }
                ]
            }
    
    def process_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados de formulário para estruturar informações da partida
        
        Args:
            form_data: Dados do formulário
            
        Returns:
            Dicionário com dados estruturados da partida
        """
        # Extrair mercados
        mercados = []
        
        # Handicap de Kills
        if form_data.get("handicapKills") and form_data.get("oddsOverKills") and form_data.get("oddsUnderKills"):
            mercados.append({
                "tipo": "handicap_kills",
                "valor": float(form_data["handicapKills"]),
                "odds_over": float(form_data["oddsOverKills"]),
                "odds_under": float(form_data["oddsUnderKills"])
            })
        
        # Duração da Partida
        if form_data.get("handicapDuration") and form_data.get("oddsOverDuration") and form_data.get("oddsUnderDuration"):
            mercados.append({
                "tipo": "duracao_partida",
                "valor": float(form_data["handicapDuration"]),
                "odds_over": float(form_data["oddsOverDuration"]),
                "odds_under": float(form_data["oddsUnderDuration"])
            })
        
        # Total de Kills
        if form_data.get("totalKills") and form_data.get("oddsOverTotal") and form_data.get("oddsUnderTotal"):
            mercados.append({
                "tipo": "total_kills",
                "valor": float(form_data["totalKills"]),
                "odds_over": float(form_data["oddsOverTotal"]),
                "odds_under": float(form_data["oddsUnderTotal"])
            })
        
        # Construir resultado
        result = {
            "time_radiant": form_data.get("timeRadiant", "Time A"),
            "time_dire": form_data.get("timeDire", "Time B"),
            "torneio": form_data.get("torneio", "Torneio não especificado"),
            "odds": {
                "vitoria_radiant": float(form_data.get("oddsRadiant", 2.0)),
                "vitoria_dire": float(form_data.get("oddsDire", 1.8))
            },
            "mercados": mercados
        }
        
        return result
    
    def generate_predictions(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera previsões com base nos dados da partida
        
        Args:
            match_data: Dados da partida
            
        Returns:
            Dicionário com previsões
        """
        # Calcular diferença de odds como indicador de força relativa
        odds_diff = match_data["odds"]["vitoria_radiant"] - match_data["odds"]["vitoria_dire"]
        
        # Previsão de duração
        duration_base = 35.0
        if odds_diff > 1:
            duration_base -= 3.0  # Partidas desbalanceadas tendem a ser mais curtas
        elif odds_diff < -1:
            duration_base -= 2.0
        
        # Adicionar variação aleatória
        duration_variation = (np.random.random() * 4) - 2
        duration_prediction = max(25, duration_base + duration_variation)
        
        # Previsão de total de kills
        kills_base = 47.0
        if odds_diff > 1 or odds_diff < -1:
            kills_base += 3.0  # Partidas desbalanceadas tendem a ter mais kills
        
        # Adicionar variação aleatória
        kills_variation = (np.random.random() * 6) - 3
        kills_prediction = max(30, kills_base + kills_variation)
        
        # Previsão de diferença de kills
        kill_diff_base = -odds_diff * 3.0
        
        # Adicionar variação aleatória
        kill_diff_variation = (np.random.random() * 4) - 2
        kill_diff_prediction = kill_diff_base + kill_diff_variation
        
        # Identificar valuebets
        valuebets = []
        
        # Verificar mercados
        for mercado in match_data.get("mercados", []):
            if mercado["tipo"] == "duracao_partida":
                # Verificar valuebet para duração
                if mercado["valor"] < duration_prediction - 3:
                    # Over é valuebet
                    valuebets.append({
                        "mercado": mercado["tipo"],
                        "handicap": mercado["valor"],
                        "recomendacao": "over",
                        "odds": mercado["odds_over"],
                        "valor_esperado": 0.15 + (np.random.random() * 0.1),
                        "confianca": 0.75 + (np.random.random() * 0.15)
                    })
                elif mercado["valor"] > duration_prediction + 3:
                    # Under é valuebet
                    valuebets.append({
                        "mercado": mercado["tipo"],
                        "handicap": mercado["valor"],
                        "recomendacao": "under",
                        "odds": mercado["odds_under"],
                        "valor_esperado": 0.15 + (np.random.random() * 0.1),
                        "confianca": 0.75 + (np.random.random() * 0.15)
                    })
            elif mercado["tipo"] == "total_kills":
                # Verificar valuebet para total de kills
                if mercado["valor"] < kills_prediction - 5:
                    # Over é valuebet
                    valuebets.append({
                        "mercado": mercado["tipo"],
                        "handicap": mercado["valor"],
                        "recomendacao": "over",
                        "odds": mercado["odds_over"],
                        "valor_esperado": 0.18 + (np.random.random() * 0.1),
                        "confianca": 0.78 + (np.random.random() * 0.12)
                    })
                elif mercado["valor"] > kills_prediction + 5:
                    # Under é valuebet
                    valuebets.append({
                        "mercado": mercado["tipo"],
                        "handicap": mercado["valor"],
               
(Content truncated due to size limit. Use line ranges to read in chunks)