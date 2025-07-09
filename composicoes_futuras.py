"""
Módulo para suporte a análise futura com composições para o Analisador de Partidas de Dota 2 - Versão Offline

Este módulo estende o analisador offline para suportar análises futuras com composições.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional, Union
from analisador_offline import AnalisadorPartidas

class AnalisadorComposicoes:
    """Classe para análise de composições de equipes em partidas de Dota 2"""
    
    def __init__(self):
        """Inicializa o analisador de composições"""
        self.analisador = AnalisadorPartidas()
        self.analises_pendentes = []
        self.carregar_analises_pendentes()
    
    def carregar_analises_pendentes(self):
        """Carrega as análises pendentes de composição, se existirem"""
        try:
            if os.path.exists("analises_pendentes.json"):
                with open("analises_pendentes.json", "r", encoding="utf-8") as f:
                    self.analises_pendentes = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar análises pendentes: {str(e)}")
            self.analises_pendentes = []
    
    def salvar_analises_pendentes(self):
        """Salva as análises pendentes de composição"""
        try:
            with open("analises_pendentes.json", "w", encoding="utf-8") as f:
                json.dump(self.analises_pendentes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar análises pendentes: {str(e)}")
    
    def adicionar_analise_pendente(self, analise: Dict[str, Any]):
        """
        Adiciona uma análise à lista de pendentes para futura análise com composição
        
        Args:
            analise: Dicionário com dados da análise
        """
        # Adicionar timestamp
        analise["timestamp_pendente"] = datetime.datetime.now().isoformat()
        
        # Adicionar à lista de pendentes
        self.analises_pendentes.append(analise)
        
        # Salvar lista atualizada
        self.salvar_analises_pendentes()
    
    def listar_analises_pendentes(self) -> List[Dict[str, Any]]:
        """
        Lista as análises pendentes de composição
        
        Returns:
            Lista de análises pendentes
        """
        return self.analises_pendentes
    
    def atualizar_com_composicao(self, indice: int, composicao: str) -> Dict[str, Any]:
        """
        Atualiza uma análise pendente com dados de composição
        
        Args:
            indice: Índice da análise pendente
            composicao: Texto contendo as composições das equipes
            
        Returns:
            Dicionário com a análise atualizada
        """
        if indice < 0 or indice >= len(self.analises_pendentes):
            raise ValueError("Índice inválido")
        
        # Obter análise pendente
        analise_pendente = self.analises_pendentes[indice]
        
        # Extrair dados da partida
        match_data = analise_pendente["match_data"]
        texto_odds = self._reconstruir_texto_odds(match_data)
        
        # Realizar nova análise com composição
        nova_analise = self.analisador.analisar_partida(texto_odds, composicao)
        
        # Remover da lista de pendentes
        self.analises_pendentes.pop(indice)
        self.salvar_analises_pendentes()
        
        return nova_analise
    
    def _reconstruir_texto_odds(self, match_data: Dict[str, Any]) -> str:
        """
        Reconstrói o texto de odds a partir dos dados da partida
        
        Args:
            match_data: Dicionário com dados da partida
            
        Returns:
            Texto com as odds reconstruídas
        """
        time_radiant = match_data["time_radiant"]
        time_dire = match_data["time_dire"]
        torneio = match_data.get("torneio", "")
        odds = match_data.get("odds", {})
        mercados = match_data.get("mercados", [])
        
        # Montar texto de odds
        texto_odds = f"{time_radiant} vs {time_dire}\n"
        if torneio:
            texto_odds += f"{torneio}\n"
        
        texto_odds += f"\nOdds vencedor:\n"
        texto_odds += f"{time_radiant}: {odds.get('vitoria_radiant', 'N/A')}\n"
        texto_odds += f"{time_dire}: {odds.get('vitoria_dire', 'N/A')}\n"
        
        # Adicionar mercados
        for mercado in mercados:
            tipo = mercado.get("tipo", "")
            valor = mercado.get("valor", 0)
            odds_over = mercado.get("odds_over", 0)
            odds_under = mercado.get("odds_under", 0)
            
            if tipo == "total_kills":
                texto_odds += f"\nTotal de kills:\n"
                texto_odds += f"Over {valor}: {odds_over}\n"
                texto_odds += f"Under {valor}: {odds_under}\n"
            elif tipo == "duracao":
                texto_odds += f"\nDuração:\n"
                texto_odds += f"Over {valor}: {odds_over}\n"
                texto_odds += f"Under {valor}: {odds_under}\n"
            elif tipo == "handicap_kills":
                texto_odds += f"\nHandicap de kills:\n"
                texto_odds += f"{time_radiant} ({valor}): {odds_over}\n"
                texto_odds += f"{time_dire} ({-valor}): {odds_under}\n"
        
        return texto_odds

def integrar_com_interface(interface_arquivo: str):
    """
    Integra o suporte a composições futuras com a interface existente
    
    Args:
        interface_arquivo: Caminho para o arquivo da interface
    """
    try:
        # Ler o arquivo da interface
        with open(interface_arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        # Verificar se já está integrado
        if "def atualizar_analise_pendente():" in conteudo:
            print("Interface já integrada com suporte a composições futuras.")
            return
        
        # Adicionar importação
        conteudo = conteudo.replace(
            "from analisador_offline import AnalisadorPartidas",
            "from analisador_offline import AnalisadorPartidas\nfrom composicoes_futuras import AnalisadorComposicoes"
        )
        
        # Adicionar inicialização
        conteudo = conteudo.replace(
            "def main():\n    \"\"\"Função principal\"\"\"\n    analisador = AnalisadorPartidas()",
            "def main():\n    \"\"\"Função principal\"\"\"\n    analisador = AnalisadorPartidas()\n    analisador_comp = AnalisadorComposicoes()"
        )
        
        # Adicionar opção no menu
        conteudo = conteudo.replace(
            "    print(\"3. Ver histórico de análises\")\n    print(\"4. Sobre o analisador\")",
            "    print(\"3. Ver histórico de análises\")\n    print(\"4. Atualizar análise com composição\")\n    print(\"5. Sobre o analisador\")"
        )
        
        # Adicionar tratamento da nova opção
        conteudo = conteudo.replace(
            "            elif escolha == 4:\n                # Sobre o analisador\n                sobre()",
            "            elif escolha == 4:\n                # Atualizar análise com composição\n                atualizar_analise_pendente()\n            elif escolha == 5:\n                # Sobre o analisador\n                sobre()"
        )
        
        # Adicionar função para atualizar análise pendente
        nova_funcao = """
