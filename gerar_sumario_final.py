import json
import os
from datetime import datetime

# Diretório base
base_dir = '/home/ubuntu/dota2_knowledge_base'

# Carregar o sumário existente
with open(os.path.join(base_dir, 'sumario_arquivos.json'), 'r', encoding='utf-8') as f:
    sumario = json.load(f)

# Função para compilar metadados de versionamento
def compilar_metadados_versionamento():
    print("Compilando metadados de versionamento...")
    
    # Carregar a base de conhecimento mais recente
    with open(os.path.join(base_dir, 'dota2_knowledge_base_updated.json'), 'r', encoding='utf-8') as f:
        base_conhecimento = json.load(f)
    
    # Extrair metadados da base de conhecimento
    metadados_base = base_conhecimento.get('metadata', {})
    
    # Compilar metadados de versionamento
    metadados_versionamento = {
        "versao_atual": "6.0.0",
        "versao_anterior": "5.0.0",
        "data_atualizacao": datetime.now().strftime('%Y-%m-%d'),
        "total_informacoes": metadados_base.get('total_information_count', 0),
        "novas_informacoes": 3,  # As 3 hipóteses validadas incorporadas
        "categorias_atualizadas": ["betting", "meta_game", "teams_players"],
        "arquivos_base": [
            {
                "nome": "dota2_knowledge_base_updated.json",
                "tamanho": os.path.getsize(os.path.join(base_dir, 'dota2_knowledge_base_updated.json')),
                "tamanho_formatado": f"{os.path.getsize(os.path.join(base_dir, 'dota2_knowledge_base_updated.json')) / (1024 * 1024):.2f} MB",
                "data_modificacao": datetime.fromtimestamp(os.path.getmtime(os.path.join(base_dir, 'dota2_knowledge_base_updated.json'))).strftime('%Y-%m-%d %H:%M:%S'),
                "total_informacoes": metadados_base.get('total_information_count', 0)
            }
        ],
        "hipoteses_validadas": {
            "total": 31,
            "alta_validade": 3,
            "media_validade": 27,
            "sem_evidencias": 1,
            "incorporadas": 3
        },
        "recomendacoes_versionamento": [
            "Utilizar o arquivo dota2_knowledge_base_updated.json como base para o Oráculo 6.0",
            "Manter a estrutura de diretórios atual, com separação clara entre scripts, dados extraídos, dados consolidados e resultados de análise",
            "Implementar um sistema de controle de versão (como Git) para rastrear mudanças na base de conhecimento ao longo do tempo",
            "Incluir metadados detalhados em cada versão da base de conhecimento, como número de versão, data de atualização, total de informações e mudanças em relação à versão anterior",
            "Continuar o processo de validação de hipóteses antes de incorporá-las na base de conhecimento, seguindo o fluxo de trabalho estabelecido neste projeto"
        ],
        "proximos_passos": [
            "Implementar um sistema de validação contínua de hipóteses",
            "Desenvolver um pipeline automatizado para incorporação de novas informações",
            "Criar uma interface de usuário para visualização e exploração da base de conhecimento",
            "Expandir a base de conhecimento para incluir outros jogos, começando com CS2",
            "Implementar um sistema de feedback para melhorar a qualidade das previsões"
        ]
    }
    
    return metadados_versionamento

