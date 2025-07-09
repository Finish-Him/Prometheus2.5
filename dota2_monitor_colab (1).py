#!/usr/bin/env python3
"""
Script para monitoramento automático de partidas de Dota 2 no Google Colab.
Salva dados a cada 1 minuto com nomes baseados no tempo de jogo.
Consolida dados a cada 5 minutos em formatos CSV, XML e JSON.
"""

import requests
import json
import csv
import time
import os
import xml.dom.minidom as md
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from google.colab import files
import pandas as pd

# Configurações
OPENDOTA_API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
STRATZ_API_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJTdWJqZWN0IjoiNWRhYmM3NGUtNzYxMS00MjNmLThlZjgtMWViYjgwMzU1YTg3IiwiU3RlYW1J"
    "ZCI6IjEwNjU5NzkxMyIsIm5iZiI6MTc0NTYzOTI2NiwiZXhwIjoxNzc3MTc1MjY2LCJpYXQiOjE3"
    "NDU2MzkyNjYsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ."
    "KJgOXBLBd44AEWed8FmVP-gNQixPBlhlnA2aaYYw1Nc"
)

# Intervalo de monitoramento
MONITOR_INTERVAL = 60  # 1 minuto em segundos
CONSOLIDATE_INTERVAL = 5  # Consolidar a cada 5 capturas

# Times para monitorar (deixe vazio para monitorar qualquer partida profissional)
TARGET_TEAMS = []  # Exemplo: ['Team Spirit', 'Tidebound']

# Diretórios para salvar os dados
def setup_directories():
    """Cria os diretórios necessários para salvar os dados."""
    directories = ['data', 'data/json', 'data/csv', 'data/xml', 'data/consolidated']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    return True

# Função para obter partidas ao vivo da OpenDota
def get_opendota_live_matches():
    """Obtém partidas ao vivo da API OpenDota."""
    url = f"https://api.opendota.com/api/live?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter partidas ao vivo da OpenDota: {e}")
        return []

# Função para obter partidas profissionais recentes
def get_opendota_pro_matches():
    """Obtém partidas profissionais recentes da API OpenDota."""
    url = f"https://api.opendota.com/api/proMatches?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter partidas profissionais da OpenDota: {e}")
        return []

# Função para filtrar partidas dos times alvo
def filter_target_matches(matches):
    """Filtra partidas dos times alvo ou retorna todas as partidas profissionais se TARGET_TEAMS estiver vazio."""
    if not TARGET_TEAMS:
        return matches[:5]  # Retorna as 5 partidas mais recentes se nenhum time específico for definido
    
    filtered_matches = []
    target_teams_lower = [team.lower() for team in TARGET_TEAMS]
    
    for match in matches:
        radiant_name = match.get("team_name_radiant", "").lower()
        dire_name = match.get("team_name_dire", "").lower()
        
        # Verificar se algum dos times alvo está jogando
        if any(team in radiant_name for team in target_teams_lower) or any(team in dire_name for team in target_teams_lower):
            filtered_matches.append(match)
    
    return filtered_matches

# Função para obter informações sobre heróis
def get_hero_info():
    """Obtém informações sobre heróis da API OpenDota."""
    url = f"https://api.opendota.com/api/constants/heroes?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter informações sobre heróis: {e}")
        return {}

# Função para obter informações sobre itens
def get_items_info():
    """Obtém informações sobre itens da API OpenDota."""
    url = f"https://api.opendota.com/api/constants/items?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter informações sobre itens: {e}")
        return {}

# Função para obter detalhes de uma partida específica
def get_match_details(match_id):
    """Obtém detalhes de uma partida específica da API OpenDota."""
    url = f"https://api.opendota.com/api/matches/{match_id}?api_key={OPENDOTA_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter detalhes da partida {match_id}: {e}")
        return None

