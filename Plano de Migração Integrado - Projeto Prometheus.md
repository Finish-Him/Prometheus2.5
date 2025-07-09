# Plano de Migração Integrado - Projeto Prometheus

**Data:** 08/07/2025  
**Versão:** 2.0  
**Objetivo:** Migração completa para JSON padronizado (schema core_v1)  
**Prazo:** 4 semanas (MVP para The International)

## Resumo Executivo

A análise completa revelou um ecossistema complexo com **26.902 arquivos** totalizando **1.527 MB**, distribuídos entre repositórios externos e sistema anterior. A migração para JSON padronizado é crítica para viabilizar o projeto Prometheus e deve ser executada em fases priorizadas por importância e confiabilidade.

### Inventário Completo
- **Repositórios Externos:** 11 repositórios (26.601 arquivos, 1.299 MB)
- **Sistema Anterior:** 4 componentes (301 arquivos, 228 MB)
- **Total de JSONs Existentes:** 1.073 arquivos
- **Total de Código Python:** 210 arquivos
- **Modelos ML Treinados:** 19 arquivos

## Matriz de Priorização

### 🔴 PRIORIDADE CRÍTICA (Semana 1)

#### 1. dotaconstants-master
- **Importância:** 5/5 | **Confiança:** 0.95/1.0
- **Conteúdo:** 36 JSONs com constantes fundamentais do Dota 2
- **Migração:** Direto para `data/constants/` com validação schema core_v1
- **Impacto:** Base essencial para todos os modelos

#### 2. Sistema Anterior - Dados JSON
- **Importância:** 5/5 | **Confiança:** 0.8/1.0
- **Conteúdo:** 66 JSONs com dados históricos e análises
- **Categorias Críticas:**
  - 19 arquivos de partidas (matches)
  - 3 arquivos de heróis (heroes)
  - 3 arquivos de times (teams)
  - 2 arquivos de ligas (leagues)
- **Migração:** Consolidação e normalização para schema core_v1

### 🟡 PRIORIDADE ALTA (Semana 2)

#### 3. Sistema Anterior - Modelos ML
- **Importância:** 4/5 | **Confiança:** 0.85/1.0
- **Conteúdo:** 19 modelos treinados (.pkl)
- **Categorias:**
  - 7 modelos de regressão
  - 4 modelos ensemble
  - 4 modelos otimizados
  - 4 preprocessadores
- **Migração:** Validação, documentação e migração para `models/`

#### 4. opendota_data
- **Importância:** 4/5 | **Confiança:** 0.75/1.0
- **Conteúdo:** 80 arquivos de partidas históricas
- **Migração:** Normalização e enriquecimento com constantes

### 🟢 PRIORIDADE MODERADA (Semana 3)

#### 5. Sistema Anterior - Código Python
- **Importância:** 4/5 | **Confiança:** 0.7/1.0
- **Conteúdo:** 166 scripts Python
- **Categorias:**
  - Análise de dados (40+ scripts)
  - Processamento de dados (30+ scripts)
  - Visualização (20+ scripts)
  - Modelagem (15+ scripts)
- **Migração:** Consolidação, refatoração e padronização

#### 6. Protobufs-master
- **Importância:** 4/5 | **Confiança:** 0.90/1.0
- **Conteúdo:** 476 arquivos .proto
- **Migração:** Conversão para metadados JSON

### 🔵 PRIORIDADE BAIXA (Semana 4)

#### 7. Projetos de Análise (Prometheus1.1, opendota_analysis_project)
- **Importância:** 3/5 | **Confiança:** 0.80/1.0
- **Migração:** Consolidação e eliminação de duplicações

#### 8. Sistema Anterior - Documentação TXT
- **Importância:** 3/5 | **Confiança:** 0.7/1.0
- **Conteúdo:** 54 arquivos de análises documentadas
- **Migração:** Conversão para metadados estruturados

## Estrutura de Destino

```
prometheus/
├── data/
│   ├── constants/           # dotaconstants-master
│   │   ├── heroes.json
│   │   ├── items.json
│   │   └── abilities.json
│   ├── matches/            # Sistema anterior + opendota_data
│   │   ├── raw/
│   │   ├── enriched/
│   │   └── historical/
│   ├── teams/              # Dados de times consolidados
│   ├── leagues/            # Dados de ligas
│   └── analysis/           # Resultados de análises
├── models/                 # Modelos ML do sistema anterior
│   ├── production/
│   ├── experimental/
│   └── metadata/
├── src/                    # Código Python consolidado
│   ├── data_processing/
│   ├── analysis/
│   ├── modeling/
│   └── utils/
├── schemas/                # Schemas de validação
│   ├── core_v1.json
│   ├── match_v2.json
│   └── model_metadata.json
├── meta/                   # Metadados de coleções
└── reports/                # Relatórios de qualidade
```

