import pandas as pd

# Load the main dataset
try:
    main_df = pd.read_csv("/home/ubuntu/opendota_data/opendota_pro_matches_main_detailed.csv", low_memory=False)
    print("Main dataset loaded successfully.")
except Exception as e:
    print(f"Error loading main dataset: {e}")
    exit()

# Check unique values and counts in the 'patch' column
print("\n--- Patch Distribution ---")
patch_distribution = main_df["patch"].value_counts().sort_index()
print(patch_distribution)

# Save the distribution to a file
try:
    patch_distribution.to_csv("/home/ubuntu/opendota_data/patch_distribution.csv")
    print("\nPatch distribution saved to patch_distribution.csv")
except Exception as e:
    print(f"Error saving patch distribution: {e}")

print("\nScript finished.")

