import pandas as pd
import json
import os
from datetime import datetime

# Diretórios
consolidated_dir = "/home/ubuntu/oraculo_6_7/consolidado"
output_file_txt = os.path.join(consolidated_dir, "oraculo_6_7_conhecimento.txt")
consolidated_csv_path = os.path.join(consolidated_dir, "oraculo_6_7_consolidado.csv")
metadata_path = os.path.join(consolidated_dir, "consolidacao_metadata.json")

print("Iniciando Passo 020: Compilação de Conhecimento em TXT")

# --- 1. Carregar Dados Consolidados ---
print(f"Carregando CSV consolidado: {consolidated_csv_path}")
try:
    df_consolidated = pd.read_csv(consolidated_csv_path)
    print(f"  Carregado com sucesso: {len(df_consolidated)} linhas, {len(df_consolidated.columns)} colunas")
except Exception as e:
    print(f"Erro ao carregar CSV consolidado: {e}")
    df_consolidated = None

# --- 2. Carregar Metadados ---
print(f"Carregando metadados: {metadata_path}")
try:
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    print("  Metadados carregados com sucesso.")
except Exception as e:
    print(f"Erro ao carregar metadados: {e}")
    metadata = None

# --- 3. Compilar em TXT ---
print(f"Compilando dados em TXT: {output_file_txt}")
try:
    with open(output_file_txt, 'w', encoding='utf-8') as f_txt:
        # Cabeçalho
        f_txt.write("=" * 80 + "\n")
        f_txt.write(f"ORÁCULO 6.7 - BASE DE CONHECIMENTO CONSOLIDADA\n")
        f_txt.write(f"Data de geração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_txt.write("=" * 80 + "\n\n")
        
        # Metadados
        if metadata:
            f_txt.write("METADADOS\n")
            f_txt.write("-" * 80 + "\n")
            f_txt.write(f"Versão do Oráculo: {metadata.get('versao_oraculo', 'N/A')}\n")
            f_txt.write(f"Data de criação: {metadata.get('data_criacao', 'N/A')}\n")
            f_txt.write(f"Patch atual: {metadata.get('patch_atual', 'N/A')}\n")
            f_txt.write(f"Dimensões finais: {metadata.get('dimensoes_finais', {}).get('linhas', 'N/A')} linhas, {metadata.get('dimensoes_finais', {}).get('colunas', 'N/A')} colunas\n")
            
            # Arquivos de origem
            f_txt.write("\nArquivos de origem:\n")
            for arquivo in metadata.get('arquivos_origem', []):
                f_txt.write(f"- {arquivo}\n")
            
            # Eventos importantes
            f_txt.write("\nEventos importantes monitorados:\n")
            for evento in metadata.get('eventos_importantes', []):
                f_txt.write(f"- {evento}\n")
            
            f_txt.write("\n" + "-" * 80 + "\n\n")
        
        # Dados
        if df_consolidated is not None:
            f_txt.write("DADOS CONSOLIDADOS\n")
            f_txt.write("-" * 80 + "\n")
            
            # Colunas
            f_txt.write("Colunas disponíveis:\n")
            for col in df_consolidated.columns:
                f_txt.write(f"- {col}\n")
            f_txt.write("\n")
            
            # Estatísticas básicas
            f_txt.write("Estatísticas básicas:\n")
            for col in df_consolidated.columns:
                if pd.api.types.is_numeric_dtype(df_consolidated[col]):
                    f_txt.write(f"- {col}: min={df_consolidated[col].min()}, max={df_consolidated[col].max()}, média={df_consolidated[col].mean():.2f}\n")
            f_txt.write("\n")
            
            # Primeiras 10 linhas
            f_txt.write("Primeiras 10 linhas de dados:\n")
            f_txt.write("-" * 80 + "\n")
            
            # Formatar cabeçalho
            header = " | ".join(str(col) for col in df_consolidated.columns)
            f_txt.write(header + "\n")
            f_txt.write("-" * len(header) + "\n")
            
            # Formatar linhas
            for idx, row in df_consolidated.head(10).iterrows():
                line = " | ".join(str(val) for val in row.values)
                f_txt.write(line + "\n")
            
            f_txt.write("\n" + "-" * 80 + "\n")
            
            # Resumo de eventos importantes (se existirem)
            event_columns = [col for col in df_consolidated.columns if any(keyword in str(col).lower() for keyword in ['roshan', 'tower', 'tormentor', 'torre', 'objective', 'first'])]
            
            if event_columns:
                f_txt.write("\nResumo de eventos importantes:\n")
                for col in event_columns:
                    if pd.api.types.is_numeric_dtype(df_consolidated[col]):
                        count_1 = (df_consolidated[col] == 1).sum()
                        percent_1 = (count_1 / len(df_consolidated)) * 100
                        f_txt.write(f"- {col}: {count_1} ocorrências ({percent_1:.1f}%)\n")
                f_txt.write("\n")
            
            # Resumo de patch 7.38 (se existir)
            patch_columns = [col for col in df_consolidated.columns if 'patch' in str(col).lower()]
            if patch_columns:
                f_txt.write("\nResumo do patch 7.38:\n")
                for col in patch_columns:
                    if df_consolidated[col].dtype == object:  # Se for string
                        count_738 = df_consolidated[col].astype(str).str.contains('7.38').sum()
                        percent_738 = (count_738 / len(df_consolidated)) * 100
                        f_txt.write(f"- Partidas no patch 7.38: {count_738} ({percent_738:.1f}%)\n")
                f_txt.write("\n")
        else:
            f_txt.write("AVISO: Dados consolidados não disponíveis para compilação em TXT.\n\n")
        
        # Rodapé
        f_txt.write("=" * 80 + "\n")
        f_txt.write("FIM DO DOCUMENTO\n")
        f_txt.write("=" * 80 + "\n")
    
    print(f"  Compilação em TXT concluída.")

except Exception as e:
    print(f"Erro durante a compilação em TXT: {e}")

print("\nPasso 020 (Compilação em TXT) concluído.")
