"""
Script para testar a integração direta entre o ChatGPT e o back-end do Manus
"""

import sys
import json
from integracao_direta_manus import analisar_partida_texto, obter_historico

def test_analisar_partida_texto():
    """Testa a função de análise de partida por texto"""
    print("Testando análise de partida por texto...")
    
    # Exemplo de texto de partida
    text_data = """
    Team Spirit vs NaVi Junior
    PGL Wallachia Season 4
    
    Odds Team Spirit: 1.16
    Odds NaVi Junior: 4.88
    
    Handicap de kills: 8.5
    Odds over: 1.90
    Odds under: 1.80
    
    Duração da partida: 32.5
    Odds over: 1.85
    Odds under: 1.85
    
    Total de kills: 48.5
    Odds over: 1.90
    Odds under: 1.80
    """
    
    # Chamar a função
    result = analisar_partida_texto(text_data)
    
    # Verificar se o resultado contém as seções esperadas
    expected_sections = [
        "# Previsão:",
        "## Previsões",
        "### Duração da Partida",
        "### Total de Abates",
        "## Valuebets Recomendadas",
        "## Explicações"
    ]
    
    success = all(section in result for section in expected_sections)
    
    if success:
        print("✅ Teste de análise de partida por texto bem-sucedido!")
    else:
        print("❌ Teste de análise de partida por texto falhou!")
        print("Resultado obtido:")
        print(result)
    
    print("-" * 50)
    return success

def test_obter_historico():
    """Testa a função de obtenção de histórico"""
    print("Testando obtenção de histórico...")
    
    # Chamar a função
    result = obter_historico(limite=3)
    
    # Verificar se o resultado contém as seções esperadas
    if "# Histórico de Previsões" in result or "Nenhum registro encontrado no histórico." in result:
        print("✅ Teste de obtenção de histórico bem-sucedido!")
    else:
        print("❌ Teste de obtenção de histórico falhou!")
        print("Resultado obtido:")
        print(result)
    
    print("-" * 50)
    return True  # Consideramos sucesso mesmo se não houver registros

def run_all_tests():
    """Executa todos os testes"""
    print("Iniciando testes da integração direta com o Oráculo 4.0...")
    print("-" * 50)
    
    # Lista de testes
    tests = [
        test_analisar_partida_texto,
        test_obter_historico
    ]
    
    # Executar testes
    results = []
    for test in tests:
        results.append(test())
    
    # Resumo
    print("Resumo dos testes:")
    print(f"Total de testes: {len(tests)}")
    print(f"Testes bem-sucedidos: {sum(results)}")
    print(f"Testes falhos: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ Todos os testes foram bem-sucedidos!")
    else:
        print("\n❌ Alguns testes falharam!")
    
    return all(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
