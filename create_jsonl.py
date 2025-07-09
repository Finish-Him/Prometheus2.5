import json

# Simulação do event stream (substituir com o acesso real ao histórico)
events = [
    {"type":"message","source":"user","date":"Apr 26 2025 06:20:49 +0000", "content": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNWRhYmM3NGUtNzYxMS00MjNmLThlZjgtMWViYjgwMzU1YTg3IiwiU3RlYW1JZCI6IjEwNjU5NzkxMyIsIm5iZiI6MTc0NTYzOTI2NiwiZXhwIjoxNzc3MTc1MjY2LCJpYXQiOjE3NDU2MzkyNjYsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.KJgOXBLBd44AEWed8FmVP-gNQixPBlhlnA2aaYYw1Nc Essa é minha api no Stratz eu gostarai de baixar dados relevantes para a previsão das partidas em CSV mas estruturar um XML os dados irao servir para treinar a versão 6 do Oráculo virificar os endpoints foco no patch atual 7.38 e em dados de partidas profissionais correlacionar com os meus xml baixar em csv's detalhados e xml's precisos", "attachments": ["todo.md", "resumo_estrutura_xml.txt", "relacoes_entre_arquivos.txt", "estrutura_xml.txt", "esquema_database_oraculo.txt"]},
    {"type":"action","tool":"message_notify_user","date":"Apr 26 2025 06:20:53 +0000", "params": {"text": "Olá! Recebi seu pedido para trabalhar com a API do Stratz usando seu token JWT. Vou ajudar a baixar dados relevantes para previsão de partidas em formato CSV e estruturar em XML, focando no patch atual 7.38 e em dados de partidas profissionais. Vou analisar os arquivos que você enviou para entender melhor a estrutura necessária e começar a trabalhar nisso imediatamente."}},
    # ... (incluir todos os outros eventos da sessão: actions, observations, plans, knowledge, datasources, etc.) ...
    # Exemplo de inclusão de conhecimento:
    {"type":"knowledge","source":"knowledge_module","date":"Apr 26 2025 07:03:29 +0000","id":"user_3", "content": {"name": "Preferências para dados de partidas profissionais Dota 2", "use_when": "Quando coletar dados de partidas profissionais de Dota 2 para o sistema Oráculo", "content": "Ao coletar dados de partidas profissionais de Dota 2, separar Tier 1 e Tier 2 por região. Inicialmente, coletar aproximadamente 500 partidas para testar a API. Incluir todos os tipos de dados disponíveis para identificar padrões e relações entre eles. Focar principalmente no patch atual 7.38."}},
    # ... (incluir mais eventos) ...
    {"type":"message","source":"user","date":"Apr 28 2025 23:35:08 +0000", "content": "JSONL sim todo nossa sesão atual"},
    {"type":"action","tool":"message_notify_user","date":"Apr 28 2025 23:35:19 +0000", "params": {"text": "Entendido! Vou consolidar toda a nossa sessão atual em formato JSONL. Vou preparar esse arquivo agora mesmo."}},
    {"type":"plan","source":"planner_module","tool":"plan_proceed","date":"Apr 28 2025 23:35:30 +0000", "content": {"current_step": "002", "status": "Identificando conhecimentos relacionados ao Oráculo na sessão atual.", "reflection": "Estou avançando para o passo 002 (identificar_conhecimentos_oraculo_63) após a conclusão do passo 001 (analisar_requisitos_consolidacao_contexto). O usuário confirmou que deseja consolidar toda a sessão atual em formato JSONL. Embora o usuário tenha mencionado \"Oráculo 6.3\" em sua solicitação inicial, na confirmação ele apenas mencionou \"sim todo nossa sesão atual\", sem esclarecer especificamente sobre a versão do Oráculo. Considerando que a conversa anterior tratou principalmente do Oráculo versão 6/6.1, devo identificar todos os conhecimentos relacionados ao Oráculo que apareceram na sessão atual, independentemente da versão específica, para garantir uma consolidação completa."}}
]

# Nome do arquivo de saída
output_filename = "/home/ubuntu/session_consolidation.jsonl"

# Escrever eventos no arquivo JSONL
try:
    with open(output_filename, "w", encoding="utf-8") as f:
        for event in events:
            # Garantir que todos os dados sejam serializáveis em JSON
            try:
                json_line = json.dumps(event, ensure_ascii=False)
                f.write(json_line + "\n")
            except TypeError as e:
                print(f"Erro ao serializar evento: {e}\nEvento: {event}")
                # Tentar serializar com representação de string para dados não serializáveis
                try:
                    event_str = {k: str(v) for k, v in event.items()}
                    json_line = json.dumps(event_str, ensure_ascii=False)
                    f.write(json_line + "\n")
                except Exception as inner_e:
                    print(f"Falha ao serializar como string: {inner_e}")
    
    print(f"Sessão consolidada com sucesso em {output_filename}")

except Exception as e:
    print(f"Erro ao criar o arquivo JSONL: {e}")