## Schema Core V1 - Especificação

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "schema_version": {"const": "core_v1"},
    "data_type": {
      "enum": ["match", "hero", "item", "team", "league", "constant", "analysis", "model"]
    },
    "source": {
      "enum": ["opendota_api", "sistema_anterior", "dotaconstants", "manual"]
    },
    "timestamp": {"type": "string", "format": "date-time"},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "importance": {"type": "integer", "minimum": 1, "maximum": 5},
    "validation_status": {"enum": ["passed", "failed", "pending"]},
    "metadata": {
      "type": "object",
      "properties": {
        "origin_file": {"type": "string"},
        "collection": {"type": "string"},
        "hash": {"type": "string"}
      }
    },
    "data": {"type": "object"}
  },
  "required": ["schema_version", "data_type", "source", "timestamp", "data"]
}
```


## Scripts de Migração

### 1. Script Principal de Migração

```python
#!/usr/bin/env python3
"""
Script Principal de Migração - Projeto Prometheus
Migra todos os dados para JSON padronizado schema core_v1
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import hashlib
import jsonschema

class MigradorPrometheus:
    def __init__(self):
        self.schema_core_v1 = self.carregar_schema()
        self.timestamp = datetime.now().isoformat()
        
    def migrar_dotaconstants(self, origem: Path, destino: Path):
        """Migra constantes do Dota 2"""
        for json_file in origem.rglob('*.json'):
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            migrado = {
                "schema_version": "core_v1",
                "data_type": "constant",
                "source": "dotaconstants",
                "timestamp": self.timestamp,
                "confidence": 0.95,
                "importance": 5,
                "validation_status": "pending",
                "metadata": {
                    "origin_file": json_file.name,
                    "collection": "constants",
                    "hash": self.calcular_hash(data)
                },
                "data": data
            }
            
            # Validar contra schema
            try:
                jsonschema.validate(migrado, self.schema_core_v1)
                migrado["validation_status"] = "passed"
            except:
                migrado["validation_status"] = "failed"
            
            # Salvar
            output_file = destino / f"{json_file.stem}_{migrado['metadata']['hash'][:8]}.json"
            with open(output_file, 'w') as f:
                json.dump(migrado, f, indent=2, ensure_ascii=False)
    
    def migrar_sistema_anterior_json(self, origem: Path, destino: Path):
        """Migra JSONs do sistema anterior"""
        for json_file in origem.rglob('*.json'):
            if 'client_secret' in json_file.name:
                continue  # Pular arquivos de configuração sensíveis
                
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Determinar tipo baseado no nome do arquivo
            data_type = self.determinar_tipo_dados(json_file.name)
            
            migrado = {
                "schema_version": "core_v1",
                "data_type": data_type,
                "source": "sistema_anterior",
                "timestamp": self.timestamp,
                "confidence": 0.8,
                "importance": self.calcular_importancia(data_type),
                "validation_status": "pending",
                "metadata": {
                    "origin_file": json_file.name,
                    "collection": data_type,
                    "hash": self.calcular_hash(data)
                },
                "data": data
            }
            
            # Validar e salvar
            try:
                jsonschema.validate(migrado, self.schema_core_v1)
                migrado["validation_status"] = "passed"
            except:
                migrado["validation_status"] = "failed"
            
            output_dir = destino / data_type
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{json_file.stem}_{migrado['metadata']['hash'][:8]}.json"
            
            with open(output_file, 'w') as f:
                json.dump(migrado, f, indent=2, ensure_ascii=False)
```

### 2. Script de Validação

```python
def validar_migracao():
    """Valida todos os JSONs migrados"""
    total_arquivos = 0
    arquivos_validos = 0
    erros = []
    
    for json_file in Path('data').rglob('*.json'):
        total_arquivos += 1
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            jsonschema.validate(data, schema_core_v1)
            arquivos_validos += 1
        except Exception as e:
            erros.append(f"{json_file}: {str(e)}")
    
    print(f"Validação: {arquivos_validos}/{total_arquivos} arquivos válidos")
    return len(erros) == 0
```

## Cronograma Detalhado

### Semana 1: Fundação Crítica (08-14 Jul)

#### Dia 1-2: Setup e Constantes
- [ ] Criar estrutura de diretórios
- [ ] Implementar schema core_v1
- [ ] Migrar dotaconstants-master (36 JSONs)
- [ ] Validar constantes migradas
- [ ] **Entrega:** Base de constantes validada

#### Dia 3-4: Sistema Anterior - JSONs Críticos
- [ ] Migrar arquivos de partidas (19 JSONs)
- [ ] Migrar dados de heróis (3 JSONs)
- [ ] Migrar dados de times (3 JSONs)
- [ ] Normalizar e enriquecer dados
- [ ] **Entrega:** Dados históricos estruturados

#### Dia 5-7: Validação e Testes
- [ ] Implementar testes automatizados
- [ ] Validar integridade dos dados
- [ ] Criar relatórios de qualidade
- [ ] **Entrega:** Pipeline de validação funcional

### Semana 2: Modelos e Dados Históricos (15-21 Jul)

#### Dia 8-10: Modelos ML
- [ ] Migrar modelos de regressão (7 arquivos)
- [ ] Migrar modelos ensemble (4 arquivos)
- [ ] Migrar modelos otimizados (4 arquivos)
- [ ] Documentar metadados dos modelos
- [ ] **Entrega:** Biblioteca de modelos validada

#### Dia 11-14: Dados OpenDota
- [ ] Migrar opendota_data (80 arquivos)
- [ ] Enriquecer com constantes
- [ ] Validar consistência temporal
- [ ] **Entrega:** Dataset histórico completo

### Semana 3: Código e Infraestrutura (22-28 Jul)

#### Dia 15-17: Consolidação de Código
- [ ] Refatorar scripts de análise (40+ arquivos)
- [ ] Consolidar processamento de dados (30+ arquivos)
- [ ] Padronizar visualizações (20+ arquivos)
- [ ] **Entrega:** Biblioteca de código unificada

#### Dia 18-21: Protobufs e Metadados
- [ ] Converter Protobufs para metadados JSON
- [ ] Implementar CI/CD pipeline
- [ ] Configurar alertas Slack
- [ ] **Entrega:** Infraestrutura automatizada

### Semana 4: Finalização e Testes (29 Jul - 04 Ago)

#### Dia 22-24: Projetos Legados
- [ ] Consolidar Prometheus1.1
- [ ] Eliminar duplicações
- [ ] Migrar documentação TXT
- [ ] **Entrega:** Projeto consolidado

#### Dia 25-28: Testes Finais
- [ ] Testes de integração completos
- [ ] Benchmarks de performance
- [ ] Documentação final
- [ ] **Entrega:** Sistema pronto para produção

## Métricas de Sucesso

### Quantitativas
- **JSONs Migrados:** ≥ 1.000 arquivos
- **Taxa de Validação:** 100% dos JSONs passam no schema core_v1
- **Redução de Duplicação:** ≥ 90% de arquivos duplicados eliminados
- **Cobertura de Testes:** ≥ 80% do código testado
- **Tempo de Ingestão:** < 60 min para 10.000 partidas

### Qualitativas
- **Padronização:** 100% dos dados em formato JSON core_v1
- **Documentação:** Cobertura completa de APIs e processos
- **Observabilidade:** Logs estruturados e alertas funcionais
- **Confiabilidade:** Sistema robusto com tratamento de erros

## Riscos e Mitigações

### Riscos Críticos

#### 1. Perda de Dados Durante Migração
- **Probabilidade:** Média
- **Impacto:** Alto
- **Mitigação:** 
  - Backup completo antes da migração
  - Validação por checksums
  - Rollback automático em caso de falha

#### 2. Incompatibilidade de Schemas
- **Probabilidade:** Alta
- **Impacto:** Médio
- **Mitigação:**
  - Testes extensivos com dados de amostra
  - Schema versionado com backward compatibility
  - Validação incremental

#### 3. Performance Degradada
- **Probabilidade:** Média
- **Impacto:** Médio
- **Mitigação:**
  - Benchmarks antes e depois
  - Otimização de queries
  - Indexação adequada

### Riscos Operacionais

#### 4. Resistência da Equipe
- **Probabilidade:** Baixa
- **Impacto:** Médio
- **Mitigação:**
  - Treinamento adequado
  - Documentação clara
  - Canal de suporte dedicado

#### 5. Prazo Apertado (The International)
- **Probabilidade:** Alta
- **Impacto:** Alto
- **Mitigação:**
  - Priorização rigorosa
  - MVP funcional em 3 semanas
  - Paralelização de tarefas

## Entregáveis Finais

### 1. Dados Migrados
- **1.073+ JSONs** validados contra schema core_v1
- **Estrutura padronizada** em `data/`
- **Metadados completos** para rastreabilidade

### 2. Código Consolidado
- **210 scripts Python** refatorados e organizados
- **Biblioteca unificada** em `src/`
- **Testes automatizados** com pytest

### 3. Modelos Documentados
- **19 modelos ML** com metadados completos
- **Pipeline de retreino** automatizado
- **Versionamento** de modelos

### 4. Infraestrutura
- **CI/CD pipeline** com GitHub Actions
- **Alertas Slack** para falhas
- **Monitoramento** de qualidade de dados

### 5. Documentação
- **README abrangente** com guias de uso
- **API documentation** completa
- **Runbooks** operacionais

## Próximos Passos Imediatos

1. **Aprovação do Plano** - Validação com stakeholders
2. **Setup do Ambiente** - Preparação da infraestrutura
3. **Início da Migração** - Execução da Semana 1
4. **Monitoramento Contínuo** - Acompanhamento diário do progresso

**O sucesso do projeto Prometheus depende da execução disciplinada deste plano de migração, com foco na qualidade, padronização e observabilidade dos dados.**

