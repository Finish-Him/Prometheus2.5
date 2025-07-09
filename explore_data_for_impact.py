import pandas as pd
import os

# Define file paths
purchase_log_file = "/home/ubuntu/dota_data/purchase_logs.parquet"
pgl_matches_file = "/home/ubuntu/analysis_data/pgl_wallachia/pgl_wallachia_s4_matches_full_details.parquet"
pro_matches_additional_file = "/home/ubuntu/analysis_data/pro_matches/home/ubuntu/opendota_pro_matches_additional_detailed.parquet"
pro_matches_main_file = "/home/ubuntu/analysis_data/pro_matches/home/ubuntu/opendota_pro_matches_main_detailed.csv"

# Function to load data and print info
def load_and_inspect(file_path, file_type, name, nrows=5):
    print(f"\n--- Inspecting {name} ({file_path}) ---")
    try:
        if file_type == "parquet":
            # For parquet, load all columns for info, then maybe sample if large
            df = pd.read_parquet(file_path)
            df_sample = df.head(nrows)
        elif file_type == "csv":
            # Try detecting encoding issues, default to utf-8
            try:
                df_sample = pd.read_csv(file_path, nrows=nrows)
            except UnicodeDecodeError:
                print(f"UTF-8 decoding failed for {file_path}, trying latin1.")
                df_sample = pd.read_csv(file_path, nrows=nrows, encoding='latin1')
            # For CSV, load all columns initially to see what's available
            print(f"Loading full CSV columns for inspection (this might take a moment for large files)...")
            df_full_cols = pd.read_csv(file_path, nrows=0) # Load only headers
            print("Available columns:")
            print(list(df_full_cols.columns))
            # Reload with nrows for head display
            try:
                df_sample = pd.read_csv(file_path, nrows=nrows)
            except UnicodeDecodeError:
                df_sample = pd.read_csv(file_path, nrows=nrows, encoding='latin1')
            # Assign df_sample to df for consistent processing below
            df = df_sample
        else:
            print(f"Unsupported file type: {file_type}")
            return None

        print(f"Successfully loaded sample data. Shape (sample): {df_sample.shape}")
        print("Columns and Data Types (from sample):")
        df_sample.info()
        print("First few rows:")
        print(df_sample.head())

        # Check for specific columns related to teamfights or detailed logs in the full dataframe (if parquet) or headers (if csv)
        if file_type == "parquet":
            all_columns = df.columns
        elif file_type == "csv":
            all_columns = df_full_cols.columns
        else:
            all_columns = []
            
        potential_tf_cols = [col for col in all_columns if 'fight' in col.lower() or 'tf_' in col.lower()]
        potential_log_cols = [col for col in all_columns if 'log' in col.lower() or '_times' in col.lower() or '_per_min' in col.lower()]

        if potential_tf_cols:
            print(f"\nPotential Teamfight Columns Found: {potential_tf_cols}")
        else:
            print("\nNo obvious teamfight columns found in the available data.")

        if potential_log_cols:
            print(f"Potential Log/Time-Series Columns Found: {potential_log_cols}")
        else:
            print("No obvious log/time-series columns found in the available data.")

        # Return the sample dataframe for inspection if needed (or full df if parquet)
        return df

    except FileNotFoundError:
        print(f"Error: File not found.")
        return None
    except Exception as e:
        print(f"Error loading or inspecting file: {e}")
        return None

# Inspect files
load_and_inspect(purchase_log_file, "parquet", "Purchase Logs")
load_and_inspect(pgl_matches_file, "parquet", "PGL Matches Full Details")
load_and_inspect(pro_matches_additional_file, "parquet", "Pro Matches Additional Details")
load_and_inspect(pro_matches_main_file, "csv", "Pro Matches Main Details")

print("\nData exploration script finished. Review the output to determine data availability for teamfight/impact analysis.")

