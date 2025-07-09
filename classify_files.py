import os
import shutil
import re

BASE_DIR = "/home/ubuntu/oraculo_6_7/organizado"
TYPE_DIRS = ["Codigos_Python", "Tabelas_CSV", "Documentos_TXT", "Arquivos_XML", "Arquivos_JSON", "Outros_Arquivos"]
IMPORTANCE_LEVELS = ["Alta_Importancia", "Media_Importancia", "Baixa_Importancia"]

# Define patterns for classification (examples, needs refinement)
# Order matters, more specific rules first

# --- High Importance Patterns ---
high_importance_patterns = [
    # Keywords
    re.compile(r'core', re.IGNORECASE),
    re.compile(r'main', re.IGNORECASE),
    re.compile(r'final', re.IGNORECASE),
    re.compile(r'validated', re.IGNORECASE),
    re.compile(r'validadas', re.IGNORECASE),
    re.compile(r'detalhado', re.IGNORECASE),
    re.compile(r'detailed', re.IGNORECASE),
    re.compile(r'database', re.IGNORECASE), # Careful, might match parent folder
    re.compile(r'treinamento', re.IGNORECASE),
    re.compile(r'knowledge_base', re.IGNORECASE),
    re.compile(r'conhecimento', re.IGNORECASE), # Careful, might match parent folder
    re.compile(r'analisador', re.IGNORECASE),
    re.compile(r'analysis', re.IGNORECASE),
    re.compile(r'predição', re.IGNORECASE),
    re.compile(r'prediction', re.IGNORECASE),
    # Specific filenames
    re.compile(r'pgl_wallachia_opendota_full\.csv', re.IGNORECASE),
    re.compile(r'match_players\.csv', re.IGNORECASE),
    re.compile(r'players_from_matches\.csv', re.IGNORECASE),
    re.compile(r'Database Oráculo 3\.0\.xlsx', re.IGNORECASE), # From Outros
    # Paths
    re.compile(r'Oráculo [4-6]', re.IGNORECASE), # Newer versions more important
    re.compile(r'IA Predição Esportiva', re.IGNORECASE),
    re.compile(r'Conhecimento validado', re.IGNORECASE),
]

# --- Low Importance Patterns ---
low_importance_patterns = [
    # Keywords/Types
    re.compile(r'temp', re.IGNORECASE),
    re.compile(r'log', re.IGNORECASE),
    re.compile(r'test', re.IGNORECASE),
    re.compile(r'example', re.IGNORECASE),
    re.compile(r'backup', re.IGNORECASE),
    re.compile(r'\.bak$', re.IGNORECASE),
    re.compile(r'~$', re.IGNORECASE),
    re.compile(r'readme\.md', re.IGNORECASE), # Often low importance unless specific project doc
    re.compile(r'\.png$', re.IGNORECASE),
    re.compile(r'\.jpg$', re.IGNORECASE),
    re.compile(r'\.jpeg$', re.IGNORECASE),
    re.compile(r'\.gif$', re.IGNORECASE),
    re.compile(r'\.css$', re.IGNORECASE),
    re.compile(r'\.js$', re.IGNORECASE),
    re.compile(r'\.exe$', re.IGNORECASE),
    re.compile(r'\.zip$', re.IGNORECASE), # Internal zips might be lower prio unless specified
    # Specific filenames/paths
    re.compile(r'PGL_Dota2 - Twitch_files', re.IGNORECASE),
    re.compile(r'Nova pasta', re.IGNORECASE), # Generic names often less important
    re.compile(r'download', re.IGNORECASE),
    re.compile(r'\((\d+)\)\.', re.IGNORECASE), # Files like file(1).csv might be duplicates or temp
]

# --- Medium Importance is the default if not High or Low ---