# Função para gerar um documento sumário final
def gerar_documento_sumario_final(metadados_versionamento):
    print("Gerando documento sumário final...")
    
    # Adicionar metadados de versionamento ao sumário
    sumario["metadados_versionamento"] = metadados_versionamento
    
    # Gerar documento sumário em formato JSON
    with open(os.path.join(base_dir, 'sumario_final.json'), 'w', encoding='utf-8') as f:
        json.dump(sumario, f, ensure_ascii=False, indent=2)
    print(f"Documento sumário final em formato JSON salvo em {os.path.join(base_dir, 'sumario_final.json')}")
    
    # Gerar documento sumário em formato Markdown
    markdown = f"# Sumário Final para o Oráculo 6.0\n\n"
    markdown += f"**Data de Geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    markdown += "## Metadados de Versionamento\n\n"
    markdown += f"**Versão Atual:** {metadados_versionamento['versao_atual']}\n\n"
    markdown += f"**Versão Anterior:** {metadados_versionamento['versao_anterior']}\n\n"
    markdown += f"**Data de Atualização:** {metadados_versionamento['data_atualizacao']}\n\n"
    markdown += f"**Total de Informações:** {metadados_versionamento['total_informacoes']}\n\n"
    markdown += f"**Novas Informações:** {metadados_versionamento['novas_informacoes']}\n\n"
    
    markdown += "### Categorias Atualizadas\n\n"
    for categoria in metadados_versionamento['categorias_atualizadas']:
        markdown += f"- {categoria}\n"
    markdown += "\n"
    
    markdown += "### Arquivos Base\n\n"
    for arquivo in metadados_versionamento['arquivos_base']:
        markdown += f"- **Nome:** {arquivo['nome']}\n"
        markdown += f"  - **Tamanho:** {arquivo['tamanho_formatado']}\n"
        markdown += f"  - **Data de Modificação:** {arquivo['data_modificacao']}\n"
        markdown += f"  - **Total de Informações:** {arquivo['total_informacoes']}\n\n"
    
    markdown += "### Hipóteses Validadas\n\n"
    markdown += f"- **Total:** {metadados_versionamento['hipoteses_validadas']['total']}\n"
    markdown += f"- **Alta Validade:** {metadados_versionamento['hipoteses_validadas']['alta_validade']}\n"
    markdown += f"- **Média Validade:** {metadados_versionamento['hipoteses_validadas']['media_validade']}\n"
    markdown += f"- **Sem Evidências:** {metadados_versionamento['hipoteses_validadas']['sem_evidencias']}\n"
    markdown += f"- **Incorporadas:** {metadados_versionamento['hipoteses_validadas']['incorporadas']}\n\n"
    
    markdown += "## Resumo de Arquivos\n\n"
    markdown += f"**Total de Arquivos:** {sumario['total_arquivos']}\n\n"
    
    markdown += "### Categorias de Arquivos\n\n"
    for categoria, info in sumario["categorias"].items():
        markdown += f"- **{categoria.replace('_', ' ').title()}:** {info['total_arquivos']} arquivos\n"
    markdown += "\n"
    
    markdown += "## Recomendações para Versionamento\n\n"
    for i, recomendacao in enumerate(metadados_versionamento['recomendacoes_versionamento']):
        markdown += f"{i+1}. {recomendacao}\n"
    markdown += "\n"
    
    markdown += "## Próximos Passos\n\n"
    for i, passo in enumerate(metadados_versionamento['proximos_passos']):
        markdown += f"{i+1}. {passo}\n"
    markdown += "\n"
    
    markdown += "## Conclusão\n\n"
    markdown += "Este sumário apresenta uma visão geral dos arquivos e metadados disponíveis para o desenvolvimento do Oráculo 6.0. A base de conhecimento atualizada contém 14.072 informações, incluindo 3 hipóteses validadas recentemente incorporadas. Recomenda-se utilizar o arquivo `dota2_knowledge_base_updated.json` como base para o Oráculo 6.0, seguindo as recomendações de versionamento e próximos passos descritos neste documento.\n\n"
    markdown += "Para mais detalhes sobre os arquivos individuais, consulte o arquivo `sumario_arquivos.md`.\n"
    
    with open(os.path.join(base_dir, 'sumario_final.md'), 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"Documento sumário final em formato Markdown salvo em {os.path.join(base_dir, 'sumario_final.md')}")

# Executar as funções
metadados_versionamento = compilar_metadados_versionamento()
gerar_documento_sumario_final(metadados_versionamento)

print("Compilação de metadados de versionamento e geração de documento sumário final concluídos com sucesso!")
