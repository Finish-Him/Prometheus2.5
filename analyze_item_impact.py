import pandas as pd
import os
import json
from ast import literal_eval # Safely evaluate string literals

# Define file paths
purchase_log_file = "/home/ubuntu/dota_data/purchase_logs.parquet"
pro_matches_additional_file = "/home/ubuntu/analysis_data/pro_matches/home/ubuntu/opendota_pro_matches_additional_detailed.parquet"

# Output directory
output_dir = "/home/ubuntu/analysis_results"
os.makedirs(output_dir, exist_ok=True)

# Function to load data with error handling
def load_data(file_path, file_type, name, columns=None):
    print(f"Loading {name} data from {file_path}...")
    try:
        if file_type == "parquet":
            df = pd.read_parquet(file_path, columns=columns)
        elif file_type == "csv":
            try:
                df = pd.read_csv(file_path, usecols=columns)
            except UnicodeDecodeError:
                print(f"UTF-8 decoding failed for {file_path}, trying latin1.")
                df = pd.read_csv(file_path, usecols=columns, encoding='latin1') # Corrected encoding string
        else:
            print(f"Unsupported file type: {file_type} for file {file_path}")
            return None
        print(f"Successfully loaded {name} data. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# Load purchase logs and teamfight data
purchase_logs = load_data(purchase_log_file, "parquet", "Purchase Logs")
# Load the full additional details file, specifically needing teamfight columns
teamfight_data = load_data(pro_matches_additional_file, "parquet", "Pro Matches Additional", columns=["match_id", "radiant_teamfights", "dire_teamfights"])

# --- Data Validation ---
if purchase_logs is None or purchase_logs.empty:
    print("Purchase logs data is missing or empty. Cannot proceed.")
    exit()
if teamfight_data is None or teamfight_data.empty:
    print("Teamfight data is missing or empty. Cannot proceed with teamfight impact analysis.")
    exit()
if "radiant_teamfights" not in teamfight_data.columns or "dire_teamfights" not in teamfight_data.columns:
     print("Teamfight columns not found in the loaded data. Cannot proceed.")
     exit()

# --- Teamfight Data Parsing ---
print("Parsing teamfight data...")
all_fights = []

def parse_fight_column(row, column_name):
    match_id = row["match_id"]
    fights_str = row[column_name]
    parsed_fights = []
    if isinstance(fights_str, str):
        try:
            # Use literal_eval for safety if it's a string representation of a list
            fights_list = literal_eval(fights_str)
            if isinstance(fights_list, list):
                 for fight in fights_list:
                     if isinstance(fight, dict):
                         fight["match_id"] = match_id
                         # Add side info if needed (e.g., radiant/dire)
                         fight["side"] = "radiant" if "radiant" in column_name else "dire"
                         parsed_fights.append(fight)
            else:
                print(f"Warning: Unexpected data type after eval for {column_name} in match {match_id}: {type(fights_list)}")
        except (ValueError, SyntaxError, TypeError) as e:
            # Handle cases where the string is not a valid list literal (e.g., None, empty string, malformed)
            # print(f"Warning: Could not parse {column_name} for match {match_id}: {e}, value: {fights_str[:100]}")
            pass # Ignore parsing errors for now
    elif isinstance(fights_str, list): # Already a list
        for fight in fights_str:
            if isinstance(fight, dict):
                fight["match_id"] = match_id
                fight["side"] = "radiant" if "radiant" in column_name else "dire"
                parsed_fights.append(fight)
    # Handle None or other types if necessary
    elif fights_str is not None:
        print(f"Warning: Unexpected data type for {column_name} in match {match_id}: {type(fights_str)}")

    return parsed_fights

# Apply parsing row by row (can be slow for very large data)
# Consider optimizing if performance is an issue (e.g., using apply with error handling)
for index, row in teamfight_data.iterrows():
    all_fights.extend(parse_fight_column(row, "radiant_teamfights"))
    all_fights.extend(parse_fight_column(row, "dire_teamfights"))

if not all_fights:
    print("Error: No teamfights could be parsed from the data.")
    exit()

fights_df = pd.DataFrame(all_fights)
print(f"Successfully parsed {len(fights_df)} teamfight records.")

# --- Merge and Analyze --- 
print("Merging purchase logs with fight data...")

# Ensure time columns are numeric
purchase_logs["time"] = pd.to_numeric(purchase_logs["time"], errors="coerce")
fights_df["start"] = pd.to_numeric(fights_df["start"], errors="coerce")
fights_df["end"] = pd.to_numeric(fights_df["end"], errors="coerce")

# Filter out invalid times
purchase_logs = purchase_logs.dropna(subset=["time"])
fights_df = fights_df.dropna(subset=["start", "end"])

# Create a structure to hold item presence before each fight
# This is complex: requires iterating through fights, finding relevant players, 
# and checking their purchases before the fight start time.

# Simplified Approach: Analyze correlation between having *ever* bought an item and overall fight performance
# This ignores timing but is easier to implement with current structure.

# 1. Get unique items purchased per hero per match
items_per_hero_match = purchase_logs.groupby(["match_id", "hero_id"])["key"].unique().reset_index()
items_per_hero_match["items_set"] = items_per_hero_match["key"].apply(set)

# 2. Aggregate fight stats per hero per match (requires player details in fights_df)
# The provided teamfight data seems aggregated per team, not per player within the fight.
# Example structure assumed for fights_df: {start, end, deaths, players: [{player_slot, deaths, damage,...}], match_id, side}
# If `players` list is not present or detailed, we cannot directly link items to player performance *within* fights.

# Let's check the columns of the parsed fights_df
print("\nColumns in parsed fights_df:")
print(fights_df.columns)

# --- Analysis based on available fight data --- 
# The teamfight data seems aggregated per team (`radiant_teamfights`, `dire_teamfights`)
# It might contain total deaths/damage per fight, but likely not per-player details linked to items.
# Example columns might be: 'start', 'end', 'last_death', 'deaths', 'match_id', 'side'

if "deaths" in fights_df.columns and "start" in fights_df.columns:
    print("\nAnalyzing correlation between item purchases and overall match fight deaths...")
    # Aggregate total deaths per match from fights
    deaths_per_match = fights_df.groupby("match_id")["deaths"].sum().reset_index(name="total_fight_deaths")

    # Aggregate items purchased per match (any hero)
    items_per_match = purchase_logs.groupby("match_id")["key"].unique().reset_index()
    items_per_match["items_set"] = items_per_match["key"].apply(set)

    # Merge deaths with items
    fight_item_corr = pd.merge(deaths_per_match, items_per_match, on="match_id", how="inner")

    # Analyze if presence of certain items correlates with total fight deaths
    # Example: Check for Black King Bar (item key might vary, assume 'bkb' for now)
    # Need item key mapping!
    ITEM_KEY_BKB = "bkb" # Placeholder - Replace with actual key
    fight_item_corr["has_bkb"] = fight_item_corr["items_set"].apply(lambda x: ITEM_KEY_BKB in x)

    avg_deaths_with_bkb = fight_item_corr[fight_item_corr["has_bkb"]]["total_fight_deaths"].mean()
    avg_deaths_without_bkb = fight_item_corr[~fight_item_corr["has_bkb"]]["total_fight_deaths"].mean()

    print(f"Average total fight deaths in matches WHERE BKB WAS PURCHASED: {avg_deaths_with_bkb:.2f}")
    print(f"Average total fight deaths in matches WHERE BKB WAS NOT PURCHASED: {avg_deaths_without_bkb:.2f}")

    # Save this correlation data
    corr_file = os.path.join(output_dir, "item_presence_vs_fight_deaths.csv")
    fight_item_corr.to_csv(corr_file, index=False)
    print(f"Saved item presence vs fight deaths analysis to {corr_file}")

else:
    print("\nCould not perform correlation analysis: Missing 'deaths' or 'start' columns in parsed fight data.")

print("\nTeamfight impact analysis script finished. Note: Analysis is limited by the structure of available teamfight data.")

