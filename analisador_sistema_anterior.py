#!/usr/bin/env python3
"""
Analisador do Sistema Anterior para o Projeto Prometheus
Analisa arquivos JSON, Python, TXT e Models do sistema anterior
"""

import os
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess

class AnalisadorSistemaAnterior:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.data_atual = datetime.now().strftime("%Y-%m-%d")
        self.sistema_anterior = {}
        
    def obter_tamanho_mb(self, caminho: Path) -> float:
        """Obtém tamanho em MB de um diretório"""
        try:
            result = subprocess.run(['du', '-sm', str(caminho)], 
                                  capture_output=True, text=True)
            return float(result.stdout.split()[0])
        except:
            return 0.0
    
    def analisar_arquivos_json(self, caminho: Path) -> Dict[str, Any]:
        """Analisa arquivos JSON do sistema anterior"""
        json_files = list(caminho.rglob('*.json'))
        
        # Categorizar JSONs por tipo
        categorias = {
            'matches': [],
            'heroes': [],
            'teams': [],
            'leagues': [],
            'stats': [],
            'config': [],
            'outros': []
        }
        
        for json_file in json_files:
            nome = json_file.name.lower()
            if 'match' in nome or 'partida' in nome:
                categorias['matches'].append(json_file.name)
            elif 'hero' in nome or 'heroi' in nome:
                categorias['heroes'].append(json_file.name)
            elif 'team' in nome or 'time' in nome:
                categorias['teams'].append(json_file.name)
            elif 'league' in nome or 'liga' in nome:
                categorias['leagues'].append(json_file.name)
            elif 'stat' in nome or 'estatistica' in nome:
                categorias['stats'].append(json_file.name)
            elif 'config' in nome or 'secret' in nome:
                categorias['config'].append(json_file.name)
            else:
                categorias['outros'].append(json_file.name)
        
        # Analisar alguns JSONs importantes
        dados_importantes = {}
        for json_file in json_files[:5]:  # Primeiros 5 arquivos
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        dados_importantes[json_file.name] = {
                            'tipo': 'array',
                            'total_registros': len(data),
                            'exemplo_keys': list(data[0].keys()) if data and isinstance(data[0], dict) else []
                        }
                    elif isinstance(data, dict):
                        dados_importantes[json_file.name] = {
                            'tipo': 'object',
                            'keys_principais': list(data.keys())[:10]
                        }
            except:
                dados_importantes[json_file.name] = {'tipo': 'erro_leitura'}
        
        return {
            'total_arquivos': len(json_files),
            'categorias': categorias,
            'dados_importantes': dados_importantes,
            'tamanho_mb': self.obter_tamanho_mb(caminho)
        }
    
    def analisar_arquivos_python(self, caminho: Path) -> Dict[str, Any]:
        """Analisa arquivos Python do sistema anterior"""
        py_files = list(caminho.rglob('*.py'))
        
        # Categorizar por funcionalidade
        categorias = {
            'analysis': [],
            'data_processing': [],
            'visualization': [],
            'modeling': [],
            'utils': [],
            'outros': []
        }
        
        for py_file in py_files:
            nome = py_file.name.lower()
            if 'analy' in nome or 'analise' in nome:
                categorias['analysis'].append(py_file.name)
            elif 'data' in nome or 'process' in nome or 'load' in nome:
                categorias['data_processing'].append(py_file.name)
            elif 'visual' in nome or 'plot' in nome or 'chart' in nome:
                categorias['visualization'].append(py_file.name)
            elif 'model' in nome or 'predict' in nome or 'train' in nome:
                categorias['modeling'].append(py_file.name)
            elif 'util' in nome or 'helper' in nome:
                categorias['utils'].append(py_file.name)
            else:
                categorias['outros'].append(py_file.name)
        
        return {
            'total_arquivos': len(py_files),
            'categorias': categorias,
            'tamanho_mb': self.obter_tamanho_mb(caminho)
        }
    
    def analisar_arquivos_txt(self, caminho: Path) -> Dict[str, Any]:
        """Analisa arquivos TXT do sistema anterior"""
        txt_files = list(caminho.rglob('*.txt'))
        
        # Categorizar por tipo de análise
        categorias = {
            'analysis_results': [],
            'hypotheses': [],
            'summaries': [],
            'stats': [],
            'outros': []
        }
        
        for txt_file in txt_files:
            nome = txt_file.name.lower()
            if 'analysis' in nome or 'analise' in nome:
                categorias['analysis_results'].append(txt_file.name)
            elif 'hypothesis' in nome or 'hipotese' in nome:
                categorias['hypotheses'].append(txt_file.name)
            elif 'summary' in nome or 'resumo' in nome:
                categorias['summaries'].append(txt_file.name)
            elif 'stat' in nome or 'rate' in nome:
                categorias['stats'].append(txt_file.name)
            else:
                categorias['outros'].append(txt_file.name)
        
        return {
            'total_arquivos': len(txt_files),
            'categorias': categorias,
            'tamanho_mb': self.obter_tamanho_mb(caminho)
        }
    
    def analisar_models(self, caminho: Path) -> Dict[str, Any]:
        """Analisa modelos de machine learning"""
        model_files = list(caminho.rglob('*.pkl'))
        
        # Categorizar modelos
        categorias = {
            'regression': [],
            'ensemble': [],
            'preprocessing': [],
            'optimized': [],
            'outros': []
        }
        
        for model_file in model_files:
            nome = model_file.name.lower()
            if 'regression' in nome or 'ridge' in nome or 'lasso' in nome or 'elastic' in nome:
                categorias['regression'].append(model_file.name)
            elif 'forest' in nome or 'gradient' in nome or 'boosting' in nome:
                categorias['ensemble'].append(model_file.name)
            elif 'scaler' in nome or 'preprocess' in nome:
                categorias['preprocessing'].append(model_file.name)
            elif 'optimized' in nome or 'best' in nome:
                categorias['optimized'].append(model_file.name)
            else:
                categorias['outros'].append(model_file.name)
        
        # Tentar carregar informações dos modelos
        model_info = {}
        for model_file in model_files[:3]:  # Primeiros 3 modelos
            try:
                with open(model_file, 'rb') as f:
                    model = pickle.load(f)
                    model_info[model_file.name] = {
                        'tipo': type(model).__name__,
                        'tamanho_bytes': model_file.stat().st_size
                    }
            except:
                model_info[model_file.name] = {'tipo': 'erro_carregamento'}
        
        return {
            'total_arquivos': len(model_files),
            'categorias': categorias,
            'model_info': model_info,
            'tamanho_mb': self.obter_tamanho_mb(caminho)
        }
    
    def calcular_importancia_sistema_anterior(self, tipo: str, total_arquivos: int) -> int:
        """Calcula importância baseada no tipo e quantidade"""
        if tipo == 'json' and total_arquivos > 50:
            return 5  # Dados críticos
        elif tipo == 'models' and total_arquivos > 10:
            return 4  # Modelos treinados
        elif tipo == 'python' and total_arquivos > 100:
            return 4  # Código extenso
        elif tipo == 'txt' and total_arquivos > 30:
            return 3  # Análises documentadas
        else:
            return 2
    
    def calcular_confianca_sistema_anterior(self, tipo: str, categorias: Dict) -> float:
        """Calcula confiança baseada na organização e categorização"""
        if tipo == 'json':
            # Mais categorias organizadas = maior confiança
            cats_com_dados = sum(1 for cat in categorias.values() if cat)
            return min(0.9, 0.5 + (cats_com_dados * 0.1))
        elif tipo == 'models':
            # Modelos otimizados = maior confiança
            if categorias.get('optimized'):
                return 0.85
            return 0.75
        elif tipo == 'python':
            # Código categorizado = maior confiança
            cats_com_dados = sum(1 for cat in categorias.values() if cat)
            return min(0.8, 0.4 + (cats_com_dados * 0.1))
        else:
            return 0.7
    
    def analisar_sistema_completo(self) -> Dict[str, Any]:
        """Analisa todo o sistema anterior"""
        resultados = {}
        
        # Analisar cada tipo de arquivo
        for subdir in self.base_dir.iterdir():
            if subdir.is_dir():
                nome = subdir.name
                
                if 'JSON' in nome:
                    print(f"Analisando arquivos JSON...")
                    analise = self.analisar_arquivos_json(subdir)
                    resultados['json'] = {
                        'id': 'sistema_anterior_json',
                        'tipo': 'dados_json',
                        'descricao': f"Dados JSON do sistema anterior ({analise['total_arquivos']} arquivos)",
                        'origem': 'sistema_anterior',
                        'tamanho_mb': analise['tamanho_mb'],
                        'arquivos_totais': analise['total_arquivos'],
                        'categorias': analise['categorias'],
                        'dados_importantes': analise['dados_importantes'],
                        'importancia': self.calcular_importancia_sistema_anterior('json', analise['total_arquivos']),
                        'confianca': self.calcular_confianca_sistema_anterior('json', analise['categorias']),
                        'schema': 'sistema_anterior_v1',
                        'data_analise': self.data_atual
                    }
                
                elif 'Python' in nome:
                    print(f"Analisando arquivos Python...")
                    analise = self.analisar_arquivos_python(subdir)
                    resultados['python'] = {
                        'id': 'sistema_anterior_python',
                        'tipo': 'codigo_python',
                        'descricao': f"Código Python do sistema anterior ({analise['total_arquivos']} arquivos)",
                        'origem': 'sistema_anterior',
                        'tamanho_mb': analise['tamanho_mb'],
                        'arquivos_totais': analise['total_arquivos'],
                        'categorias': analise['categorias'],
                        'importancia': self.calcular_importancia_sistema_anterior('python', analise['total_arquivos']),
                        'confianca': self.calcular_confianca_sistema_anterior('python', analise['categorias']),
                        'schema': 'sistema_anterior_v1',
                        'data_analise': self.data_atual
                    }
                
                elif 'TXT' in nome:
                    print(f"Analisando arquivos TXT...")
                    analise = self.analisar_arquivos_txt(subdir)
                    resultados['txt'] = {
                        'id': 'sistema_anterior_txt',
                        'tipo': 'documentacao_analises',
                        'descricao': f"Documentação e análises do sistema anterior ({analise['total_arquivos']} arquivos)",
                        'origem': 'sistema_anterior',
                        'tamanho_mb': analise['tamanho_mb'],
                        'arquivos_totais': analise['total_arquivos'],
                        'categorias': analise['categorias'],
                        'importancia': self.calcular_importancia_sistema_anterior('txt', analise['total_arquivos']),
                        'confianca': self.calcular_confianca_sistema_anterior('txt', analise['categorias']),
                        'schema': 'sistema_anterior_v1',
                        'data_analise': self.data_atual
                    }
                
                elif 'models' in nome:
                    print(f"Analisando modelos...")
                    analise = self.analisar_models(subdir)
                    resultados['models'] = {
                        'id': 'sistema_anterior_models',
                        'tipo': 'modelos_ml',
                        'descricao': f"Modelos de ML do sistema anterior ({analise['total_arquivos']} arquivos)",
                        'origem': 'sistema_anterior',
                        'tamanho_mb': analise['tamanho_mb'],
                        'arquivos_totais': analise['total_arquivos'],
                        'categorias': analise['categorias'],
                        'model_info': analise['model_info'],
                        'importancia': self.calcular_importancia_sistema_anterior('models', analise['total_arquivos']),
                        'confianca': self.calcular_confianca_sistema_anterior('models', analise['categorias']),
                        'schema': 'sistema_anterior_v1',
                        'data_analise': self.data_atual
                    }
        
        return resultados

def main():
    analisador = AnalisadorSistemaAnterior('/home/ubuntu/analise_arquivos/sistema_anterior')
    
    print("🔍 Iniciando análise do sistema anterior...")
    resultados = analisador.analisar_sistema_completo()
    
    # Salvar resultados
    output_file = '/home/ubuntu/analise_arquivos/analise_sistema_anterior.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Análise do sistema anterior concluída!")
    print(f"📊 Componentes analisados: {len(resultados)}")
    
    total_arquivos = sum(r['arquivos_totais'] for r in resultados.values())
    total_tamanho = sum(r['tamanho_mb'] for r in resultados.values())
    
    print(f"📁 Total de arquivos: {total_arquivos}")
    print(f"💾 Tamanho total: {total_tamanho} MB")
    print(f"💾 Arquivo salvo: {output_file}")

if __name__ == "__main__":
    main()

