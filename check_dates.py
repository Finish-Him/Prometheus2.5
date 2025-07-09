import pandas as pd

# Load the main dataset
try:
    main_df = pd.read_csv("/home/ubuntu/opendota_data/opendota_pro_matches_main_detailed.csv", low_memory=False)
    print("Main dataset loaded successfully.")
except Exception as e:
    print(f"Error loading main dataset: {e}")
    exit()

# Check the range of match dates
print("\n--- Match Date Range ---")

# Convert start_time (Unix timestamp) to datetime objects
main_df["start_datetime"] = pd.to_datetime(main_df["start_time"], unit="s")

# Find min and max dates
min_date = main_df["start_datetime"].min()
max_date = main_df["start_datetime"].max()

print(f"Earliest match date: {min_date}")
print(f"Latest match date: {max_date}")

# Define patch 7.38 release date
patch_738_release_date = pd.Timestamp("2025-02-19")

# Check if the date range spans the patch release
if min_date < patch_738_release_date and max_date >= patch_738_release_date:
    print(f"\nThe dataset spans the patch 7.38 release date ({patch_738_release_date.date()}).")
    print("It is possible to compare matches before and after this date.")
elif max_date < patch_738_release_date:
    print(f"\nAll matches in the dataset occurred BEFORE the patch 7.38 release date ({patch_738_release_date.date()}).")
    print("Comparison between pre-7.38 and post-7.38 is not possible with this dataset.")
elif min_date >= patch_738_release_date:
    print(f"\nAll matches in the dataset occurred ON or AFTER the patch 7.38 release date ({patch_738_release_date.date()}).")
    # Check if it spans 7.38b or 7.38c
    patch_738b_release_date = pd.Timestamp("2025-03-04")
    patch_738c_release_date = pd.Timestamp("2025-03-27")
    if min_date < patch_738b_release_date and max_date >= patch_738b_release_date:
        print(f"The dataset spans the patch 7.38b release date ({patch_738b_release_date.date()}). Comparison between 7.38 and 7.38b might be possible.")
    elif min_date < patch_738c_release_date and max_date >= patch_738c_release_date:
         print(f"The dataset spans the patch 7.38c release date ({patch_738c_release_date.date()}). Comparison between 7.38b and 7.38c might be possible.")
    else:
        print("All matches seem to be within a single sub-patch version (likely 7.38c based on max date).")
    print("Comparison between pre-7.38 and post-7.38 is not possible with this dataset.")

print("\nScript finished.")

