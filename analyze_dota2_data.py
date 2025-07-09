import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configurar o estilo dos gráficos
plt.style.use('ggplot')
sns.set(style="whitegrid")

# Diretório de dados coletados
DATA_DIR = "collected_data"
# Diretório para análises
ANALYSIS_DIR = "analysis_results"
os.makedirs(ANALYSIS_DIR, exist_ok=True)

# Função para carregar dados CSV
def load_csv(filename):
    filepath = os.path.join(DATA_DIR, filename)
    return pd.read_csv(filepath)

# Função para carregar dados JSON
def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Função para salvar dataframe como CSV
def save_to_csv(df, filename):
    filepath = os.path.join(ANALYSIS_DIR, filename)
    df.to_csv(filepath, index=False)
    print(f"Dados salvos em {filepath}")
    return filepath

# Função para salvar figura
def save_figure(fig, filename):
    filepath = os.path.join(ANALYSIS_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Figura salva em {filepath}")
    return filepath

# Função para analisar duração de partidas
def analyze_match_duration():
    print("Analisando duração de partidas...")
    
    # Carregar dados de partidas da OpenDota
    opendota_matches = load_csv("opendota_pro_matches_simplified.csv")
    
    # Converter duração de segundos para minutos
    opendota_matches['duration_minutes'] = opendota_matches['duration'] / 60
    
    # Estatísticas básicas de duração
    duration_stats = opendota_matches['duration_minutes'].describe()
    print("Estatísticas de duração de partidas (minutos):")
    print(duration_stats)
    
    # Salvar estatísticas
    duration_stats_df = pd.DataFrame(duration_stats).reset_index()
    duration_stats_df.columns = ['Estatística', 'Valor']
    save_to_csv(duration_stats_df, "match_duration_stats.csv")
    
    # Histograma de duração
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(opendota_matches['duration_minutes'], bins=20, kde=True, ax=ax)
    ax.set_title('Distribuição da Duração de Partidas Profissionais de Dota 2')
    ax.set_xlabel('Duração (minutos)')
    ax.set_ylabel('Frequência')
    save_figure(fig, "match_duration_histogram.png")
    
    # Boxplot de duração por resultado (vitória do Radiant vs Dire)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='radiant_win', y='duration_minutes', data=opendota_matches, ax=ax)
    ax.set_title('Duração de Partidas por Resultado')
    ax.set_xlabel('Vitória do Radiant')
    ax.set_ylabel('Duração (minutos)')
    save_figure(fig, "match_duration_by_result.png")
    
    # Análise de duração por patch
    if 'patch' in opendota_matches.columns:
        patch_duration = opendota_matches.groupby('patch')['duration_minutes'].agg(['mean', 'median', 'std', 'count']).reset_index()
        patch_duration = patch_duration.sort_values('patch', ascending=False)
        save_to_csv(patch_duration, "match_duration_by_patch.csv")
        
        # Gráfico de duração média por patch
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x='patch', y='mean', data=patch_duration, ax=ax)
        ax.set_title('Duração Média de Partidas por Patch')
        ax.set_xlabel('Patch')
        ax.set_ylabel('Duração Média (minutos)')
        plt.xticks(rotation=45)
        save_figure(fig, "match_duration_by_patch.png")
    
    return duration_stats

