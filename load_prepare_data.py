import pandas as pd
import os

# Define file paths
purchase_log_file = "/home/ubuntu/dota_data/purchase_logs.parquet"
pgl_matches_file = "/home/ubuntu/analysis_data/pgl_wallachia/pgl_wallachia_s4_matches_full_details.parquet"
pro_matches_additional_file = "/home/ubuntu/analysis_data/pro_matches/home/ubuntu/opendota_pro_matches_additional_detailed.parquet"
pro_matches_main_file = "/home/ubuntu/analysis_data/pro_matches/home/ubuntu/opendota_pro_matches_main_detailed.csv"

# Create a dictionary to store loaded dataframes
dataframes = {}

# Function to load data with error handling
def load_data(file_path, file_type, name):
    print(f"Loading {name} data from {file_path}...")
    try:
        if file_type == "parquet":
            df = pd.read_parquet(file_path)
        elif file_type == "csv":
            df = pd.read_csv(file_path)
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

# Load purchase logs (from previous task)
dataframes["purchase_logs"] = load_data(purchase_log_file, "parquet", "Purchase Logs")

# Load PGL Wallachia match details
dataframes["pgl_matches"] = load_data(pgl_matches_file, "parquet", "PGL Wallachia Matches")

# Load Pro Matches Additional details
dataframes["pro_matches_additional"] = load_data(pro_matches_additional_file, "parquet", "Pro Matches Additional")

# Load Pro Matches Main details
dataframes["pro_matches_main"] = load_data(pro_matches_main_file, "csv", "Pro Matches Main")

# --- Data Preparation (Initial Steps) ---

# Example: Display info for loaded dataframes
for name, df in dataframes.items():
    if df is not None:
        print(f"\nInfo for {name}:")
        df.info()
        print(f"First 5 rows of {name}:")
        print(df.head())
    else:
        print(f"\n{name} dataframe failed to load.")

# Further preparation steps will involve merging, cleaning, and feature engineering
# based on the specific analysis requirements (steps 004-007).
# For now, just saving the script.

print("\nInitial data loading script created. Next steps involve data merging and cleaning.")


