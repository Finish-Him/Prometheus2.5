"""
Módulo para extrair e processar a estrutura de dados do Oráculo 3.0
"""

import pandas as pd
import os
import json
from typing import Dict, Any, List, Optional, Union

class OraculoDataProcessor:
    """Classe para processar dados da base Oráculo 3.0"""
    
    def __init__(self, base_dir: str = "/home/ubuntu"):
        """
        Inicializa o processador de dados
        
        Args:
            base_dir: Diretório base onde os arquivos estão localizados
        """
        self.base_dir = base_dir
        self.upload_dir = os.path.join(base_dir, "upload")
        self.excel_path = os.path.join(self.upload_dir, "Database Oráculo 3.0.xlsx")
        self.doc_path = os.path.join(self.upload_dir, "Documentação da Base de Dados Oráculo 3.docx")
        self.liquipedia_path = os.path.join(self.upload_dir, "Análise detalhada da Liquipédia-Dota.docx")
        
        # Dicionário para armazenar dados carregados
        self.data_cache = {}
        
        # Mapeamento de planilhas importantes
        self.key_sheets = {
            "heroes": "Hero_Stats",
            "items": "Itens",
            "matches": "Pro Match",
            "players": "PGL Players 2",
            "match_details": "Match Detail",
            "dataset_predictor": "Dataset Previsor",
            "dataset_composition": "Dataset Final Composição"
        }
    
    def extract_data_structure(self) -> Dict[str, Any]:
        """
        Extrai a estrutura de dados do Oráculo 3.0
        
        Returns:
            Dicionário com a estrutura de dados
        """
        print("Extraindo estrutura de dados do Oráculo 3.0...")
        
        # Listar todas as planilhas
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            sheet_names = excel_file.sheet_names
            
            # Estrutura para armazenar informações
            structure = {
                "sheets": {},
                "relationships": [],
                "key_entities": {}
            }
            
            # Analisar planilhas principais
            for key, sheet_name in self.key_sheets.items():
                if sheet_name in sheet_names:
                    print(f"Analisando planilha: {sheet_name}")
                    
                    # Ler apenas as primeiras linhas para entender a estrutura
                    try:
                        df = pd.read_excel(self.excel_path, sheet_name=sheet_name, nrows=5)
                        
                        # Obter informações sobre as colunas
                        columns = list(df.columns)
                        data_types = {col: str(df[col].dtype) for col in columns}
                        
                        # Adicionar à estrutura
                        structure["sheets"][sheet_name] = {
                            "columns": columns,
                            "data_types": data_types,
                            "row_count": len(pd.read_excel(self.excel_path, sheet_name=sheet_name, usecols=[0]))
                        }
                        
                        # Adicionar à lista de entidades principais
                        structure["key_entities"][key] = {
                            "sheet_name": sheet_name,
                            "primary_key": self._identify_primary_key(columns),
                            "main_columns": self._identify_main_columns(columns)
                        }
                    except Exception as e:
                        print(f"Erro ao analisar planilha {sheet_name}: {str(e)}")
                        structure["sheets"][sheet_name] = {
                            "error": str(e)
                        }
            
            # Identificar relacionamentos entre planilhas
            structure["relationships"] = self._identify_relationships(structure["key_entities"])
            
            return structure
        
        except Exception as e:
            print(f"Erro ao extrair estrutura de dados: {str(e)}")
            return {"error": str(e)}
    
    def _identify_primary_key(self, columns: List[str]) -> str:
        """
        Identifica a chave primária provável de uma planilha
        
        Args:
            columns: Lista de colunas da planilha
            
        Returns:
            Nome da coluna que provavelmente é a chave primária
        """
        # Heurística simples para identificar chave primária
        primary_key_candidates = ["id", "match_id", "hero_id", "player_id", "account_id"]
        
        for candidate in primary_key_candidates:
            if candidate in columns:
                return candidate
        
        # Se não encontrar candidatos óbvios, usar a primeira coluna
        return columns[0] if columns else "unknown"
    
    def _identify_main_columns(self, columns: List[str]) -> List[str]:
        """
        Identifica as colunas principais de uma planilha
        
        Args:
            columns: Lista de colunas da planilha
            
        Returns:
            Lista de colunas principais
        """
        # Limitar a 10 colunas principais para simplificar
        return columns[:10] if len(columns) > 10 else columns
    
    def _identify_relationships(self, key_entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Identifica relacionamentos entre entidades principais
        
        Args:
            key_entities: Dicionário com entidades principais
            
        Returns:
            Lista de relacionamentos
        """
        relationships = []
        
        # Relacionamentos conhecidos em bases de dados de Dota 2
        if "heroes" in key_entities and "matches" in key_entities:
            relationships.append({
                "from": "matches",
                "to": "heroes",
                "type": "many-to-many",
                "description": "Partidas contêm múltiplos heróis"
            })
        
        if "players" in key_entities and "matches" in key_entities:
            relationships.append({
                "from": "matches",
                "to": "players",
                "type": "one-to-many",
                "description": "Uma partida contém múltiplos jogadores"
            })
        
        if "heroes" in key_entities and "players" in key_entities:
            relationships.append({
                "from": "players",
                "to": "heroes",
                "type": "many-to-many",
                "description": "Jogadores utilizam múltiplos heróis em diferentes partidas"
            })
        
        if "items" in key_entities and "heroes" in key_entities:
            relationships.append({
                "from": "heroes",
                "to": "items",
                "type": "many-to-many",
                "description": "Heróis utilizam múltiplos itens"
            })
        
        return relationships
    
    def load_hero_data(self) -> pd.DataFrame:
        """
        Carrega dados de heróis
        
        Returns:
            DataFrame com dados de heróis
        """
        if "heroes" in self.data_cache:
            return self.data_cache["heroes"]
        
        sheet_name = self.key_sheets.get("heroes")
        if not sheet_name:
            raise ValueError("Planilha de heróis não encontrada")
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            # Processar dados se necessário
            # Verificar se há apenas uma coluna com dados em CSV
            if len(df.columns) == 1 and ',' in str(df.iloc[0, 0]):
                # Dados estão em formato CSV em uma única coluna
                # Extrair cabeçalhos da primeira linha
                headers = df.iloc[0, 0].split(',')
                
                # Criar novo DataFrame
                rows = []
                for _, row in df.iterrows():
                    values = row[0].split(',')
                    if len(values) == len(headers):
                        rows.append(values)
                
                # Criar novo DataFrame com os dados extraídos
                df = pd.DataFrame(rows[1:], columns=headers)
            
            self.data_cache["heroes"] = df
            return df
        
        except Exception as e:
            print(f"Erro ao carregar dados de heróis: {str(e)}")
            # Retornar DataFrame vazio em caso de erro
            return pd.DataFrame()
    
    def load_match_data(self) -> pd.DataFrame:
        """
        Carrega dados de partidas
        
        Returns:
            DataFrame com dados de partidas
        """
        if "matches" in self.data_cache:
            return self.data_cache["matches"]
        
        sheet_name = self.key_sheets.get("matches")
        if not sheet_name:
            raise ValueError("Planilha de partidas não encontrada")
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            # Processar dados se necessário
            # Verificar se há apenas uma coluna com dados em CSV
            if len(df.columns) == 1 and ',' in str(df.iloc[0, 0]):
                # Dados estão em formato CSV em uma única coluna
                # Extrair cabeçalhos da primeira linha
                headers = df.iloc[0, 0].split(',')
                
                # Criar novo DataFrame
                rows = []
                for _, row in df.iterrows():
                    values = row[0].split(',')
                    if len(values) == len(headers):
                        rows.append(values)
                
                # Criar novo DataFrame com os dados extraídos
                df = pd.DataFrame(rows[1:], columns=headers)
            
            self.data_cache["matches"] = df
            return df
        
        except Exception as e:
            print(f"Erro ao carregar dados de partidas: {str(e)}")
            # Retornar DataFrame vazio em caso de erro
            return pd.DataFrame()
    
    def load_player_data(self) -> pd.DataFrame:
        """
        Carrega dados de jogadores
        
        Returns:
            DataFrame com dados de jogadores
        """
        if "players" in self.data_cache:
            return self.data_cache["players"]
        
        sheet_name = self.key_sheets.get("players")
        if not sheet_name:
            raise ValueError("Planilha de jogadores não encontrada")
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            # Processar dados se necessário
            # Verificar se há apenas uma coluna com dados em CSV
            if len(df.columns) == 1 and ',' in str(df.iloc[0, 0]):
                # Dados estão em formato CSV em uma única coluna
                # Extrair cabeçalhos da primeira linha
                headers = df.iloc[0, 0].split(',')
                
                # Criar novo DataFrame
                rows = []
                for _, row in df.iterrows():
                    values = row[0].split(',')
                    if len(values) == len(headers):
                        rows.append(values)
                
                # Criar novo DataFrame com os dados extraídos
                df = pd.DataFrame(rows[1:], columns=headers)
            
            self.data_cache["players"] = df
            return df
        
        except Exception as e:
            print(f"Erro ao carregar dados de jogadores: {str(e)}")
            # Retornar DataFrame vazio em caso de erro
            return pd.DataFrame()
    
    def load_predictor_dataset(self) -> pd.DataFrame:
        """
        Carrega dataset para previsão
        
        Returns:
            DataFrame com dataset para previsão
        """
        if "predictor_dataset" in self.data_cache:
            return self.data_cache["predictor_dataset"]
        
        sheet_name = self.key_sheets.get("dataset_predictor")
        if not sheet_name:
            raise ValueError("Planilha de dataset para previsão não encontrada")
        
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            # Processar dados se necessário
            # Verificar se há apenas uma coluna com dados em CSV
            if len(df.columns) == 1 and ',' in str(df.iloc[0, 0]):
                # Dados estão em formato CSV em uma única coluna
                # Extrair cabeçalhos da primeira linha
                headers = df.iloc[0, 0].split(',')
                
                # Criar novo DataFrame
                rows = []
                for _, row in df.iterrows():
                    values = row[0].split(',')
                    if len(values) == len(headers):
                        rows.append(values)
                
                # Criar novo DataFrame com os dados extraídos
                df = pd.DataFrame(rows[1:], columns=headers)
            
            self.data_cache["predictor_dataset"] = df
            return df
        
        except Exception as e:
            print(f"Erro ao carregar dataset para previsão: {str(e)}")
            # Retornar DataFrame vazio em caso de erro
            return pd.DataFrame()
    
    def save_structure(self, structure: Dict[str, Any], output_path: str) -> None:
        """
        Salva a estrutura de dados em um arquivo JSON
        
        Args:
            structure: Dicionário com a estrutura de dados
            output_path: Caminho para o arquivo de saída
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)
            print(f"Estrutura de dados salva em: {output_path}")
        except Exception as e:
            print(f"Erro ao salvar estrutura de dados: {str(e)}")

# Função para executar a extração da estrutura
def extract_oraculo_structure():
    """Extrai e salva a estrutura de dados do Oráculo 3.0"""
    processor = OraculoDataProcessor()
    structure = processor.extract_data_structure()
    processor.save_structure(structure, "/home/ubuntu/oraculo_structure.json")
    return structure

if __name__ == "__main__":
    extract_oraculo_structure()