# Função para analisar estatísticas de heróis
def analyze_hero_stats():
    print("Analisando estatísticas de heróis...")
    
    # Carregar dados de heróis da OpenDota
    hero_stats = load_csv("opendota_hero_stats_simplified.csv")
    
    # Calcular taxa de vitória em partidas profissionais
    hero_stats['pro_winrate'] = hero_stats['pro_win'] / hero_stats['pro_pick']
    
    # Filtrar heróis com pelo menos 10 picks profissionais
    hero_stats_filtered = hero_stats[hero_stats['pro_pick'] >= 10].copy()
    
    # Top 10 heróis mais escolhidos em partidas profissionais
    top_picked = hero_stats_filtered.sort_values('pro_pick', ascending=False).head(10)
    save_to_csv(top_picked, "top_picked_heroes.csv")
    
    # Top 10 heróis com maior taxa de vitória em partidas profissionais
    top_winrate = hero_stats_filtered.sort_values('pro_winrate', ascending=False).head(10)
    save_to_csv(top_winrate, "top_winrate_heroes.csv")
    
    # Top 10 heróis mais banidos em partidas profissionais
    top_banned = hero_stats_filtered.sort_values('pro_ban', ascending=False).head(10)
    save_to_csv(top_banned, "top_banned_heroes.csv")
    
    # Gráfico de picks vs winrate
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(
        hero_stats_filtered['pro_pick'], 
        hero_stats_filtered['pro_winrate'] * 100, 
        alpha=0.7, 
        s=hero_stats_filtered['pro_ban'] / 5,
        c=hero_stats_filtered['pro_ban'],
        cmap='viridis'
    )
    
    # Adicionar nomes dos heróis para os top 10 mais escolhidos
    for _, row in top_picked.iterrows():
        ax.annotate(
            row['name'], 
            (row['pro_pick'], row['pro_winrate'] * 100),
            xytext=(5, 5),
            textcoords='offset points'
        )
    
    ax.set_title('Relação entre Picks e Taxa de Vitória em Partidas Profissionais')
    ax.set_xlabel('Número de Picks')
    ax.set_ylabel('Taxa de Vitória (%)')
    ax.axhline(y=50, color='r', linestyle='--', alpha=0.3)  # Linha de 50% de winrate
    plt.colorbar(scatter, label='Número de Bans')
    save_figure(fig, "hero_pick_vs_winrate.png")
    
    # Análise por atributo primário
    attr_stats = hero_stats.groupby('primary_attr').agg({
        'pro_pick': 'sum',
        'pro_win': 'sum',
        'pro_ban': 'sum'
    }).reset_index()
    attr_stats['pro_winrate'] = attr_stats['pro_win'] / attr_stats['pro_pick']
    save_to_csv(attr_stats, "hero_stats_by_attribute.csv")
    
    # Gráfico de taxa de vitória por atributo
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='primary_attr', y='pro_winrate', data=attr_stats, ax=ax)
    ax.set_title('Taxa de Vitória por Atributo Primário em Partidas Profissionais')
    ax.set_xlabel('Atributo Primário')
    ax.set_ylabel('Taxa de Vitória')
    save_figure(fig, "winrate_by_attribute.png")
    
    return hero_stats_filtered

# Função para analisar partidas ao vivo
def analyze_live_matches():
    print("Analisando partidas ao vivo...")
    
    # Carregar dados de partidas ao vivo da Steam
    try:
        live_games = load_csv("steam_live_games_simplified.csv")
        
        if live_games.empty:
            print("Não há partidas ao vivo disponíveis para análise.")
            return None
        
        # Estatísticas básicas
        live_stats = {
            "total_matches": len(live_games),
            "leagues": live_games['league_id'].nunique(),
            "teams": len(set(filter(None, live_games['radiant_team'].tolist() + live_games['dire_team'].tolist())))
        }
        
        # Salvar estatísticas
        live_stats_df = pd.DataFrame([live_stats])
        save_to_csv(live_stats_df, "live_matches_stats.csv")
        
        # Análise de espectadores se disponível
        if 'spectators' in live_games.columns:
            spectator_stats = live_games['spectators'].describe()
            spectator_stats_df = pd.DataFrame(spectator_stats).reset_index()
            spectator_stats_df.columns = ['Estatística', 'Valor']
            save_to_csv(spectator_stats_df, "live_matches_spectators.csv")
            
            # Gráfico de espectadores por partida
            fig, ax = plt.subplots(figsize=(12, 6))
            live_games_sorted = live_games.sort_values('spectators', ascending=False)
            sns.barplot(x=live_games_sorted.index, y='spectators', data=live_games_sorted, ax=ax)
            ax.set_title('Número de Espectadores por Partida ao Vivo')
            ax.set_xlabel('Partida')
            ax.set_ylabel('Número de Espectadores')
            plt.xticks([])  # Remover rótulos do eixo x
            save_figure(fig, "live_matches_spectators.png")
        
        return live_stats
    except Exception as e:
        print(f"Erro ao analisar partidas ao vivo: {e}")
        return None

# Função para analisar equipes
def analyze_teams():
    print("Analisando equipes...")
    
    # Carregar dados de equipes da Steam
    try:
        teams = load_csv("steam_teams_simplified.csv")
        
        # Estatísticas básicas
        team_stats = teams['games_played'].describe()
        team_stats_df = pd.DataFrame(team_stats).reset_index()
        team_stats_df.columns = ['Estatística', 'Valor']
        save_to_csv(team_stats_df, "team_games_played_stats.csv")
        
        # Top 10 equipes com mais jogos
        top_teams = teams.sort_values('games_played', ascending=False).head(10)
        save_to_csv(top_teams, "top_teams_by_games.csv")
        
        # Gráfico de jogos por equipe (top 10)
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x='name', y='games_played', data=top_teams, ax=ax)
        ax.set_title('Top 10 Equipes com Mais Jogos')
        ax.set_xlabel('Equipe')
        ax.set_ylabel('Número de Jogos')
        plt.xticks(rotation=45, ha='right')
        save_figure(fig, "top_teams_by_games.png")
        
        # Distribuição de jogos por equipe
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(teams['games_played'], bins=20, kde=True, ax=ax)
        ax.set_title('Distribuição do Número de Jogos por Equipe')
        ax.set_xlabel('Número de Jogos')
        ax.set_ylabel('Frequência')
        save_figure(fig, "team_games_distribution.png")
        
        return team_stats
    except Exception as e:
        print(f"Erro ao analisar equipes: {e}")
        return None

