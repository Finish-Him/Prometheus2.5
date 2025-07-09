import pandas as pd
import numpy as np

# Function to save analysis results
def save_output(data, filename, header):
    try:
        with open(filename, 'w') as f:
            f.write(header + "\n\n")
            if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
                f.write(data.to_string())
            else:
                f.write(str(data))
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

# Load the main dataset
try:
    main_df = pd.read_csv('/home/ubuntu/opendota_data/opendota_pro_matches_main_detailed.csv', low_memory=False)
    print("Main dataset loaded successfully.")
except Exception as e:
    print(f"Error loading main dataset: {e}")
    exit()

output_dir = '/home/ubuntu/opendota_data/analysis_results'
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1000)

# Create output directory
import os
os.makedirs(output_dir, exist_ok=True)

# --- 1. Correlation Analysis (Player Level KPIs vs Win) ---
print("\n--- Calculating KPI Correlations ---")
kpi_cols = [
    'kills', 'deaths', 'assists', 'last_hits', 'denies', 'gold_per_min',
    'xp_per_min', 'level', 'net_worth', 'gold_spent', 'hero_damage',
    'tower_damage', 'hero_healing', 'win'
]
correlation_df = main_df[kpi_cols].copy()
# Convert 'win' boolean to integer (1 for True, 0 for False)
correlation_df['win'] = correlation_df['win'].astype(int)

# Handle potential missing values (if any in these specific columns)
correlation_df.dropna(inplace=True)

correlation_matrix = correlation_df.corr()
win_correlation = correlation_matrix['win'].sort_values(ascending=False)
save_output(win_correlation, f"{output_dir}/kpi_win_correlation.txt", "Correlation of Player KPIs with Win Status")

# --- 2. KPI Comparison (Winners vs Losers) ---
print("\n--- Comparing KPIs for Winners vs Losers ---")
kpi_comparison = main_df.groupby('win')[kpi_cols[:-1]].mean().T # Exclude 'win' itself
kpi_comparison.columns = ['Loser_Avg', 'Winner_Avg']
kpi_comparison['Difference (Winner - Loser)'] = kpi_comparison['Winner_Avg'] - kpi_comparison['Loser_Avg']
kpi_comparison['Relative_Difference (%)'] = (kpi_comparison['Difference (Winner - Loser)'] / kpi_comparison['Loser_Avg']) * 100
save_output(kpi_comparison, f"{output_dir}/kpi_comparison_win_loss.txt", "Average Player KPIs for Winners vs Losers")

# --- 3. Hero Win Rates --- 
print("\n--- Calculating Hero Win Rates ---")
hero_stats = main_df.groupby('hero_id').agg(
    picks=('win', 'size'),
    wins=('win', 'sum')
)
hero_stats['win_rate'] = (hero_stats['wins'] / hero_stats['picks']) * 100

# Filter for heroes with a reasonable number of picks (e.g., > 50)
min_picks = 50
reliable_hero_stats = hero_stats[hero_stats['picks'] >= min_picks].sort_values('win_rate', ascending=False)
save_output(reliable_hero_stats, f"{output_dir}/hero_win_rates.txt", f"Hero Win Rates (Minimum {min_picks} Picks)")

# --- 4. Team Win Rates --- 
print("\n--- Calculating Team Win Rates ---")
# Need match-level win information
match_wins = main_df[['match_id', 'radiant_win']].drop_duplicates()

# Get radiant and dire team info per match
radiant_teams = main_df[['match_id', 'radiant_team_id', 'radiant_name']].drop_duplicates()
dire_teams = main_df[['match_id', 'dire_team_id', 'dire_name']].drop_duplicates()

# Merge win info with team info
radiant_data = pd.merge(radiant_teams, match_wins, on='match_id')
dire_data = pd.merge(dire_teams, match_wins, on='match_id')

# Calculate wins for each team
radiant_data['win'] = radiant_data['radiant_win']
dire_data['win'] = ~dire_data['radiant_win'] # Dire wins if radiant_win is False

# Prepare for concatenation
radiant_final = radiant_data[['radiant_team_id', 'radiant_name', 'win']].rename(columns={'radiant_team_id': 'team_id', 'radiant_name': 'team_name'})
dire_final = dire_data[['dire_team_id', 'dire_name', 'win']].rename(columns={'dire_team_id': 'team_id', 'dire_name': 'team_name'})

# Combine and calculate stats
all_teams = pd.concat([radiant_final, dire_final])
all_teams = all_teams.dropna(subset=['team_id']) # Remove matches with missing team IDs
all_teams['team_id'] = all_teams['team_id'].astype(int)

team_stats = all_teams.groupby(['team_id', 'team_name']).agg(
    games=('win', 'size'),
    wins=('win', 'sum')
)
team_stats['win_rate'] = (team_stats['wins'] / team_stats['games']) * 100

# Filter for teams with a reasonable number of games (e.g., > 20 matches, which is 200 player rows)
min_games = 20 
reliable_team_stats = team_stats[team_stats['games'] >= min_games].sort_values('win_rate', ascending=False)
save_output(reliable_team_stats, f"{output_dir}/team_win_rates.txt", f"Team Win Rates (Minimum {min_games} Games Played)")

print("\nPattern and trend analysis script finished.")

