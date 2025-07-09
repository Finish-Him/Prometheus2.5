import pandas as pd

# Load the datasets
try:
    main_df = pd.read_csv('/home/ubuntu/opendota_data/opendota_pro_matches_main_detailed.csv')
    additional_df = pd.read_csv('/home/ubuntu/opendota_data/opendota_pro_matches_additional_detailed.csv')
    print("Datasets loaded successfully.")
except Exception as e:
    print(f"Error loading datasets: {e}")
    exit()

# --- Analysis of main_df (Player-level data) ---
print("\n--- Descriptive Statistics for Main Dataset (Numerical Columns) ---")
descriptive_stats_main = main_df.describe()
print(descriptive_stats_main)

print("\n--- Value Counts for Key Categorical Columns in Main Dataset ---")

print("\nTop 10 Heroes Picked:")
print(main_df["hero_id"].value_counts().head(10))

print("\nRadiant Win Distribution:")
print(main_df.drop_duplicates(subset=["match_id"])["radiant_win"].value_counts(normalize=True))

print("\nTop 10 Leagues:")
print(main_df["league_name"].value_counts().head(10))

# --- Analysis of additional_df (Match-level data) ---
print("\n--- Descriptive Statistics for Additional Dataset (Numerical Columns) ---")
# Note: gold_adv and xp_adv are all nulls based on previous exploration, roshan_kills is object type
# Convert roshan_kills to a more usable format if needed later, for now describe numericals
descriptive_stats_additional = additional_df.describe()
print(descriptive_stats_additional)

# Save statistics to files
try:
    descriptive_stats_main.to_csv('/home/ubuntu/opendota_data/descriptive_stats_main.csv')
    descriptive_stats_additional.to_csv('/home/ubuntu/opendota_data/descriptive_stats_additional.csv')
    print("\nDescriptive statistics saved to CSV files.")
except Exception as e:
    print(f"Error saving statistics: {e}")

# Optional: Merge dataframes for combined analysis (Example)
# merged_df = pd.merge(main_df, additional_df.drop(columns=['duration']), on='match_id', how='left')
# print("\n--- Merged DataFrame Info ---")
# print(merged_df.info())
# print(merged_df.head())

print("\nDescriptive analysis script finished.")


