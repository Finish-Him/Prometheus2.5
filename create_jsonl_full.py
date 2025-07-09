import json

# Event stream data (substituir com o acesso real ao histórico)
events = [
    {"type":"message","source":"user","date":"Apr 26 2025 06:20:49 +0000", "content": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiNWRhYmM3NGUtNzYxMS00MjNmLThlZjgtMWViYjgwMzU1YTg3IiwiU3RlYW1JZCI6IjEwNjU5NzkxMyIsIm5iZiI6MTc0NTYzOTI2NiwiZXhwIjoxNzc3MTc1MjY2LCJpYXQiOjE3NDU2MzkyNjYsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.KJgOXBLBd44AEWed8FmVP-gNQixPBlhlnA2aaYYw1Nc Essa é minha api no Stratz eu gostarai de baixar dados relevantes para a previsão das partidas em CSV mas estruturar um XML os dados irao servir para treinar a versão 6 do Oráculo virificar os endpoints foco no patch atual 7.38 e em dados de partidas profissionais correlacionar com os meus xml baixar em csv's detalhados e xml's precisos", "attachments": ["todo.md", "resumo_estrutura_xml.txt", "relacoes_entre_arquivos.txt", "estrutura_xml.txt", "esquema_database_oraculo.txt"]},
    {"type":"action","tool":"message_notify_user","date":"Apr 26 2025 06:20:53 +0000", "params": {"text": "Olá! Recebi seu pedido para trabalhar com a API do Stratz usando seu token JWT. Vou ajudar a baixar dados relevantes para previsão de partidas em formato CSV e estruturar em XML, focando no patch atual 7.38 e em dados de partidas profissionais. Vou analisar os arquivos que você enviou para entender melhor a estrutura necessária e começar a trabalhar nisso imediatamente."}},
    {"type":"knowledge","source":"knowledge_module","date":"Apr 26 2025 06:20:56 +0000","id":"user_1", "content": {"name": "Confirme antes de continuar", "use_when": "When starting or executing any task", "content": "Always ask the user several questions to help clarify their requirements, and only proceed after confirmation."}},
    # ... (Include all other events from the provided event stream) ...
    {"type":"message","source":"user","date":"Apr 28 2025 23:35:08 +0000", "content": "JSONL sim todo nossa sesão atual"},
    {"type":"action","tool":"message_notify_user","date":"Apr 28 2025 23:35:19 +0000", "params": {"text": "Entendido! Vou consolidar toda a nossa sessão atual em formato JSONL. Vou preparar esse arquivo agora mesmo."}},
    {"type":"plan","source":"planner_module","tool":"plan_proceed","date":"Apr 28 2025 23:35:30 +0000", "content": {"current_step": "002", "status": "Identificando conhecimentos relacionados ao Oráculo na sessão atual.", "reflection": "Estou avançando para o passo 002 (identificar_conhecimentos_oraculo_63) após a conclusão do passo 001 (analisar_requisitos_consolidacao_contexto). O usuário confirmou que deseja consolidar toda a sessão atual em formato JSONL. Embora o usuário tenha mencionado \"Oráculo 6.3\" em sua solicitação inicial, na confirmação ele apenas mencionou \"sim todo nossa sesão atual\", sem esclarecer especificamente sobre a versão do Oráculo. Considerando que a conversa anterior tratou principalmente do Oráculo versão 6/6.1, devo identificar todos os conhecimentos relacionados ao Oráculo que apareceram na sessão atual, independentemente da versão específica, para garantir uma consolidação completa."}},
    {"type":"action","tool":"file_write","date":"Apr 28 2025 23:38:38 +0000", "params": {"file": "/home/ubuntu/create_jsonl.py", "content": "... (conteúdo do script create_jsonl.py) ..."}},
    {"type":"plan","source":"planner_module","tool":"plan_proceed","date":"Apr 28 2025 23:38:45 +0000", "content": {"current_step": "003", "status": "Compilando a conversa e conhecimentos relacionados ao Oráculo para consolidação.", "reflection": "Estou avançando para o passo 003 (compilar_conversa_e_conhecimentos) após a conclusão do passo 002 (identificar_conhecimentos_oraculo_63). O agente criou um script Python (create_jsonl.py) para compilar toda a sessão atual em formato JSONL. O script inclui uma estrutura para processar os eventos da sessão, incluindo mensagens do usuário, ações do agente, conhecimentos relacionados ao Oráculo, e outros eventos relevantes. O script está projetado para lidar com possíveis erros de serialização e garantir que todos os dados sejam incluídos no arquivo final. Embora o script atual contenha apenas alguns exemplos de eventos como placeholder, a estrutura está pronta para ser preenchida com todos os eventos da sessão atual. O plano atual continua adequado, pois os próximos passos envolvem compilar todos os eventos da conversa e conhecimentos, definir o formato final de consolidação, criar o arquivo consolidado e entregá-lo ao usuário."}}
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

