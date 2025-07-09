#!/usr/bin/env python3
"""
Script integrado para coleta de dados das APIs PandaScore, OpenDota e Steam Web API para Dota 2.
Foco em partidas profissionais do patch 7.38 (após 19/02/2025) em torneios Tier 1 e 2.
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("integrated_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("integrated_collector")

# Diretório base para dados coletados
BASE_DIR = "collected_data"
SCRIPTS_DIR = "scripts"

# Criar diretório base
os.makedirs(BASE_DIR, exist_ok=True)

def run_collector_script(script_name):
    """Executa um script de coleta de dados."""
    logger.info(f"Executando script: {script_name}")
    
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    
    try:
        # Verificar se o script existe
        if not os.path.exists(script_path):
            logger.error(f"Script não encontrado: {script_path}")
            return False
        
        # Executar o script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        # Verificar resultado
        if result.returncode == 0:
            logger.info(f"Script {script_name} executado com sucesso")
            return True
        else:
            logger.error(f"Erro ao executar script {script_name}: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Exceção ao executar script {script_name}: {e}")
        return False

def collect_all_data():
    """Coleta dados de todas as APIs."""
    start_time = datetime.now()
    logger.info(f"Iniciando coleta integrada de dados em {start_time}")
    
    # Lista de scripts a serem executados
    scripts = [
        "pandascore_collector.py",
        "opendota_collector.py",
        "steam_collector.py"
    ]
    
    results = {}
    
    # Executar cada script
    for script in scripts:
        script_start_time = datetime.now()
        success = run_collector_script(script)
        script_end_time = datetime.now()
        script_duration = script_end_time - script_start_time
        
        results[script] = {
            "success": success,
            "start_time": script_start_time.isoformat(),
            "end_time": script_end_time.isoformat(),
            "duration_seconds": script_duration.total_seconds()
        }
        
        # Aguardar um pouco entre scripts para evitar sobrecarga
        time.sleep(5)
    
    # Resumo da coleta
    end_time = datetime.now()
    duration = end_time - start_time
    
    summary = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration.total_seconds(),
        "scripts_results": results
    }
    
    # Salvar resumo
    with open(os.path.join(BASE_DIR, "integrated_collection_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Coleta integrada de dados concluída em {duration.total_seconds()} segundos")
    logger.info(f"Resumo: {json.dumps(summary, indent=2)}")
    
    return summary

def verify_collected_data():
    """Verifica os dados coletados e gera estatísticas."""
    logger.info("Verificando dados coletados")
    
    # Diretórios a serem verificados
    directories = [
        "pandascore",
        "opendota",
        "steam"
    ]
    
    stats = {}
    
    for directory in directories:
        dir_path = os.path.join(BASE_DIR, directory)
        
        if not os.path.exists(dir_path):
            logger.warning(f"Diretório não encontrado: {dir_path}")
            stats[directory] = {"status": "not_found"}
            continue
        
        # Verificar arquivos de resumo
        summary_path = os.path.join(dir_path, "collection_summary.json")
        
        if os.path.exists(summary_path):
            try:
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                
                stats[directory] = {
                    "status": "success",
                    "summary": summary
                }
            except Exception as e:
                logger.error(f"Erro ao ler resumo de {directory}: {e}")
                stats[directory] = {"status": "error_reading_summary"}
        else:
            # Contar arquivos manualmente
            file_count = sum(len(files) for _, _, files in os.walk(dir_path))
            
            stats[directory] = {
                "status": "no_summary",
                "file_count": file_count
            }
    
    # Salvar estatísticas
    with open(os.path.join(BASE_DIR, "data_verification.json"), "w") as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"Verificação de dados concluída: {json.dumps(stats, indent=2)}")
    
    return stats

def main():
    """Função principal."""
    logger.info("Iniciando coleta integrada de dados para Dota 2")
    
    # 1. Coletar dados de todas as APIs
    collection_summary = collect_all_data()
    
    # 2. Verificar dados coletados
    verification_stats = verify_collected_data()
    
    # 3. Exibir resumo final
    logger.info("Coleta integrada de dados concluída com sucesso")
    logger.info(f"Resumo da coleta: {json.dumps(collection_summary, indent=2)}")
    logger.info(f"Estatísticas de verificação: {json.dumps(verification_stats, indent=2)}")

if __name__ == "__main__":
    main()