def classify_file(file_path, filename):
    # Check High Importance
    for pattern in high_importance_patterns:
        if pattern.search(filename) or pattern.search(file_path):
             # Exception for database/conhecimento in path vs filename
            if (pattern.pattern == 'database' or pattern.pattern == 'conhecimento') and pattern.search(os.path.dirname(file_path)) and not pattern.search(filename):
                 continue # Don't classify as high just because parent folder matches
            # Prioritize newer versions if path matches older version but filename is important
            if re.search(r'Oráculo [1-3]', file_path, re.IGNORECASE) and not re.search(r'Oráculo [4-6]', file_path, re.IGNORECASE):
                 pass
            return "Alta_Importancia"

    # Check Low Importance
    for pattern in low_importance_patterns:
        if pattern.search(filename) or pattern.search(file_path):
            # Avoid classifying essential docs like README in root as low
            if pattern.pattern == 'readme\\.md' and os.path.dirname(file_path).count(os.sep) < 3: # Heuristic for root/near-root
                 return "Media_Importancia"
            # Don't classify main DB file as low just because it ends in .zip if it was extracted
            if pattern.pattern == '\\.zip$' and 'knowledge_base' in filename:
                 return "Media_Importancia" # Or potentially high if it's the core KB
            # Downgrade importance if it's a low-importance type AND in an old Oraculo version
            if re.search(r'Oráculo [1-3]', file_path, re.IGNORECASE):
                return "Baixa_Importancia"
            # Otherwise, might be medium if it's a recent image/asset needed
            if re.search(r'\.(png|jpg|jpeg|gif|css|js)$', filename, re.IGNORECASE):
                return "Media_Importancia" # Keep recent assets as medium
            return "Baixa_Importancia"

    # Default to Medium Importance
    return "Media_Importancia"

# --- Main Classification Logic ---
print("Iniciando classificação de arquivos por importância...")

for type_dir in TYPE_DIRS:
    source_dir_path = os.path.join(BASE_DIR, type_dir)
    print(f"Processando diretório: {type_dir}")

    oraculo_base_in_type_dir = os.path.join(source_dir_path, "Oráculo")

    if not os.path.exists(oraculo_base_in_type_dir):
        print(f"  Aviso: Diretório 'Oráculo' não encontrado em {source_dir_path}. Pulando.")
        continue

    files_to_move = []
    for root, dirs, files in os.walk(oraculo_base_in_type_dir):
        if any(level in root for level in IMPORTANCE_LEVELS):
            continue

        for filename in files:
            source_file_path = os.path.join(root, filename)
            relative_path_from_type_dir = os.path.relpath(source_file_path, source_dir_path)
            importance = classify_file(relative_path_from_type_dir, filename)
            target_dir = os.path.join(source_dir_path, importance)
            target_subdir = os.path.join(target_dir, os.path.relpath(root, source_dir_path))
            target_file_path = os.path.join(target_subdir, filename)
            files_to_move.append((source_file_path, target_subdir, target_file_path))

    moved_counts = {level: 0 for level in IMPORTANCE_LEVELS}
    for source_path, target_sub, target_path in files_to_move:
        try:
            if not os.path.exists(target_sub):
                os.makedirs(target_sub)
            # Ensure the source file still exists before moving
            if os.path.exists(source_path):
                shutil.move(source_path, target_path)
                for level in IMPORTANCE_LEVELS:
                    if level in target_sub:
                        moved_counts[level] += 1
                        break
            else:
                print(f"  Aviso: Arquivo de origem não encontrado (pode já ter sido movido): {source_path}")
        except Exception as e:
            print(f"  Erro ao mover {source_path} para {target_path}: {e}")

    print(f"  Classificação concluída para {type_dir}:")
    for level, count in moved_counts.items():
        print(f"    - {level}: {count} ficheiros movidos")

# Clean up empty 'Oráculo' directories left after moving files
print("Limpando diretórios 'Oráculo' vazios...")
for type_dir in TYPE_DIRS:
    oraculo_base_in_type_dir = os.path.join(BASE_DIR, type_dir, "Oráculo")
    if os.path.exists(oraculo_base_in_type_dir):
        try:
            # Walk bottom-up to remove empty dirs
            for root, dirs, files in os.walk(oraculo_base_in_type_dir, topdown=False):
                if not files and not dirs:
                    print(f"Removendo diretório vazio: {root}")
                    os.rmdir(root)
            # Try removing the top 'Oráculo' dir if it's now empty
            if not os.listdir(oraculo_base_in_type_dir):
                 print(f"Removendo diretório vazio: {oraculo_base_in_type_dir}")
                 os.rmdir(oraculo_base_in_type_dir)
        except OSError as e:
             print(f"  Aviso ao limpar {oraculo_base_in_type_dir} (pode não estar vazio ou já removido): {e}")
        except Exception as e:
            print(f"  Erro inesperado ao limpar {oraculo_base_in_type_dir}: {e}")


print("Classificação e limpeza concluídas.")

