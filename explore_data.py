import pandas as pd

def analyze_data(file_path, file_type='csv'):
    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        elif file_type == 'parquet':
            df = pd.read_parquet(file_path)
        else:
            print(f"Unsupported file type: {file_type}")
            return

        print(f"\n--- Analysis for {file_path} ---")
        print(f"Shape: {df.shape}")
        print("\nColumns and Data Types:")
        print(df.info())
        print("\nFirst 5 rows:")
        print(df.head())

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

# Analyze CSV files
analyze_data('/home/ubuntu/opendota_data/opendota_pro_matches_main_detailed.csv', 'csv')
analyze_data('/home/ubuntu/opendota_data/opendota_pro_matches_additional_detailed.csv', 'csv')

# Analyze Parquet file
analyze_data('/home/ubuntu/opendota_data/opendota_pro_matches_additional_detailed.parquet', 'parquet')

