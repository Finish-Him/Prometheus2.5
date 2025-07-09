import os
import json
from datetime import datetime

# Diretório base
base_dir = '/home/ubuntu/dota2_knowledge_base'

# Função para categorizar os arquivos
def categorizar_arquivos():
    categorias = {
        "scripts_extracao": [],
        "scripts_analise": [],
        "scripts_consolidacao": [],
        "dados_extraidos": [],
        "dados_consolidados": [],
        "base_conhecimento": [],
        "analise_hipoteses": [],
        "resultados_analise": []
    }
    
    # Listar todos os arquivos
    arquivos = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            caminho_completo = os.path.join(root, file)
            arquivos.append(caminho_completo)
    
    # Categorizar cada arquivo
    for arquivo in arquivos:
        nome_arquivo = os.path.basename(arquivo)
        
        # Scripts de extração
        if nome_arquivo.startswith('extract_') and nome_arquivo.endswith('.py'):
            categorias["scripts_extracao"].append(arquivo)
        
        # Scripts de análise
        elif nome_arquivo in ['analisar_licoes_aprendidas.py', 'comparar_hipoteses.py', 'testar_validade_hipoteses.py']:
            categorias["scripts_analise"].append(arquivo)
        
        # Scripts de consolidação
        elif nome_arquivo.startswith('consolidate_') or nome_arquivo in ['structure_knowledge.py', 'generate_final_json.py', 'optimize_for_ml.py', 'increase_information.py', 'compilar_resultados.py', 'incorporar_hipoteses.py']:
            categorias["scripts_consolidacao"].append(arquivo)
        
        # Dados extraídos
        elif nome_arquivo.endswith('_extracted_data.json') or nome_arquivo in ['licoes_aprendidas_texto.txt', 'hipoteses_extraidas.json']:
            categorias["dados_extraidos"].append(arquivo)
        
        # Dados consolidados
        elif 'consolidated' in arquivo and arquivo.endswith('.json'):
            categorias["dados_consolidados"].append(arquivo)
        
        # Base de conhecimento
        elif nome_arquivo.startswith('dota2_knowledge_base') and nome_arquivo.endswith('.json'):
            categorias["base_conhecimento"].append(arquivo)
        
        # Análise de hipóteses
        elif 'licoes_validadas' in arquivo:
            categorias["analise_hipoteses"].append(arquivo)
        
        # Resultados da análise
        elif 'resultados_analise' in arquivo:
            categorias["resultados_analise"].append(arquivo)
    
    return categorias