def atualizar_analise_pendente():
    \"\"\"Atualiza uma análise pendente com dados de composição\"\"\"
    analisador_comp = AnalisadorComposicoes()
    analises_pendentes = analisador_comp.listar_analises_pendentes()
    
    if not analises_pendentes:
        limpar_tela()
        print("Nenhuma análise pendente encontrada.")
        input("\\nPressione Enter para continuar...")
        return
    
    while True:
        limpar_tela()
        print("=" * 60)
        print("           ATUALIZAR ANÁLISE COM COMPOSIÇÃO")
        print("=" * 60)
        print("\\nEscolha uma análise para atualizar:")
        
        for i, analise in enumerate(analises_pendentes, 1):
            match_data = analise["match_data"]
            timestamp = analise.get("timestamp_pendente", "Data desconhecida")
            print(f"{i}. {match_data['time_radiant']} vs {match_data['time_dire']} - {timestamp}")
        
        print("\\n0. Voltar ao menu principal")
        print("\\n" + "=" * 60)
        
        try:
            escolha = int(input("\\nSua escolha: "))
            if escolha == 0:
                break
            elif 1 <= escolha <= len(analises_pendentes):
                # Solicitar composição
                limpar_tela()
                print("=" * 60)
                print("           ENTRADA DE COMPOSIÇÕES")
                print("=" * 60)
                print("\\nInsira as composições das equipes.")
                print("Deixe em branco e pressione Enter para usar valores de exemplo.\\n")
                
                match_data = analises_pendentes[escolha-1]["match_data"]
                time_radiant = match_data["time_radiant"]
                time_dire = match_data["time_dire"]
                
                print(f"Composição para {time_radiant} vs {time_dire}\\n")
                
                composicao = input(f"Composições (formato: '{time_radiant}: herói1, herói2, ... | {time_dire}: herói1, herói2, ...'): ")
                if not composicao:
                    # Usar exemplo
                    composicao = f"{time_radiant}:\\nJuggernaut\\nStorm Spirit\\nEnigma\\nCrystal Maiden\\nUndying\\n\\n{time_dire}:\\nSpectre\\nInvoker\\nTidehunter\\nLion\\nEarthshaker"
                else:
                    # Formatar composição
                    if "|" in composicao:
                        partes = composicao.split("|")
                        if len(partes) == 2:
                            radiant = partes[0].strip()
                            dire = partes[1].strip()
                            
                            if ":" in radiant and ":" in dire:
                                composicao = f"{radiant.split(':', 1)[0].strip()}:\\n{radiant.split(':', 1)[1].strip().replace(',', '\\n')}\\n\\n{dire.split(':', 1)[0].strip()}:\\n{dire.split(':', 1)[1].strip().replace(',', '\\n')}"
                
                # Atualizar análise
                try:
                    nova_analise = analisador_comp.atualizar_com_composicao(escolha-1, composicao)
                    caminho_arquivo = salvar_analise(nova_analise)
                    
                    limpar_tela()
                    print(f"Análise atualizada e salva em: {caminho_arquivo}")
                    print("\\nResultados da análise:")
                    exibir_analise(nova_analise)
                    break
                except Exception as e:
                    print(f"Erro ao atualizar análise: {str(e)}")
                    input("\\nPressione Enter para continuar...")
            else:
                print("Opção inválida!")
                input("\\nPressione Enter para continuar...")
        except ValueError:
            print("Entrada inválida! Digite um número.")
            input("\\nPressione Enter para continuar...")
"""
        
        # Adicionar a nova função antes da função main
        conteudo = conteudo.replace("def main():", nova_funcao + "\ndef main():")
        
        # Modificar a função de análise para adicionar à lista de pendentes
        conteudo = conteudo.replace(
            "                analise = analisador.analisar_partida(texto_odds)\n                caminho_arquivo = salvar_analise(analise)",
            "                analise = analisador.analisar_partida(texto_odds)\n                # Adicionar à lista de pendentes para futura análise com composição\n                analisador_comp.adicionar_analise_pendente(analise)\n                caminho_arquivo = salvar_analise(analise)"
        )
        
        # Escrever o arquivo modificado
        with open(interface_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)
        
        print(f"Interface {interface_arquivo} atualizada com suporte a composições futuras.")
    
    except Exception as e:
        print(f"Erro ao integrar com interface: {str(e)}")

if __name__ == "__main__":
    # Integrar com a interface existente
    integrar_com_interface("interface_analisador.py")
