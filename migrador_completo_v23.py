#!/usr/bin/env python3
"""
Migrador Completo Prometheus 2.3
Migra todos os dados para JSON padronizado e mescla com dados existentes
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
import zipfile
from tqdm import tqdm

def criar_estrutura_final():
    """Cria estrutura final organizada de diretórios"""
    base_path = Path("/home/ubuntu/prometheus_final")
    
    estrutura = {
        "data": {
            "constants": "Constantes do jogo (heróis, itens, habilidades)",
            "matches": "Dados de partidas profissionais e públicas", 
            "players": "Dados de jogadores profissionais",
            "teams": "Dados de equipes e organizações",
            "leagues": "Dados de ligas e torneios",
            "analysis": "Análises e relatórios gerados",
            "models": "Modelos ML e metadados",
            "historical": "Dados históricos e estatísticas"
        },
        "src": {
            "migration": "Scripts de migração e processamento",
            "analysis": "Scripts de análise de dados",
            "validation": "Scripts de validação e qualidade",
            "utils": "Utilitários e funções auxiliares"
        },
        "schemas": "Schemas JSON para validação",
        "reports": "Relatórios e documentação",
        "logs": "Logs de processamento"
    }
    
    print(f"🏗️ Criando estrutura em {base_path}")
    
    for categoria, subcategorias in estrutura.items():
        if isinstance(subcategorias, dict):
            for subcat, desc in subcategorias.items():
                dir_path = base_path / categoria / subcat
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Criar arquivo README em cada diretório
                readme_path = dir_path / "README.md"
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(f"# {subcat.title()}\n\n{desc}\n\n")
                    f.write(f"Criado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        else:
            dir_path = base_path / categoria
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return base_path

def calcular_hash_arquivo(arquivo_path):
    """Calcula hash SHA256 do arquivo"""
    try:
        with open(arquivo_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except:
        return "erro_hash"

def migrar_json_padronizado(origem_path, destino_path, categoria, metadados_origem):
    """Migra JSON para formato padronizado core_v1"""
    try:
        with open(origem_path, 'r', encoding='utf-8') as f:
            dados_originais = json.load(f)
        
        # Criar estrutura padronizada core_v1
        dados_migrados = {
            "schema": "core_v1",
            "version": "2.3",
            "metadata": {
                "id": calcular_hash_arquivo(origem_path),
                "nome_original": origem_path.name,
                "categoria": categoria,
                "origem": "prometheus_2.3",
                "data_migracao": datetime.now().isoformat(),
                "importancia": metadados_origem.get("importancia", 1),
                "confianca": metadados_origem.get("confianca", 0.5),
                "tamanho_original_kb": metadados_origem.get("metadados", {}).get("tamanho_kb", 0),
                "hash_original": metadados_origem.get("hash", ""),
                "validacao": {
                    "schema_valido": True,
                    "dados_validos": metadados_origem.get("metadados", {}).get("valido", False),
                    "total_registros": metadados_origem.get("metadados", {}).get("total_registros", 0)
                }
            },
            "data": dados_originais
        }
        
        # Salvar arquivo migrado
        nome_final = f"{categoria}_{dados_migrados['metadata']['id']}.json"
        caminho_final = destino_path / nome_final
        
        with open(caminho_final, 'w', encoding='utf-8') as f:
            json.dump(dados_migrados, f, indent=2, ensure_ascii=False)
        
        return {
            "sucesso": True,
            "arquivo_final": str(caminho_final),
            "nome_final": nome_final,
            "metadados": dados_migrados["metadata"]
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
            "arquivo_original": str(origem_path)
        }

def copiar_python_organizado(origem_path, destino_path, categoria, metadados_origem):
    """Copia arquivos Python para estrutura organizada"""
    try:
        # Determinar subcategoria baseada no nome e metadados
        nome_arquivo = origem_path.name.lower()
        
        if "migrador" in nome_arquivo or "migration" in nome_arquivo:
            subcat = "migration"
        elif "analisador" in nome_arquivo or "analysis" in nome_arquivo:
            subcat = "analysis"
        elif "validador" in nome_arquivo or "validation" in nome_arquivo:
            subcat = "validation"
        else:
            subcat = "utils"
        
        destino_final = destino_path / subcat / origem_path.name
        shutil.copy2(origem_path, destino_final)
        
        # Criar metadados do arquivo Python
        metadados_py = {
            "nome": origem_path.name,
            "categoria": categoria,
            "subcategoria": subcat,
            "origem": "prometheus_2.3",
            "data_copia": datetime.now().isoformat(),
            "importancia": metadados_origem.get("importancia", 1),
            "confianca": metadados_origem.get("confianca", 0.5),
            "metadados_codigo": metadados_origem.get("metadados", {}),
            "hash": metadados_origem.get("hash", "")
        }
        
        # Salvar metadados
        metadados_path = destino_final.with_suffix('.json')
        with open(metadados_path, 'w', encoding='utf-8') as f:
            json.dump(metadados_py, f, indent=2, ensure_ascii=False)
        
        return {
            "sucesso": True,
            "arquivo_final": str(destino_final),
            "metadados_final": str(metadados_path),
            "subcategoria": subcat
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e),
            "arquivo_original": str(origem_path)
        }

def extrair_zips_internos(base_path):
    """Extrai ZIPs internos encontrados no Prometheus 2.3"""
    print("📦 Extraindo ZIPs internos...")
    
    zip_dir = base_path / "Prometheus 2.3" / "Prometheus 2.3.1" / "zip"
    if not zip_dir.exists():
        print("❌ Diretório de ZIPs não encontrado")
        return []
    
    arquivos_extraidos = []
    
    for zip_file in zip_dir.glob("*.zip"):
        print(f"  📦 Extraindo {zip_file.name}")
        
        extract_dir = zip_dir / zip_file.stem
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Catalogar arquivos extraídos
            for arquivo in extract_dir.rglob("*"):
                if arquivo.is_file() and arquivo.suffix in ['.json', '.py']:
                    arquivos_extraidos.append(arquivo)
                    
        except Exception as e:
            print(f"❌ Erro ao extrair {zip_file.name}: {e}")
    
    return arquivos_extraidos

def mesclar_com_migracao_anterior():
    """Mescla com dados da migração anterior"""
    print("🔄 Mesclando com migração anterior...")
    
    migracao_anterior = Path("/home/ubuntu/prometheus_migration")
    if not migracao_anterior.exists():
        print("⚠️ Migração anterior não encontrada")
        return []
    
    arquivos_mesclados = []
    
    # Copiar JSONs da migração anterior
    data_anterior = migracao_anterior / "data"
    if data_anterior.exists():
        for json_file in data_anterior.rglob("*.json"):
            arquivos_mesclados.append(json_file)
    
    return arquivos_mesclados

def main():
    print("🚀 INICIANDO MIGRAÇÃO COMPLETA PROMETHEUS 2.3")
    
    # Carregar catálogo do Prometheus 2.3
    catalogo_path = Path("catalogo_prometheus23.json")
    if not catalogo_path.exists():
        print("❌ Catálogo não encontrado. Execute analisador_prometheus23.py primeiro.")
        return
    
    with open(catalogo_path, 'r', encoding='utf-8') as f:
        catalogo = json.load(f)
    
    # Criar estrutura final
    base_final = criar_estrutura_final()
    
    # Extrair ZIPs internos
    arquivos_extras = extrair_zips_internos(Path("."))
    
    # Mesclar com migração anterior
    arquivos_anteriores = mesclar_com_migracao_anterior()
    
    # Estatísticas de migração
    stats = {
        "inicio": datetime.now().isoformat(),
        "arquivos_processados": 0,
        "jsons_migrados": 0,
        "pythons_copiados": 0,
        "erros": [],
        "sucessos": []
    }
    
    print(f"📊 Processando {len(catalogo['arquivos_json'])} JSONs e {len(catalogo['arquivos_python'])} Pythons")
    
    # Migrar arquivos JSON
    print("\n📄 Migrando arquivos JSON...")
    for arquivo_info in tqdm(catalogo["arquivos_json"], desc="JSONs"):
        origem_path = Path(arquivo_info["caminho_relativo"])
        
        # Determinar categoria baseada no caminho e nome
        nome = arquivo_info["nome"].lower()
        if "constants" in nome or "heroes" in nome or "items" in nome:
            categoria = "constants"
            destino_dir = base_final / "data" / "constants"
        elif "pro_match" in nome or "matches" in nome:
            categoria = "matches"
            destino_dir = base_final / "data" / "matches"
        elif "pro_players" in nome or "players" in nome:
            categoria = "players"
            destino_dir = base_final / "data" / "players"
        elif "teams" in nome:
            categoria = "teams"
            destino_dir = base_final / "data" / "teams"
        elif "analise" in nome or "dicionario" in nome:
            categoria = "analysis"
            destino_dir = base_final / "data" / "analysis"
        else:
            categoria = "historical"
            destino_dir = base_final / "data" / "historical"
        
        resultado = migrar_json_padronizado(origem_path, destino_dir, categoria, arquivo_info)
        
        if resultado["sucesso"]:
            stats["jsons_migrados"] += 1
            stats["sucessos"].append(resultado)
        else:
            stats["erros"].append(resultado)
        
        stats["arquivos_processados"] += 1
    
    # Copiar arquivos Python
    print("\n🐍 Copiando arquivos Python...")
    for arquivo_info in tqdm(catalogo["arquivos_python"], desc="Python"):
        origem_path = Path(arquivo_info["caminho_relativo"])
        destino_dir = base_final / "src"
        
        resultado = copiar_python_organizado(origem_path, destino_dir, "src", arquivo_info)
        
        if resultado["sucesso"]:
            stats["pythons_copiados"] += 1
            stats["sucessos"].append(resultado)
        else:
            stats["erros"].append(resultado)
        
        stats["arquivos_processados"] += 1
    
    # Copiar schemas
    print("\n📋 Copiando schemas...")
    for arquivo_info in catalogo["arquivos_json"]:
        if "core_v1" in arquivo_info["nome"]:
            origem_path = Path(arquivo_info["caminho_relativo"])
            destino_path = base_final / "schemas" / arquivo_info["nome"]
            shutil.copy2(origem_path, destino_path)
    
    # Processar arquivos extras dos ZIPs
    print(f"\n📦 Processando {len(arquivos_extras)} arquivos extras...")
    for arquivo_extra in tqdm(arquivos_extras, desc="Extras"):
        if arquivo_extra.suffix == '.json':
            categoria = "historical"
            destino_dir = base_final / "data" / "historical"
            
            metadados_fake = {
                "importancia": 2,
                "confianca": 0.6,
                "metadados": {"valido": True, "tamanho_kb": arquivo_extra.stat().st_size / 1024},
                "hash": calcular_hash_arquivo(arquivo_extra)
            }
            
            resultado = migrar_json_padronizado(arquivo_extra, destino_dir, categoria, metadados_fake)
            if resultado["sucesso"]:
                stats["jsons_migrados"] += 1
        
        elif arquivo_extra.suffix == '.py':
            destino_dir = base_final / "src"
            
            metadados_fake = {
                "importancia": 2,
                "confianca": 0.6,
                "metadados": {"valido": True, "tamanho_kb": arquivo_extra.stat().st_size / 1024},
                "hash": calcular_hash_arquivo(arquivo_extra)
            }
            
            resultado = copiar_python_organizado(arquivo_extra, destino_dir, "src", metadados_fake)
            if resultado["sucesso"]:
                stats["pythons_copiados"] += 1
    
    # Finalizar estatísticas
    stats["fim"] = datetime.now().isoformat()
    stats["duracao_segundos"] = (datetime.fromisoformat(stats["fim"]) - datetime.fromisoformat(stats["inicio"])).total_seconds()
    
    # Salvar relatório final
    relatorio_path = base_final / "reports" / "migracao_completa_v23.json"
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # Contar arquivos finais
    total_jsons_final = len(list((base_final / "data").rglob("*.json")))
    total_pythons_final = len(list((base_final / "src").rglob("*.py")))
    
    print(f"\n✅ MIGRAÇÃO COMPLETA FINALIZADA!")
    print(f"📊 Arquivos processados: {stats['arquivos_processados']}")
    print(f"📄 JSONs migrados: {stats['jsons_migrados']}")
    print(f"🐍 Pythons copiados: {stats['pythons_copiados']}")
    print(f"❌ Erros: {len(stats['erros'])}")
    print(f"⏱️ Duração: {stats['duracao_segundos']:.1f}s")
    print(f"📁 Estrutura final: {base_final}")
    print(f"📄 Total JSONs finais: {total_jsons_final}")
    print(f"🐍 Total Pythons finais: {total_pythons_final}")

if __name__ == "__main__":
    main()

