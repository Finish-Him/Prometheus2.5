import pandas as pd
import os

# Input and Output paths
input_dir = "/home/ubuntu/dota_data"
output_dir = "/home/ubuntu/dota_data"
csv_file = os.path.join(input_dir, "purchase_logs.csv")
parquet_file = os.path.join(output_dir, "purchase_logs.parquet")

print(f"Converting {csv_file} to {parquet_file}...")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

try:
    # Load CSV data
    df = pd.read_csv(csv_file, encoding='utf-8')

    # Check if DataFrame is empty
    if df.empty:
        print(f"Warning: CSV file {csv_file} is empty or could not be read properly. Creating an empty Parquet file.")
        # Save an empty DataFrame to Parquet
        df.to_parquet(parquet_file, index=False)
    else:
        # Save DataFrame to Parquet
        # Using 'snappy' compression as a common default, can be changed if needed
        df.to_parquet(parquet_file, index=False, compression='snappy')

    print(f"Successfully converted CSV to Parquet: {parquet_file}")

except FileNotFoundError:
    print(f"Error: Input CSV file not found at {csv_file}")
except Exception as e:
    print(f"An unexpected error occurred during CSV to Parquet conversion: {e}")