# Função para analisar dados mesclados
def analyze_merged_data():
    print("Analisando dados mesclados...")
    
    # Carregar dados mesclados de partidas
    try:
        merged_matches = load_csv("merged_match_data.csv")
        
        # Verificar se há dados suficientes para análise
        if merged_matches.empty:
            print("Não há dados mesclados suficientes para análise.")
            return None
        
        # Análise de correspondência entre APIs
        api_overlap = {
            "total_matches": len(merged_matches),
            "matches_with_pandascore_data": merged_matches.filter(like='pandascore').notna().any(axis=1).sum(),
            "matches_with_opendota_data": merged_matches.filter(like='opendota').notna().any(axis=1).sum(),
            "matches_with_steam_data": merged_matches.filter(like='steam').notna().any(axis=1).sum(),
            "matches_with_all_apis": merged_matches.filter(like='pandascore').notna().any(axis=1) & 
                                    merged_matches.filter(like='opendota').notna().any(axis=1) & 
                                    merged_matches.filter(like='steam').notna().any(axis=1)
        }
        
        # Converter para DataFrame e salvar
        api_overlap_df = pd.DataFrame([api_overlap])
        save_to_csv(api_overlap_df, "api_overlap_stats.csv")
        
        # Gráfico de sobreposição de APIs
        fig, ax = plt.subplots(figsize=(10, 6))
        overlap_data = [
            api_overlap["matches_with_pandascore_data"],
            api_overlap["matches_with_opendota_data"],
            api_overlap["matches_with_steam_data"],
            api_overlap["matches_with_all_apis"]
        ]
        overlap_labels = [
            "PandaScore",
            "OpenDota",
            "Steam",
            "Todas as APIs"
        ]
        sns.barplot(x=overlap_labels, y=overlap_data, ax=ax)
        ax.set_title('Sobreposição de Dados entre APIs')
        ax.set_xlabel('API')
        ax.set_ylabel('Número de Partidas')
        plt.xticks(rotation=45, ha='right')
        save_figure(fig, "api_overlap.png")
        
        return api_overlap
    except Exception as e:
        print(f"Erro ao analisar dados mesclados: {e}")
        return None

# Função para gerar relatório de análise
def generate_analysis_report():
    print("Gerando relatório de análise...")
    
    # Carregar resumo da coleta
    collection_summary = load_json("collection_summary.json")
    
    # Executar análises
    duration_stats = analyze_match_duration()
    hero_stats = analyze_hero_stats()
    live_stats = analyze_live_matches()
    team_stats = analyze_teams()
    api_overlap = analyze_merged_data()
    
    # Criar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "collection_summary": collection_summary,
        "analyses_performed": [
            "match_duration",
            "hero_stats",
            "live_matches",
            "teams",
            "merged_data"
        ],
        "key_findings": {
            "match_duration": {
                "mean_duration_minutes": duration_stats["mean"] if duration_stats is not None else None,
                "median_duration_minutes": duration_stats["50%"] if duration_stats is not None else None
            },
            "hero_stats": {
                "top_picked_hero": hero_stats.sort_values('pro_pick', ascending=False).iloc[0]['name'] if hero_stats is not None else None,
                "top_winrate_hero": hero_stats.sort_values('pro_winrate', ascending=False).iloc[0]['name'] if hero_stats is not None else None
            },
            "live_matches": {
                "total_live_matches": live_stats["total_matches"] if live_stats is not None else 0
            },
            "teams": {
                "total_teams": len(team_stats) if team_stats is not None else 0
            },
            "api_overlap": {
                "matches_with_all_apis": api_overlap["matches_with_all_apis"] if api_overlap is not None else 0
            }
        }
    }
    
    # Salvar relatório
    with open(os.path.join(ANALYSIS_DIR, "analysis_report.json"), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)
    
    print("Relatório de análise gerado com sucesso!")
    return report

# Função principal
def main():
    print("Iniciando análise de dados de Dota 2...")
    report = generate_analysis_report()
    print("Análise concluída!")
    return report

if __name__ == "__main__":
    main()
