#!/usr/bin/env python3
"""
Analisador Completo do Prometheus 2.3
Cataloga todos os arquivos JSON e Python para migração
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import sys

def calcular_hash(arquivo_path):
    """Calcula hash SHA256 do arquivo"""
    try:
        with open(arquivo_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:8]
    except:
        return "erro_hash"

def analisar_json(arquivo_path):
    """Analisa arquivo JSON e extrai metadados"""
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Determinar tipo de dados
        if isinstance(dados, list):
            tipo_dados = "array"
            total_registros = len(dados)
            campos_principais = list(dados[0].keys()) if dados and isinstance(dados[0], dict) else []
        elif isinstance(dados, dict):
            tipo_dados = "object"
            total_registros = 1
            campos_principais = list(dados.keys())
        else:
            tipo_dados = "primitive"
            total_registros = 1
            campos_principais = []
        
        return {
            "valido": True,
            "tipo_dados": tipo_dados,
            "total_registros": total_registros,
            "campos_principais": campos_principais[:10],  # Primeiros 10 campos
            "tamanho_kb": round(os.path.getsize(arquivo_path) / 1024, 2)
        }
    except Exception as e:
        return {
            "valido": False,
            "erro": str(e),
            "tamanho_kb": round(os.path.getsize(arquivo_path) / 1024, 2)
        }

def analisar_python(arquivo_path):
    """Analisa arquivo Python e extrai metadados"""
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        linhas = conteudo.split('\n')
        linhas_codigo = [l for l in linhas if l.strip() and not l.strip().startswith('#')]
        
        # Detectar imports
        imports = [l.strip() for l in linhas if l.strip().startswith('import ') or l.strip().startswith('from ')]
        
        # Detectar funções
        funcoes = [l.strip() for l in linhas if l.strip().startswith('def ')]
        
        # Detectar classes
        classes = [l.strip() for l in linhas if l.strip().startswith('class ')]
        
        return {
            "valido": True,
            "total_linhas": len(linhas),
            "linhas_codigo": len(linhas_codigo),
            "imports": imports[:10],  # Primeiros 10 imports
            "funcoes": len(funcoes),
            "classes": len(classes),
            "tamanho_kb": round(os.path.getsize(arquivo_path) / 1024, 2)
        }
    except Exception as e:
        return {
            "valido": False,
            "erro": str(e),
            "tamanho_kb": round(os.path.getsize(arquivo_path) / 1024, 2)
        }

def determinar_importancia(caminho, nome_arquivo, metadados):
    """Determina importância do arquivo baseado em heurísticas"""
    nome_lower = nome_arquivo.lower()
    caminho_lower = caminho.lower()
    
    # Arquivos críticos (importância 5)
    if any(x in nome_lower for x in ['constants', 'heroes', 'items', 'core_v1']):
        return 5
    
    # Dados de partidas profissionais (importância 4)
    if any(x in nome_lower for x in ['pro_match', 'pro_players', 'teams']):
        return 4
    
    # Scripts de migração e análise (importância 4)
    if any(x in nome_lower for x in ['migrador', 'analisador', 'validador']):
        return 4
    
    # Dados históricos e estatísticas (importância 3)
    if any(x in nome_lower for x in ['stats', 'distributions', 'metadata', 'public_matches']):
        return 3
    
    # Relatórios e documentação (importância 2)
    if any(x in nome_lower for x in ['relatorio', 'plano', 'todo']):
        return 2
    
    # Outros arquivos (importância 1)
    return 1

def determinar_confianca(metadados, importancia):
    """Determina confiança baseada na qualidade dos dados"""
    if not metadados.get('valido', False):
        return 0.1
    
    # JSON com dados estruturados
    if 'tipo_dados' in metadados:
        if metadados['tipo_dados'] == 'array' and metadados['total_registros'] > 100:
            return 0.9
        elif metadados['tipo_dados'] == 'object' and len(metadados['campos_principais']) > 5:
            return 0.85
        else:
            return 0.7
    
    # Python com código estruturado
    if 'funcoes' in metadados:
        if metadados['funcoes'] > 5 and metadados['linhas_codigo'] > 50:
            return 0.9
        elif metadados['funcoes'] > 0:
            return 0.8
        else:
            return 0.6
    
    return 0.5

def main():
    print("🔍 ANALISANDO PROMETHEUS 2.3...")
    
    base_path = Path(".")
    catalogo = {
        "versao": "prometheus_2.3",
        "data_analise": datetime.now().isoformat(),
        "resumo": {
            "total_arquivos": 0,
            "total_json": 0,
            "total_python": 0,
            "tamanho_total_mb": 0
        },
        "arquivos_json": [],
        "arquivos_python": [],
        "estrutura_diretorios": []
    }
    
    # Mapear estrutura de diretórios
    for root, dirs, files in os.walk(base_path):
        if any(skip in root for skip in ['.git', '__pycache__', '.venv']):
            continue
            
        rel_path = os.path.relpath(root, base_path)
        if rel_path != '.':
            catalogo["estrutura_diretorios"].append(rel_path)
    
    # Analisar arquivos JSON
    print("📄 Analisando arquivos JSON...")
    for arquivo_json in base_path.rglob("*.json"):
        if any(skip in str(arquivo_json) for skip in ['.git', '__pycache__']):
            continue
            
        print(f"  📄 {arquivo_json.name}")
        
        metadados = analisar_json(arquivo_json)
        importancia = determinar_importancia(str(arquivo_json), arquivo_json.name, metadados)
        confianca = determinar_confianca(metadados, importancia)
        
        arquivo_info = {
            "nome": arquivo_json.name,
            "caminho_relativo": str(arquivo_json.relative_to(base_path)),
            "hash": calcular_hash(arquivo_json),
            "importancia": importancia,
            "confianca": confianca,
            "metadados": metadados,
            "schema": "core_v1" if metadados.get('valido', False) else "invalido"
        }
        
        catalogo["arquivos_json"].append(arquivo_info)
        catalogo["resumo"]["total_json"] += 1
        catalogo["resumo"]["tamanho_total_mb"] += metadados.get('tamanho_kb', 0) / 1024
    
    # Analisar arquivos Python
    print("🐍 Analisando arquivos Python...")
    for arquivo_py in base_path.rglob("*.py"):
        if any(skip in str(arquivo_py) for skip in ['.git', '__pycache__']):
            continue
            
        print(f"  🐍 {arquivo_py.name}")
        
        metadados = analisar_python(arquivo_py)
        importancia = determinar_importancia(str(arquivo_py), arquivo_py.name, metadados)
        confianca = determinar_confianca(metadados, importancia)
        
        arquivo_info = {
            "nome": arquivo_py.name,
            "caminho_relativo": str(arquivo_py.relative_to(base_path)),
            "hash": calcular_hash(arquivo_py),
            "importancia": importancia,
            "confianca": confianca,
            "metadados": metadados
        }
        
        catalogo["arquivos_python"].append(arquivo_info)
        catalogo["resumo"]["total_python"] += 1
        catalogo["resumo"]["tamanho_total_mb"] += metadados.get('tamanho_kb', 0) / 1024
    
    catalogo["resumo"]["total_arquivos"] = catalogo["resumo"]["total_json"] + catalogo["resumo"]["total_python"]
    catalogo["resumo"]["tamanho_total_mb"] = round(catalogo["resumo"]["tamanho_total_mb"], 2)
    
    # Salvar catálogo
    with open("catalogo_prometheus23.json", "w", encoding="utf-8") as f:
        json.dump(catalogo, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ ANÁLISE CONCLUÍDA!")
    print(f"📊 Total de arquivos: {catalogo['resumo']['total_arquivos']}")
    print(f"📄 Arquivos JSON: {catalogo['resumo']['total_json']}")
    print(f"🐍 Arquivos Python: {catalogo['resumo']['total_python']}")
    print(f"💾 Tamanho total: {catalogo['resumo']['tamanho_total_mb']} MB")
    print(f"📁 Catálogo salvo em: catalogo_prometheus23.json")

if __name__ == "__main__":
    main()

