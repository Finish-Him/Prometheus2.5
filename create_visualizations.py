import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Function to load data safely
def load_data(file_path, file_type="csv", **kwargs):
    try:
        if file_type == "csv":
            return pd.read_csv(file_path, **kwargs)
        elif file_type == "parquet":
            return pd.read_parquet(file_path, **kwargs)
        elif file_type == "text": # For reading pre-computed stats
            # Basic text file reading, might need adjustments based on format
            # For this script, we reload the original data and recompute where needed
            # or load specific formats if saved previously.
            # Let's reload the main_df as it contains most needed info.
            print(f"Text file loading not implemented for {file_path}, reloading main_df.")
            return None
        else:
            print(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# --- Setup ---
output_dir = "/home/ubuntu/opendota_data/visualizations"
os.makedirs(output_dir, exist_ok=True)
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 7) # Default figure size

# Load main dataset
main_df = load_data("/home/ubuntu/opendota_data/opendota_pro_matches_main_detailed.csv", low_memory=False)
if main_df is None:
    exit()

# --- Visualizations ---

# 1. Top 10 Most Picked Heroes
print("Generating: Top 10 Most Picked Heroes")
top_heroes = main_df["hero_id"].value_counts().head(10)
plt.figure()
sns.barplot(x=top_heroes.index, y=top_heroes.values, palette="viridis", order=top_heroes.index, hue=top_heroes.index, legend=False)
plt.title("Top 10 Most Picked Heroes")
plt.xlabel("Hero ID")
plt.ylabel("Number of Picks")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{output_dir}/top_10_picked_heroes.png")
plt.close()
print(f"Saved: {output_dir}/top_10_picked_heroes.png")

# 2. Top 10 Hero Win Rates (Min 50 Picks)
print("Generating: Top 10 Hero Win Rates")
hero_stats = main_df.groupby("hero_id").agg(
    picks=("win", "size"),
    wins=("win", "sum")
)
hero_stats["win_rate"] = (hero_stats["wins"] / hero_stats["picks"]) * 100
min_picks = 50
reliable_hero_stats = hero_stats[hero_stats["picks"] >= min_picks].sort_values("win_rate", ascending=False).head(10)
plt.figure()
sns.barplot(x=reliable_hero_stats.index, y=reliable_hero_stats["win_rate"], palette="magma", order=reliable_hero_stats.index, hue=reliable_hero_stats.index, legend=False)
plt.title(f"Top 10 Hero Win Rates (Minimum {min_picks} Picks)")
plt.xlabel("Hero ID")
plt.ylabel("Win Rate (%)")
plt.xticks(rotation=45)
plt.ylim(bottom=reliable_hero_stats["win_rate"].min() - 2) # Adjust y-axis for better visibility
plt.tight_layout()
plt.savefig(f"{output_dir}/top_10_hero_win_rates.png")
plt.close()
print(f"Saved: {output_dir}/top_10_hero_win_rates.png")

# 3. KPI Correlation with Win Status (Heatmap)
print("Generating: KPI Correlation Heatmap")
kpi_cols = [
    "kills", "deaths", "assists", "last_hits", "denies", "gold_per_min",
    "xp_per_min", "level", "net_worth", "gold_spent", "hero_damage",
    "tower_damage", "hero_healing", "win"
]
correlation_df = main_df[kpi_cols].copy()
correlation_df["win"] = correlation_df["win"].astype(int)
correlation_df.dropna(inplace=True)
correlation_matrix = correlation_df.corr()
plt.figure(figsize=(14, 10))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=.5)
plt.title("Correlation Matrix of Player KPIs and Win Status")
plt.xticks(rotation=45, ha='right') # Corrected this line
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{output_dir}/kpi_win_correlation_heatmap.png")
plt.close()
print(f"Saved: {output_dir}/kpi_win_correlation_heatmap.png")

