import pandas as pd
import os
import json
import numpy as np
from ast import literal_eval # Safely evaluate string literals

# Define file paths
purchase_log_file = "/home/ubuntu/dota_data/purchase_logs.parquet"
pro_matches_main_file = "/home/ubuntu/analysis_data/pro_matches/home/ubuntu/opendota_pro_matches_main_detailed.csv"
item_constants_file = "/home/ubuntu/analysis_data/pgl_wallachia/item_constants.json" # Assuming this exists from provided files

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
        elif file_type == "json":
            with open(file_path, "r") as f:
                # Load JSON data directly, might not be a DataFrame initially
                df_data = json.load(f)
                # If it's a list of records, convert to DataFrame
                if isinstance(df_data, list):
                    df = pd.DataFrame(df_data)
                # If it's a dict (like item constants), return as is
                elif isinstance(df_data, dict):
                    df = df_data # Return the dict itself
                else:
                     print(f"Loaded JSON data is not a list or dict: {type(df_data)}")
                     return None
        else:
            print(f"Unsupported file type: {file_type} for file {file_path}")
            return None
        print(f"Successfully loaded {name} data.")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# --- Load Data ---
purchase_logs = load_data(purchase_log_file, "parquet", "Purchase Logs", columns=["match_id", "hero_id", "key", "time"])
# Load relevant columns from the main match data
match_cols = [
    "match_id", "hero_id", "player_slot", "win", "kills", "deaths", "assists",
    "gold_per_min", "xp_per_min", "hero_damage", "tower_damage", "hero_healing",
    "item_0", "item_1", "item_2", "item_3", "item_4", "item_5",
    "backpack_0", "backpack_1", "backpack_2", "item_neutral"
]
matches_main = load_data(pro_matches_main_file, "csv", "Pro Matches Main", columns=match_cols)

# --- Load Item Constants for Mapping ---
item_constants = load_data(item_constants_file, "json", "Item Constants")
item_mapping = {}
if item_constants and isinstance(item_constants, dict):
    # Assuming item_constants is a dict like { "item_name": { "id": item_id, ... } }
    try:
        item_mapping = {v["id"]: v.get("dname", k) for k, v in item_constants.items() if isinstance(v, dict) and "id" in v}
        print(f"Created item mapping for {len(item_mapping)} items from dict structure.")
    except Exception as e:
        print(f"Error processing item constants dict: {e}")
        item_mapping = {}
else:
    print("Item constants not loaded or not in expected dict format. Item names will not be available in results.")

# --- Data Validation ---
if purchase_logs is None or purchase_logs.empty:
    print("Purchase logs data is missing or empty. Cannot proceed.")
    exit()
if matches_main is None or matches_main.empty:
    print("Main match data is missing or empty. Cannot proceed.")
    exit()

# --- Data Preparation ---
print("Preparing data for impact analysis...")

# 1. Map purchase log keys to item names if possible
# The purchase log `key` seems to be the item name string already
print("Sample purchase log keys:", purchase_logs["key"].unique()[:20])
item_name_to_id = {v: k for k, v in item_mapping.items()}

# 2. Identify items purchased per player per match from purchase_logs
items_bought_per_player = purchase_logs.groupby(["match_id", "hero_id"])["key"].apply(set).reset_index(name="items_bought_set")

# 3. Merge items bought with main match stats
matches_with_items = pd.merge(matches_main, items_bought_per_player, on=["match_id", "hero_id"], how="left")
matches_with_items["items_bought_set"] = matches_with_items["items_bought_set"].apply(lambda x: x if isinstance(x, set) else set())

print(f"Merged match data with purchase logs. Shape: {matches_with_items.shape}")

# --- Impact Analysis --- 
print("Analyzing item impact on win rate and stats...")

# Define key items to analyze (using string names from purchase logs)
key_items = [
    "black_king_bar", "blink", "aghanims_shard", "refresher_shard", "refresher",
    "pipe", "mekansm", "crimson_guard", "force_staff", "glimmer_cape",
    "aeon_disk", "wind_waker", "sheepstick", "abyssal_blade", "satanic",
    "skadi", "butterfly", "monkey_king_bar", "rapier", "silver_edge", "bloodthorn"
]

results = []

for item_name in key_items:
    print(f"Analyzing impact of: {item_name}")

    # Check if item exists in any purchase log
    if not any(item_name in s for s in matches_with_items["items_bought_set"] if isinstance(s, set)):
        print(f"  Item ", item_name, " not found in purchase logs. Skipping.")
        continue

    matches_with_items["has_item"] = matches_with_items["items_bought_set"].apply(lambda x: item_name in x if isinstance(x, set) else False)

    # Calculate overall win rate with/without item
    win_rate_with = matches_with_items[matches_with_items["has_item"]]["win"].mean()
    win_rate_without = matches_with_items[~matches_with_items["has_item"]]["win"].mean()
    count_with = matches_with_items["has_item"].sum()
    count_without = len(matches_with_items) - count_with

    # Calculate average stats with/without item
    stats_cols = ["kills", "deaths", "assists", "gold_per_min", "xp_per_min", "hero_damage", "tower_damage", "hero_healing"]
    avg_stats_with = matches_with_items[matches_with_items["has_item"]][stats_cols].mean()
    avg_stats_without = matches_with_items[~matches_with_items["has_item"]][stats_cols].mean()

    result_row = {
        "item_name": item_name,
        "count_with_item": count_with,
        "count_without_item": count_without,
        "win_rate_with_item": win_rate_with,
        "win_rate_without_item": win_rate_without,
    }

    for stat in stats_cols:
        result_row[f"avg_{stat}_with"] = avg_stats_with.get(stat, np.nan)
        result_row[f"avg_{stat}_without"] = avg_stats_without.get(stat, np.nan)

    results.append(result_row)

    # Clean up temporary column
    matches_with_items = matches_with_items.drop(columns=["has_item"])

# --- Save Results --- 
if results:
    impact_df = pd.DataFrame(results)
    output_file = os.path.join(output_dir, "item_impact_analysis.csv")
    impact_df.to_csv(output_file, index=False)
    print(f"\nSaved item impact analysis results to {output_file}")
else:
    print("\nNo results generated from item impact analysis.")

print("\nItem impact analysis script finished.")

