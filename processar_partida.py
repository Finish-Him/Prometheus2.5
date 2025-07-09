"""
Script para processar os dados da partida via backend do Manus e apresentar os resultados
"""

import sys
import os
from manus_backend_integration import processar_texto, formatar_previsao

def main():
    # Ler os dados formatados
    with open('/home/ubuntu/dados_formatados.txt', 'r') as f:
        dados_partida = f.read()
    
    print("Processando dados da partida via backend do Manus...")
    
    # Processar os dados via backend do Manus
    resultado = processar_texto(dados_partida)
    
    # Formatar os resultados para apresentação
    analise_formatada = formatar_previsao(resultado)
    
    # Salvar a análise formatada
    with open('/home/ubuntu/analise_partida.md', 'w') as f:
        f.write(analise_formatada)
    
    print("Análise concluída e salva em /home/ubuntu/analise_partida.md")
    
    # Exibir a análise
    print("\n" + "="*50 + "\n")
    print(analise_formatada)
    print("\n" + "="*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
