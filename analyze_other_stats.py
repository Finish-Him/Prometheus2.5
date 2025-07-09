import pandas as pd

# Load the classified dataset
try:
    classified_df = pd.read_parquet("/home/ubuntu/opendota_data/opendota_pro_matches_classified.parquet")
    print("Classified dataset loaded successfully.")
except Exception as e:
    print(f"Error loading classified dataset: {e}")
    exit()

# Define KPIs to analyze
kpi_cols = [
    "kills", "deaths", "assists", "last_hits", "denies", "gold_per_min",
    "xp_per_min", "level", "net_worth", "gold_spent", "hero_damage",
    "tower_damage", "hero_healing"
]

# --- Analyze Player KPIs by Period and Tier ---
print("\nAnalyzing player KPIs by period and team tier...")

# Group by period and team tier, calculate mean for KPIs
# Filter out Unknown tier for clearer comparison between T1 and T2/Other
kpi_analysis = classified_df[classified_df["team_tier"] != "Unknown"].groupby(["period", "team_tier"])[kpi_cols].mean()

print("\n--- Average Player KPIs by Period and Team Tier ---")
print(kpi_analysis)

# --- Analyze Hero Pick Rates by Period and Tier ---
print("\nAnalyzing hero pick rates by period and team tier...")

# Filter out Unknown tier
hero_picks_analysis = classified_df[classified_df["team_tier"] != "Unknown"].groupby(["period", "team_tier", "hero_id"]).size().reset_index(name="picks")

# Calculate total picks per period/tier group
total_picks_per_group = hero_picks_analysis.groupby(["period", "team_tier"])["picks"].sum().reset_index(name="total_picks")

# Merge total picks back to calculate pick rate
hero_picks_analysis = pd.merge(hero_picks_analysis, total_picks_per_group, on=["period", "team_tier"])
hero_picks_analysis["pick_rate_percent"] = (hero_picks_analysis["picks"] / hero_picks_analysis["total_picks"]) * 100

# Pivot for better readability (optional, might be large)
# hero_pick_rates_pivot = hero_picks_analysis.pivot_table(index="hero_id", columns=["period", "team_tier"], values="pick_rate_percent", fill_value=0)
# print("\n--- Hero Pick Rates (%) by Period and Team Tier (Pivot Table) ---")
# print(hero_pick_rates_pivot.head()) # Displaying head to avoid excessive output

# Find heroes with notable changes in pick rate between periods (e.g., within T1)
t1_picks = hero_picks_analysis[hero_picks_analysis["team_tier"] == "T1"].pivot_table(index="hero_id", columns="period", values="pick_rate_percent", fill_value=0)
t1_picks["change"] = t1_picks["April_2nd_Half"] - t1_picks["April_1st_Half"]
t1_picks_sorted_change = t1_picks.sort_values("change", ascending=False)

print("\n--- Heroes with Biggest Pick Rate Change (T1 Teams, 2nd Half vs 1st Half) ---")
print("Top Increases:")
print(t1_picks_sorted_change.head(10))
print("\nTop Decreases:")
print(t1_picks_sorted_change.tail(10))

# --- Save Results --- 
try:
    output_file = "/home/ubuntu/opendota_data/analysis_results/other_stats_evolution_analysis.txt"
    with open(output_file, "w") as f:
        f.write("Analysis of Other Stats Evolution (Patch 7.38c - April 2025)\n")
        f.write("=============================================================\n\n")
        f.write("Average Player KPIs by Period and Team Tier:\n")
        f.write(kpi_analysis.to_string())
        f.write("\n\n")
        f.write("Heroes with Biggest Pick Rate Change (T1 Teams, 2nd Half vs 1st Half):\n")
        f.write("\nTop Increases:\n")
        f.write(t1_picks_sorted_change.head(10).to_string())
        f.write("\n\nTop Decreases:\n")
        f.write(t1_picks_sorted_change.tail(10).to_string())

    print(f"\nAnalysis results saved to {output_file}")
except Exception as e:
    print(f"Error saving analysis results: {e}")

print("\nOther stats analysis script finished.")

