import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Input directory
input_dir = "/home/ubuntu/analysis_results"

# Output directory for visualizations
output_viz_dir = os.path.join(input_dir, "visualizations")
os.makedirs(output_viz_dir, exist_ok=True)

# File paths
item_impact_file = os.path.join(input_dir, "item_impact_summary_table.csv")
game_patterns_file = os.path.join(input_dir, "game_patterns_summary_table.csv")
pgl_comparison_file = os.path.join(input_dir, "pgl_vs_general_purchase_comparison.csv")

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

# Load data
item_impact = load_csv(item_impact_file, "Item Impact Summary")
game_patterns = load_csv(game_patterns_file, "Game Patterns Summary")
pgl_comparison = load_csv(pgl_comparison_file, "PGL vs General Comparison")

# Set plot style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 7) # Default figure size

# --- Visualization 1: Item Impact on Win Rate ---
if item_impact is not None and not item_impact.empty:
    print("Generating Item Impact on Win Rate visualization...")
    # Sort by win rate difference for better visualization
    item_impact_sorted = item_impact.sort_values(by="win_rate_diff", ascending=False).head(15) # Top 15 items
    
    plt.figure(figsize=(15, 8))
    sns.barplot(x="win_rate_diff", y="item_name", data=item_impact_sorted, palette="vlag")
    plt.title("Diferença na Taxa de Vitória ao Comprar Item Chave (Top 15)")
    plt.xlabel("Aumento/Diminuição na Taxa de Vitória")
    plt.ylabel("Item")
    plt.tight_layout()
    plt.savefig(os.path.join(output_viz_dir, "item_win_rate_difference.png"))
    plt.close()
    print("Saved item_win_rate_difference.png")

    # Plot absolute win rates
    item_impact_melt = item_impact_sorted.melt(id_vars=["item_name"], 
                                               value_vars=["win_rate_with_item", "win_rate_without_item"], 
                                               var_name="Condition", value_name="Win Rate")
    item_impact_melt["Condition"] = item_impact_melt["Condition"].map({"win_rate_with_item": "Com Item", "win_rate_without_item": "Sem Item"})
    
    plt.figure(figsize=(15, 8))
    sns.barplot(x="Win Rate", y="item_name", hue="Condition", data=item_impact_melt, palette="coolwarm")
    plt.title("Taxa de Vitória Com vs Sem Item Chave (Top 15 por Diferença)")
    plt.xlabel("Taxa de Vitória Média")
    plt.ylabel("Item")
    plt.legend(title="Condição")
    plt.tight_layout()
    plt.savefig(os.path.join(output_viz_dir, "item_win_rate_comparison.png"))
    plt.close()
    print("Saved item_win_rate_comparison.png")

# --- Visualization 2: Game Patterns (Side Win Rate, FB Win Rate) ---
if game_patterns is not None and not game_patterns.empty:
    print("Generating Game Patterns visualization...")
    # Side Win Rate
    side_wr = game_patterns[game_patterns["Metric"].isin(["Radiant Win Rate", "Dire Win Rate"])].copy()
    side_wr["Side"] = side_wr["Metric"].apply(lambda x: "Radiant" if "Radiant" in x else "Dire")
    side_wr["Win Rate"] = side_wr["Value"].str.rstrip("%").astype(float) / 100.0
    
    plt.figure(figsize=(6, 5))
    sns.barplot(x="Side", y="Win Rate", data=side_wr, palette=["red", "blue"])
    plt.title("Taxa de Vitória por Lado (PGL Wallachia S4)")
    plt.ylabel("Taxa de Vitória")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(output_viz_dir, "side_win_rate.png"))
    plt.close()
    print("Saved side_win_rate.png")

    # First Blood Win Rate
    fb_wr_row = game_patterns[game_patterns["Metric"] == "Win Rate with First Blood"]
    if not fb_wr_row.empty:
        fb_wr_val = fb_wr_row["Value"].iloc[0]
        if fb_wr_val != "N/A":
            fb_wr = float(fb_wr_val.rstrip("%")) / 100.0
            fb_lose_wr = 1.0 - fb_wr
            fb_df = pd.DataFrame({
                "Condition": ["Conseguiu FB", "Não Conseguiu FB"],
                "Win Rate": [fb_wr, fb_lose_wr]
            })
            
            plt.figure(figsize=(6, 5))
            sns.barplot(x="Condition", y="Win Rate", data=fb_df, palette="viridis")
            plt.title("Taxa de Vitória vs First Blood (PGL Wallachia S4)")
            plt.ylabel("Taxa de Vitória")
            plt.xlabel("")
            plt.ylim(0, 1)
            plt.tight_layout()
            plt.savefig(os.path.join(output_viz_dir, "first_blood_win_rate.png"))
            plt.close()
            print("Saved first_blood_win_rate.png")
        else:
            print("First Blood win rate data not available.")
    else:
        print("First Blood win rate metric not found.")

# --- Visualization 3: PGL vs General Pro Purchase Counts (Example: Top N items) ---
if pgl_comparison is not None and not pgl_comparison.empty:
    print("Generating PGL vs General Pro Purchase Comparison visualization...")
    # Aggregate counts per item across all heroes
    item_counts_agg = pgl_comparison.groupby("key")[["pgl_purchase_count", "general_pro_purchase_count"]].sum().reset_index()
    item_counts_agg["total_count"] = item_counts_agg["pgl_purchase_count"] + item_counts_agg["general_pro_purchase_count"]
    
    # Get top N items by total count
    top_items = item_counts_agg.sort_values(by="total_count", ascending=False).head(20)
    
    # Melt for plotting
    top_items_melt = top_items.melt(id_vars=["key"], 
                                    value_vars=["pgl_purchase_count", "general_pro_purchase_count"], 
                                    var_name="Source", value_name="Count")
    top_items_melt["Source"] = top_items_melt["Source"].map({"pgl_purchase_count": "PGL", "general_pro_purchase_count": "Geral Pro"})

    plt.figure(figsize=(15, 8))
    sns.barplot(x="Count", y="key", hue="Source", data=top_items_melt, palette="muted")
    plt.title("Contagem de Compra: PGL vs Geral Pro (Top 20 Itens)")
    plt.xlabel("Número de Vezes Comprado")
    plt.ylabel("Item")
    plt.legend(title="Fonte")
    plt.tight_layout()
    plt.savefig(os.path.join(output_viz_dir, "pgl_vs_general_top_items.png"))
    plt.close()
    print("Saved pgl_vs_general_top_items.png")

print("\nVisualization script finished.")

