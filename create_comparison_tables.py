import pandas as pd
import os
import re

# Input directory
input_dir = "/home/ubuntu/analysis_results"

# Output directory
output_dir = "/home/ubuntu/analysis_results"
os.makedirs(output_dir, exist_ok=True)

# File paths
pgl_counts_file = os.path.join(input_dir, "pgl_hero_item_counts.csv")
general_counts_file = os.path.join(input_dir, "general_pro_hero_item_counts.csv")
item_impact_file = os.path.join(input_dir, "item_impact_analysis.csv")
patterns_summary_file = os.path.join(input_dir, "analysis_patterns_summary.txt")

# Output file paths
pgl_comparison_output = os.path.join(output_dir, "pgl_vs_general_purchase_comparison.csv")
item_impact_summary_output = os.path.join(output_dir, "item_impact_summary_table.csv")
game_patterns_output = os.path.join(output_dir, "game_patterns_summary_table.csv")

# Function to load CSV with error handling
def load_csv(file_path, name):
    print(f"Loading {name} data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {name} data. Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# --- Table 1: PGL vs General Pro Purchase Comparison ---
print("\n--- Creating PGL vs General Pro Purchase Comparison Table ---")
pgl_counts = load_csv(pgl_counts_file, "PGL Counts")
general_counts = load_csv(general_counts_file, "General Pro Counts")

if pgl_counts is not None and general_counts is not None:
    # Merge the dataframes
    comparison_df = pd.merge(pgl_counts, general_counts, on=["hero_id", "key"], how="outer")
    
    # Fill NaN values with 0 for counts
    comparison_df["pgl_purchase_count"] = comparison_df["pgl_purchase_count"].fillna(0).astype(int)
    comparison_df["general_pro_purchase_count"] = comparison_df["general_pro_purchase_count"].fillna(0).astype(int)
    
    # Sort for better readability (e.g., by hero_id, then maybe difference or total count)
    comparison_df["total_count"] = comparison_df["pgl_purchase_count"] + comparison_df["general_pro_purchase_count"]
    comparison_df = comparison_df.sort_values(by=["hero_id", "total_count"], ascending=[True, False])
    
    # Save the comparison table
    try:
        comparison_df.to_csv(pgl_comparison_output, index=False)
        print(f"Saved PGL vs General Pro purchase comparison table to {pgl_comparison_output}")
    except Exception as e:
        print(f"Error saving comparison table: {e}")
else:
    print("Skipping PGL vs General Pro comparison due to missing input files.")

# --- Table 2: Item Impact Summary ---
print("\n--- Creating Item Impact Summary Table ---")
item_impact = load_csv(item_impact_file, "Item Impact Analysis")

if item_impact is not None:
    # Calculate win rate difference
    item_impact["win_rate_diff"] = item_impact["win_rate_with_item"] - item_impact["win_rate_without_item"]
    
    # Select and reorder columns for summary
    summary_cols = [
        "item_name", 
        "win_rate_with_item", 
        "win_rate_without_item", 
        "win_rate_diff", 
        "count_with_item", 
        "count_without_item",
        "avg_kills_with", "avg_kills_without",
        "avg_deaths_with", "avg_deaths_without",
        "avg_assists_with", "avg_assists_without",
        "avg_gold_per_min_with", "avg_gold_per_min_without",
        "avg_xp_per_min_with", "avg_xp_per_min_without",
        "avg_hero_damage_with", "avg_hero_damage_without"
    ]
    # Filter out columns that might not exist if stats calculation failed for some items
    summary_cols = [col for col in summary_cols if col in item_impact.columns]
    item_impact_summary = item_impact[summary_cols]
    
    # Sort by win rate difference or count
    item_impact_summary = item_impact_summary.sort_values(by="win_rate_diff", ascending=False)
    
    # Save the summary table
    try:
        item_impact_summary.to_csv(item_impact_summary_output, index=False, float_format="%.4f")
        print(f"Saved Item Impact summary table to {item_impact_summary_output}")
    except Exception as e:
        print(f"Error saving item impact summary table: {e}")
else:
    print("Skipping Item Impact summary due to missing input file.")

# --- Table 3: Game Patterns Summary ---
print("\n--- Creating Game Patterns Summary Table ---")
try:
    with open(patterns_summary_file, "r", encoding="utf-8") as f:
        summary_text = f.read()
    
    patterns_data = []
    # Use regex to extract key metrics
    patterns_data.append({"Metric": "Total Matches Analyzed", "Value": re.search(r"\((\d+) partidas\)", summary_text).group(1) if re.search(r"\((\d+) partidas\)", summary_text) else "N/A"})
    patterns_data.append({"Metric": "Radiant Win Rate", "Value": re.search(r"Radiant: \d+ vitórias \((.*?%)\)", summary_text).group(1) if re.search(r"Radiant: \d+ vitórias \((.*?%)\)", summary_text) else "N/A"})
    patterns_data.append({"Metric": "Dire Win Rate", "Value": re.search(r"Dire:.*?\((.*?%)\)", summary_text).group(1) if re.search(r"Dire:.*?\((.*?%)\)", summary_text) else "N/A"})
    patterns_data.append({"Metric": "Matches with First Blood", "Value": re.search(r"Partidas com First Blood registrado: (\d+)", summary_text).group(1) if re.search(r"Partidas com First Blood registrado: (\d+)", summary_text) else "N/A"})
    patterns_data.append({"Metric": "Win Rate with First Blood", "Value": re.search(r"Vitórias do time que conseguiu First Blood: \d+ \((.*?%)\)", summary_text).group(1) if re.search(r"Vitórias do time que conseguiu First Blood: \d+ \((.*?%)\)", summary_text) else "N/A"})
    # Add other patterns if needed (Tower, Roshan, Rax) - they were 0 in the example run
    
    patterns_df = pd.DataFrame(patterns_data)
    
    # Save the patterns table
    try:
        patterns_df.to_csv(game_patterns_output, index=False)
        print(f"Saved Game Patterns summary table to {game_patterns_output}")
    except Exception as e:
        print(f"Error saving game patterns summary table: {e}")
        
except FileNotFoundError:
    print(f"Error: Patterns summary file not found at {patterns_summary_file}")
except Exception as e:
    print(f"Error processing patterns summary file: {e}")

print("\nComparison table creation script finished.")

