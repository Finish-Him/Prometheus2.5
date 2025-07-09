#!/usr/bin/env python3
"""
Validador Final da Migração JSON - Projeto Prometheus
Verifica integridade, qualidade e estatísticas dos dados migrados
"""

import json
import os
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
import jsonschema
from datetime import datetime

def carregar_schema():
    """Carrega o schema core_v1 para validação"""
    try:
        with open('schemas/core_v1.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  Schema core_v1.json não encontrado, pulando validação de schema")
        return None

def validar_arquivo_json(caminho_arquivo, schema=None):
    """Valida um arquivo JSON individual"""
    resultado = {
        'arquivo': str(caminho_arquivo),
        'valido': False,
        'tamanho_bytes': 0,
        'schema_valido': False,
        'tem_metadados': False,
        'data_type': None,
        'source': None,
        'confidence': None,
        'importance': None,
        'erros': []
    }
    
    try:
        # Verificar tamanho do arquivo
        resultado['tamanho_bytes'] = caminho_arquivo.stat().st_size
        
        # Carregar JSON
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        resultado['valido'] = True
        
        # Verificar campos obrigatórios
        if 'schema_version' in dados:
            resultado['schema_valido'] = dados.get('schema_version') == 'core_v1'
        
        if 'metadata' in dados:
            resultado['tem_metadados'] = True
        
        resultado['data_type'] = dados.get('data_type')
        resultado['source'] = dados.get('source')
        resultado['confidence'] = dados.get('confidence')
        resultado['importance'] = dados.get('importance')
        
        # Validar contra schema se disponível
        if schema:
            try:
                jsonschema.validate(dados, schema)
                resultado['schema_valido'] = True
            except jsonschema.ValidationError as e:
                resultado['erros'].append(f"Schema inválido: {e.message}")
        
    except json.JSONDecodeError as e:
        resultado['erros'].append(f"JSON inválido: {e}")
    except Exception as e:
        resultado['erros'].append(f"Erro geral: {e}")
    
    return resultado

def gerar_estatisticas(resultados):
    """Gera estatísticas detalhadas da validação"""
    stats = {
        'total_arquivos': len(resultados),
        'arquivos_validos': 0,
        'arquivos_com_schema': 0,
        'arquivos_com_metadados': 0,
        'tamanho_total_mb': 0,
        'por_data_type': Counter(),
        'por_source': Counter(),
        'por_importance': Counter(),
        'confidence_media': 0,
        'arquivos_com_erros': 0,
        'erros_unicos': set()
    }
    
    confidences = []
    
    for resultado in resultados:
        if resultado['valido']:
            stats['arquivos_validos'] += 1
        
        if resultado['schema_valido']:
            stats['arquivos_com_schema'] += 1
        
        if resultado['tem_metadados']:
            stats['arquivos_com_metadados'] += 1
        
        stats['tamanho_total_mb'] += resultado['tamanho_bytes'] / (1024 * 1024)
        
        if resultado['data_type']:
            stats['por_data_type'][resultado['data_type']] += 1
        
        if resultado['source']:
            stats['por_source'][resultado['source']] += 1
        
        if resultado['importance']:
            stats['por_importance'][resultado['importance']] += 1
        
        if resultado['confidence']:
            confidences.append(resultado['confidence'])
        
        if resultado['erros']:
            stats['arquivos_com_erros'] += 1
            for erro in resultado['erros']:
                stats['erros_unicos'].add(erro)
    
    if confidences:
        stats['confidence_media'] = sum(confidences) / len(confidences)
    
    return stats

def main():
    """Função principal de validação"""
    print("🔍 Iniciando Validação Final da Migração JSON - Projeto Prometheus")
    print("=" * 70)
    
    # Carregar schema
    schema = carregar_schema()
    
    # Encontrar todos os arquivos JSON
    data_dir = Path('data')
    if not data_dir.exists():
        print("❌ Diretório 'data' não encontrado!")
        return
    
    arquivos_json = list(data_dir.rglob('*.json'))
    print(f"📁 Encontrados {len(arquivos_json)} arquivos JSON para validação")
    
    # Validar cada arquivo
    resultados = []
    print("\n🔄 Validando arquivos...")
    
    for i, arquivo in enumerate(arquivos_json, 1):
        print(f"  [{i:2d}/{len(arquivos_json)}] {arquivo.name}", end="")
        resultado = validar_arquivo_json(arquivo, schema)
        resultados.append(resultado)
        
        if resultado['valido']:
            print(" ✅")
        else:
            print(" ❌")
    
    # Gerar estatísticas
    print("\n📊 Gerando estatísticas...")
    stats = gerar_estatisticas(resultados)
    
    # Exibir relatório
    print("\n" + "=" * 70)
    print("📋 RELATÓRIO DE VALIDAÇÃO FINAL")
    print("=" * 70)
    
    print(f"📁 Total de arquivos: {stats['total_arquivos']}")
    print(f"✅ Arquivos válidos: {stats['arquivos_validos']} ({stats['arquivos_validos']/stats['total_arquivos']*100:.1f}%)")
    print(f"🔧 Com schema core_v1: {stats['arquivos_com_schema']} ({stats['arquivos_com_schema']/stats['total_arquivos']*100:.1f}%)")
    print(f"📋 Com metadados: {stats['arquivos_com_metadados']} ({stats['arquivos_com_metadados']/stats['total_arquivos']*100:.1f}%)")
    print(f"💾 Tamanho total: {stats['tamanho_total_mb']:.2f} MB")
    print(f"🎯 Confiança média: {stats['confidence_media']:.3f}")
    print(f"❌ Arquivos com erros: {stats['arquivos_com_erros']}")
    
    print("\n📊 DISTRIBUIÇÃO POR CATEGORIA:")
    print("-" * 40)
    for data_type, count in stats['por_data_type'].most_common():
        print(f"  {data_type}: {count} arquivos")
    
    print("\n📊 DISTRIBUIÇÃO POR FONTE:")
    print("-" * 40)
    for source, count in stats['por_source'].most_common():
        print(f"  {source}: {count} arquivos")
    
    print("\n📊 DISTRIBUIÇÃO POR IMPORTÂNCIA:")
    print("-" * 40)
    for importance, count in stats['por_importance'].most_common():
        print(f"  Nível {importance}: {count} arquivos")
    
    if stats['erros_unicos']:
        print("\n⚠️  ERROS ENCONTRADOS:")
        print("-" * 40)
        for erro in sorted(stats['erros_unicos']):
            print(f"  • {erro}")
    
    # Salvar relatório detalhado
    relatorio_detalhado = {
        'timestamp': datetime.now().isoformat(),
        'estatisticas': stats,
        'arquivos_detalhados': resultados
    }
    
    with open('relatorio_validacao_detalhado.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio_detalhado, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Relatório detalhado salvo em: relatorio_validacao_detalhado.json")
    
    # Status final
    if stats['arquivos_com_erros'] == 0:
        print("\n🎉 MIGRAÇÃO VALIDADA COM SUCESSO!")
        print("   Todos os arquivos estão íntegros e prontos para uso.")
    else:
        print(f"\n⚠️  MIGRAÇÃO CONCLUÍDA COM {stats['arquivos_com_erros']} ARQUIVOS COM PROBLEMAS")
        print("   Verifique os erros acima e corrija se necessário.")
    
    print("\n🚀 Projeto Prometheus pronto para a próxima fase!")

if __name__ == "__main__":
    main()

