"""
Módulo de simulação de dados para o Analisador de Partidas de Dota 2 - Versão Offline

Este módulo fornece funções para simular dados de partidas quando não há dados reais disponíveis.
"""

import random
from typing import Dict, Any, List, Optional, Union

class SimuladorDados:
    """Classe para simulação de dados de partidas de Dota 2"""
    
    def __init__(self):
        """Inicializa o simulador de dados"""
        # Lista de times populares
        self.times_populares = [
            "Team Liquid", "Tundra", "OG", "Team Spirit", "Gaimin Gladiators",
            "PSG.LGD", "Xtreme Gaming", "Azure Ray", "BetBoom", "9Pandas",
            "Virtus.pro", "Entity", "Falcons", "Talon", "TSM", "Shopify Rebellion"
        ]
        
        # Lista de torneios populares
        self.torneios_populares = [
            "The International", "ESL One", "DPC", "Major", "Riyadh Masters",
            "DreamLeague", "BTS Pro Series", "PGL", "EPIC League", "WePlay"
        ]
        
        # Lista de heróis por posição
        self.herois = {
            "carry": [
                "Anti-Mage", "Faceless Void", "Juggernaut", "Phantom Assassin", 
                "Spectre", "Terrorblade", "Phantom Lancer", "Lifestealer", 
                "Slark", "Ursa", "Troll Warlord", "Wraith King", "Morphling",
                "Drow Ranger", "Luna", "Medusa", "Naga Siren", "Monkey King"
            ],
            "mid": [
                "Invoker", "Shadow Fiend", "Storm Spirit", "Queen of Pain", 
                "Puck", "Ember Spirit", "Void Spirit", "Templar Assassin", 
                "Lina", "Sniper", "Outworld Destroyer", "Kunkka", "Tinker",
                "Zeus", "Death Prophet", "Leshrac", "Viper", "Razor"
            ],
            "offlane": [
                "Axe", "Centaur Warrunner", "Tidehunter", "Mars", "Bristleback", 
                "Timbersaw", "Necrophos", "Doom", "Dark Seer", "Beastmaster", 
                "Legion Commander", "Night Stalker", "Sand King", "Underlord",
                "Pangolier", "Batrider", "Brewmaster", "Dragon Knight"
            ],
            "support": [
                "Crystal Maiden", "Lion", "Rubick", "Shadow Shaman", "Witch Doctor", 
                "Disruptor", "Jakiro", "Lich", "Oracle", "Winter Wyvern", 
                "Warlock", "Dazzle", "Bane", "Ancient Apparition", "Grimstroke",
                "Enchantress", "Chen", "Io", "Earth Spirit", "Snapfire", "Hoodwink"
            ]
        }
    
    def gerar_partida_aleatoria(self) -> Dict[str, str]:
        """
        Gera dados aleatórios para uma partida
        
        Returns:
            Dicionário com dados da partida
        """
        # Selecionar times aleatórios
        time_a, time_b = random.sample(self.times_populares, 2)
        
        # Selecionar torneio aleatório
        torneio = random.choice(self.torneios_populares)
        if random.random() < 0.7:  # 70% de chance de adicionar detalhes ao torneio
            torneio += f" {random.choice(['Season', 'Tour', 'Division'])} {random.randint(1, 5)}"
        
        # Gerar odds de vitória
        # Quanto menor a odd, maior a chance de vitória
        # Odds entre 1.1 e 5.0
        if random.random() < 0.3:  # 30% de chance de partida equilibrada
            odd_a = round(random.uniform(1.8, 2.2), 2)
            odd_b = round(random.uniform(1.8, 2.2), 2)
        else:  # 70% de chance de um time ser favorito
            if random.random() < 0.5:  # Time A favorito
                odd_a = round(random.uniform(1.1, 1.8), 2)
                odd_b = round(random.uniform(2.2, 5.0), 2)
            else:  # Time B favorito
                odd_a = round(random.uniform(2.2, 5.0), 2)
                odd_b = round(random.uniform(1.1, 1.8), 2)
        
        # Gerar linha de total de kills
        # Média de kills em partidas profissionais: entre 40 e 55
        total_kills = round(random.uniform(40, 55), 1)
        if total_kills == int(total_kills):
            total_kills += 0.5  # Garantir que seja x.5
        
        # Gerar odds de over/under para total de kills
        if random.random() < 0.6:  # 60% de chance de odds equilibradas
            odd_over_kills = round(random.uniform(1.8, 1.95), 2)
            odd_under_kills = round(random.uniform(1.8, 1.95), 2)
        else:  # 40% de chance de um lado ser favorito
            if random.random() < 0.5:  # Over favorito
                odd_over_kills = round(random.uniform(1.5, 1.8), 2)
                odd_under_kills = round(random.uniform(1.9, 2.4), 2)
            else:  # Under favorito
                odd_over_kills = round(random.uniform(1.9, 2.4), 2)
                odd_under_kills = round(random.uniform(1.5, 1.8), 2)
        
        # Gerar linha de duração
        # Média de duração em partidas profissionais: entre 30 e 45 minutos
        duracao = round(random.uniform(30, 45), 1)
        if duracao == int(duracao):
            duracao += 0.5  # Garantir que seja x.5
        
        # Gerar odds de over/under para duração
        if random.random() < 0.6:  # 60% de chance de odds equilibradas
            odd_over_duracao = round(random.uniform(1.8, 1.95), 2)
            odd_under_duracao = round(random.uniform(1.8, 1.95), 2)
        else:  # 40% de chance de um lado ser favorito
            if random.random() < 0.5:  # Over favorito
                odd_over_duracao = round(random.uniform(1.5, 1.8), 2)
                odd_under_duracao = round(random.uniform(1.9, 2.4), 2)
            else:  # Under favorito
                odd_over_duracao = round(random.uniform(1.9, 2.4), 2)
                odd_under_duracao = round(random.uniform(1.5, 1.8), 2)
        
        # Gerar linha de handicap de kills
        # Handicap baseado na diferença de odds
        diff_odds = abs(odd_a - odd_b)
        handicap = round(diff_odds * 2.5, 1)
        if handicap < 1.5:
            handicap = 1.5
        if handicap == int(handicap):
            handicap += 0.5  # Garantir que seja x.5
        
        # Determinar qual time recebe o handicap positivo
        if odd_a > odd_b:  # Time A é underdog, recebe handicap positivo
            handicap_a = handicap
            handicap_b = -handicap
        else:  # Time B é underdog, recebe handicap positivo
            handicap_a = -handicap
            handicap_b = handicap
        
        # Gerar odds de handicap
        odd_handicap_a = round(random.uniform(1.7, 2.0), 2)
        odd_handicap_b = round(random.uniform(1.7, 2.0), 2)
        
        # Gerar odds de first blood
        if odd_a < odd_b:  # Time A favorito
            odd_fb_a = round(random.uniform(1.6, 1.9), 2)
            odd_fb_b = round(random.uniform(1.9, 2.2), 2)
        else:  # Time B favorito
            odd_fb_a = round(random.uniform(1.9, 2.2), 2)
            odd_fb_b = round(random.uniform(1.6, 1.9), 2)
        
        # Gerar odds de race to kills
        races = [5, 10, 15, 20]
        race_odds = {}
        
        for race in races:
            if odd_a < odd_b:  # Time A favorito
                race_odds[race] = {
                    "a": round(random.uniform(1.5, 1.8), 2),
                    "b": round(random.uniform(1.9, 2.3), 2)
                }
            else:  # Time B favorito
                race_odds[race] = {
                    "a": round(random.uniform(1.9, 2.3), 2),
                    "b": round(random.uniform(1.5, 1.8), 2)
                }
        
        # Montar texto de odds
        texto_odds = f"{time_a} vs {time_b}\n"
        texto_odds += f"{torneio}\n\n"
        
        texto_odds += f"Odds vencedor:\n"
        texto_odds += f"{time_a}: {odd_a}\n"
        texto_odds += f"{time_b}: {odd_b}\n\n"
        
        texto_odds += f"Total de kills:\n"
        texto_odds += f"Over {total_kills}: {odd_over_kills}\n"
        texto_odds += f"Under {total_kills}: {odd_under_kills}\n\n"
        
        texto_odds += f"Duração:\n"
        texto_odds += f"Over {duracao}: {odd_over_duracao}\n"
        texto_odds += f"Under {duracao}: {odd_under_duracao}\n\n"
        
        texto_odds += f"Handicap de kills:\n"
        texto_odds += f"{time_a} ({handicap_a}): {odd_handicap_a}\n"
        texto_odds += f"{time_b} ({handicap_b}): {odd_handicap_b}\n\n"
        
        texto_odds += f"First Blood:\n"
        texto_odds += f"{time_a}: {odd_fb_a}\n"
        texto_odds += f"{time_b}: {odd_fb_b}\n\n"
        
        texto_odds += f"Race to kills:\n"
        for race in races:
            texto_odds += f"Race to {race} kills - {time_a}: {race_odds[race]['a']}\n"
            texto_odds += f"Race to {race} kills - {time_b}: {race_odds[race]['b']}\n"
        
        return {
            "texto_odds": texto_odds,
            "time_a": time_a,
            "time_b": time_b,
            "torneio": torneio
        }
    
    def gerar_composicao_aleatoria(self, time_a: str, time_b: str) -> str:
        """
        Gera composições aleatórias para os times
        
        Args:
            time_a: Nome do time A
            time_b: Nome do time B
            
        Returns:
            Texto com as composições
        """
        # Gerar heróis para cada time
        herois_a = self._gerar_herois_time()
        herois_b = self._gerar_herois_time()
        
        # Montar texto de composição
        texto_composicao = f"Radiant ({time_a}):\n"
        for heroi in herois_a:
            texto_composicao += f"{heroi}\n"
        
        texto_composicao += f"\nDire ({time_b}):\n"
        for heroi in herois_b:
            texto_composicao += f"{heroi}\n"
        
        return texto_composicao
    
    def _gerar_herois_time(self) -> List[str]:
        """
        Gera uma lista de 5 heróis para um time
        
        Returns:
            Lista de heróis
        """
        herois_time = []
        
        # Selecionar um herói de cada posição
        herois_time.append(random.choice(self.herois["carry"]))
        herois_time.append(random.choice(self.herois["mid"]))
        herois_time.append(random.choice(self.herois["offlane"]))
        
        # Selecionar dois suportes
        supports = random.sample(self.herois["support"], 2)
        herois_time.extend(supports)
        
        return herois_time
    
    def gerar_exemplo_partida(self) -> Dict[str, str]:
        """
        Gera um exemplo de partida com dados realistas
        
        Returns:
            Dicionário com dados da partida
        """
        return {
            "texto_odds": """Team Liquid vs Tundra
DPC Western Europe Division 1

Odds vencedor:
Team Liquid: 1.52
Tundra: 2.35

Total de kills:
Over 46.5: 1.80
Under 46.5: 1.80

Duração:
Over 38.5: 1.80
Under 38.5: 1.80

Handicap de kills:
Team Liquid (-7.5): 1.78
Tundra (7.5): 1.85

First Blood:
Team Liquid: 1.78
Tundra: 1.92

Race to kills:
Race to 5 kills - Team Liquid: 1.68
Race to 5 kills - Tundra: 2.05
Race to 10 kills - Team Liquid: 1.65
Race to 10 kills - Tundra: 2.10
Race to 15 kills - Team Liquid: 1.62
Race to 15 kills - Tundra: 2.15
Race to 20 kills - Team Liquid: 1.55
Race to 20 kills - Tundra: 2.30""",
            "time_a": "Team Liquid",
            "time_b": "Tundra",
            "torneio": "DPC Western Europe Division 1"
        }
    
    def gerar_exemplo_composicao(self) -> str:
        """
        Gera um exemplo de composição com dados realistas
        
        Returns:
            Texto com as composições
        """
        return """Radiant (Team Liquid):
Terrorblade
Storm Spirit
Mars
Crystal Maiden
Rubick

Dire (Tundra):
Spectre
Invoker
Tidehunter
Lion
Winter Wyvern"""
