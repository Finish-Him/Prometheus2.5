import requests
import json
import os
import time
from datetime import datetime

# Configuração da API OpenDota
API_KEY = "91fdee34-226f-4681-8f72-ee87bd85abcf"
BASE_URL = "https://api.opendota.com/api"

# Função para fazer requisições à API com paginação
def get_all_pages(endpoint, params=None, max_pages=10, page_size=100):
    """
    Obtém todos os dados de um endpoint com paginação
    
    Args:
        endpoint: Endpoint da API
        params: Parâmetros adicionais
        max_pages: Número máximo de páginas a serem obtidas
        page_size: Tamanho da página
    
    Returns:
        Lista com todos os dados obtidos
    """
    if params is None:
        params = {}
    
    all_data = []
    
    # Adicionar API key aos parâmetros se fornecida
    if API_KEY:
        params['api_key'] = API_KEY
    
    # Para endpoints que suportam paginação
    if endpoint in ["/proMatches", "/publicMatches"]:
        for page in range(max_pages):
            # Configurar parâmetros de paginação
            page_params = params.copy()
            if page > 0:
                # Usar o último ID da página anterior como referência para a próxima página
                if all_data and len(all_data) > 0 and 'match_id' in all_data[-1]:
                    page_params['less_than_match_id'] = all_data[-1]['match_id']
            
            page_params['limit'] = page_size
            
            url = f"{BASE_URL}{endpoint}"
            
            # Adicionar delay para evitar rate limiting
            time.sleep(1)
            
            print(f"Obtendo página {page+1} de {endpoint}...")
            response = requests.get(url, params=page_params)
            
            if response.status_code == 200:
                data = response.json()
                if not data or len(data) == 0:
                    break
                    
                all_data.extend(data)
            else:
                print(f"Erro: {response.status_code} - {response.text}")
                break
    else:
        # Para endpoints que não suportam paginação
        url = f"{BASE_URL}{endpoint}"
        
        # Adicionar delay para evitar rate limiting
        time.sleep(1)
        
        print(f"Obtendo dados de {endpoint}...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                all_data.extend(data)
            else:
                all_data = data  # Para endpoints que retornam objetos em vez de listas
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    
    return all_data

# Função para salvar resultados em arquivo JSON
def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Dados salvos em {filename}")

# Função para coletar partidas profissionais recentes
def collect_pro_matches(limit=100):
    """
    Coleta partidas profissionais recentes
    
    Args:
        limit: Número máximo de partidas a serem coletadas
    
    Returns:
        Lista de partidas profissionais
    """
    print(f"\nColetando até {limit} partidas profissionais recentes...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    # Coletar partidas profissionais
    pro_matches = get_all_pages("/proMatches", max_pages=pages_needed, page_size=100)
    
    # Limitar ao número desejado
    if len(pro_matches) > limit:
        pro_matches = pro_matches[:limit]
    
    print(f"Coletadas {len(pro_matches)} partidas profissionais")
    save_to_json(pro_matches, "pro_matches_detailed.json")
    
    return pro_matches

# Função para coletar partidas públicas recentes
def collect_public_matches(limit=100):
    """
    Coleta partidas públicas recentes
    
    Args:
        limit: Número máximo de partidas a serem coletadas
    
    Returns:
        Lista de partidas públicas
    """
    print(f"\nColetando até {limit} partidas públicas recentes...")
    
    # Calcular número de páginas necessárias
    pages_needed = (limit + 99) // 100  # Arredondamento para cima
    
    # Coletar partidas públicas
    public_matches = get_all_pages("/publicMatches", max_pages=pages_needed, page_size=100)
    
    # Limitar ao número desejado
    if len(public_matches) > limit:
        public_matches = public_matches[:limit]
    
    print(f"Coletadas {len(public_matches)} partidas públicas")
    save_to_json(public_matches, "public_matches_detailed.json")
    
    return public_matches

# Função para coletar detalhes de partidas específicas
def collect_match_details(match_ids):
    """
    Coleta detalhes de partidas específicas
    
    Args:
        match_ids: Lista de IDs de partidas
    
    Returns:
        Dicionário com detalhes das partidas
    """
    print(f"\nColetando detalhes de {len(match_ids)} partidas...")
    
    match_details = {}
    
    for match_id in match_ids:
        print(f"Obtendo detalhes da partida {match_id}...")
        
        # Adicionar delay para evitar rate limiting
        time.sleep(1)
        
        url = f"{BASE_URL}/matches/{match_id}"
        params = {}
        if API_KEY:
            params['api_key'] = API_KEY
            
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            match_details[match_id] = response.json()
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    
    print(f"Coletados detalhes de {len(match_details)} partidas")
    save_to_json(match_details, "match_details_collection.json")
    
    return match_details

# Função para coletar estatísticas de heróis
def collect_hero_stats():
    """
    Coleta estatísticas de heróis
    
    Returns:
        Lista de estatísticas de heróis
    """
    print("\nColetando estatísticas de heróis...")
    
    # Coletar estatísticas de heróis
    hero_stats = get_all_pages("/heroStats")
    
    print(f"Coletadas estatísticas de {len(hero_stats)} heróis")
    save_to_json(hero_stats, "hero_stats_detailed.json")
    
    return hero_stats

# Função para coletar jogadores profissionais
def collect_pro_players():
    """
    Coleta informações de jogadores profissionais
    
    Returns:
        Lista de jogadores profissionais
    """
    print("\nColetando jogadores profissionais...")
    
    # Coletar jogadores profissionais
    pro_players = get_all_pages("/proPlayers")
    
    print(f"Coletados {len(pro_players)} jogadores profissionais")
    save_to_json(pro_players, "pro_players_detailed.json")
    
    return pro_players

# Função para coletar estatísticas de um jogador específico
def collect_player_stats(account_id):
    """
    Coleta estatísticas de um jogador específico
    
    Args:
        account_id: ID da conta do jogador
    
    Returns:
        Dicionário com estatísticas do jogador
    """
    print(f"\nColetando estatísticas do jogador {account_id}...")
    
    player_stats = {}
    
    # Endpoints a serem consultados
    endpoints = [
        "",  # Informações gerais
        "/wl",  # Vitórias/Derrotas
        "/recentMatches",  # Partidas recentes
        "/heroes",  # Estatísticas por herói
        "/peers",  # Colegas de equipe
        "/totals",  # Totais
        "/counts",  # Contagens
        "/histograms/duration",  # Histograma de duração
        "/wardmap",  # Mapa de wards
        "/wordcloud"  # Nuvem de palavras
    ]
    
    for endpoint in endpoints:
        endpoint_name = endpoint.replace("/", "_").strip("_")
        if not endpoint_name:
            endpoint_name = "profile"
            
        print(f"Obtendo {endpoint_name}...")
        
        # Adicionar delay para evitar rate limiting
        time.sleep(1)
        
        url = f"{BASE_URL}/players/{account_id}{endpoint}"
        params = {}
        if API_KEY:
            params['api_key'] = API_KEY
            
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            player_stats[endpoint_name] = response.json()
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    
    print(f"Coletadas estatísticas do jogador {account_id}")
    save_to_json(player_stats, f"player_{account_id}_stats.json")
    
    return player_stats

# Função para coletar distribuições de MMR
def collect_distributions():
    """
    Coleta distribuições de MMR e outros dados
    
    Returns:
        Dados de distribuições
    """
    print("\nColetando distribuições de MMR e outros dados...")
    
    # Coletar distribuições
    distributions = get_all_pages("/distributions")
    
    print("Coletadas distribuições")
    save_to_json(distributions, "distributions_detailed.json")
    
    return distributions

# Função para coletar ligas
def collect_leagues():
    """
    Coleta informações sobre ligas
    
    Returns:
        Lista de ligas
    """
    print("\nColetando informações sobre ligas...")
    
    # Coletar ligas
    leagues = get_all_pages("/leagues")
    
    print(f"Coletadas informações de {len(leagues)} ligas")
    save_to_json(leagues, "leagues_detailed.json")
    
    return leagues

# Função para coletar metadados
def collect_metadata():
    """
    Coleta metadados da API
    
    Returns:
        Metadados
    """
    print("\nColetando metadados da API...")
    
    # Coletar metadados
    metadata = get_all_pages("/metadata")
    
    print("Coletados metadados")
    save_to_json(metadata, "metadata_detailed.json")
    
    return metadata

# Função principal
def main():
    print("Iniciando coleta detalhada de dados da OpenDota API...")
    
    # Criar diretório para os dados se não existir
    os.makedirs("dados_detalhados", exist_ok=True)
    os.chdir("dados_detalhados")
    
    # Coletar partidas profissionais recentes
    pro_matches = collect_pro_matches(limit=100)
    
    # Coletar partidas públicas recentes
    public_matches = collect_public_matches(limit=100)
    
    # Coletar detalhes de algumas partidas profissionais
    if pro_matches and len(pro_matches) > 0:
        match_ids = [match['match_id'] for match in pro_matches[:10]]  # Limitar a 10 partidas
        match_details = collect_match_details(match_ids)
    
    # Coletar estatísticas de heróis
    hero_stats = collect_hero_stats()
    
    # Coletar jogadores profissionais
    pro_players = collect_pro_players()
    
    # Coletar estatísticas de alguns jogadores profissionais
    if pro_players and len(pro_players) > 0:
        for player in pro_players[:3]:  # Limitar a 3 jogadores
            account_id = player['account_id']
            player_stats = collect_player_stats(account_id)
    
    # Coletar distribuições
    distributions = collect_distributions()
    
    # Coletar ligas
    leagues = collect_leagues()
    
    # Coletar metadados
    metadata = collect_metadata()
    
    # Criar resumo dos dados coletados
    summary = {
        "timestamp": datetime.now().isoformat(),
        "pro_matches_count": len(pro_matches) if pro_matches else 0,
        "public_matches_count": len(public_matches) if public_matches else 0,
        "match_details_count": len(match_details) if 'match_details' in locals() else 0,
        "hero_stats_count": len(hero_stats) if hero_stats else 0,
        "pro_players_count": len(pro_players) if pro_players else 0,
        "leagues_count": len(leagues) if leagues else 0
    }
    
    save_to_json(summary, "summary.json")
    
    print("\nColeta de dados concluída!")
    print(f"Total de partidas profissionais: {summary['pro_matches_count']}")
    print(f"Total de partidas públicas: {summary['public_matches_count']}")
    print(f"Total de detalhes de partidas: {summary['match_details_count']}")
    print(f"Total de estatísticas de heróis: {summary['hero_stats_count']}")
    print(f"Total de jogadores profissionais: {summary['pro_players_count']}")
    print(f"Total de ligas: {summary['leagues_count']}")

if __name__ == "__main__":
    main()
