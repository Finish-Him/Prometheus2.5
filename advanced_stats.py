#!/usr/bin/env python3
"""
Script para compilar estatísticas avançadas sobre a partida entre Team Spirit e Tidebound.
"""

import json
import os
from datetime import datetime

# Carregar dados da partida
def load_match_data():
    # Encontrar o arquivo JSON mais recente
    json_files = [f for f in os.listdir() if f.startswith("team_spirit_vs_tidebound_data_") and f.endswith(".json")]
    if not json_files:
        return None
    
    latest_file = max(json_files)
    
    try:
        with open(latest_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return None

# Analisar composições de heróis
def analyze_hero_synergy(match_data):
    if not match_data:
        return {}
    
    # Definir sinergias conhecidas entre heróis
    synergies = {
        # Combos de controle
        ("Jakiro", "Tiny"): "Alto controle com stuns em área",
        ("Jakiro", "Pangolier"): "Combo de ultimates em área",
        ("Underlord", "Jakiro"): "Controle de área forte",
        ("Tiny", "Pangolier"): "Combo de iniciação e controle",
        
        # Combos de dano
        ("Ember Spirit", "Clinkz"): "Alto dano mágico e físico",
        ("Windranger", "Clinkz"): "Foco em alvos únicos",
        
        # Combos de tanque/suporte
        ("Centaur Warrunner", "Ember Spirit"): "Iniciação e escape",
        ("Ring Master", "Centaur Warrunner"): "Tanque e controle",
        
        # Combos de push
        ("Clinkz", "Windranger"): "Push rápido de torres",
        ("Underlord", "Tiny"): "Push e anti-push forte"
    }
    
    # Analisar sinergias em cada time
    radiant_heroes = [p["hero_name"] for p in match_data.get("radiant_players", [])]
    dire_heroes = [p["hero_name"] for p in match_data.get("dire_players", [])]
    
    radiant_synergies = []
    dire_synergies = []
    
    # Verificar sinergias no time Radiant
    for i, hero1 in enumerate(radiant_heroes):
        for hero2 in radiant_heroes[i+1:]:
            if (hero1, hero2) in synergies:
                radiant_synergies.append((hero1, hero2, synergies[(hero1, hero2)]))
            elif (hero2, hero1) in synergies:
                radiant_synergies.append((hero2, hero1, synergies[(hero2, hero1)]))
    
    # Verificar sinergias no time Dire
    for i, hero1 in enumerate(dire_heroes):
        for hero2 in dire_heroes[i+1:]:
            if (hero1, hero2) in synergies:
                dire_synergies.append((hero1, hero2, synergies[(hero1, hero2)]))
            elif (hero2, hero1) in synergies:
                dire_synergies.append((hero2, hero1, synergies[(hero2, hero1)]))
    
    return {
        "radiant_synergies": radiant_synergies,
        "dire_synergies": dire_synergies
    }

# Analisar pontos fortes e fracos das composições
def analyze_team_strengths(match_data):
    if not match_data:
        return {}
    
    # Definir características dos heróis
    hero_characteristics = {
        "Ring Master": ["controle", "suporte", "resistência"],
        "Ember Spirit": ["mobilidade", "dano mágico", "farm"],
        "Clinkz": ["dano físico", "push", "invisibilidade"],
        "Centaur Warrunner": ["tanque", "iniciação", "controle"],
        "Windranger": ["dano único", "disable", "mobilidade"],
        
        "Pangolier": ["mobilidade", "dano em área", "controle"],
        "Jakiro": ["dano em área", "push", "controle"],
        "Muerta": ["dano físico", "resistência", "controle"],
        "Underlord": ["tanque", "aura", "controle de área"],
        "Tiny": ["burst", "controle", "push"]
    }
    
    # Analisar características de cada time
    radiant_heroes = [p["hero_name"] for p in match_data.get("radiant_players", [])]
    dire_heroes = [p["hero_name"] for p in match_data.get("dire_players", [])]
    
    radiant_characteristics = {}
    dire_characteristics = {}
    
    # Contar características do time Radiant
    for hero in radiant_heroes:
        if hero in hero_characteristics:
            for characteristic in hero_characteristics[hero]:
                radiant_characteristics[characteristic] = radiant_characteristics.get(characteristic, 0) + 1
    
    # Contar características do time Dire
    for hero in dire_heroes:
        if hero in hero_characteristics:
            for characteristic in hero_characteristics[hero]:
                dire_characteristics[characteristic] = dire_characteristics.get(characteristic, 0) + 1
    
    # Identificar pontos fortes (características com contagem >= 2)
    radiant_strengths = [c for c, count in radiant_characteristics.items() if count >= 2]
    dire_strengths = [c for c, count in dire_characteristics.items() if count >= 2]
    
    # Identificar pontos fracos (características ausentes ou com contagem < 2)
    important_characteristics = ["controle", "dano físico", "dano mágico", "tanque", "mobilidade", "push"]
    
    radiant_weaknesses = [c for c in important_characteristics if c not in radiant_characteristics or radiant_characteristics[c] < 2]
    dire_weaknesses = [c for c in important_characteristics if c not in dire_characteristics or dire_characteristics[c] < 2]
    
    return {
        "radiant_strengths": radiant_strengths,
        "radiant_weaknesses": radiant_weaknesses,
        "dire_strengths": dire_strengths,
        "dire_weaknesses": dire_weaknesses
    }

# Analisar timing de poder dos times
def analyze_power_timings(match_data):
    if not match_data:
        return {}
    
    # Definir timings de poder dos heróis
    hero_timings = {
        "Ring Master": "mid_game",
        "Ember Spirit": "late_game",
        "Clinkz": "mid_game",
        "Centaur Warrunner": "mid_game",
        "Windranger": "mid_game",
        
        "Pangolier": "mid_game",
        "Jakiro": "early_game",
        "Muerta": "late_game",
        "Underlord": "mid_game",
        "Tiny": "mid_game"
    }
    
    # Analisar timings de cada time
    radiant_heroes = [p["hero_name"] for p in match_data.get("radiant_players", [])]
    dire_heroes = [p["hero_name"] for p in match_data.get("dire_players", [])]
    
    radiant_timings = {"early_game": 0, "mid_game": 0, "late_game": 0}
    dire_timings = {"early_game": 0, "mid_game": 0, "late_game": 0}
    
    # Contar timings do time Radiant
    for hero in radiant_heroes:
        if hero in hero_timings:
            radiant_timings[hero_timings[hero]] += 1
    
    # Contar timings do time Dire
    for hero in dire_heroes:
        if hero in hero_timings:
            dire_timings[hero_timings[hero]] += 1
    
    # Determinar fase de poder principal de cada time
    radiant_power_phase = max(radiant_timings.items(), key=lambda x: x[1])[0]
    dire_power_phase = max(dire_timings.items(), key=lambda x: x[1])[0]
    
    # Analisar vantagem atual com base no tempo de jogo e fase de poder
    game_time = match_data.get("game_time", 0)
    current_phase = "early_game" if game_time < 600 else "mid_game" if game_time < 1800 else "late_game"
    
    radiant_timing_advantage = (radiant_power_phase == current_phase)
    dire_timing_advantage = (dire_power_phase == current_phase)
    
    return {
        "radiant_timings": radiant_timings,
        "dire_timings": dire_timings,
        "radiant_power_phase": radiant_power_phase,
        "dire_power_phase": dire_power_phase,
        "current_phase": current_phase,
        "radiant_timing_advantage": radiant_timing_advantage,
        "dire_timing_advantage": dire_timing_advantage
    }

# Analisar objetivos e próximos movimentos
def analyze_objectives(match_data):
    if not match_data:
        return {}
    
    game_time = match_data.get("game_time", 0)
    radiant_lead = match_data.get("radiant_lead", 0)
    
    # Determinar time com vantagem
    leading_team = "radiant" if radiant_lead > 0 else "dire" if radiant_lead < 0 else "none"
    advantage_size = abs(radiant_lead)
    
    # Analisar próximos objetivos com base no tempo de jogo
    if game_time < 600:  # < 10 minutos
        next_objectives = {
            "radiant": ["Controle de bounty runes", "Domínio de lanes", "Stacking de neutrals"],
            "dire": ["Controle de bounty runes", "Domínio de lanes", "Stacking de neutrals"]
        }
    elif game_time < 1200:  # < 20 minutos
        next_objectives = {
            "radiant": ["Torres tier 1", "Controle de outposts", "Invasão de jungle"],
            "dire": ["Torres tier 1", "Controle de outposts", "Invasão de jungle"]
        }
    elif game_time < 1800:  # < 30 minutos
        next_objectives = {
            "radiant": ["Roshan", "Torres tier 2", "Controle de mapa"],
            "dire": ["Roshan", "Torres tier 2", "Controle de mapa"]
        }
    else:
        next_objectives = {
            "radiant": ["Aegis do Roshan", "High ground push", "Controle de mapa"],
            "dire": ["Aegis do Roshan", "High ground push", "Controle de mapa"]
        }
    
    # Ajustar prioridades com base na vantagem
    if leading_team != "none" and advantage_size > 3000:
        if leading_team == "radiant":
            next_objectives["radiant"] = ["Push agressivo", "Roshan", "Controle de mapa"]
            next_objectives["dire"] = ["Defesa de torres", "Farm seguro", "Smoke ganks"]
        else:
            next_objectives["dire"] = ["Push agressivo", "Roshan", "Controle de mapa"]
            next_objectives["radiant"] = ["Defesa de torres", "Farm seguro", "Smoke ganks"]
    
    return {
        "leading_team": leading_team,
        "advantage_size": advantage_size,
        "next_objectives": next_objectives
    }

# Gerar relatório de estatísticas avançadas
def generate_advanced_stats_report():
    # Carregar dados da partida
    match_data = load_match_data()
    
    if not match_data:
        return "Não foi possível carregar os dados da partida."
    
    # Analisar sinergias entre heróis
    synergy_analysis = analyze_hero_synergy(match_data)
    
    # Analisar pontos fortes e fracos das composições
    strength_analysis = analyze_team_strengths(match_data)
    
    # Analisar timing de poder dos times
    timing_analysis = analyze_power_timings(match_data)
    
    # Analisar objetivos e próximos movimentos
    objective_analysis = analyze_objectives(match_data)
    
    # Construir relatório
    report = []
    report.append("=" * 60)
    report.append("ESTATÍSTICAS AVANÇADAS: Team Tidebound vs Team Spirit")
    report.append("=" * 60)
    report.append("")
    
    # Informações básicas
    report.append("INFORMAÇÕES BÁSICAS:")
    report.append(f"ID da Partida: {match_data['match_id']}")
    minutes, seconds = divmod(match_data["game_time"], 60)
    report.append(f"Tempo de Jogo: {minutes}:{seconds:02d}")
    report.append(f"Placar: {match_data['radiant_team']} {match_data['radiant_score']} - {match_data['dire_score']} {match_data['dire_team']}")
    
    if "radiant_lead" in match_data:
        if match_data["radiant_lead"] > 0:
            report.append(f"Vantagem de Ouro: {match_data['radiant_team']} lidera por {match_data['radiant_lead']} de ouro")
        elif match_data["radiant_lead"] < 0:
            report.append(f"Vantagem de Ouro: {match_data['dire_team']} lidera por {abs(match_data['radiant_lead'])} de ouro")
        else:
            report.append("Vantagem de Ouro: Empate")
    
    report.append("")
    
    # Sinergias entre heróis
    report.append("SINERGIAS ENTRE HERÓIS:")
    
    report.append(f"\n{match_data['radiant_team']} (Radiant):")
    if synergy_analysis["radiant_synergies"]:
        for hero1, hero2, description in synergy_analysis["radiant_synergies"]:
            report.append(f"- {hero1} + {hero2}: {description}")
    else:
        report.append("- Nenhuma sinergia significativa identificada")
    
    report.append(f"\n{match_data['dire_team']} (Dire):")
    if synergy_analysis["dire_synergies"]:
        for hero1, hero2, description in synergy_analysis["dire_synergies"]:
            report.append(f"- {hero1} + {hero2}: {description}")
    else:
        report.append("- Nenhuma sinergia significativa identificada")
    
    report.append("")
    
    # Pontos fortes e fracos
    report.append("PONTOS FORTES E FRACOS:")
    
    report.append(f"\n{match_data['radiant_team']} (Radiant):")
    report.append("Pontos Fortes:")
    for strength in strength_analysis["radiant_strengths"]:
        report.append(f"- {strength.capitalize()}")
    
    report.append("Pontos Fracos:")
    for weakness in strength_analysis["radiant_weaknesses"]:
        report.append(f"- {weakness.capitalize()}")
    
    report.append(f"\n{match_data['dire_team']} (Dire):")
    report.append("Pontos Fortes:")
    for strength in strength_analysis["dire_strengths"]:
        report.append(f"- {strength.capitalize()}")
    
    report.append("Pontos Fracos:")
    for weakness in strength_analysis["dire_weaknesses"]:
        report.append(f"- {weakness.capitalize()}")
    
    report.append("")
    
    # Timing de poder
    report.append("TIMING DE PODER:")
    
    report.append(f"\n{match_data['radiant_team']} (Radiant):")
    report.append(f"Fase de poder principal: {timing_analysis['radiant_power_phase'].replace('_', ' ').capitalize()}")
    report.append(f"Distribuição de timing: Early Game ({timing_analysis['radiant_timings']['early_game']}), Mid Game ({timing_analysis['radiant_timings']['mid_game']}), Late Game ({timing_analysis['radiant_timings']['late_game']})")
    
    report.append(f"\n{match_data['dire_team']} (Dire):")
    report.append(f"Fase de poder principal: {timing_analysis['dire_power_phase'].replace('_', ' ').capitalize()}")
    report.append(f"Distribuição de timing: Early Game ({timing_analysis['dire_timings']['early_game']}), Mid Game ({timing_analysis['dire_timings']['mid_game']}), Late Game ({timing_analysis['dire_timings']['late_game']})")
    
    report.append(f"\nFase atual do jogo: {timing_analysis['current_phase'].replace('_', ' ').capitalize()}")
    
    if timing_analysis["radiant_timing_advantage"]:
        report.append(f"{match_data['radiant_team']} está na sua fase de poder principal")
    
    if timing_analysis["dire_timing_advantage"]:
        report.append(f"{match_data['dire_team']} está na sua fase de poder principal")
    
    report.append("")
    
    # Objetivos e próximos movimentos
    report.append("OBJETIVOS E PRÓXIMOS MOVIMENTOS:")
    
    leading_team_name = match_data['radiant_team'] if objective_analysis["leading_team"] == "radiant" else match_data['dire_team'] if objective_analysis["leading_team"] == "dire" else "Nenhum time"
    
    if objective_analysis["leading_team"] != "none":
        report.append(f"Time com vantagem: {leading_team_name} ({objective_analysis['advantage_size']} de ouro)")
    else:
        report.append("Partida equilibrada, sem vantagem significativa")
    
    report.append(f"\nPróximos objetivos para {match_data['radiant_team']} (Radiant):")
    for objective in objective_analysis["next_objectives"]["radiant"]:
        report.append(f"- {objective}")
    
    report.append(f"\nPróximos objetivos para {match_data['dire_team']} (Dire):")
    for objective in objective_analysis["next_objectives"]["dire"]:
        report.append(f"- {objective}")
    
    report.append("")
    
    # Previsão
    report.append("PREVISÃO:")
    
    # Calcular chance de vitória com base em vantagem e timing
    radiant_win_chance = 50  # Base: 50%
    
    # Ajustar com base na vantagem de ouro
    if "radiant_lead" in match_data:
        gold_advantage_factor = min(30, abs(match_data["radiant_lead"]) / 1000 * 5)  # Máximo de 30% por vantagem de ouro
        if match_data["radiant_lead"] > 0:
            radiant_win_chance += gold_advantage_factor
        else:
            radiant_win_chance -= gold_advantage_factor
    
    # Ajustar com base no timing de poder
    if timing_analysis["radiant_timing_advantage"]:
        radiant_win_chance += 10
    
    if timing_analysis["dire_timing_advantage"]:
        radiant_win_chance -= 10
    
    # Ajustar co
(Content truncated due to size limit. Use line ranges to read in chunks)