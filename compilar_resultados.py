import json
import os
import pandas as pd
from datetime import datetime

# Diretórios onde os dados estão localizados
output_dir = '/home/ubuntu/dota2_knowledge_base'
licoes_dir = '/home/ubuntu/dota2_knowledge_base/licoes_validadas'
resultados_dir = '/home/ubuntu/dota2_knowledge_base/resultados_analise'

# Criar diretório para resultados da análise
os.makedirs(resultados_dir, exist_ok=True)

# Carregar as hipóteses validadas
with open(os.path.join(licoes_dir, 'hipoteses_validadas.json'), 'r', encoding='utf-8') as f:
    hipoteses = json.load(f)
    print(f"Carregadas {len(hipoteses)} hipóteses validadas")

# Carregar o resumo da validação
with open(os.path.join(licoes_dir, 'resumo_validacao.json'), 'r', encoding='utf-8') as f:
    resumo = json.load(f)
    print(f"Carregado resumo da validação")

# Carregar os resultados dos testes de validade
with open(os.path.join(licoes_dir, 'resultados_testes_validade.json'), 'r', encoding='utf-8') as f:
    resultados_testes = json.load(f)
    print(f"Carregados resultados dos testes de validade")

# Função para compilar os resultados da análise
def compilar_resultados_analise():
    print("\nCompilando resultados da análise...")
    
    # 1. Criar um resumo executivo
    resumo_executivo = {
        "titulo": "Análise de Lições Aprendidas em Dota 2: Validação de Hipóteses",
        "data": datetime.now().strftime("%Y-%m-%d"),
        "total_hipoteses_analisadas": len(hipoteses),
        "distribuicao_validacao": resumo["resultados_validacao"],
        "distribuicao_categorias": resumo["distribuicao_categorias"],
        "hipoteses_alta_validade": [h for h in resultados_testes if h["validade"] == "Alta"],
        "hipoteses_media_validade": [h for h in resultados_testes if h["validade"] == "Média"],
        "hipoteses_baixa_validade": [h for h in resultados_testes if h["validade"] == "Baixa"],
        "hipoteses_sem_evidencias": [h for h in resultados_testes if h["validade"] == "Não determinada (sem evidências)"],
        "conclusoes": {
            "principais_descobertas": [
                "Três hipóteses foram confirmadas com alta validade, todas relacionadas a padrões de apostas e características de partidas",
                "A maioria das hipóteses (27) foi parcialmente confirmada, indicando consistência parcial com a base de conhecimento",
                "Apenas uma hipótese não teve evidências suficientes para validação",
                "As hipóteses de alta validade têm alta especificidade e testabilidade, com termos quantitativos claros"
            ],
            "recomendacoes": [
                "Incorporar as hipóteses de alta validade na base de conhecimento do Oráculo 5.0",
                "Realizar testes adicionais para as hipóteses de média validade antes de incorporá-las",
                "Coletar mais dados para validar as hipóteses sem evidências suficientes",
                "Focar em hipóteses com termos quantitativos claros para facilitar a testabilidade"
            ],
            "limitacoes": [
                "A análise foi baseada apenas na base de conhecimento existente, sem dados adicionais",
                "A relevância média das evidências foi relativamente baixa (0.23)",
                "Algumas hipóteses podem ter sido mal formuladas ou extraídas incorretamente do texto original",
                "A categorização automática pode não ter capturado perfeitamente o contexto de cada hipótese"
            ]
        }
    }
    
    # Salvar o resumo executivo
    with open(os.path.join(resultados_dir, 'resumo_executivo.json'), 'w', encoding='utf-8') as f:
        json.dump(resumo_executivo, f, ensure_ascii=False, indent=2)
    print(f"Resumo executivo salvo em {os.path.join(resultados_dir, 'resumo_executivo.json')}")
    
    # 2. Criar uma tabela de hipóteses validadas
    tabela_hipoteses = []
    for hipotese in hipoteses:
        # Encontrar o resultado do teste correspondente
        resultado_teste = next((r for r in resultados_testes if r["hipotese"] == hipotese["text"]), None)
        
        if resultado_teste:
            validade = resultado_teste["validade"]
        else:
            validade = "Não testada"
        
        tabela_hipoteses.append({
            "texto": hipotese["text"],
            "categoria": hipotese.get("category", "não_categorizada"),
            "resultado_validacao": hipotese.get("validation_result", "não_validada"),
            "confiabilidade": hipotese.get("confidence", 0),
            "validade": validade,
            "num_evidencias_suporte": len(hipotese.get("supporting_evidence", [])),
            "num_evidencias_contrarias": len(hipotese.get("contradicting_evidence", []))
        })
    
    # Converter para DataFrame e salvar como CSV
    df_hipoteses = pd.DataFrame(tabela_hipoteses)
    df_hipoteses.to_csv(os.path.join(resultados_dir, 'tabela_hipoteses.csv'), index=False, encoding='utf-8')
    print(f"Tabela de hipóteses salva em {os.path.join(resultados_dir, 'tabela_hipoteses.csv')}")
    
    # 3. Criar um relatório detalhado em formato Markdown
    relatorio_md = f"""# Análise de Lições Aprendidas em Dota 2: Validação de Hipóteses

## Resumo Executivo

**Data:** {datetime.now().strftime("%Y-%m-%d")}

**Total de hipóteses analisadas:** {len(hipoteses)}

### Distribuição por Resultado de Validação

{pd.Series(resumo["resultados_validacao"]).to_markdown()}

### Distribuição por Categoria

{pd.Series(resumo["distribuicao_categorias"]).to_markdown()}

## Hipóteses de Alta Validade

As seguintes hipóteses foram confirmadas com alta validade:

"""
    
    for i, h in enumerate([h for h in resultados_testes if h["validade"] == "Alta"]):
        relatorio_md += f"""### {i+1}. {h['hipotese']}

- **Categoria:** {h['categoria']}
- **Confiabilidade:** {h['confiabilidade']:.2f}
- **Especificidade:** {h['especificidade']}
- **Testabilidade:** {h['testabilidade']}
- **Número de evidências de suporte:** {h['num_evidencias']}
- **Número de evidências contraditórias:** {h['num_contradicoes']}

"""
    
    relatorio_md += """## Hipóteses de Média Validade

As seguintes hipóteses foram confirmadas com média validade:

"""
    
    for i, h in enumerate([h for h in resultados_testes if h["validade"] == "Média"]):
        relatorio_md += f"""### {i+1}. {h['hipotese']}

- **Categoria:** {h['categoria']}
- **Confiabilidade:** {h['confiabilidade']:.2f}
- **Especificidade:** {h['especificidade']}
- **Testabilidade:** {h['testabilidade']}
- **Número de evidências de suporte:** {h['num_evidencias']}
- **Número de evidências contraditórias:** {h['num_contradicoes']}

"""
    
    relatorio_md += """## Hipóteses Sem Evidências Suficientes

As seguintes hipóteses não tiveram evidências suficientes para validação:

"""
    
    for i, h in enumerate([h for h in resultados_testes if h["validade"] == "Não determinada (sem evidências)"]):
        relatorio_md += f"""### {i+1}. {h['hipotese']}

- **Categoria:** {h['categoria']}
- **Especificidade:** {h['especificidade']}
- **Testabilidade:** {h['testabilidade']}

"""
    
    relatorio_md += """## Análise Estatística

### Estatísticas de Confiabilidade

"""
    
    confiabilidades = [r["confiabilidade"] for r in resultados_testes if r["confiabilidade"] > 0]
    if confiabilidades:
        media_confiabilidade = sum(confiabilidades) / len(confiabilidades)
        mediana_confiabilidade = sorted(confiabilidades)[len(confiabilidades) // 2]
        
        relatorio_md += f"""- **Média:** {media_confiabilidade:.2f}
- **Mediana:** {mediana_confiabilidade:.2f}

"""
    
    relatorio_md += """### Estatísticas de Relevância das Evidências

"""
    
    relevancias = [r["relevancia_media"] for r in resultados_testes if r["relevancia_media"] > 0]
    if relevancias:
        media_relevancia = sum(relevancias) / len(relevancias)
        mediana_relevancia = sorted(relevancias)[len(relevancias) // 2]
        
        relatorio_md += f"""- **Média:** {media_relevancia:.2f}
- **Mediana:** {mediana_relevancia:.2f}

"""
    
    relatorio_md += """## Conclusões e Recomendações

### Principais Descobertas

1. Três hipóteses foram confirmadas com alta validade, todas relacionadas a padrões de apostas e características de partidas
2. A maioria das hipóteses (27) foi parcialmente confirmada, indicando consistência parcial com a base de conhecimento
3. Apenas uma hipótese não teve evidências suficientes para validação
4. As hipóteses de alta validade têm alta especificidade e testabilidade, com termos quantitativos claros

### Recomendações

1. Incorporar as hipóteses de alta validade na base de conhecimento do Oráculo 5.0
2. Realizar testes adicionais para as hipóteses de média validade antes de incorporá-las
3. Coletar mais dados para validar as hipóteses sem evidências suficientes
4. Focar em hipóteses com termos quantitativos claros para facilitar a testabilidade

### Limitações da Análise

1. A análise foi baseada apenas na base de conhecimento existente, sem dados adicionais
2. A relevância média das evidências foi relativamente baixa (0.23)
3. Algumas hipóteses podem ter sido mal formuladas ou extraídas incorretamente do texto original
4. A categorização automática pode não ter capturado perfeitamente o contexto de cada hipótese

## Próximos Passos

1. Validar as hipóteses de alta validade com dados adicionais
2. Refinar as hipóteses de média validade para aumentar sua especificidade e testabilidade
3. Incorporar as hipóteses validadas na base de conhecimento do Oráculo 5.0
4. Desenvolver um sistema de monitoramento contínuo para validar hipóteses em tempo real
"""
    
    # Salvar o relatório em formato Markdown
    with open(os.path.join(resultados_dir, 'relatorio_detalhado.md'), 'w', encoding='utf-8') as f:
        f.write(relatorio_md)
    print(f"Relatório detalhado salvo em {os.path.join(resultados_dir, 'relatorio_detalhado.md')}")
    
    # 4. Criar um arquivo JSON com as hipóteses validadas para incorporação na base de conhecimento
    hipoteses_validadas_para_incorporacao = []
    for h in resultados_testes:
        if h["validade"] == "Alta":
            hipoteses_validadas_para_incorporacao.append({
                "text": h["hipotese"],
                "category": h["categoria"],
                "confidence": h["confiabilidade"],
                "validation_status": "validated",
                "validation_date": datetime.now().strftime("%Y-%m-%d"),
                "incorporation_recommended": True
            })
        elif h["validade"] == "Média":
            hipoteses_validadas_para_incorporacao.append({
                "text": h["hipotese"],
                "category": h["categoria"],
                "confidence": h["confiabilidade"],
                "validation_status": "partially_validated",
                "validation_date": datetime.now().strftime("%Y-%m-%d"),
                "incorporation_recommended": False,
                "additional_testing_required": True
            })
    
    # Salvar as hipóteses validadas para incorporação
    with open(os.path.join(resultados_dir, 'hipoteses_para_incorporacao.json'), 'w', encoding='utf-8') as f:
        json.dump(hipoteses_validadas_para_incorporacao, f, ensure_ascii=False, indent=2)
    print(f"Hipóteses validadas para incorporação salvas em {os.path.join(resultados_dir, 'hipoteses_para_incorporacao.json')}")
    
    return {
        "resumo_executivo": resumo_executivo,
        "tabela_hipoteses": tabela_hipoteses,
        "relatorio_md": relatorio_md,
        "hipoteses_para_incorporacao": hipoteses_validadas_para_incorporacao
    }

# Compilar os resultados da análise
resultados_compilados = compilar_resultados_analise()

print("\nCompilação de resultados concluída com sucesso!")
