import json
import sys
import pandas as pd

input_file = "/home/ubuntu/hero_stats_with_phase.json"
output_file = "/home/ubuntu/hero_attribute_gain_analysis.txt"
TOP_N = 15 # Number of heroes to show in top/bottom lists

# Carregar dados dos heróis com fase
print(f"Carregando dados dos heróis: {input_file}")
try:
    # Corrected file open mode
    with open(input_file, 'r', encoding='utf-8') as f:
        hero_stats = json.load(f)
    print(f"Dados de {len(hero_stats)} heróis carregados.")
except Exception as e:
    print(f"Erro ao carregar dados dos heróis: {e}")
    sys.exit(1)

# Extrair dados relevantes para análise de atributos
attribute_data = []
for hero_id_str, stats in hero_stats.items():
    # Corrected key access
    if stats['picks'] > 0:
        # Corrected key access
        str_gain = stats.get('str_gain')
        agi_gain = stats.get('agi_gain')
        int_gain = stats.get('int_gain')
        
        # Verificar se os ganhos são válidos
        if str_gain is not None and agi_gain is not None and int_gain is not None:
            total_gain = str_gain + agi_gain + int_gain
            attribute_data.append({
                # Corrected key access
                'name': stats.get('name', f"ID:{hero_id_str}"),
                'str_gain': str_gain,
                'agi_gain': agi_gain,
                'int_gain': int_gain,
                'total_gain': total_gain
            })
        else:
            # Corrected key access and f-string
            print(f"Aviso: Dados de ganho de atributo ausentes para {stats.get('name', f'ID:{hero_id_str}')}")

if not attribute_data:
    print("Nenhum dado de atributo válido encontrado para análise.")
    sys.exit(1)

# Converter para DataFrame para facilitar ordenação
df = pd.DataFrame(attribute_data)

# Ordenar por cada ganho de atributo e ganho total
# Corrected column names
df_sorted_str = df.sort_values(by='str_gain', ascending=False)
df_sorted_agi = df.sort_values(by='agi_gain', ascending=False)
df_sorted_int = df.sort_values(by='int_gain', ascending=False)
df_sorted_total = df.sort_values(by='total_gain', ascending=False)

# Preparar texto do resultado
results_text = f"# Análise de Ganho de Atributos por Nível - PGL Wallachia Season 4\n\n"
results_text += f"Total de Heróis Analisados (com picks > 0 e dados de atributos): {len(df)}\n\n"

def format_rankings(df_sorted, attribute_name, display_name):
    text = f"## Top {TOP_N} Heróis por Ganho de {display_name}\n\n"
    text += f"| Rank | Herói | Ganho de {display_name} |\n"
    text += "|------|-------|-----------------|\n"
    # Use rank method for correct ranking in case of ties
    df_sorted['rank'] = df_sorted[attribute_name].rank(method='min', ascending=False)
    for i, row in df_sorted.head(TOP_N).iterrows():
        # Corrected key access
        text += f"| {int(row['rank'])} | {row['name']} | {row[attribute_name]:.2f} |\n"
    text += "\n"
    return text

# Corrected column names
results_text += format_rankings(df_sorted_str, 'str_gain', "Força (STR)")
results_text += format_rankings(df_sorted_agi, 'agi_gain', "Agilidade (AGI)")
results_text += format_rankings(df_sorted_int, 'int_gain', "Inteligência (INT)")
results_text += format_rankings(df_sorted_total, 'total_gain', "Atributos Totais")

# Salvar resultados
print(f"Salvando resultados em {output_file}")
# Corrected file open mode
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(results_text)

print("Análise de ganho de atributos concluída.")

