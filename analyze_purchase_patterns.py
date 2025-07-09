import pandas as pd
import os
import numpy as np

# Define file paths
purchase_log_file = "/home/ubuntu/dota_data/purchase_logs.parquet"
pgl_matches_file = "/home/ubuntu/analysis_data/pgl_wallachia/pgl_wallachia_s4_matches_full_details.parquet"
pro_matches_main_file = "/home/ubuntu/analysis_data/pro_matches/home/ubuntu/opendota_pro_matches_main_detailed.csv"

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
            # Try detecting encoding issues, default to utf-8
            try:
                df = pd.read_csv(file_path, usecols=columns)
            except UnicodeDecodeError:
                print(f"UTF-8 decoding failed for {file_path}, trying latin1.")
                df = pd.read_csv(file_path, usecols=columns, encoding='latin1')
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

# Load necessary data
purchase_logs = load_data(purchase_log_file, "parquet", "Purchase Logs")
pgl_matches = load_data(pgl_matches_file, "parquet", "PGL Matches", columns=["match_id"])
# Load only relevant columns from the large pro_matches_main CSV
pro_matches_main = load_data(pro_matches_main_file, "csv", "Pro Matches Main", columns=["match_id", "hero_id"])

# --- Data Validation ---
if purchase_logs is None or purchase_logs.empty:
    print("Purchase logs data is missing or empty. Cannot proceed with analysis.")
    exit()
if pgl_matches is None:
    print("PGL matches data failed to load. Analysis will exclude PGL comparison.")
if pro_matches_main is None:
    print("Pro matches main data failed to load. Cannot link purchases to heroes accurately.")
    # Might still be possible to analyze overall purchase patterns if hero_id is in purchase_logs
    if 'hero_id' not in purchase_logs.columns:
        print("hero_id not found in purchase_logs either. Exiting.")
        exit()

# --- Analysis --- 
print("\nStarting purchase pattern analysis...")

# Ensure required columns exist
required_cols = ['match_id', 'hero_id', 'key', 'time']
if not all(col in purchase_logs.columns for col in required_cols):
    print(f"Error: Purchase logs missing one or more required columns: {required_cols}")
    exit()

# 1. Overall Purchase Frequency (All Pro Matches in the log)
print("\nCalculating overall item purchase frequency per hero...")
overall_purchase_counts = purchase_logs.groupby(['hero_id', 'key']).size().reset_index(name='purchase_count')
overall_purchase_counts = overall_purchase_counts.sort_values(by=['hero_id', 'purchase_count'], ascending=[True, False])

# Save overall counts
overall_counts_file = os.path.join(output_dir, "overall_hero_item_counts.csv")
overall_purchase_counts.to_csv(overall_counts_file, index=False)
print(f"Saved overall purchase counts to {overall_counts_file}")

# 2. Average Purchase Time (Overall)
print("\nCalculating average purchase time per hero/item...")
# Convert time to numeric, coercing errors
purchase_logs['time_numeric'] = pd.to_numeric(purchase_logs['time'], errors='coerce')
# Filter out potential negative times (e.g., pre-game items) for average calculation if needed, or analyze separately
positive_time_purchases = purchase_logs[purchase_logs['time_numeric'] >= 0]

average_purchase_time = positive_time_purchases.groupby(['hero_id', 'key'])['time_numeric'].mean().reset_index(name='average_purchase_time_seconds')
average_purchase_time = average_purchase_time.sort_values(by=['hero_id', 'average_purchase_time_seconds'], ascending=[True, True])

# Save average times
average_time_file = os.path.join(output_dir, "average_hero_item_purchase_time.csv")
average_purchase_time.to_csv(average_time_file, index=False)
print(f"Saved average purchase times to {average_time_file}")

# 3. PGL vs General Pro Match Comparison (if PGL data available)
if pgl_matches is not None and not pgl_matches.empty:
    print("\nComparing PGL vs General Pro purchase patterns...")
    pgl_match_ids = set(pgl_matches['match_id'])
    
    # Separate purchase logs
    pgl_purchases = purchase_logs[purchase_logs['match_id'].isin(pgl_match_ids)]
    general_pro_purchases = purchase_logs[~purchase_logs['match_id'].isin(pgl_match_ids)]
    
    # Calculate counts for PGL
    pgl_purchase_counts = pgl_purchases.groupby(['hero_id', 'key']).size().reset_index(name='pgl_purchase_count')
    pgl_counts_file = os.path.join(output_dir, "pgl_hero_item_counts.csv")
    pgl_purchase_counts.to_csv(pgl_counts_file, index=False)
    print(f"Saved PGL purchase counts to {pgl_counts_file}")

    # Calculate counts for General Pro
    general_pro_counts = general_pro_purchases.groupby(['hero_id', 'key']).size().reset_index(name='general_pro_purchase_count')
    general_counts_file = os.path.join(output_dir, "general_pro_hero_item_counts.csv")
    general_pro_counts.to_csv(general_counts_file, index=False)
    print(f"Saved General Pro purchase counts to {general_counts_file}")

    # Optional: Merge for direct comparison (might create large file)
    # comparison_df = pd.merge(pgl_purchase_counts, general_pro_counts, on=['hero_id', 'key'], how='outer').fillna(0)
    # comparison_file = os.path.join(output_dir, "pgl_vs_general_hero_item_counts.csv")
    # comparison_df.to_csv(comparison_file, index=False)
    # print(f"Saved comparison counts to {comparison_file}")
else:
    print("\nSkipping PGL comparison due to missing PGL match data.")


# --- Placeholder for Item Name Mapping ---
# TODO: Need to map 'key' (item identifier) to actual item names for better readability.
# This might involve loading an item constants file or using an external mapping.
# Example: item_mapping = {1: 'blink', 2: 'blades_of_attack', ...}
# overall_purchase_counts['item_name'] = overall_purchase_counts['key'].map(item_mapping)

print("\nPurchase pattern analysis script finished.")

