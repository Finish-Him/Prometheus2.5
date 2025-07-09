import pandas as pd

# Load the classified dataset
try:
    classified_df = pd.read_parquet("/home/ubuntu/opendota_data/opendota_pro_matches_classified.parquet")
    print("Classified dataset loaded successfully.")
except Exception as e:
    print(f"Error loading classified dataset: {e}")
    exit()

# --- Prepare Match-Level Data with Tiers ---
print("\nPreparing match-level data...")

# Get unique match info (ID, duration, period)
match_df = classified_df[["match_id", "duration", "period"]].drop_duplicates().reset_index(drop=True)

# Get radiant and dire tiers for each match
# Need to handle cases where a team might be Unknown in some player rows but not others for the same match
# Let's take the most common tier assigned to players of a team in a match
def get_team_tier(group):
    # Get the tier assigned to the players of this team in this match
    tiers = group["team_tier"].value_counts()
    if not tiers.empty:
        # Return the most frequent tier (mode)
        return tiers.idxmax()
    return "Unknown"

radiant_tiers = classified_df[classified_df["isRadiant"]].groupby("match_id").apply(get_team_tier).reset_index(name="radiant_tier")
dire_tiers = classified_df[~classified_df["isRadiant"]].groupby("match_id").apply(get_team_tier).reset_index(name="dire_tier")

# Merge tiers into match_df
match_df = pd.merge(match_df, radiant_tiers, on="match_id", how="left")
match_df = pd.merge(match_df, dire_tiers, on="match_id", how="left")

# Define match tier type function
def classify_match_tier(row):
    r_tier = row["radiant_tier"]
    d_tier = row["dire_tier"]

    if r_tier == "T1" and d_tier == "T1":
        return "T1 vs T1"
    elif (r_tier == "T1" and d_tier == "T2/Other") or (r_tier == "T2/Other" and d_tier == "T1"):
        return "T1 vs T2/Other"
    elif r_tier == "T2/Other" and d_tier == "T2/Other":
        return "T2/Other vs T2/Other"
    else:
        # Includes cases with "Unknown"
        return "Unknown/Mixed"

match_df["match_tier_type"] = match_df.apply(classify_match_tier, axis=1)

print("Match-level data prepared.")
print("\nMatch Tier Type distribution:")
print(match_df["match_tier_type"].value_counts())

# --- Analyze Duration Evolution --- 
print("\nAnalyzing match duration evolution...")

# Calculate average duration in seconds
avg_duration_seconds = match_df.groupby(["period", "match_tier_type"])["duration"].agg(["mean", "count"])
overall_avg_duration_seconds = match_df.groupby("period")["duration"].agg(["mean", "count"])

# Convert mean duration to minutes
avg_duration_minutes = avg_duration_seconds.copy()
avg_duration_minutes["mean"] = avg_duration_minutes["mean"] / 60
avg_duration_minutes = avg_duration_minutes.rename(columns={"mean": "mean_duration_minutes"})

overall_avg_duration_minutes = overall_avg_duration_seconds.copy()
overall_avg_duration_minutes["mean"] = overall_avg_duration_minutes["mean"] / 60
overall_avg_duration_minutes = overall_avg_duration_minutes.rename(columns={"mean": "mean_duration_minutes"})

print("\n--- Average Match Duration (Minutes) by Period and Tier Type ---")
print(avg_duration_minutes)

print("\n--- Overall Average Match Duration (Minutes) by Period ---")
print(overall_avg_duration_minutes)

# --- Save Results --- 
try:
    output_file = "/home/ubuntu/opendota_data/analysis_results/duration_evolution_analysis.txt"
    with open(output_file, "w") as f:
        f.write("Analysis of Match Duration Evolution (Patch 7.38c - April 2025)\n")
        f.write("==============================================================\n\n")
        f.write("Match Tier Type Distribution:\n")
        f.write(match_df["match_tier_type"].value_counts().to_string())
        f.write("\n\n")
        f.write("Average Match Duration (Minutes) by Period and Tier Type:\n")
        f.write(avg_duration_minutes.to_string())
        f.write("\n\n")
        f.write("Overall Average Match Duration (Minutes) by Period:\n")
        f.write(overall_avg_duration_minutes.to_string())
    print(f"\nAnalysis results saved to {output_file}")
except Exception as e:
    print(f"Error saving analysis results: {e}")

print("\nDuration analysis script finished.")

