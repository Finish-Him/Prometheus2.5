import os
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pprint

BASE_DIR = "/home/ubuntu/oraculo_6_7/organizado"
OUTPUT_DIR = "/home/ubuntu/oraculo_6_7"
TYPE_DIRS = ["Codigos_Python", "Tabelas_CSV", "Documentos_TXT", "Arquivos_XML", "Arquivos_JSON", "Outros_Arquivos"]
IMPORTANCE_LEVELS = ["Alta_Importancia", "Media_Importancia", "Baixa_Importancia"]

summary_data = []
summary_dict = {} # For JSON/Python dict format

print("Iniciando a criação dos sumários...")

for type_dir in TYPE_DIRS:
    summary_dict[type_dir] = {}
    for importance_level in IMPORTANCE_LEVELS:
        summary_dict[type_dir][importance_level] = []
        current_dir = os.path.join(BASE_DIR, type_dir, importance_level)
        if not os.path.exists(current_dir):
            print(f"Aviso: Diretório não encontrado, pulando: {current_dir}")
            continue

        # Check if current_dir is actually a directory
        if not os.path.isdir(current_dir):
            print(f"Aviso: {current_dir} não é um diretório, pulando.")
            continue

        for root, dirs, files in os.walk(current_dir):
            # Skip the root directory itself if it contains no subdirs initially
            # This prevents adding the importance level dir itself as a relative path
            if root == current_dir and not dirs and not files:
                 continue

            for filename in files:
                full_path = os.path.join(root, filename)
                # Get path relative to the importance level directory
                relative_path = os.path.relpath(full_path, current_dir)
                file_info = {
                    "tipo": type_dir,
                    "importancia": importance_level,
                    "caminho_relativo": relative_path,
                    "nome_arquivo": filename
                }
                summary_data.append(file_info)
                # Store only the relative path in the dictionary structure
                summary_dict[type_dir][importance_level].append(relative_path)

# Ensure lists are sorted for consistent output
for type_dir in summary_dict:
    for importance_level in summary_dict[type_dir]:
        summary_dict[type_dir][importance_level].sort()

# --- Generate JSON Summary ---
json_path = os.path.join(OUTPUT_DIR, "sumario_estrutura.json")
print(f"Gerando sumário JSON em: {json_path}")
try:
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_dict, f, indent=4, ensure_ascii=False)
except Exception as e:
    print(f"Erro ao gerar JSON: {e}")

# --- Generate CSV Summary --- (Using the flat list summary_data)
csv_path = os.path.join(OUTPUT_DIR, "sumario_estrutura.csv")
print(f"Gerando sumário CSV em: {csv_path}")
try:
    # Sort summary_data for consistent CSV output
    summary_data.sort(key=lambda x: (x['tipo'], x['importancia'], x['caminho_relativo']))
    if summary_data:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
            writer.writeheader()
            writer.writerows(summary_data)
    else:
        # Write header even if empty
        with open(csv_path, 'w', encoding='utf-8') as f:
             f.write("tipo,importancia,caminho_relativo,nome_arquivo\n")
        print("Aviso: Nenhum dado para escrever no CSV.")
except Exception as e:
    print(f"Erro ao gerar CSV: {e}")

# --- Generate TXT Summary --- (Using the nested summary_dict)
txt_path = os.path.join(OUTPUT_DIR, "sumario_estrutura.txt")
print(f"Gerando sumário TXT em: {txt_path}")
try:
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("Sumário da Estrutura Organizada do Oráculo 6.7\n")
        f.write("===============================================\n\n")
        for type_dir, levels in sorted(summary_dict.items()):
            f.write(f"Tipo: {type_dir}\n")
            for level, files in sorted(levels.items()):
                f.write(f"  Importância: {level}\n")
                if files:
                    for file_rel_path in files: # Already sorted
                        f.write(f"    - {file_rel_path}\n")
                else:
                    f.write("    (Nenhum ficheiro)\n")
            f.write("\n")
except Exception as e:
    print(f"Erro ao gerar TXT: {e}")

# --- Generate Python Summary (pprint) --- (Using the nested summary_dict)
py_path = os.path.join(OUTPUT_DIR, "sumario_estrutura.py")
print(f"Gerando sumário Python em: {py_path}")
try:
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write("# Sumário da Estrutura Organizada do Oráculo 6.7 (Representação Python)\n")
        f.write("estrutura_oraculo = ")
        # Use pprint with sorted dict for consistent output
        # Convert dict to sorted list of tuples for sorting keys
        sorted_summary_dict = {k: dict(sorted(v.items())) for k, v in sorted(summary_dict.items())}
        pprint.pprint(sorted_summary_dict, stream=f, indent=4, sort_dicts=False) # sort_dicts=False because we pre-sorted
except Exception as e:
    print(f"Erro ao gerar Python: {e}")

# --- Generate XML Summary --- (Using the nested summary_dict)
xml_path = os.path.join(OUTPUT_DIR, "sumario_estrutura.xml")
print(f"Gerando sumário XML em: {xml_path}")
try:
    root = ET.Element("EstruturaOraculo")
    for type_dir, levels in sorted(summary_dict.items()):
        type_elem = ET.SubElement(root, "TipoArquivo", nome=type_dir)
        for level, files in sorted(levels.items()):
            level_elem = ET.SubElement(type_elem, "NivelImportancia", nome=level)
            if files:
                for file_rel_path in files: # Already sorted
                    file_elem = ET.SubElement(level_elem, "Arquivo")
                    # Sanitize path for XML if necessary, though usually ok
                    file_elem.text = file_rel_path
            else:
                 level_elem.set("ficheiros", "0") # Indicate no files

    # Pretty print XML
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    dom = minidom.parseString(xml_str)
    pretty_xml_str = dom.toprettyxml(indent="  ")

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)
except Exception as e:
    print(f"Erro ao gerar XML: {e}")


print("Criação de todos os sumários concluída.")

