import pandas as pd
import json
import os

# Input and Output paths
input_dir = "/home/ubuntu/dota_data"
output_dir = "/home/ubuntu/dota_data"
json_file = os.path.join(input_dir, "purchase_logs.json")
csv_file = os.path.join(output_dir, "purchase_logs.csv")

print(f"Converting {json_file} to {csv_file}...")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

try:
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Check if data is empty
    if not data:
        print(f"Warning: JSON file {json_file} is empty. Creating an empty CSV file.")
        # Create an empty DataFrame or handle as needed
        df = pd.DataFrame()
    else:
        # Convert JSON to DataFrame
        df = pd.json_normalize(data)

    # Save DataFrame to CSV
    df.to_csv(csv_file, index=False, encoding='utf-8')

    print(f"Successfully converted JSON to CSV: {csv_file}")

except FileNotFoundError:
    print(f"Error: Input JSON file not found at {json_file}")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {json_file}")
except Exception as e:
    print(f"An unexpected error occurred during JSON to CSV conversion: {e}")