# 4. Average KPIs: Winners vs Losers
print("Generating: Average KPIs Comparison (Winners vs Losers)")
kpi_comparison = main_df.groupby("win")[kpi_cols[:-1]].mean().T
kpi_comparison.columns = ["Loser_Avg", "Winner_Avg"]
kpi_comparison_melted = kpi_comparison.reset_index().melt(id_vars="index", var_name="Outcome", value_name="Average Value")
plt.figure(figsize=(15, 8))
sns.barplot(data=kpi_comparison_melted, x="index", y="Average Value", hue="Outcome", palette=["red", "green"])
plt.title("Average Player KPIs: Winners vs Losers")
plt.xlabel("KPI")
plt.ylabel("Average Value")
plt.xticks(rotation=45, ha='right') # Corrected this line
plt.tight_layout()
plt.savefig(f"{output_dir}/avg_kpi_comparison_win_loss.png")
plt.close()
print(f"Saved: {output_dir}/avg_kpi_comparison_win_loss.png")

# 5. GPM Distribution: Winners vs Losers
print("Generating: GPM Distribution (Winners vs Losers)")
plt.figure()
sns.histplot(data=main_df, x="gold_per_min", hue="win", kde=True, palette=["red", "green"], bins=50)
plt.title("Gold Per Minute (GPM) Distribution: Winners vs Losers")
plt.xlabel("GPM")
plt.ylabel("Frequency")
plt.xlim(0, main_df["gold_per_min"].quantile(0.99)) # Limit x-axis to 99th percentile for better view
plt.tight_layout()
plt.savefig(f"{output_dir}/gpm_distribution_win_loss.png")
plt.close()
print(f"Saved: {output_dir}/gpm_distribution_win_loss.png")

# 6. XPM Distribution: Winners vs Losers
print("Generating: XPM Distribution (Winners vs Losers)")
plt.figure()
sns.histplot(data=main_df, x="xp_per_min", hue="win", kde=True, palette=["red", "green"], bins=50)
plt.title("Experience Per Minute (XPM) Distribution: Winners vs Losers")
plt.xlabel("XPM")
plt.ylabel("Frequency")
plt.xlim(0, main_df["xp_per_min"].quantile(0.99)) # Limit x-axis to 99th percentile
plt.tight_layout()
plt.savefig(f"{output_dir}/xpm_distribution_win_loss.png")
plt.close()
print(f"Saved: {output_dir}/xpm_distribution_win_loss.png")

# 7. Top 10 Team Win Rates (Min 20 Games)
# Recalculate team stats as loading from text is not implemented
print("Generating: Top 10 Team Win Rates")
match_wins = main_df[["match_id", "radiant_win"]].drop_duplicates()
radiant_teams = main_df[["match_id", "radiant_team_id", "radiant_name"]].drop_duplicates()
dire_teams = main_df[["match_id", "dire_team_id", "dire_name"]].drop_duplicates()
radiant_data = pd.merge(radiant_teams, match_wins, on="match_id")
dire_data = pd.merge(dire_teams, match_wins, on="match_id")
radiant_data["win"] = radiant_data["radiant_win"]
dire_data["win"] = ~dire_data["radiant_win"]
radiant_final = radiant_data[["radiant_team_id", "radiant_name", "win"]].rename(columns={"radiant_team_id": "team_id", "radiant_name": "team_name"})
dire_final = dire_data[["dire_team_id", "dire_name", "win"]].rename(columns={"dire_team_id": "team_id", "dire_name": "team_name"})
all_teams = pd.concat([radiant_final, dire_final])
all_teams = all_teams.dropna(subset=["team_id", "team_name"])
all_teams["team_id"] = all_teams["team_id"].astype(int)
team_stats = all_teams.groupby("team_name").agg(
    games=("win", "size"),
    wins=("win", "sum")
)
team_stats["win_rate"] = (team_stats["wins"] / team_stats["games"]) * 100
min_games = 20
reliable_team_stats = team_stats[team_stats["games"] >= min_games].sort_values("win_rate", ascending=False).head(10)
plt.figure(figsize=(14, 8))
sns.barplot(x=reliable_team_stats.index, y=reliable_team_stats["win_rate"], palette="coolwarm", order=reliable_team_stats.index, hue=reliable_team_stats.index, legend=False)
plt.title(f"Top 10 Team Win Rates (Minimum {min_games} Games)")
plt.xlabel("Team Name")
plt.ylabel("Win Rate (%)")
plt.xticks(rotation=45, ha='right') # Corrected this line
plt.ylim(bottom=reliable_team_stats["win_rate"].min() - 2)
plt.tight_layout()
plt.savefig(f"{output_dir}/top_10_team_win_rates.png")
plt.close()
print(f"Saved: {output_dir}/top_10_team_win_rates.png")

print("\nVisualization script finished.")

