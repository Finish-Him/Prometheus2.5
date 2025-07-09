import json
import os
import re
import numpy as np
from datetime import datetime

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'
licoes_dir = '/home/ubuntu/dota2_knowledge_base/licoes_validadas'

# Carregar as hipóteses validadas
with open(os.path.join(licoes_dir, 'hipoteses_validadas.json'), 'r', encoding='utf-8') as f:
    hipoteses = json.load(f)
    print(f"Carregadas {len(hipoteses)} hipóteses validadas")

# Carregar o resumo da validação
with open(os.path.join(licoes_dir, 'resumo_validacao.json'), 'r', encoding='utf-8') as f:
    resumo = json.load(f)
    print(f"Carregado resumo da validação")

# Carregar a base de conhecimento
with open(os.path.join(output_dir, 'dota2_knowledge_base_final.json'), 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)
    print(f"Carregada base de conhecimento com {knowledge_base['metadata']['total_information_count']} informações")

# Função para testar a validade das hipóteses
def testar_validade_hipoteses():
    print("\nTestando a validade das hipóteses...")
    
    # Estrutura para armazenar os resultados dos testes
    resultados_testes = []
    
    # 1. Testar hipóteses confirmadas
    print("\n1. Testando hipóteses confirmadas:")
    for i, hipotese in enumerate(resumo["hipoteses_confirmadas"]):
        print(f"\nHipótese {i+1}: {hipotese['text']}")
        
        # Verificar a consistência das evidências
        evidencias = hipotese.get("supporting_evidence", [])
        num_evidencias = len(evidencias)
        
        print(f"  - Número de evidências de suporte: {num_evidencias}")
        
        # Calcular a relevância média das evidências
        if num_evidencias > 0:
            relevancia_media = sum(e.get("relevance", 0) for e in evidencias) / num_evidencias
            print(f"  - Relevância média das evidências: {relevancia_media:.2f}")
        else:
            relevancia_media = 0
            print("  - Sem evidências de suporte")
        
        # Verificar se há contradições
        contradicoes = hipotese.get("contradicting_evidence", [])
        num_contradicoes = len(contradicoes)
        
        print(f"  - Número de evidências contraditórias: {num_contradicoes}")
        
        # Calcular a confiabilidade da hipótese
        if num_evidencias > 0:
            if num_contradicoes == 0:
                confiabilidade = min(0.5 + 0.1 * num_evidencias, 0.9)
            else:
                confiabilidade = 0.5 + 0.1 * (num_evidencias - num_contradicoes) / (num_evidencias + num_contradicoes)
        else:
            confiabilidade = 0
        
        print(f"  - Confiabilidade calculada: {confiabilidade:.2f}")
        print(f"  - Confiabilidade atribuída: {hipotese.get('confidence', 0):.2f}")
        
        # Verificar se a confiabilidade calculada é consistente com a atribuída
        consistencia_confiabilidade = abs(confiabilidade - hipotese.get('confidence', 0)) < 0.1
        print(f"  - Consistência da confiabilidade: {'Sim' if consistencia_confiabilidade else 'Não'}")
        
        # Verificar se a hipótese é específica e testável
        palavras = len(re.findall(r'\b\w+\b', hipotese['text']))
        especificidade = "Alta" if palavras > 15 else "Média" if palavras > 8 else "Baixa"
        print(f"  - Especificidade da hipótese: {especificidade} ({palavras} palavras)")
        
        # Verificar se a hipótese contém termos quantitativos
        termos_quantitativos = re.findall(r'\b\d+[%]?|\b(mais|menos|maior|menor|acima|abaixo|superior|inferior)\b', hipotese['text'].lower())
        testabilidade = "Alta" if len(termos_quantitativos) > 0 else "Baixa"
        print(f"  - Testabilidade da hipótese: {testabilidade} ({len(termos_quantitativos)} termos quantitativos)")
        
        # Avaliar a validade geral da hipótese
        if confiabilidade >= 0.7 and especificidade != "Baixa" and testabilidade == "Alta":
            validade = "Alta"
        elif confiabilidade >= 0.5 and (especificidade != "Baixa" or testabilidade == "Alta"):
            validade = "Média"
        else:
            validade = "Baixa"
        
        print(f"  - Validade geral da hipótese: {validade}")
        
        # Armazenar os resultados do teste
        resultados_testes.append({
            "hipotese": hipotese['text'],
            "categoria": hipotese.get('category', 'não_categorizada'),
            "num_evidencias": num_evidencias,
            "relevancia_media": relevancia_media,
            "num_contradicoes": num_contradicoes,
            "confiabilidade": confiabilidade,
            "especificidade": especificidade,
            "testabilidade": testabilidade,
            "validade": validade,
            "resultado_validacao": hipotese.get('validation_result', 'não_validada')
        })
    
    # 2. Testar uma amostra das hipóteses parcialmente confirmadas
    print("\n2. Testando uma amostra das hipóteses parcialmente confirmadas:")
    # Selecionar 5 hipóteses parcialmente confirmadas aleatoriamente
    amostra_parcial = resumo["hipoteses_parcialmente_confirmadas"][:5]
    
    for i, hipotese in enumerate(amostra_parcial):
        print(f"\nHipótese {i+1}: {hipotese['text']}")
        
        # Verificar a consistência das evidências
        evidencias = hipotese.get("supporting_evidence", [])
        num_evidencias = len(evidencias)
        
        print(f"  - Número de evidências de suporte: {num_evidencias}")
        
        # Calcular a relevância média das evidências
        if num_evidencias > 0:
            relevancia_media = sum(e.get("relevance", 0) for e in evidencias) / num_evidencias
            print(f"  - Relevância média das evidências: {relevancia_media:.2f}")
        else:
            relevancia_media = 0
            print("  - Sem evidências de suporte")
        
        # Verificar se há contradições
        contradicoes = hipotese.get("contradicting_evidence", [])
        num_contradicoes = len(contradicoes)
        
        print(f"  - Número de evidências contraditórias: {num_contradicoes}")
        
        # Calcular a confiabilidade da hipótese
        if num_evidencias > 0:
            if num_contradicoes == 0:
                confiabilidade = min(0.5 + 0.1 * num_evidencias, 0.9)
            else:
                confiabilidade = 0.5 + 0.1 * (num_evidencias - num_contradicoes) / (num_evidencias + num_contradicoes)
        else:
            confiabilidade = 0
        
        print(f"  - Confiabilidade calculada: {confiabilidade:.2f}")
        print(f"  - Confiabilidade atribuída: {hipotese.get('confidence', 0):.2f}")
        
        # Verificar se a confiabilidade calculada é consistente com a atribuída
        consistencia_confiabilidade = abs(confiabilidade - hipotese.get('confidence', 0)) < 0.1
        print(f"  - Consistência da confiabilidade: {'Sim' if consistencia_confiabilidade else 'Não'}")
        
        # Verificar se a hipótese é específica e testável
        palavras = len(re.findall(r'\b\w+\b', hipotese['text']))
        especificidade = "Alta" if palavras > 15 else "Média" if palavras > 8 else "Baixa"
        print(f"  - Especificidade da hipótese: {especificidade} ({palavras} palavras)")
        
        # Verificar se a hipótese contém termos quantitativos
        termos_quantitativos = re.findall(r'\b\d+[%]?|\b(mais|menos|maior|menor|acima|abaixo|superior|inferior)\b', hipotese['text'].lower())
        testabilidade = "Alta" if len(termos_quantitativos) > 0 else "Baixa"
        print(f"  - Testabilidade da hipótese: {testabilidade} ({len(termos_quantitativos)} termos quantitativos)")
        
        # Avaliar a validade geral da hipótese
        if confiabilidade >= 0.7 and especificidade != "Baixa" and testabilidade == "Alta":
            validade = "Alta"
        elif confiabilidade >= 0.5 and (especificidade != "Baixa" or testabilidade == "Alta"):
            validade = "Média"
        else:
            validade = "Baixa"
        
        print(f"  - Validade geral da hipótese: {validade}")
        
        # Armazenar os resultados do teste
        resultados_testes.append({
            "hipotese": hipotese['text'],
            "categoria": hipotese.get('category', 'não_categorizada'),
            "num_evidencias": num_evidencias,
            "relevancia_media": relevancia_media,
            "num_contradicoes": num_contradicoes,
            "confiabilidade": confiabilidade,
            "especificidade": especificidade,
            "testabilidade": testabilidade,
            "validade": validade,
            "resultado_validacao": hipotese.get('validation_result', 'não_validada')
        })
    
    # 3. Testar hipóteses sem evidências
    print("\n3. Testando hipóteses sem evidências:")
    for i, hipotese in enumerate(resumo["hipoteses_sem_evidencias"]):
        print(f"\nHipótese {i+1}: {hipotese['text']}")
        
        # Verificar se a hipótese é específica e testável
        palavras = len(re.findall(r'\b\w+\b', hipotese['text']))
        especificidade = "Alta" if palavras > 15 else "Média" if palavras > 8 else "Baixa"
        print(f"  - Especificidade da hipótese: {especificidade} ({palavras} palavras)")
        
        # Verificar se a hipótese contém termos quantitativos
        termos_quantitativos = re.findall(r'\b\d+[%]?|\b(mais|menos|maior|menor|acima|abaixo|superior|inferior)\b', hipotese['text'].lower())
        testabilidade = "Alta" if len(termos_quantitativos) > 0 else "Baixa"
        print(f"  - Testabilidade da hipótese: {testabilidade} ({len(termos_quantitativos)} termos quantitativos)")
        
        # Avaliar a validade geral da hipótese
        validade = "Não determinada (sem evidências)"
        print(f"  - Validade geral da hipótese: {validade}")
        
        # Armazenar os resultados do teste
        resultados_testes.append({
            "hipotese": hipotese['text'],
            "categoria": hipotese.get('category', 'não_categorizada'),
            "num_evidencias": 0,
            "relevancia_media": 0,
            "num_contradicoes": 0,
            "confiabilidade": 0,
            "especificidade": especificidade,
            "testabilidade": testabilidade,
            "validade": validade,
            "resultado_validacao": hipotese.get('validation_result', 'não_validada')
        })
    
    # 4. Análise estatística dos resultados
    print("\n4. Análise estatística dos resultados:")
    
    # Contar hipóteses por validade
    contagem_validade = {}
    for resultado in resultados_testes:
        validade = resultado["validade"]
        contagem_validade[validade] = contagem_validade.get(validade, 0) + 1
    
    print("Distribuição de hipóteses por validade:")
    for validade, contagem in contagem_validade.items():
        print(f"  - {validade}: {contagem} hipóteses")
    
    # Calcular estatísticas de confiabilidade
    confiabilidades = [r["confiabilidade"] for r in resultados_testes if r["confiabilidade"] > 0]
    if confiabilidades:
        media_confiabilidade = sum(confiabilidades) / len(confiabilidades)
        mediana_confiabilidade = sorted(confiabilidades)[len(confiabilidades) // 2]
        desvio_padrao_confiabilidade = np.std(confiabilidades)
        
        print(f"\nEstatísticas de confiabilidade:")
        print(f"  - Média: {media_confiabilidade:.2f}")
        print(f"  - Mediana: {mediana_confiabilidade:.2f}")
        print(f"  - Desvio padrão: {desvio_padrao_confiabilidade:.2f}")
    
    # Calcular estatísticas de relevância
    relevancias = [r["relevancia_media"] for r in resultados_testes if r["relevancia_media"] > 0]
    if relevancias:
        media_relevancia = sum(relevancias) / len(relevancias)
        mediana_relevancia = sorted(relevancias)[len(relevancias) // 2]
        desvio_padrao_relevancia = np.std(relevancias)
        
        print(f"\nEstatísticas de relevância das evidências:")
        print(f"  - Média: {media_relevancia:.2f}")
        print(f"  - Mediana: {mediana_relevancia:.2f}")
        print(f"  - Desvio padrão: {desvio_padrao_relevancia:.2f}")
    
    # 5. Conclusões sobre a validade das hipóteses
    print("\n5. Conclusões sobre a validade das hipóteses:")
    
    # Hipóteses de alta validade
    hipoteses_alta_validade = [r for r in resultados_testes if r["validade"] == "Alta"]
    print(f"Hipóteses de alta validade: {len(hipoteses_alta_validade)}")
    for i, h in enumerate(hipoteses_alta_validade):
        print(f"  {i+1}. {h['hipotese'][:100]}...")
    
    # Hipóteses de média validade
    hipoteses_media_validade = [r for r in resultados_testes if r["validade"] == "Média"]
    print(f"\nHipóteses de média validade: {len(hipoteses_media_validade)}")
    for i, h in enumerate(hipoteses_media_validade[:3]):  # Mostrar apenas as 3 primeiras
        print(f"  {i+1}. {h['hipotese'][:100]}...")
    
    # Hipóteses de baixa validade
    hipoteses_baixa_validade = [r for r in resultados_testes if r["validade"] == "Baixa"]
    print(f"\nHipóteses de baixa validade: {len(hipoteses_baixa_validade)}")
    for i, h in enumerate(hipoteses_baixa_validade[:3]):  # Mostrar apenas as 3 primeiras
        print(f"  {i+1}. {h['hipotese'][:100]}...")
    
    return resultados_testes

# Testar a validade das hipóteses
resultados_testes = testar_validade_hipoteses()

# Salvar os resultados dos testes
with open(os.path.join(licoes_dir, 'resultados_testes_validade.json'), 'w', encoding='utf-8') as f:
    json.dump(resultados_testes, f, ensure_ascii=False, indent=2)
print(f"\nResultados dos testes de validade salvos em {os.path.join(licoes_dir, 'resultados_testes_validade.json')}")

print("\nTestes de validade concluídos com sucesso!")
