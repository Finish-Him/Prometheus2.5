#!/usr/bin/env python3
"""
Analisador de Repositórios para o Projeto Prometheus
Gera dicionário global JSON com metadados de todos os repositórios
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess

class AnalisadorRepositorios:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.repositorios = {}
        self.data_atual = datetime.now().strftime("%Y-%m-%d")
        
    def calcular_hash_arquivo(self, caminho: Path) -> str:
        """Calcula hash MD5 de um arquivo"""
        try:
            with open(caminho, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return "erro_hash"
    
    def obter_tamanho_mb(self, caminho: Path) -> float:
        """Obtém tamanho em MB de um diretório"""
        try:
            result = subprocess.run(['du', '-sm', str(caminho)], 
                                  capture_output=True, text=True)
            return float(result.stdout.split()[0])
        except:
            return 0.0
    
    def contar_arquivos_por_tipo(self, caminho: Path) -> Dict[str, int]:
        """Conta arquivos por extensão"""
        contadores = {
            'json': 0, 'py': 0, 'js': 0, 'ts': 0, 'md': 0, 
            'txt': 0, 'csv': 0, 'parquet': 0, 'proto': 0,
            'pdf': 0, 'zip': 0, 'outros': 0
        }
        
        for arquivo in caminho.rglob('*'):
            if arquivo.is_file():
                ext = arquivo.suffix.lower().lstrip('.')
                if ext in contadores:
                    contadores[ext] += 1
                else:
                    contadores['outros'] += 1
                    
        return contadores
    
    def identificar_tipo_repositorio(self, nome: str, contadores: Dict[str, int]) -> str:
        """Identifica o tipo do repositório baseado no nome e conteúdo"""
        nome_lower = nome.lower()
        
        if 'constants' in nome_lower:
            return 'constantes'
        elif 'protobufs' in nome_lower:
            return 'protos'
        elif 'gametracking' in nome_lower:
            return 'arquivos_jogo'
        elif 'extractor' in nome_lower:
            return 'codigo_extracao'
        elif 'data' in nome_lower and contadores['parquet'] > 0:
            return 'dataset'
        elif 'analysis' in nome_lower or 'prometheus' in nome_lower:
            return 'projeto_analise'
        elif contadores['py'] > contadores['js']:
            return 'codigo_python'
        elif contadores['js'] > 0 or contadores['ts'] > 0:
            return 'codigo_javascript'
        elif contadores['md'] > 5:
            return 'documentacao'
        else:
            return 'misto'
    
    def calcular_importancia(self, tipo: str, contadores: Dict[str, int], tamanho_mb: float) -> int:
        """Calcula importância de 1-5 baseado no tipo e conteúdo"""
        if tipo == 'constantes':
            return 5  # Fundamental para o jogo
        elif tipo == 'protos':
            return 4  # Importante para comunicação
        elif tipo == 'dataset':
            return 4  # Dados de treinamento
        elif tipo == 'projeto_analise':
            return 3  # Código de análise
        elif tipo == 'codigo_extracao':
            return 3  # Scripts de extração
        elif tipo == 'arquivos_jogo':
            return 2  # Arquivos auxiliares
        else:
            return 2  # Outros
    
    def calcular_confianca(self, tipo: str, contadores: Dict[str, int]) -> float:
        """Calcula confiança de 0.0-1.0 baseado na qualidade dos dados"""
        if tipo == 'constantes' and contadores['json'] > 10:
            return 0.95
        elif tipo == 'protos':
            return 0.90
        elif tipo == 'dataset' and contadores['parquet'] > 0:
            return 0.85
        elif contadores['py'] > 5:
            return 0.80
        elif contadores['md'] > 0:
            return 0.75
        else:
            return 0.70
    
    def analisar_repositorio(self, caminho: Path) -> Dict[str, Any]:
        """Analisa um repositório específico"""
        nome = caminho.name
        contadores = self.contar_arquivos_por_tipo(caminho)
        tamanho_mb = self.obter_tamanho_mb(caminho)
        tipo = self.identificar_tipo_repositorio(nome, contadores)
        importancia = self.calcular_importancia(tipo, contadores, tamanho_mb)
        confianca = self.calcular_confianca(tipo, contadores)
        
        # Obter diretórios principais
        top_dirs = []
        try:
            for item in caminho.iterdir():
                if item.is_dir():
                    top_dirs.append(item.name)
        except:
            pass
        
        # Contar arquivos totais
        total_arquivos = sum(contadores.values())
        
        return {
            "id": nome,
            "tipo": tipo,
            "descricao": self.gerar_descricao(nome, tipo, contadores),
            "origem": "upload",
            "tamanho_mb": tamanho_mb,
            "arquivos_totais": total_arquivos,
            "arquivos_json": contadores['json'],
            "arquivos_py": contadores['py'],
            "arquivos_js": contadores['js'],
            "arquivos_ts": contadores['ts'],
            "arquivos_md": contadores['md'],
            "arquivos_parquet": contadores['parquet'],
            "arquivos_proto": contadores['proto'],
            "top_dirs": top_dirs[:5],  # Primeiros 5 diretórios
            "importancia": importancia,
            "confianca": confianca,
            "schema": "core_v1" if contadores['json'] > 0 else "n/a",
            "data_analise": self.data_atual
        }
    
    def gerar_descricao(self, nome: str, tipo: str, contadores: Dict[str, int]) -> str:
        """Gera descrição baseada no tipo e conteúdo"""
        descricoes = {
            'constantes': f"Constantes do jogo Dota 2 ({contadores['json']} JSONs)",
            'protos': f"Definições Protocol Buffers ({contadores['proto']} arquivos .proto)",
            'arquivos_jogo': f"Arquivos de rastreamento do jogo ({contadores['outros']} arquivos)",
            'codigo_extracao': f"Scripts de extração de dados ({contadores['py']} Python, {contadores['js']} JS)",
            'dataset': f"Dataset de partidas ({contadores['parquet']} parquet, {contadores['json']} JSON)",
            'projeto_analise': f"Projeto de análise principal ({contadores['py']} Python)",
            'codigo_python': f"Código Python ({contadores['py']} arquivos .py)",
            'codigo_javascript': f"Código JavaScript/TypeScript ({contadores['js']} JS, {contadores['ts']} TS)",
            'documentacao': f"Documentação ({contadores['md']} Markdown)",
            'misto': f"Repositório misto ({sum(contadores.values())} arquivos)"
        }
        return descricoes.get(tipo, f"Repositório {nome}")
    
    def analisar_todos_repositorios(self) -> Dict[str, Any]:
        """Analisa todos os repositórios no diretório base"""
        repositorios_analisados = []
        
        for item in self.base_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                print(f"Analisando: {item.name}")
                analise = self.analisar_repositorio(item)
                repositorios_analisados.append(analise)
        
        # Ordenar por importância (decrescente) e depois por confiança
        repositorios_analisados.sort(
            key=lambda x: (x['importancia'], x['confianca']), 
            reverse=True
        )
        
        # Criar dicionário global
        dicionario_global = {
            "projeto": "Prometheus",
            "versao": "1.1",
            "data_analise": self.data_atual,
            "total_repositorios": len(repositorios_analisados),
            "schema_version": "core_v1",
            "repositorios": repositorios_analisados,
            "resumo": self.gerar_resumo(repositorios_analisados)
        }
        
        return dicionario_global
    
    def gerar_resumo(self, repositorios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera resumo estatístico dos repositórios"""
        total_arquivos = sum(r['arquivos_totais'] for r in repositorios)
        total_tamanho = sum(r['tamanho_mb'] for r in repositorios)
        total_json = sum(r['arquivos_json'] for r in repositorios)
        total_python = sum(r['arquivos_py'] for r in repositorios)
        
        tipos = {}
        for repo in repositorios:
            tipo = repo['tipo']
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return {
            "total_arquivos": total_arquivos,
            "total_tamanho_mb": round(total_tamanho, 2),
            "total_json": total_json,
            "total_python": total_python,
            "tipos_repositorio": tipos,
            "importancia_media": round(sum(r['importancia'] for r in repositorios) / len(repositorios), 2),
            "confianca_media": round(sum(r['confianca'] for r in repositorios) / len(repositorios), 2)
        }

def main():
    analisador = AnalisadorRepositorios('/home/ubuntu/analise_arquivos')
    
    print("🔍 Iniciando análise dos repositórios...")
    dicionario_global = analisador.analisar_todos_repositorios()
    
    # Salvar JSON
    output_file = '/home/ubuntu/analise_arquivos/dicionario_global_repositorios.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dicionario_global, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Análise concluída! Arquivo salvo: {output_file}")
    print(f"📊 Total de repositórios analisados: {dicionario_global['total_repositorios']}")
    print(f"📁 Total de arquivos: {dicionario_global['resumo']['total_arquivos']}")
    print(f"💾 Tamanho total: {dicionario_global['resumo']['total_tamanho_mb']} MB")

if __name__ == "__main__":
    main()

