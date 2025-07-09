"""
Script para testar a integração com o Oráculo 4.0
"""

import requests
import json
import base64
import os

# URL base do servidor
BASE_URL = "http://localhost:8000"

# Token de autenticação
API_KEY = "oraculo_v4_api_key_manus_integration_2025_04_24_8f7d3e1a9b2c5d6e"

# Headers para requisições
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_root():
    """Testa a rota raiz do servidor"""
    response = requests.get(f"{BASE_URL}/")
    print(f"Teste da rota raiz: {response.status_code}")
    print(response.json())
    print()

def test_process_text():
    """Testa o processamento de texto"""
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
    
    payload = {"text": text_data}
    
    try:
        response = requests.post(f"{BASE_URL}/process/text", headers=HEADERS, json=payload)
        print(f"Teste de processamento de texto: {response.status_code}")
        if response.status_code == 200:
            print("Processamento de texto bem-sucedido!")
            # Imprimir apenas parte da resposta para não sobrecarregar o console
            result = response.json()
            print(f"Match: {result.get('match_data', {}).get('time_radiant', '')} vs {result.get('match_data', {}).get('time_dire', '')}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro ao testar processamento de texto: {str(e)}")
    print()

def test_openapi_yaml():
    """Testa o acesso ao arquivo OpenAPI"""
    response = requests.get(f"{BASE_URL}/openapi.yaml")
    print(f"Teste do arquivo OpenAPI: {response.status_code}")
    if response.status_code == 200:
        print("Arquivo OpenAPI acessível!")
    else:
        print(f"Erro: {response.text}")
    print()

def test_plugin_manifest():
    """Testa o acesso ao manifesto do plugin"""
    response = requests.get(f"{BASE_URL}/.well-known/ai-plugin.json")
    print(f"Teste do manifesto do plugin: {response.status_code}")
    if response.status_code == 200:
        print("Manifesto do plugin acessível!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erro: {response.text}")
    print()

def test_logo():
    """Testa o acesso ao logo"""
    response = requests.get(f"{BASE_URL}/logo.png")
    print(f"Teste do logo: {response.status_code}")
    if response.status_code == 200:
        print("Logo acessível!")
    else:
        print(f"Erro: {response.text}")
    print()

if __name__ == "__main__":
    print("Iniciando testes da integração com o Oráculo 4.0...")
    print("Certifique-se de que o servidor está em execução!")
    print("-" * 50)
    
    # Executar testes
    test_root()
    test_openapi_yaml()
    test_plugin_manifest()
    test_logo()
    
    # O teste de process_text pode falhar se o backend real não estiver disponível
    # Comentado para evitar erros durante os testes iniciais
    # test_process_text()
    
    print("-" * 50)
    print("Testes concluídos!")
