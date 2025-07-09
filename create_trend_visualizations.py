import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Setup ---
output_dir = "/home/ubuntu/opendota_data/visualizations"
os.makedirs(output_dir, exist_ok=True)
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 7) # Default figure size

# Load the classified dataset
try:
    classified_df = pd.read_parquet("/home/ubuntu/opendota_data/opendota_pro_matches_classified.parquet")
    print("Classified dataset loaded successfully.")
except Exception as e:
    print(f"Error loading classified dataset: {e}")
    exit()

# --- Recalculate/Prepare Data for Plotting ---

# 1. Match Duration Data
print("Preparing match duration data for plotting...")
match_df = classified_df[["match_id", "duration", "period", "start_datetime"]].drop_duplicates().reset_index(drop=True)
def get_team_tier(group):
    tiers = group["team_tier"].value_counts()
    return tiers.idxmax() if not tiers.empty else "Unknown"
radiant_tiers = classified_df[classified_df["isRadiant"]].groupby("match_id").apply(get_team_tier).reset_index(name="radiant_tier")
dire_tiers = classified_df[~classified_df["isRadiant"]].groupby("match_id").apply(get_team_tier).reset_index(name="dire_tier")
match_df = pd.merge(match_df, radiant_tiers, on="match_id", how="left")
match_df = pd.merge(match_df, dire_tiers, on="match_id", how="left")
def classify_match_tier(row):
    r_tier, d_tier = row["radiant_tier"], row["dire_tier"]
    if r_tier == "T1" and d_tier == "T1": return "T1 vs T1"
    if (r_tier == "T1" and d_tier == "T2/Other") or (r_tier == "T2/Other" and d_tier == "T1"): return "T1 vs T2/Other"
    if r_tier == "T2/Other" and d_tier == "T2/Other": return "T2/Other vs T2/Other"
    return "Unknown/Mixed"
match_df["match_tier_type"] = match_df.apply(classify_match_tier, axis=1)
match_df["duration_minutes"] = match_df["duration"] / 60
duration_plot_data = match_df.groupby(["period", "match_tier_type"])["duration_minutes"].mean().reset_index()

# 2. Hero Pick Rate Change Data (T1)
print("Preparing hero pick rate change data for plotting...")
hero_picks_analysis = classified_df[classified_df["team_tier"] == "T1"].groupby(["period", "hero_id"]).size().reset_index(name="picks")
total_picks_per_group = hero_picks_analysis.groupby("period")["picks"].sum().reset_index(name="total_picks")
hero_picks_analysis = pd.merge(hero_picks_analysis, total_picks_per_group, on="period")
hero_picks_analysis["pick_rate_percent"] = (hero_picks_analysis["picks"] / hero_picks_analysis["total_picks"]) * 100
t1_picks_pivot = hero_picks_analysis.pivot_table(index="hero_id", columns="period", values="pick_rate_percent", fill_value=0)
t1_picks_pivot["change"] = t1_picks_pivot["April_2nd_Half"] - t1_picks_pivot["April_1st_Half"]
t1_picks_sorted_change = t1_picks_pivot.sort_values("change", ascending=False)

# Select top N rising and falling heroes
N = 7
top_rising = t1_picks_sorted_change.head(N)
top_falling = t1_picks_sorted_change.tail(N).sort_values("change") # Sort ascending for plot
hero_change_plot_data = pd.concat([top_rising, top_falling])
hero_change_plot_data = hero_change_plot_data.reset_index()

# --- Create Visualizations ---

# 1. Average Match Duration Evolution
print("Generating: Average Match Duration Evolution by Tier Type")
plt.figure(figsize=(14, 8))
sns.barplot(data=duration_plot_data, x="match_tier_type", y="duration_minutes", hue="period", palette="coolwarm", order=["T1 vs T1", "T1 vs T2/Other", "T2/Other vs T2/Other", "Unknown/Mixed"])
plt.title("Average Match Duration Evolution (April 2025 - Patch 7.38c)")
plt.xlabel("Match Tier Type")
plt.ylabel("Average Duration (Minutes)")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(f"{output_dir}/duration_evolution_by_tier.png")
plt.close()
print(f"Saved: {output_dir}/duration_evolution_by_tier.png")

# 2. Hero Pick Rate Change (T1 Teams)
print("Generating: Hero Pick Rate Change (T1 Teams)")
plt.figure(figsize=(15, 8))
sns.barplot(data=hero_change_plot_data, x="hero_id", y="change", palette=sns.color_palette("vlag", n_colors=len(hero_change_plot_data)), order=hero_change_plot_data["hero_id"], hue="hero_id", legend=False)
plt.axhline(0, color='grey', linewidth=0.8)
plt.title(f"Top {N} Rising & Falling Heroes Pick Rate Change (T1 Teams, April 2nd Half vs 1st Half)")
plt.xlabel("Hero ID")
plt.ylabel("Change in Pick Rate (% points)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{output_dir}/hero_pick_rate_change_t1.png")
plt.close()
print(f"Saved: {output_dir}/hero_pick_rate_change_t1.png")

print("\nTrend visualization script finished.")

