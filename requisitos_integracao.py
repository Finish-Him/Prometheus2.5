"""
Análise de requisitos para integração com a base de dados Oráculo 3.0

Este módulo define os requisitos para criar um código único que integre
todas as funcionalidades com a base de dados Oráculo 3.0 e permita
análises offline de partidas de Dota 2.
"""

class RequirementAnalysis:
    """Classe para análise de requisitos de integração"""
    
    def __init__(self):
        """Inicializa a análise de requisitos"""
        # Requisitos funcionais
        self.functional_requirements = [
            {
                "id": "FR1",
                "name": "Carregamento de dados",
                "description": "O sistema deve carregar dados da base Oráculo 3.0 em formato Excel",
                "priority": "Alta",
                "components": ["DataLoader"]
            },
            {
                "id": "FR2",
                "name": "Análise de partidas",
                "description": "O sistema deve analisar partidas de Dota 2 com base nas odds",
                "priority": "Alta",
                "components": ["MatchAnalyzer"]
            },
            {
                "id": "FR3",
                "name": "Análise de composições",
                "description": "O sistema deve analisar composições (drafts) das equipes",
                "priority": "Alta",
                "components": ["CompositionAnalyzer"]
            },
            {
                "id": "FR4",
                "name": "Previsões estatísticas",
                "description": "O sistema deve gerar previsões estatísticas sobre duração, kills e resultado",
                "priority": "Alta",
                "components": ["StatisticalPredictor"]
            },
            {
                "id": "FR5",
                "name": "Recomendações de apostas",
                "description": "O sistema deve recomendar apostas com base nas análises",
                "priority": "Alta",
                "components": ["BetRecommender"]
            },
            {
                "id": "FR6",
                "name": "Funcionamento offline",
                "description": "O sistema deve funcionar sem conexão com a internet",
                "priority": "Alta",
                "components": ["OfflineMode"]
            },
            {
                "id": "FR7",
                "name": "Interface de usuário",
                "description": "O sistema deve fornecer uma interface para interação do usuário",
                "priority": "Média",
                "components": ["UserInterface"]
            },
            {
                "id": "FR8",
                "name": "Histórico de análises",
                "description": "O sistema deve manter um histórico de análises anteriores",
                "priority": "Média",
                "components": ["AnalysisHistory"]
            },
            {
                "id": "FR9",
                "name": "Exportação de resultados",
                "description": "O sistema deve permitir exportar resultados em formato markdown",
                "priority": "Baixa",
                "components": ["ResultExporter"]
            }
        ]
        
        # Requisitos não funcionais
        self.non_functional_requirements = [
            {
                "id": "NFR1",
                "name": "Desempenho",
                "description": "O sistema deve processar análises em menos de 5 segundos",
                "priority": "Média"
            },
            {
                "id": "NFR2",
                "name": "Usabilidade",
                "description": "O sistema deve ser fácil de usar, com interface intuitiva",
                "priority": "Média"
            },
            {
                "id": "NFR3",
                "name": "Portabilidade",
                "description": "O sistema deve funcionar em Windows, macOS e Linux",
                "priority": "Alta"
            },
            {
                "id": "NFR4",
                "name": "Manutenibilidade",
                "description": "O código deve ser bem estruturado e documentado",
                "priority": "Média"
            },
            {
                "id": "NFR5",
                "name": "Confiabilidade",
                "description": "O sistema deve ser robusto a erros e dados incompletos",
                "priority": "Alta"
            }
        ]
        
        # Componentes do sistema
        self.system_components = [
            {
                "name": "DataLoader",
                "description": "Carrega e processa dados da base Oráculo 3.0",
                "dependencies": []
            },
            {
                "name": "MatchAnalyzer",
                "description": "Analisa partidas com base nas odds e estatísticas",
                "dependencies": ["DataLoader"]
            },
            {
                "name": "CompositionAnalyzer",
                "description": "Analisa composições das equipes",
                "dependencies": ["DataLoader"]
            },
            {
                "name": "StatisticalPredictor",
                "description": "Gera previsões estatísticas",
                "dependencies": ["MatchAnalyzer", "CompositionAnalyzer"]
            },
            {
                "name": "BetRecommender",
                "description": "Recomenda apostas com base nas análises",
                "dependencies": ["StatisticalPredictor"]
            },
            {
                "name": "OfflineMode",
                "description": "Gerencia funcionamento offline",
                "dependencies": ["DataLoader"]
            },
            {
                "name": "UserInterface",
                "description": "Interface para interação do usuário",
                "dependencies": ["MatchAnalyzer", "CompositionAnalyzer", "BetRecommender"]
            },
            {
                "name": "AnalysisHistory",
                "description": "Gerencia histórico de análises",
                "dependencies": ["MatchAnalyzer", "CompositionAnalyzer"]
            },
            {
                "name": "ResultExporter",
                "description": "Exporta resultados em diferentes formatos",
                "dependencies": ["MatchAnalyzer", "CompositionAnalyzer", "BetRecommender"]
            }
        ]
        
        # Estrutura de dados principal
        self.data_structure = {
            "heroes": {
                "description": "Dados sobre heróis do Dota 2",
                "source": "Hero_Stats",
                "key_fields": ["id", "name", "primary_attr", "roles"]
            },
            "matches": {
                "description": "Dados sobre partidas profissionais",
                "source": "Pro Match",
                "key_fields": ["match_id", "radiant_name", "dire_name", "duration", "radiant_win"]
            },
            "players": {
                "description": "Dados sobre jogadores profissionais",
                "source": "PGL Players 2",
                "key_fields": ["account_id", "hero_id", "kills", "deaths", "assists"]
            },
            "compositions": {
                "description": "Dados sobre composições de equipes",
                "source": "Dataset Final Composição",
                "key_fields": ["match_id", "radiant_heroes", "dire_heroes"]
            },
            "predictions": {
                "description": "Dados para previsões",
                "source": "Dataset Previsor",
                "key_fields": ["match_id", "duration", "total_kills", "radiant_win"]
            }
        }
        
        # Fluxo de trabalho
        self.workflow = [
            {
                "step": 1,
                "name": "Carregar dados",
                "description": "Carregar dados da base Oráculo 3.0",
                "component": "DataLoader"
            },
            {
                "step": 2,
                "name": "Entrada de odds",
                "description": "Receber odds da partida do usuário",
                "component": "UserInterface"
            },
            {
                "step": 3,
                "name": "Análise de partida",
                "description": "Analisar partida com base nas odds",
                "component": "MatchAnalyzer"
            },
            {
                "step": 4,
                "name": "Entrada de composição (opcional)",
                "description": "Receber composição das equipes do usuário",
                "component": "UserInterface"
            },
            {
                "step": 5,
                "name": "Análise de composição",
                "description": "Analisar composição das equipes",
                "component": "CompositionAnalyzer"
            },
            {
                "step": 6,
                "name": "Previsões estatísticas",
                "description": "Gerar previsões estatísticas",
                "component": "StatisticalPredictor"
            },
            {
                "step": 7,
                "name": "Recomendações de apostas",
                "description": "Gerar recomendações de apostas",
                "component": "BetRecommender"
            },
            {
                "step": 8,
                "name": "Apresentação de resultados",
                "description": "Apresentar resultados ao usuário",
                "component": "UserInterface"
            },
            {
                "step": 9,
                "name": "Salvar análise",
                "description": "Salvar análise no histórico",
                "component": "AnalysisHistory"
            }
        ]
    
    def get_integration_requirements(self):
        """
        Retorna os requisitos de integração
        
        Returns:
            Dicionário com requisitos de integração
        """
        return {
            "functional_requirements": self.functional_requirements,
            "non_functional_requirements": self.non_functional_requirements,
            "system_components": self.system_components,
            "data_structure": self.data_structure,
            "workflow": self.workflow
        }
    
    def get_architecture_diagram(self):
        """
        Retorna um diagrama de arquitetura em formato de texto
        
        Returns:
            String com diagrama de arquitetura
        """
        return """
        +-------------------+     +-------------------+     +-------------------+
        |                   |     |                   |     |                   |
        |    DataLoader     |---->|   MatchAnalyzer   |---->| StatisticalPredictor
        |                   |     |                   |     |                   |
        +-------------------+     +-------------------+     +-------------------+
                |                         |                         |
                |                         |                         |
                v                         v                         v
        +-------------------+     +-------------------+     +-------------------+
        |                   |     |                   |     |                   |
        | CompositionAnalyzer|---->|  BetRecommender  |<----|  AnalysisHistory  |
        |                   |     |                   |     |                   |
        +-------------------+     +-------------------+     +-------------------+
                                          |
                                          |
                                          v
                                  +-------------------+     +-------------------+
                                  |                   |     |                   |
                                  |  UserInterface   |---->|  ResultExporter   |
                                  |                   |     |                   |
                                  +-------------------+     +-------------------+
                                          |
                                          |
                                          v
                                  +-------------------+
                                  |                   |
                                  |    OfflineMode    |
                                  |                   |
                                  +-------------------+
        """

# Instanciar a análise de requisitos
requirements_analysis = RequirementAnalysis()

# Obter requisitos de integração
integration_requirements = requirements_analysis.get_integration_requirements()

# Obter diagrama de arquitetura
architecture_diagram = requirements_analysis.get_architecture_diagram()

# Imprimir informações
if __name__ == "__main__":
    print("Análise de Requisitos para Integração com Base de Dados Oráculo 3.0")
    print("\nRequisitos Funcionais:")
    for req in integration_requirements["functional_requirements"]:
        print(f"  {req['id']}: {req['name']} - {req['description']} (Prioridade: {req['priority']})")
    
    print("\nComponentes do Sistema:")
    for comp in integration_requirements["system_components"]:
        deps = ", ".join(comp["dependencies"]) if comp["dependencies"] else "Nenhuma"
        print(f"  {comp['name']}: {comp['description']} (Dependências: {deps})")
    
    print("\nDiagrama de Arquitetura:")
    print(architecture_diagram)
