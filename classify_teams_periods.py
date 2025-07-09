import pandas as pd

# Load the main dataset
try:
    main_df = pd.read_csv("/home/ubuntu/opendota_data/opendota_pro_matches_main_detailed.csv", low_memory=False)
    print("Main dataset loaded successfully.")
except Exception as e:
    print(f"Error loading main dataset: {e}")
    exit()

# Convert start_time to datetime if not already done
if "start_datetime" not in main_df.columns:
     main_df["start_datetime"] = pd.to_datetime(main_df["start_time"], unit="s")

# --- Identify Tier 1 Teams based on PGL Wallachia 2025 Season 4 ---
pgl_league_name = "PGL Wallachia 2025 Season 4"
pgl_matches = main_df[main_df["league_name"] == pgl_league_name]

# Get unique team IDs and names from PGL matches (both radiant and dire)
pgl_radiant_teams = pgl_matches[["radiant_team_id", "radiant_name"]].dropna().drop_duplicates()
pgl_dire_teams = pgl_matches[["dire_team_id", "dire_name"]].dropna().drop_duplicates()

# Rename columns for consistency
pgl_radiant_teams.columns = ["team_id", "team_name"]
pgl_dire_teams.columns = ["team_id", "team_name"]

# Combine and get unique PGL teams
pgl_teams = pd.concat([pgl_radiant_teams, pgl_dire_teams]).drop_duplicates().reset_index(drop=True)
pgl_teams["team_id"] = pgl_teams["team_id"].astype(int)

print(f"\n--- Teams found in {pgl_league_name} ---")
print(pgl_teams)

# --- Define Tier 1 based on user input ---
# Exclude specific teams mentioned by the user
exceptions_names = ["Na\'vi JR", "Heroic", "EDGe"] # User provided names, using escaped apostrophe for Na'vi
exceptions_ids = set()

# Find IDs for exception names (case-insensitive check just in case)
for index, row in pgl_teams.iterrows():
    # Using exact name match after checking the printout might be safer
    # Let's stick to case-insensitive substring check for now
    if any(exc.lower() in row["team_name"].lower() for exc in exceptions_names):
        exceptions_ids.add(row["team_id"])
        print(f'Identified exception: {row["team_name"]} (ID: {row["team_id"]})')

# Define Tier 1 team IDs
tier1_team_ids = set(pgl_teams["team_id"]) - exceptions_ids
print(f"\nTotal PGL teams found: {len(pgl_teams)}")
print(f"Exceptions identified: {len(exceptions_ids)}")
print(f"Final Tier 1 teams count: {len(tier1_team_ids)}")
# print(f"Tier 1 Team IDs: {tier1_team_ids}") # Commented out to avoid excessive output


# --- Add 'tier' column to the main DataFrame ---
# This column will classify each PLAYER's team in that specific match
def assign_tier(row):
    # Check if the player is Radiant or Dire
    if row["isRadiant"]:
        team_id = row["radiant_team_id"]
    else:
        team_id = row["dire_team_id"]

    # Handle potential NaN team_id
    if pd.isna(team_id):
        return "Unknown"

    team_id = int(team_id) # Ensure it's int for comparison

    if team_id in tier1_team_ids:
        return "T1"
    else:
        # Check if the team played in PGL but was an exception
        # We don't explicitly need this check if T1 is defined as PGL minus exceptions
        # All others are T2/Other
        return "T2/Other"


print("\nAssigning tiers to each player record...")
main_df["team_tier"] = main_df.apply(assign_tier, axis=1)
print("Tier assignment complete.")
print("\nTier distribution in player records:")
print(main_df["team_tier"].value_counts())

# --- Add 'period' column --- 
# Define the midpoint date for splitting April 2025
mid_april_date = pd.Timestamp("2025-04-16") # Split point (exclusive for first half)

main_df["period"] = main_df["start_datetime"].apply(lambda date: "April_1st_Half" if date < mid_april_date else "April_2nd_Half")
print("\nPeriod assignment complete.")
print("\nPeriod distribution in player records:")
print(main_df["period"].value_counts())


# --- Save the updated DataFrame --- 
try:
    output_file = "/home/ubuntu/opendota_data/opendota_pro_matches_classified.parquet"
    main_df.to_parquet(output_file, index=False)
    print(f"\nClassified data saved to {output_file}")
except Exception as e:
    print(f"Error saving classified data: {e}")

print("\nScript finished.")