# Função para obter metadados dos arquivos
def obter_metadados_arquivos(categorias):
    metadados = {}
    
    for categoria, arquivos in categorias.items():
        metadados[categoria] = []
        
        for arquivo in arquivos:
            tamanho = os.path.getsize(arquivo)
            data_modificacao = datetime.fromtimestamp(os.path.getmtime(arquivo)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Obter informações adicionais para arquivos JSON
            info_adicional = {}
            if arquivo.endswith('.json'):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        conteudo = json.load(f)
                        
                        # Para bases de conhecimento, obter contagem de informações
                        if 'dota2_knowledge_base' in arquivo:
                            if 'metadata' in conteudo and 'total_information_count' in conteudo['metadata']:
                                info_adicional['total_informacoes'] = conteudo['metadata']['total_information_count']
                            
                            if 'metadata' in conteudo and 'last_updated' in conteudo['metadata']:
                                info_adicional['ultima_atualizacao'] = conteudo['metadata']['last_updated']
                        
                        # Para resultados de análise, obter contagem de hipóteses
                        elif 'resumo_validacao.json' in arquivo:
                            if 'total_hipoteses' in conteudo:
                                info_adicional['total_hipoteses'] = conteudo['total_hipoteses']
                            
                            if 'resultados_validacao' in conteudo:
                                info_adicional['resultados_validacao'] = conteudo['resultados_validacao']
                except Exception as e:
                    info_adicional['erro'] = str(e)
            
            # Para scripts Python, obter descrição da função principal
            elif arquivo.endswith('.py'):
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        linhas = f.readlines()
                        for i, linha in enumerate(linhas):
                            if 'def ' in linha and '(' in linha and ')' in linha:
                                # Encontrou uma definição de função
                                nome_funcao = linha.split('def ')[1].split('(')[0].strip()
                                
                                # Procurar por docstring
                                if i+1 < len(linhas) and '"""' in linhas[i+1]:
                                    docstring_inicio = i+1
                                    docstring_fim = docstring_inicio
                                    
                                    # Encontrar o fim da docstring
                                    for j in range(docstring_inicio+1, len(linhas)):
                                        if '"""' in linhas[j]:
                                            docstring_fim = j
                                            break
                                    
                                    if docstring_fim > docstring_inicio:
                                        docstring = ' '.join([linhas[j].strip() for j in range(docstring_inicio, docstring_fim+1)])
                                        docstring = docstring.replace('"""', '').strip()
                                        info_adicional['funcao_principal'] = nome_funcao
                                        info_adicional['descricao'] = docstring
                                        break
                                
                                # Se não encontrou docstring, apenas registrar o nome da função
                                if 'funcao_principal' not in info_adicional:
                                    info_adicional['funcao_principal'] = nome_funcao
                                    break
                except Exception as e:
                    info_adicional['erro'] = str(e)
            
            metadados[categoria].append({
                'arquivo': arquivo,
                'nome': os.path.basename(arquivo),
                'tamanho': tamanho,
                'tamanho_formatado': f"{tamanho / 1024:.2f} KB" if tamanho < 1024 * 1024 else f"{tamanho / (1024 * 1024):.2f} MB",
                'data_modificacao': data_modificacao,
                'info_adicional': info_adicional
            })
    
    return metadados

# Função para criar um sumário detalhado
def criar_sumario_detalhado(categorias, metadados):
    sumario = {
        "titulo": "Sumário de Arquivos para o Oráculo 6.0",
        "data_geracao": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_arquivos": sum(len(arquivos) for arquivos in categorias.values()),
        "categorias": {}
    }
    
    # Descrições das categorias
    descricoes_categorias = {
        "scripts_extracao": "Scripts Python utilizados para extrair dados de diferentes formatos (CSV, Markdown, Python, texto, DOCX)",
        "scripts_analise": "Scripts Python utilizados para analisar lições aprendidas, comparar com a base de conhecimento e testar a validade das hipóteses",
        "scripts_consolidacao": "Scripts Python utilizados para consolidar dados, estruturar conhecimento e gerar a base de conhecimento final",
        "dados_extraidos": "Dados extraídos de diferentes fontes, incluindo texto de lições aprendidas e hipóteses extraídas",
        "dados_consolidados": "Dados consolidados por categoria (meta, equipes/jogadores, apostas, APIs)",
        "base_conhecimento": "Versões da base de conhecimento do Oráculo, desde a versão inicial até a final atualizada com hipóteses validadas",
        "analise_hipoteses": "Resultados da análise de hipóteses, incluindo hipóteses validadas e resumo da validação",
        "resultados_analise": "Resultados finais da análise, incluindo relatório detalhado, resumo executivo e hipóteses para incorporação"
    }
    
    # Preencher o sumário
    for categoria, arquivos in categorias.items():
        sumario["categorias"][categoria] = {
            "descricao": descricoes_categorias.get(categoria, ""),
            "total_arquivos": len(arquivos),
            "arquivos": []
        }
        
        for arquivo_info in metadados[categoria]:
            sumario["categorias"][categoria]["arquivos"].append({
                "nome": arquivo_info["nome"],
                "caminho": arquivo_info["arquivo"],
                "tamanho": arquivo_info["tamanho_formatado"],
                "data_modificacao": arquivo_info["data_modificacao"],
                "info_adicional": arquivo_info["info_adicional"]
            })
    
    return sumario

# Função para gerar um documento de sumário em formato Markdown
def gerar_sumario_markdown(sumario):
    markdown = f"# {sumario['titulo']}\n\n"
    markdown += f"**Data de Geração:** {sumario['data_geracao']}\n\n"
    markdown += f"**Total de Arquivos:** {sumario['total_arquivos']}\n\n"
    
    markdown += "## Índice\n\n"
    for categoria in sumario["categorias"]:
        markdown += f"- [{categoria.replace('_', ' ').title()}](#{categoria})\n"
    markdown += "\n"
    
    for categoria, info in sumario["categorias"].items():
        markdown += f"## {categoria.replace('_', ' ').title()}\n\n"
        markdown += f"{info['descricao']}\n\n"
        markdown += f"**Total de Arquivos:** {info['total_arquivos']}\n\n"
        
        markdown += "| Arquivo | Tamanho | Data de Modificação | Informações Adicionais |\n"
        markdown += "|---------|---------|---------------------|------------------------|\n"
        
        for arquivo in info["arquivos"]:
            info_adicional = ""
            for chave, valor in arquivo["info_adicional"].items():
                if isinstance(valor, dict):
                    info_adicional += f"{chave}: {json.dumps(valor, ensure_ascii=False)}<br>"
                else:
                    info_adicional += f"{chave}: {valor}<br>"
            
            markdown += f"| {arquivo['nome']} | {arquivo['tamanho']} | {arquivo['data_modificacao']} | {info_adicional} |\n"
        
        markdown += "\n"
    
    markdown += "## Recomendações para Versionamento\n\n"
    markdown += "1. **Base de Conhecimento Principal:** Utilizar o arquivo `dota2_knowledge_base_updated.json` como base para o Oráculo 6.0, pois contém todas as informações consolidadas e as hipóteses validadas incorporadas.\n\n"
    markdown += "2. **Estrutura de Diretórios:** Manter a estrutura de diretórios atual, com separação clara entre scripts, dados extraídos, dados consolidados e resultados de análise.\n\n"
    markdown += "3. **Controle de Versão:** Implementar um sistema de controle de versão (como Git) para rastrear mudanças na base de conhecimento ao longo do tempo.\n\n"
    markdown += "4. **Metadados:** Incluir metadados detalhados em cada versão da base de conhecimento, como número de versão, data de atualização, total de informações e mudanças em relação à versão anterior.\n\n"
    markdown += "5. **Validação de Hipóteses:** Continuar o processo de validação de hipóteses antes de incorporá-las na base de conhecimento, seguindo o fluxo de trabalho estabelecido neste projeto.\n\n"
    
    return markdown

# Função para gerar um documento de sumário em formato JSON
def gerar_sumario_json(sumario):
    return json.dumps(sumario, ensure_ascii=False, indent=2)

# Executar as funções
categorias = categorizar_arquivos()
metadados = obter_metadados_arquivos(categorias)
sumario = criar_sumario_detalhado(categorias, metadados)

# Salvar o sumário em formato Markdown
with open(os.path.join(base_dir, 'sumario_arquivos.md'), 'w', encoding='utf-8') as f:
    f.write(gerar_sumario_markdown(sumario))
print(f"Sumário em formato Markdown salvo em {os.path.join(base_dir, 'sumario_arquivos.md')}")

# Salvar o sumário em formato JSON
with open(os.path.join(base_dir, 'sumario_arquivos.json'), 'w', encoding='utf-8') as f:
    f.write(gerar_sumario_json(sumario))
print(f"Sumário em formato JSON salvo em {os.path.join(base_dir, 'sumario_arquivos.json')}")

print("Categorização e sumário de arquivos concluídos com sucesso!")