# Função para processar dados da partida
def process_match_data(match, heroes_info):
    """Processa os dados da partida para um formato padronizado."""
    # Extrair informações básicas
    match_data = {
        "match_id": match.get("match_id"),
        "radiant_team": match.get("team_name_radiant", "Desconhecido"),
        "dire_team": match.get("team_name_dire", "Desconhecido"),
        "radiant_score": match.get("radiant_score", 0),
        "dire_score": match.get("dire_score", 0),
        "game_time": match.get("game_time", 0),
        "game_time_formatted": str(timedelta(seconds=match.get("game_time", 0))),
        "radiant_lead": match.get("radiant_lead", 0),
        "players": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Processar informações dos jogadores
    for player in match.get("players", []):
        hero_id = player.get("hero_id")
        hero_name = "Desconhecido"
        
        # Obter nome do herói
        if heroes_info and str(hero_id) in heroes_info:
            hero_name = heroes_info[str(hero_id)].get("localized_name", "Desconhecido")
        
        player_info = {
            "account_id": player.get("account_id"),
            "hero_id": hero_id,
            "hero_name": hero_name,
            "team": "Radiant" if player.get("team") == 0 else "Dire"
        }
        
        match_data["players"].append(player_info)
    
    return match_data

# Função para salvar dados em JSON
def save_to_json(data, match_id, game_time):
    """Salva os dados da partida em formato JSON."""
    # Formatar o tempo de jogo como MM:SS
    minutes, seconds = divmod(game_time, 60)
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Criar nome do arquivo
    filename = f"data/json/match_{match_id}_{time_str}.json"
    
    # Salvar dados em JSON
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Dados JSON salvos em {filename}")
    return filename

# Função para salvar dados em CSV
def save_to_csv(data, match_id, game_time):
    """Salva os dados da partida em formato CSV."""
    # Formatar o tempo de jogo como MM:SS
    minutes, seconds = divmod(game_time, 60)
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Criar nome do arquivo
    filename = f"data/csv/match_{match_id}_{time_str}.csv"
    
    # Preparar dados para CSV
    csv_data = {
        "match_id": [data["match_id"]],
        "radiant_team": [data["radiant_team"]],
        "dire_team": [data["dire_team"]],
        "radiant_score": [data["radiant_score"]],
        "dire_score": [data["dire_score"]],
        "game_time": [data["game_time"]],
        "game_time_formatted": [data["game_time_formatted"]],
        "radiant_lead": [data["radiant_lead"]],
        "timestamp": [data["timestamp"]]
    }
    
    # Adicionar dados dos jogadores
    for i, player in enumerate(data["players"]):
        prefix = f"radiant_{i+1}_" if player["team"] == "Radiant" else f"dire_{i+1}_"
        csv_data[f"{prefix}hero"] = [player["hero_name"]]
        csv_data[f"{prefix}hero_id"] = [player["hero_id"]]
    
    # Salvar dados em CSV
    df = pd.DataFrame(csv_data)
    df.to_csv(filename, index=False)
    
    print(f"Dados CSV salvos em {filename}")
    return filename

# Função para salvar dados em XML
def save_to_xml(data, match_id, game_time):
    """Salva os dados da partida em formato XML."""
    # Formatar o tempo de jogo como MM:SS
    minutes, seconds = divmod(game_time, 60)
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    # Criar nome do arquivo
    filename = f"data/xml/match_{match_id}_{time_str}.xml"
    
    # Criar estrutura XML
    root = ET.Element("Match")
    ET.SubElement(root, "MatchID").text = str(data["match_id"])
    ET.SubElement(root, "RadiantTeam").text = data["radiant_team"]
    ET.SubElement(root, "DireTeam").text = data["dire_team"]
    ET.SubElement(root, "RadiantScore").text = str(data["radiant_score"])
    ET.SubElement(root, "DireScore").text = str(data["dire_score"])
    ET.SubElement(root, "GameTime").text = str(data["game_time"])
    ET.SubElement(root, "GameTimeFormatted").text = data["game_time_formatted"]
    ET.SubElement(root, "RadiantLead").text = str(data["radiant_lead"])
    ET.SubElement(root, "Timestamp").text = data["timestamp"]
    
    # Adicionar jogadores
    players = ET.SubElement(root, "Players")
    for player in data["players"]:
        player_elem = ET.SubElement(players, "Player")
        ET.SubElement(player_elem, "AccountID").text = str(player["account_id"])
        ET.SubElement(player_elem, "HeroID").text = str(player["hero_id"])
        ET.SubElement(player_elem, "HeroName").text = player["hero_name"]
        ET.SubElement(player_elem, "Team").text = player["team"]
    
    # Formatar XML para melhor legibilidade
    xml_str = ET.tostring(root, encoding="utf-8")
    dom = md.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Salvar dados em XML
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    
    print(f"Dados XML salvos em {filename}")
    return filename

# Função para consolidar dados
def consolidate_data(match_id, data_files):
    """Consolida os dados de várias capturas em arquivos únicos."""
    # Verificar se há arquivos para consolidar
    if not data_files:
        print("Nenhum arquivo para consolidar")
        return
    
    # Obter timestamp atual
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Consolidar JSON
    json_files = [f for f in data_files if f.endswith(".json")]
    if json_files:
        consolidated_json = []
        for file in json_files:
            with open(file, "r") as f:
                consolidated_json.append(json.load(f))
        
        # Salvar JSON consolidado
        consolidated_json_file = f"data/consolidated/match_{match_id}_consolidated_{timestamp}.json"
        with open(consolidated_json_file, "w") as f:
            json.dump(consolidated_json, f, indent=2)
        print(f"JSON consolidado salvo em {consolidated_json_file}")
    
    # Consolidar CSV
    csv_files = [f for f in data_files if f.endswith(".csv")]
    if csv_files:
        # Ler todos os arquivos CSV
        dfs = [pd.read_csv(file) for file in csv_files]
        
        # Concatenar DataFrames
        consolidated_df = pd.concat(dfs, ignore_index=True)
        
        # Salvar CSV consolidado
        consolidated_csv_file = f"data/consolidated/match_{match_id}_consolidated_{timestamp}.csv"
        consolidated_df.to_csv(consolidated_csv_file, index=False)
        print(f"CSV consolidado salvo em {consolidated_csv_file}")
    
    # Consolidar XML
    xml_files = [f for f in data_files if f.endswith(".xml")]
    if xml_files:
        # Criar estrutura XML para consolidação
        root = ET.Element("ConsolidatedMatch")
        ET.SubElement(root, "MatchID").text = str(match_id)
        ET.SubElement(root, "ConsolidationTimestamp").text = timestamp
        snapshots = ET.SubElement(root, "Snapshots")
        
        # Adicionar cada arquivo XML como um snapshot
        for file in xml_files:
            try:
                tree = ET.parse(file)
                file_root = tree.getroot()
                snapshot = ET.SubElement(snapshots, "Snapshot")
                snapshot.append(file_root)
            except Exception as e:
                print(f"Erro ao processar arquivo XML {file}: {e}")
        
        # Formatar XML para melhor legibilidade
        xml_str = ET.tostring(root, encoding="utf-8")
        dom = md.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Salvar XML consolidado
        consolidated_xml_file = f"data/consolidated/match_{match_id}_consolidated_{timestamp}.xml"
        with open(consolidated_xml_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        print(f"XML consolidado salvo em {consolidated_xml_file}")
    
    return True

# Função principal para monitoramento
def monitor_matches():
    """Função principal para monitorar partidas de Dota 2."""
    print("Iniciando monitoramento de partidas de Dota 2...")
    
    # Configurar diretórios
    setup_directories()
    
    # Obter informações sobre heróis (uma vez, no início)
    heroes_info = get_hero_info()
    
    # Variáveis para controle de consolidação
    capture_count = 0
    data_files = []
    current_match_id = None
    
    try:
        while True:
            # Obter partidas ao vivo
            live_matches = get_opendota_live_matches()
            
            # Filtrar partidas dos times alvo
            target_matches = filter_target_matches(live_matches)
            
            # Se não encontrar partidas ao vivo, tentar partidas profissionais recentes
            if not target_matches:
                pro_matches = get_opendota_pro_matches()
                target_matches = filter_target_matches(pro_matches)
            
            # Processar a primeira partida encontrada
            if target_matches:
                match = target_matches[0]
                match_id = match.get("match_id")
                
                # Verificar se é uma nova partida
                if current_match_id is not None and current_match_id != match_id:
                    # Consolidar dados da partida anterior antes de mudar
                    consolidate_data(current_match_id, data_files)
                    # Resetar variáveis para a nova partida
                    capture_count = 0
                    data_files = []
                
                # Atualizar match_id atual
                current_match_id = match_id
                
                # Processar dados da partida
                match_data = process_match_data(match, heroes_info)
                
                # Salvar dados em diferentes formatos
                game_time = match.get("game_time", 0)
                json_file = save_to_json(match_data, match_id, game_time)
                csv_file = save_to_csv(match_data, match_id, game_time)
                xml_file = save_to_xml(match_data, match_id, game_time)
                
                # Adicionar arquivos à lista para consolidação
                data_files.extend([json_file, csv_file, xml_file])
                
                # Incrementar contador de capturas
                capture_count += 1
                
                # Verificar se é hora de consolidar
                if capture_count >= CONSOLIDATE_INTERVAL:
                    consolidate_data(match_id, data_files)
                    # Resetar contador e lista de arquivos
                    capture_count = 0
                    data_files = []
                
                print(f"Monitoramento concluído para a partida {match_id}. Próxima captura em {MONITOR_INTERVAL} segundos.")
            else:
                print("Nenhuma partida encontrada para monitorar. Tentando novamente em 60 segundos.")
            
            # Aguardar até o próximo intervalo
            time.sleep(MONITOR_INTERVAL)
    
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")
        # Consolidar dados finais antes de sair
        if current_match_id and data_files:
            consolidate_data(current_match_id, data_files)
    
    except Exception as e:
        print(f"Erro durante o monitoramento: {e}")
        # Tentar consolidar dados em caso de erro
        if current_match_id and data_files:
            consolidate_data(current_match_id, data_files)

# Função para download de arquivos no Google Colab
def download_files():
    """Faz o download dos arquivos consolidados no Google Colab."""
    try:
        # Verificar se há arquivos consolidados
        consolidated_files = [f for f in os.listdir("data/consolidated") if os.path.isfile(os.path.join("data/consolidated", f))]
        
        if consolidated_files:
            print("Fazendo download dos arquivos consolidados...")
            for file in consolidated_files:
                files.download(os.path.join("data/consolidated", file))
            print("Download concluído!")
        else:
            print("Nenhum arquivo consolidado encontrado para download.")
    
    except Exception as e:
        print(f"Erro ao fazer download dos arquivos: {e}")

# Executar o monitoramento
if __name__ == "__main__":
    # Este bloco será executado quando o script for executado diretamente
    monitor_matches()
