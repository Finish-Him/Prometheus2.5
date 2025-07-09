#!/usr/bin/env python3
"""
Migrador Principal - Projeto Prometheus
Converte todos os dados para JSON padronizado schema core_v1
"""

import json
import hashlib
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import jsonschema
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/prometheus_migration/logs/migration.log'),
        logging.StreamHandler()
    ]
)

class MigradorPrometheus:
    def __init__(self, base_dir: str = "/home/ubuntu/prometheus_migration"):
        self.base_dir = Path(base_dir)
        self.timestamp = datetime.now().isoformat()
        self.schema_core_v1 = self.carregar_schema()
        self.stats = {
            'total_processados': 0,
            'total_migrados': 0,
            'total_erros': 0,
            'por_tipo': {}
        }
        
    def carregar_schema(self) -> Dict:
        """Carrega o schema core_v1"""
        schema_path = self.base_dir / "schemas" / "core_v1.json"
        with open(schema_path, 'r') as f:
            return json.load(f)
    
    def calcular_hash(self, data: Any) -> str:
        """Calcula hash MD5 dos dados"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def determinar_tipo_dados(self, nome_arquivo: str) -> str:
        """Determina o tipo de dados baseado no nome do arquivo"""
        nome = nome_arquivo.lower()
        
        if any(x in nome for x in ['match', 'partida', 'game']):
            return 'match'
        elif any(x in nome for x in ['hero', 'heroi']):
            return 'hero'
        elif any(x in nome for x in ['item', 'items']):
            return 'item'
        elif any(x in nome for x in ['team', 'time', 'equipe']):
            return 'team'
        elif any(x in nome for x in ['league', 'liga', 'tournament']):
            return 'league'
        elif any(x in nome for x in ['player', 'jogador']):
            return 'player'
        elif any(x in nome for x in ['analysis', 'analise', 'stats', 'estatistica']):
            return 'analysis'
        elif any(x in nome for x in ['model', 'modelo']):
            return 'model'
        else:
            return 'constant'
    
    def calcular_importancia(self, data_type: str, tamanho: int = 0) -> int:
        """Calcula importância baseada no tipo e tamanho"""
        importancia_base = {
            'constant': 5,
            'match': 4,
            'hero': 4,
            'item': 4,
            'team': 3,
            'league': 3,
            'player': 3,
            'model': 4,
            'analysis': 2
        }
        
        base = importancia_base.get(data_type, 2)
        
        # Ajustar baseado no tamanho
        if tamanho > 100000:  # Arquivos grandes
            return min(5, base + 1)
        elif tamanho < 1000:  # Arquivos pequenos
            return max(1, base - 1)
        
        return base
    
    def calcular_confianca(self, source: str, data_type: str) -> float:
        """Calcula confiança baseada na origem e tipo"""
        confianca_source = {
            'dotaconstants': 0.95,
            'opendota_api': 0.90,
            'gametracking': 0.85,
            'sistema_anterior': 0.75,
            'protobufs': 0.90,
            'manual': 0.60
        }
        
        confianca_tipo = {
            'constant': 0.95,
            'match': 0.85,
            'hero': 0.90,
            'item': 0.90,
            'team': 0.80,
            'league': 0.80,
            'player': 0.75,
            'model': 0.80,
            'analysis': 0.70
        }
        
        conf_source = confianca_source.get(source, 0.50)
        conf_tipo = confianca_tipo.get(data_type, 0.50)
        
        return round((conf_source + conf_tipo) / 2, 2)
    
    def validar_dados(self, dados_migrados: Dict) -> bool:
        """Valida dados contra schema core_v1"""
        try:
            jsonschema.validate(dados_migrados, self.schema_core_v1)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logging.error(f"Erro de validação: {e}")
            return False
    
    def migrar_arquivo_json(self, arquivo_origem: Path, source: str, destino_dir: Path) -> bool:
        """Migra um arquivo JSON individual"""
        try:
            with open(arquivo_origem, 'r', encoding='utf-8') as f:
                data_original = json.load(f)
            
            # Determinar tipo e calcular métricas
            data_type = self.determinar_tipo_dados(arquivo_origem.name)
            tamanho = arquivo_origem.stat().st_size
            hash_dados = self.calcular_hash(data_original)
            
            # Contar registros se for lista
            records_count = len(data_original) if isinstance(data_original, list) else 1
            
            # Criar estrutura migrada
            dados_migrados = {
                "schema_version": "core_v1",
                "data_type": data_type,
                "source": source,
                "timestamp": self.timestamp,
                "confidence": self.calcular_confianca(source, data_type),
                "importance": self.calcular_importancia(data_type, tamanho),
                "validation_status": "pending",
                "metadata": {
                    "origin_file": arquivo_origem.name,
                    "collection": data_type,
                    "hash": hash_dados,
                    "size_bytes": tamanho,
                    "records_count": records_count
                },
                "data": data_original
            }
            
            # Validar
            if self.validar_dados(dados_migrados):
                dados_migrados["validation_status"] = "passed"
            else:
                dados_migrados["validation_status"] = "failed"
                logging.warning(f"Validação falhou para {arquivo_origem.name}")
            
            # Salvar arquivo migrado
            destino_dir.mkdir(parents=True, exist_ok=True)
            nome_arquivo = f"{arquivo_origem.stem}_{hash_dados[:8]}.json"
            arquivo_destino = destino_dir / nome_arquivo
            
            with open(arquivo_destino, 'w', encoding='utf-8') as f:
                json.dump(dados_migrados, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Migrado: {arquivo_origem.name} -> {arquivo_destino}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao migrar {arquivo_origem}: {e}")
            return False
    
    def migrar_dotaconstants(self) -> int:
        """Migra arquivos do dotaconstants-master"""
        logging.info("Iniciando migração dotaconstants...")
        origem = Path("/home/ubuntu/analise_arquivos/dotaconstants-master/dotaconstants-master/build")
        destino = self.base_dir / "data" / "constants"
        
        migrados = 0
        for json_file in origem.glob("*.json"):
            if self.migrar_arquivo_json(json_file, "dotaconstants", destino):
                migrados += 1
        
        logging.info(f"Dotaconstants: {migrados} arquivos migrados")
        return migrados
    
    def migrar_sistema_anterior_json(self) -> int:
        """Migra JSONs do sistema anterior"""
        logging.info("Iniciando migração sistema anterior...")
        origem = Path("/home/ubuntu/analise_arquivos/sistema_anterior")
        migrados = 0
        
        for json_file in origem.rglob("*.json"):
            # Pular arquivos sensíveis
            if 'client_secret' in json_file.name or 'secret' in json_file.name:
                continue
            
            # Determinar diretório de destino baseado no tipo
            data_type = self.determinar_tipo_dados(json_file.name)
            destino = self.base_dir / "data" / data_type
            
            if self.migrar_arquivo_json(json_file, "sistema_anterior", destino):
                migrados += 1
        
        logging.info(f"Sistema anterior: {migrados} arquivos migrados")
        return migrados
    
    def migrar_modelos_ml(self) -> int:
        """Migra modelos de machine learning"""
        logging.info("Iniciando migração modelos ML...")
        origem = Path("/home/ubuntu/analise_arquivos/sistema_anterior")
        destino = self.base_dir / "data" / "models"
        migrados = 0
        
        for pkl_file in origem.rglob("*.pkl"):
            try:
                # Tentar carregar modelo para extrair metadados
                with open(pkl_file, 'rb') as f:
                    model = pickle.load(f)
                
                # Criar metadados do modelo
                model_metadata = {
                    "model_type": type(model).__name__,
                    "file_size": pkl_file.stat().st_size,
                    "file_name": pkl_file.name,
                    "attributes": []
                }
                
                # Tentar extrair atributos do modelo
                if hasattr(model, 'get_params'):
                    try:
                        model_metadata["parameters"] = model.get_params()
                    except:
                        pass
                
                if hasattr(model, 'feature_names_in_'):
                    try:
                        model_metadata["features"] = list(model.feature_names_in_)
                    except:
                        pass
                
                # Criar estrutura migrada
                hash_dados = hashlib.md5(pkl_file.read_bytes()).hexdigest()
                
                dados_migrados = {
                    "schema_version": "core_v1",
                    "data_type": "model",
                    "source": "sistema_anterior",
                    "timestamp": self.timestamp,
                    "confidence": 0.80,
                    "importance": 4,
                    "validation_status": "passed",
                    "metadata": {
                        "origin_file": pkl_file.name,
                        "collection": "models",
                        "hash": hash_dados,
                        "size_bytes": pkl_file.stat().st_size,
                        "records_count": 1
                    },
                    "data": model_metadata
                }
                
                # Salvar metadados do modelo
                destino.mkdir(parents=True, exist_ok=True)
                nome_arquivo = f"{pkl_file.stem}_metadata_{hash_dados[:8]}.json"
                arquivo_destino = destino / nome_arquivo
                
                with open(arquivo_destino, 'w', encoding='utf-8') as f:
                    json.dump(dados_migrados, f, indent=2, ensure_ascii=False)
                
                logging.info(f"Modelo migrado: {pkl_file.name} -> {arquivo_destino}")
                migrados += 1
                
            except Exception as e:
                logging.error(f"Erro ao migrar modelo {pkl_file}: {e}")
        
        logging.info(f"Modelos ML: {migrados} arquivos migrados")
        return migrados
    
    def migrar_outros_repositorios(self) -> int:
        """Migra outros repositórios importantes"""
        logging.info("Iniciando migração outros repositórios...")
        base_analise = Path("/home/ubuntu/analise_arquivos")
        migrados = 0
        
        # Repositórios para migrar
        repos_importantes = [
            ("opendota_data", "opendota_api"),
            ("open-dota-master", "opendota_api"),
            ("opendota_analysis_project", "sistema_anterior")
        ]
        
        for repo_dir, source in repos_importantes:
            repo_path = base_analise / repo_dir
            if repo_path.exists():
                for json_file in repo_path.rglob("*.json"):
                    data_type = self.determinar_tipo_dados(json_file.name)
                    destino = self.base_dir / "data" / data_type
                    
                    if self.migrar_arquivo_json(json_file, source, destino):
                        migrados += 1
        
        logging.info(f"Outros repositórios: {migrados} arquivos migrados")
        return migrados
    
    def gerar_metadados_colecoes(self):
        """Gera metadados para cada coleção"""
        logging.info("Gerando metadados das coleções...")
        
        data_dir = self.base_dir / "data"
        meta_dir = self.base_dir / "meta"
        meta_dir.mkdir(exist_ok=True)
        
        for colecao_dir in data_dir.iterdir():
            if colecao_dir.is_dir():
                colecao = colecao_dir.name
                arquivos = list(colecao_dir.glob("*.json"))
                
                if arquivos:
                    # Calcular estatísticas
                    total_arquivos = len(arquivos)
                    total_bytes = sum(f.stat().st_size for f in arquivos)
                    
                    # Analisar primeiro arquivo para extrair info
                    with open(arquivos[0], 'r') as f:
                        sample = json.load(f)
                    
                    metadados = {
                        "colecao": colecao,
                        "schema": "core_v1",
                        "total_arquivos": total_arquivos,
                        "total_bytes": total_bytes,
                        "data_type": sample.get("data_type", "unknown"),
                        "sources": list(set(
                            json.load(open(f, 'r')).get("source", "unknown") 
                            for f in arquivos[:10]  # Sample dos primeiros 10
                        )),
                        "importancia_media": round(sum(
                            json.load(open(f, 'r')).get("importance", 1) 
                            for f in arquivos[:10]
                        ) / min(10, len(arquivos)), 1),
                        "confianca_media": round(sum(
                            json.load(open(f, 'r')).get("confidence", 0.5) 
                            for f in arquivos[:10]
                        ) / min(10, len(arquivos)), 2),
                        "data_criacao": self.timestamp
                    }
                    
                    # Salvar metadados da coleção
                    meta_file = meta_dir / f"{colecao}.json"
                    with open(meta_file, 'w', encoding='utf-8') as f:
                        json.dump(metadados, f, indent=2, ensure_ascii=False)
                    
                    logging.info(f"Metadados criados para coleção: {colecao}")
    
    def gerar_relatorio_migracao(self):
        """Gera relatório final da migração"""
        logging.info("Gerando relatório de migração...")
        
        # Contar arquivos por coleção
        data_dir = self.base_dir / "data"
        relatorio = {
            "timestamp": self.timestamp,
            "schema_version": "core_v1",
            "total_colecoes": 0,
            "total_arquivos": 0,
            "total_bytes": 0,
            "colecoes": {},
            "status": "completed"
        }
        
        for colecao_dir in data_dir.iterdir():
            if colecao_dir.is_dir():
                arquivos = list(colecao_dir.glob("*.json"))
                if arquivos:
                    total_bytes = sum(f.stat().st_size for f in arquivos)
                    
                    relatorio["colecoes"][colecao_dir.name] = {
                        "arquivos": len(arquivos),
                        "bytes": total_bytes
                    }
                    
                    relatorio["total_arquivos"] += len(arquivos)
                    relatorio["total_bytes"] += total_bytes
        
        relatorio["total_colecoes"] = len(relatorio["colecoes"])
        
        # Salvar relatório
        reports_dir = self.base_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        # Também criar versão resumida em texto
        summary_file = reports_dir / "migration_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE MIGRAÇÃO PROMETHEUS\n")
            f.write(f"================================\n\n")
            f.write(f"Data: {self.timestamp}\n")
            f.write(f"Total de Coleções: {relatorio['total_colecoes']}\n")
            f.write(f"Total de Arquivos: {relatorio['total_arquivos']}\n")
            f.write(f"Total de Bytes: {relatorio['total_bytes']:,}\n\n")
            
            f.write("DETALHES POR COLEÇÃO:\n")
            f.write("-" * 40 + "\n")
            for colecao, stats in relatorio["colecoes"].items():
                f.write(f"{colecao}: {stats['arquivos']} arquivos, {stats['bytes']:,} bytes\n")
        
        logging.info(f"Relatório salvo: {report_file}")
        return relatorio
    
    def executar_migracao_completa(self):
        """Executa migração completa de todos os dados"""
        logging.info("=== INICIANDO MIGRAÇÃO COMPLETA PROMETHEUS ===")
        
        try:
            # Fase 1: Migrar constantes críticas
            migrados_constants = self.migrar_dotaconstants()
            
            # Fase 2: Migrar sistema anterior
            migrados_sistema = self.migrar_sistema_anterior_json()
            
            # Fase 3: Migrar modelos ML
            migrados_modelos = self.migrar_modelos_ml()
            
            # Fase 4: Migrar outros repositórios
            migrados_outros = self.migrar_outros_repositorios()
            
            # Fase 5: Gerar metadados
            self.gerar_metadados_colecoes()
            
            # Fase 6: Gerar relatório
            relatorio = self.gerar_relatorio_migracao()
            
            total_migrados = migrados_constants + migrados_sistema + migrados_modelos + migrados_outros
            
            logging.info("=== MIGRAÇÃO CONCLUÍDA ===")
            logging.info(f"Total de arquivos migrados: {total_migrados}")
            logging.info(f"Constantes: {migrados_constants}")
            logging.info(f"Sistema anterior: {migrados_sistema}")
            logging.info(f"Modelos ML: {migrados_modelos}")
            logging.info(f"Outros repositórios: {migrados_outros}")
            
            return relatorio
            
        except Exception as e:
            logging.error(f"Erro durante migração: {e}")
            raise

def main():
    """Função principal"""
    migrador = MigradorPrometheus()
    relatorio = migrador.executar_migracao_completa()
    
    print("\n🎉 MIGRAÇÃO PROMETHEUS CONCLUÍDA!")
    print(f"📊 Total de arquivos migrados: {relatorio['total_arquivos']}")
    print(f"📁 Total de coleções: {relatorio['total_colecoes']}")
    print(f"💾 Total de dados: {relatorio['total_bytes']:,} bytes")
    print(f"📋 Relatório salvo em: /home/ubuntu/prometheus_migration/reports/")

if __name__ == "__main__":
    main()

