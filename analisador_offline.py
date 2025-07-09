"""
Analisador de Partidas de Dota 2 - Versão Offline

Este módulo permite analisar partidas de Dota 2 localmente, sem necessidade de conexão com internet.
Desenvolvido para uso com VSCode.
"""

import json
import os
import datetime
from typing import Dict, Any, List, Optional, Union

class AnalisadorPartidas:
    """Classe principal para análise de partidas de Dota 2"""
    
    def __init__(self):
        """Inicializa o analisador de partidas"""
        self.historico = []
        self.carregar_historico()
    
    def carregar_historico(self):
        """Carrega o histórico de análises anteriores, se existir"""
        try:
            if os.path.exists("historico_analises.json"):
                with open("historico_analises.json", "r", encoding="utf-8") as f:
                    self.historico = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar histórico: {str(e)}")
            self.historico = []
    
    def salvar_historico(self):
        """Salva o histórico de análises"""
        try:
            with open("historico_analises.json", "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {str(e)}")
    
    def analisar_partida(self, texto_odds: str, composicao: str = None) -> Dict[str, Any]:
        """
        Analisa uma partida com base nas odds e composições (opcional)
        
        Args:
            texto_odds: Texto contendo as odds da partida
            composicao: Texto contendo as composições das equipes (opcional)
            
        Returns:
            Dicionário com dados da partida e previsões
        """
        # Extrair informações básicas
        dados_partida = self.extrair_dados_partida(texto_odds)
        
        # Analisar composições se disponíveis
        if composicao:
            dados_composicao = self.analisar_composicao(composicao)
            dados_partida = self.combinar_dados(dados_partida, dados_composicao)
        
        # Gerar previsões
        previsoes = self.gerar_previsoes(dados_partida)
        
        # Gerar valuebets
        valuebets = self.gerar_valuebets(dados_partida)
        
        # Gerar explicações
        explicacoes = self.gerar_explicacoes(dados_partida)
        
        # Montar resultado final
        resultado = {
            "match_data": dados_partida,
            "predictions": {
                "previsoes": previsoes,
                "valuebets": valuebets,
                "explicacao": {
                    "fatores_chave": explicacoes
                }
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Adicionar ao histórico
        self.historico.append(resultado)
        self.salvar_historico()
        
        return resultado
    
    def extrair_dados_partida(self, texto_odds: str) -> Dict[str, Any]:
        """
        Extrai dados básicos da partida a partir do texto de odds
        
        Args:
            texto_odds: Texto contendo as odds da partida
            
        Returns:
            Dicionário com dados extraídos
        """
        linhas = texto_odds.strip().split('\n')
        
        # Extrair times
        times = linhas[0].split(' vs ')
        time_radiant = times[0].strip()
        time_dire = times[1].strip() if len(times) > 1 else "Time B"
        
        # Extrair torneio (se disponível)
        torneio = "Torneio não especificado"
        if len(linhas) > 1 and not any(x in linhas[1].lower() for x in ["odds", "kill", "map"]):
            torneio = linhas[1].strip()
        
        # Inicializar dados
        dados = {
            "time_radiant": time_radiant,
            "time_dire": time_dire,
            "torneio": torneio,
            "odds": {
                "vitoria_radiant": 0,
                "vitoria_dire": 0
            },
            "mercados": []
        }
        
        # Extrair odds de vitória
        for i, linha in enumerate(linhas):
            if "odds vencedor" in linha.lower() or "winner" in linha.lower():
                # Tentar extrair das próximas linhas
                for j in range(1, 5):
                    if i+j < len(linhas):
                        if time_radiant.lower() in linhas[i+j].lower():
                            partes = linhas[i+j].split(":")
                            if len(partes) > 1:
                                try:
                                    dados["odds"]["vitoria_radiant"] = float(partes[1].strip())
                                except ValueError:
                                    pass
                        elif time_dire.lower() in linhas[i+j].lower():
                            partes = linhas[i+j].split(":")
                            if len(partes) > 1:
                                try:
                                    dados["odds"]["vitoria_dire"] = float(partes[1].strip())
                                except ValueError:
                                    pass
        
        # Se não encontrou odds específicas, procurar por padrões numéricos
        if dados["odds"]["vitoria_radiant"] == 0 or dados["odds"]["vitoria_dire"] == 0:
            for i, linha in enumerate(linhas):
                if "winner" in linha.lower():
                    # Tentar extrair das próximas linhas
                    for j in range(1, 5):
                        if i+j < len(linhas):
                            try:
                                valor = float(linhas[i+j].strip())
                                if dados["odds"]["vitoria_radiant"] == 0:
                                    dados["odds"]["vitoria_radiant"] = valor
                                elif dados["odds"]["vitoria_dire"] == 0:
                                    dados["odds"]["vitoria_dire"] = valor
                            except ValueError:
                                pass
        
        # Extrair mercados
        self.extrair_mercado(linhas, dados, "total kills", "total_kills")
        self.extrair_mercado(linhas, dados, "duration", "duracao")
        self.extrair_mercado(linhas, dados, "kill handicap", "handicap_kills")
        
        return dados
    
    def extrair_mercado(self, linhas: List[str], dados: Dict[str, Any], termo: str, tipo: str):
        """
        Extrai dados de um mercado específico
        
        Args:
            linhas: Lista de linhas do texto
            dados: Dicionário de dados da partida
            termo: Termo a procurar nas linhas
            tipo: Tipo de mercado
        """
        for i, linha in enumerate(linhas):
            if termo.lower() in linha.lower():
                # Procurar por over/under nas próximas linhas
                valor = 0
                odds_over = 0
                odds_under = 0
                
                # Extrair valor do handicap
                try:
                    partes = linha.split("(")
                    if len(partes) > 1:
                        valor_str = partes[1].split(")")[0]
                        valor = float(valor_str)
                except:
                    pass
                
                # Se não encontrou valor no formato anterior, tentar outro formato
                if valor == 0:
                    try:
                        for j in range(0, 3):
                            if i+j < len(linhas) and "over" in linhas[i+j].lower():
                                partes = linhas[i+j].lower().split("over")
                                if len(partes) > 1:
                                    valor_str = partes[1].strip().split()[0]
                                    valor = float(valor_str)
                                    break
                    except:
                        pass
                
                # Procurar odds de over/under
                for j in range(0, 5):
                    if i+j < len(linhas):
                        linha_atual = linhas[i+j].lower()
                        if "over" in linha_atual and odds_over == 0:
                            try:
                                odds_over = float(linha_atual.split(":")[-1].strip())
                            except:
                                try:
                                    # Tentar outro formato
                                    partes = linha_atual.split()
                                    for k, parte in enumerate(partes):
                                        if "over" in parte and k+1 < len(partes):
                                            odds_over = float(partes[k+1])
                                except:
                                    pass
                        
                        if "under" in linha_atual and odds_under == 0:
                            try:
                                odds_under = float(linha_atual.split(":")[-1].strip())
                            except:
                                try:
                                    # Tentar outro formato
                                    partes = linha_atual.split()
                                    for k, parte in enumerate(partes):
                                        if "under" in parte and k+1 < len(partes):
                                            odds_under = float(partes[k+1])
                                except:
                                    pass
                
                # Se encontrou dados válidos, adicionar ao mercado
                if valor > 0 and odds_over > 0 and odds_under > 0:
                    dados["mercados"].append({
                        "tipo": tipo,
                        "valor": valor,
                        "odds_over": odds_over,
                        "odds_under": odds_under
                    })
                    break
    
    def analisar_composicao(self, composicao: str) -> Dict[str, Any]:
        """
        Analisa a composição das equipes
        
        Args:
            composicao: Texto contendo as composições
            
        Returns:
            Dicionário com dados da composição
        """
        # Implementação simplificada para análise de composição
        linhas = composicao.strip().split('\n')
        
        dados_composicao = {
            "herois_radiant": [],
            "herois_dire": [],
            "estilo_radiant": "",
            "estilo_dire": "",
            "vantagem_early": "",
            "vantagem_mid": "",
            "vantagem_late": ""
        }
        
        # Extrair heróis
        time_atual = "radiant"
        for linha in linhas:
            linha = linha.strip().lower()
            
            # Detectar mudança de time
            if "radiant" in linha or "time a" in linha:
                time_atual = "radiant"
                continue
            elif "dire" in linha or "time b" in linha:
                time_atual = "dire"
                continue
            
            # Adicionar herói ao time correspondente
            if linha and not any(x in linha for x in ["vs", "draft", "pick", "ban"]):
                if time_atual == "radiant":
                    dados_composicao["herois_radiant"].append(linha)
                else:
                    dados_composicao["herois_dire"].append(linha)
        
        # Determinar estilo de jogo com base nos heróis
        dados_composicao["estilo_radiant"] = self.determinar_estilo(dados_composicao["herois_radiant"])
        dados_composicao["estilo_dire"] = self.determinar_estilo(dados_composicao["herois_dire"])
        
        # Determinar vantagens por fase do jogo
        dados_composicao["vantagem_early"] = self.determinar_vantagem_fase(
            dados_composicao["herois_radiant"], 
            dados_composicao["herois_dire"], 
            "early"
        )
        
        dados_composicao["vantagem_mid"] = self.determinar_vantagem_fase(
            dados_composicao["herois_radiant"], 
            dados_composicao["herois_dire"], 
            "mid"
        )
        
        dados_composicao["vantagem_late"] = self.determinar_vantagem_fase(
            dados_composicao["herois_radiant"], 
            dados_composicao["herois_dire"], 
            "late"
        )
        
        return dados_composicao
    
    def determinar_estilo(self, herois: List[str]) -> str:
        """
        Determina o estilo de jogo com base nos heróis
        
        Args:
            herois: Lista de heróis
            
        Returns:
            Estilo de jogo (agressivo, equilibrado, defensivo)
        """
        # Heróis conhecidos por estilo
        herois_agressivos = ["juggernaut", "ursa", "slark", "huskar", "troll", "ember", "storm", 
                            "queen of pain", "puck", "tiny", "monkey king", "bloodseeker"]
        
        herois_defensivos = ["medusa", "spectre", "terrorblade", "naga", "arc warden", "drow", 
                            "sniper", "tinker", "techies", "treant", "winter wyvern"]
        
        # Contar estilos
        count_agressivo = sum(1 for h in herois if any(ha in h for ha in herois_agressivos))
        count_defensivo = sum(1 for h in herois if any(hd in h for hd in herois_defensivos))
        
        # Determinar estilo predominante
        if count_agressivo > count_defensivo:
            return "agressivo"
        elif count_defensivo > count_agressivo:
            return "defensivo"
        else:
            return "equilibrado"
    
    def determinar_vantagem_fase(self, herois_radiant: List[str], herois_dire: List[str], fase: str) -> str:
        """
        Determina qual time tem vantagem em determinada fase do jogo
        
        Args:
            herois_radiant: Lista de heróis do time Radiant
            herois_dire: Lista de heróis do time Dire
            fase: Fase do jogo (early, mid, late)
            
        Returns:
            Time com vantagem (radiant, dire, equilibrado)
        """
        # Heróis fortes por fase
        early_strong = ["juggernaut", "ursa", "huskar", "monkey king", "undying", "venomancer", 
                        "viper", "bristleback", "timbersaw", "batrider"]
        
        mid_strong = ["ember", "storm", "void spirit", "queen of pain", "puck", "dragon knight", 
                    "kunkka", "death prophet", "leshrac", "necrophos"]
        
        late_strong = ["medusa", "spectre", "terrorblade", "phantom lancer", "naga", "arc warden", 
                    "faceless void", "anti-mage", "morphling", "wraith king"]
        
        # Selecionar lista apropriada para a fase
        if fase == "early":
            strong_heroes = early_strong
        elif fase == "mid":
            strong_heroes = mid_strong
        else:  # late
            strong_heroes = late_strong
        
        # Contar heróis fortes por time
        count_radiant = sum(1 for h in herois_radiant if any(sh in h for sh in strong_heroes))
        count_dire = sum(1 for h in herois_dire if any(sh in h for sh in strong_heroes))
        
        # Determinar vantagem
        if count_radiant > count_dire:
            return "radiant"
        elif count_dire > count_radiant:
            return "dire"
        else:
            return "equilibrado"
    
    def combinar_dados(self, dados_partida: Dict[str, Any], dados_composicao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combina dados da partida com dados de composição
        
        Args:
            dados_partida: Dicionário com dados da partida
            dados_composicao: Dicionário com dados da composição
            
        Returns:
            Dicionário combinado
        """
        # Criar cópia dos dados da partida
        dados_combinados = dados_partida.copy()
        
        # Adicionar dados de composição
        dados_combinados["composicao"] = dados_composicao
        
        return dados_combinados
    
    def gerar_previsoes(self, dados_partida: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera previsões com base nos dados da partida
        
        Args:
            dados_partida: Dicionário com dados da partida
            
        Returns:
            Dicionário com previsões
        """
        # Inicializar previsões
        previsoes = {
            "duracao_partida": {
                "valor": 0,
                "confianca": 0,
                "range": [0, 0]
            },
            "total_kills": {
                "valor": 0,
                "confianca": 0,
                "range": [0, 0]
            },
            "diferenca_kills": {
                "valor": 0,
                "confianca": 0,
                "range": [0, 0]
            }
        }
        
        # Verificar se há dados de odds
        odds_radiant = dados_partida["odds"]["vitoria_radiant"]
        odds_dire = dados_partida["odds"]["vitoria_dire"]
        
        # Calcular diferença de kills com base nas odds
        if odds_radiant > 0 and odds_dire > 0:
            # Quanto menor a odd, maior a vantagem
            if odds_radiant < odds_dire:
                # Time Radiant é favorito
                diff_odds = odds_dire / odds_radiant
                previsoes["diferenca_kills"]["valor"] = round(diff_odds * 3)
            else:
                # Time Dire é favorito
                diff_odds = odds_radiant / odds_dire
                previsoes["diferenca_kills"]["valor"] = -round(diff_odds * 3)
            
            # Definir range e confiança
            valor_diff = abs(previsoes["diferenca_kills"]["valor"])
            previsoes["diferenca_kills"]["range"] = [max(0, valor_diff - 3), valor_diff + 3]
            previsoes["diferenca_kills"]["confianca"] = min(0.85, 0.5 + (abs(odds_radiant - odds_dire) / 10))
        
        # Processar mercados
        for mercado in dados_partida["mercados"]:
            if mercado["tipo"] == "total_kills":
                # Usar valor do mercado como base
                valor = mercado["valor"]
                
                # Ajustar com base nas odds
                odds_diff = abs(mercado["odds_over"] - mercado["odds_under"])
                if mercado["odds_over"] < mercado["odds_under"]:
                    # Over é mais provável
                    previsoes["total_kills"]["valor"] = round(valor + (odds_diff * 2))
                else:
                    # Under é mais provável
                    previsoes["total_kills"]["valor"] = round(valor - (odds_diff * 2))
                
                # Definir range e confiança
                previsoes["total_kills"]["range"] = [
                    max(0, previsoes["total_kills"]["valor"] - 4),
                    previsoes["total_kills"]["valor"] + 4
                ]
                previsoes["total_kills"]["confianca"] = min(0.85, 0.5 + (odds_diff / 2))
            
            elif mercado["tipo"] == "duracao":
                # Usar valor do mercado como base (convertendo para minutos se necessário)
                valor = mercado["valor"]
                if valor > 100:  # Se for em segundos
                    valor = valor / 60
                
                # Ajustar com base nas odds
                odds_diff = abs(mercado["odds_over"] - mercado["odds_under"])
                if mercado["odds_over"] < mercado["odds_under"]:
                    # Over é mais provável
                    previsoes["duracao_partida"]["valor"] = round(valor + (odds_diff * 1.5))
                else:
                    # Under é mais provável
                    previsoes["duracao_partida"]["valor"] = round(valor - (odds_diff * 1.5))
                
                # Definir range e confiança
                previsoes["duracao_partida"]["range"] = [
                    max(0, previsoes["duracao_partida"]["valor"] - 3),
                    previsoes["duracao_partida"]["valor"] + 3
                ]
                previsoes["duracao_partida"]["confianca"] = min(0.85, 0.5 + (odds_diff / 2))
        
        # Se não encontrou mercados específicos, usar valores padrão
        if previsoes["total_kills"]["valor"] == 0:
            previsoes["total_kills"]["valor"] = 47
            previsoes["total_kills"]["range"] = [43, 51]
            previsoes["total_kills"]["confianca"] = 0.68
        
        if previsoes["duracao_partida"]["valor"] == 0:
            previsoes["duracao_partida"]["valor"] = 38.5
            previsoes["duracao_partida"]["range"] = [36, 41]
            previsoes["duracao_partida"]["confianca"] = 0.75
        
        # Ajustar previsões com base em dados de composição, se disponíveis
        if "composicao" in dados_partida:
            self.ajustar_previsoes_com_composicao(previsoes, dados_partida["composicao"])
        
        return previsoes
    
    def ajustar_previsoes_com_composicao(self, previsoes: Dict[str, Any], dados_composicao: Dict[str, Any]):
        """
        Ajusta previsões com base nos dados de composição
        
        Args:
            previsoes: Dicionário com previsões
            dados_composicao: Dicionário com dados de composição
        """
        # Ajustar duração com base no estilo de jogo
        if dados_composicao["estilo_radiant"] == "agressivo" and dados_composicao["estilo_dire"] == "agressivo":
            # Dois times agressivos = partida mais curta
            previsoes["duracao_partida"]["valor"] = max(25, previsoes["duracao_partida"]["valor"] - 5)
            previsoes["duracao_partida"]["range"] = [
                max(20, previsoes["duracao_partida"]["valor"] - 3),
                previsoes["duracao_partida"]["valor"] + 3
            ]
        elif dados_composicao["estilo_radiant"] == "defensivo" and dados_composicao["estilo_dire"] == "defensivo":
            # Dois times defensivos = partida mais longa
            previsoes["duracao_partida"]["valor"] = min(60, previsoes["duracao_partida"]["valor"] + 7)
            previsoes["duracao_partida"]["range"] = [
                previsoes["duracao_partida"]["valor"] - 3,
                min(70, previsoes["duracao_partida"]["valor"] + 5)
            ]
        
        # Ajustar total de kills com base no estilo de jogo
        if dados_composicao["estilo_radiant"] == "agressivo" or dados_composicao["estilo_dire"] == "agressivo":
            # Times agressivos = mais kills
            previsoes["total_kills"]["valor"] = previsoes["total_kills"]["valor"] + 5
            previsoes["total_kills"]["range"] = [
                previsoes["total_kills"]["valor"] - 4,
                previsoes["total_kills"]["valor"] + 6
            ]
        
        # Ajustar diferença de kills com base nas vantagens por fase
        vantagens = {
            "radiant": 0,
            "dire": 0
        }
        
        if dados_composicao["vantagem_early"] == "radiant":
            vantagens["radiant"] += 1
        elif dados_composicao["vantagem_early"] == "dire":
            vantagens["dire"] += 1
        
        if dados_composicao["vantagem_mid"] == "radiant":
            vantagens["radiant"] += 1
        elif dados_composicao["vantagem_mid"] == "dire":
            vantagens["dire"] += 1
        
        if dados_composicao["vantagem_late"] == "radiant":
            vantagens["radiant"] += 1
        elif dados_composicao["vantagem_late"] == "dire":
            vantagens["dire"] += 1
        
        # Ajustar diferença de kills com base nas vantagens
        diff_vantagens = vantagens["radiant"] - vantagens["dire"]
        if diff_vantagens > 0:
            # Radiant tem mais vantagens
            previsoes["diferenca_kills"]["valor"] = abs(previsoes["diferenca_kills"]["valor"]) + diff_vantagens * 2
        elif diff_vantagens < 0:
            # Dire tem mais vantagens
            previsoes["diferenca_kills"]["valor"] = -abs(previsoes["diferenca_kills"]["valor"]) - abs(diff_vantagens) * 2
        
        # Aumentar confiança nas previsões
        previsoes["duracao_partida"]["confianca"] = min(0.95, previsoes["duracao_partida"]["confianca"] + 0.1)
        previsoes["total_kills"]["confianca"] = min(0.95, previsoes["total_kills"]["confianca"] + 0.1)
        previsoes["diferenca_kills"]["confianca"] = min(0.95, previsoes["diferenca_kills"]["confianca"] + 0.1)
    
    def gerar_valuebets(self, dados_partida: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera recomendações de valuebets com base nos dados da partida
        
        Args:
            dados_partida: Dicionário com dados da partida
            
        Returns:
            Lista de valuebets recomendadas
        """
        valuebets = []
        
        # Obter previsões
        previsoes = self.gerar_previsoes(dados_partida)
        
        # Analisar mercados
        for mercado in dados_partida["mercados"]:
            if mercado["tipo"] == "total_kills":
                # Comparar previsão com linha do mercado
                previsao = previsoes["total_kills"]["valor"]
                linha = mercado["valor"]
                
                if previsao > linha + 2:
                    # Recomendar Over
                    valuebets.append({
                        "mercado": "Total de kills",
                        "handicap": linha,
                        "recomendacao": "Over",
                        "odds": mercado["odds_over"],
                        "valor_esperado": min(0.3, (previsao - linha) / 20),
                        "confianca": previsoes["total_kills"]["confianca"]
                    })
                elif previsao < linha - 2:
                    # Recomendar Under
                    valuebets.append({
                        "mercado": "Total de kills",
                        "handicap": linha,
                        "recomendacao": "Under",
                        "odds": mercado["odds_under"],
                        "valor_esperado": min(0.3, (linha - previsao) / 20),
                        "confianca": previsoes["total_kills"]["confianca"]
                    })
            
            elif mercado["tipo"] == "duracao":
                # Comparar previsão com linha do mercado
                previsao = previsoes["duracao_partida"]["valor"]
                linha = mercado["valor"]
                
                if previsao > linha + 2:
                    # Recomendar Over
                    valuebets.append({
                        "mercado": "Duração da partida",
                        "handicap": linha,
                        "recomendacao": "Over",
                        "odds": mercado["odds_over"],
                        "valor_esperado": min(0.3, (previsao - linha) / 10),
                        "confianca": previsoes["duracao_partida"]["confianca"]
                    })
                elif previsao < linha - 2:
                    # Recomendar Under
                    valuebets.append({
                        "mercado": "Duração da partida",
                        "handicap": linha,
                        "recomendacao": "Under",
                        "odds": mercado["odds_under"],
                        "valor_esperado": min(0.3, (linha - previsao) / 10),
                        "confianca": previsoes["duracao_partida"]["confianca"]
                    })
            
            elif mercado["tipo"] == "handicap_kills":
                # Comparar previsão com linha do mercado
                previsao = previsoes["diferenca_kills"]["valor"]
                linha = mercado["valor"]
                
                # Determinar qual time tem handicap positivo
                time_handicap_positivo = dados_partida["time_radiant"]
                if "handicap" in mercado and mercado["handicap"] < 0:
                    time_handicap_positivo = dados_partida["time_dire"]
                
                # Ajustar previsão para formato do mercado
                if time_handicap_positivo == dados_partida["time_dire"]:
                    previsao = -previsao
                
                if previsao > linha + 2:
                    # Recomendar Over
                    valuebets.append({
                        "mercado": "Handicap de kills",
                        "handicap": linha,
                        "recomendacao": f"{time_handicap_positivo} ({linha})",
                        "odds": mercado["odds_over"],
                        "valor_esperado": min(0.3, (previsao - linha) / 10),
                        "confianca": previsoes["diferenca_kills"]["confianca"]
                    })
                elif previsao < linha - 2:
                    # Recomendar Under
                    time_oposto = dados_partida["time_dire"] if time_handicap_positivo == dados_partida["time_radiant"] else dados_partida["time_radiant"]
                    valuebets.append({
                        "mercado": "Handicap de kills",
                        "handicap": -linha,
                        "recomendacao": f"{time_oposto} ({-linha})",
                        "odds": mercado["odds_under"],
                        "valor_esperado": min(0.3, (linha - previsao) / 10),
                        "confianca": previsoes["diferenca_kills"]["confianca"]
                    })
        
        # Adicionar valuebets específicas com base nas odds de vitória
        odds_radiant = dados_partida["odds"]["vitoria_radiant"]
        odds_dire = dados_partida["odds"]["vitoria_dire"]
        
        # Verificar se há vantagem significativa
        if odds_radiant < odds_dire * 0.7:
            # Radiant é muito favorito
            valuebets.append({
                "mercado": "First Blood",
                "handicap": 0,
                "recomendacao": dados_partida["time_radiant"],
                "odds": 1.8,  # Valor estimado
                "valor_esperado": 0.15,
                "confianca": 0.73
            })
        elif odds_dire < odds_radiant * 0.7:
            # Dire é muito favorito
            valuebets.append({
                "mercado": "First Blood",
                "handicap": 0,
                "recomendacao": dados_partida["time_dire"],
                "odds": 1.8,  # Valor estimado
                "valor_esperado": 0.15,
                "confianca": 0.73
            })
        
        # Adicionar valuebets específicas com base na composição, se disponível
        if "composicao" in dados_partida:
            self.adicionar_valuebets_composicao(valuebets, dados_partida)
        
        # Ordenar valuebets por valor esperado
        valuebets.sort(key=lambda x: x["valor_esperado"], reverse=True)
        
        return valuebets
    
    def adicionar_valuebets_composicao(self, valuebets: List[Dict[str, Any]], dados_partida: Dict[str, Any]):
        """
        Adiciona valuebets específicas com base na composição
        
        Args:
            valuebets: Lista de valuebets
            dados_partida: Dicionário com dados da partida
        """
        composicao = dados_partida["composicao"]
        
        # Adicionar valuebet para First Tower com base na vantagem early
        if composicao["vantagem_early"] == "radiant":
            valuebets.append({
                "mercado": "First Tower",
                "handicap": 0,
                "recomendacao": dados_partida["time_radiant"],
                "odds": 1.8,  # Valor estimado
                "valor_esperado": 0.2,
                "confianca": 0.8
            })
        elif composicao["vantagem_early"] == "dire":
            valuebets.append({
                "mercado": "First Tower",
                "handicap": 0,
                "recomendacao": dados_partida["time_dire"],
                "odds": 1.8,  # Valor estimado
                "valor_esperado": 0.2,
                "confianca": 0.8
            })
        
        # Adicionar valuebet para First Aegis com base na vantagem mid
        if composicao["vantagem_mid"] == "radiant":
            valuebets.append({
                "mercado": "First Aegis",
                "handicap": 0,
                "recomendacao": dados_partida["time_radiant"],
                "odds": 1.85,  # Valor estimado
                "valor_esperado": 0.18,
                "confianca": 0.75
            })
        elif composicao["vantagem_mid"] == "dire":
            valuebets.append({
                "mercado": "First Aegis",
                "handicap": 0,
                "recomendacao": dados_partida["time_dire"],
                "odds": 1.85,  # Valor estimado
                "valor_esperado": 0.18,
                "confianca": 0.75
            })
        
        # Adicionar valuebet para Race to Kills com base no estilo
        if composicao["estilo_radiant"] == "agressivo" and composicao["estilo_dire"] != "agressivo":
            valuebets.append({
                "mercado": "Race to 10 kills",
                "handicap": 0,
                "recomendacao": dados_partida["time_radiant"],
                "odds": 1.75,  # Valor estimado
                "valor_esperado": 0.22,
                "confianca": 0.82
            })
        elif composicao["estilo_dire"] == "agressivo" and composicao["estilo_radiant"] != "agressivo":
            valuebets.append({
                "mercado": "Race to 10 kills",
                "handicap": 0,
                "recomendacao": dados_partida["time_dire"],
                "odds": 1.75,  # Valor estimado
                "valor_esperado": 0.22,
                "confianca": 0.82
            })
    
    def gerar_explicacoes(self, dados_partida: Dict[str, Any]) -> List[str]:
        """
        Gera explicações para as previsões
        
        Args:
            dados_partida: Dicionário com dados da partida
            
        Returns:
            Lista de explicações
        """
        explicacoes = []
        
        # Obter previsões
        previsoes = self.gerar_previsoes(dados_partida)
        
        # Explicações baseadas nas odds
        odds_radiant = dados_partida["odds"]["vitoria_radiant"]
        odds_dire = dados_partida["odds"]["vitoria_dire"]
        
        if odds_radiant < odds_dire:
            # Radiant é favorito
            explicacoes.append(f"{dados_partida['time_radiant']} é favorito com odds de {odds_radiant} contra {odds_dire} do {dados_partida['time_dire']}.")
            
            if odds_radiant < 1.5:
                explicacoes.append(f"{dados_partida['time_radiant']} é fortemente favorito, o que sugere uma vitória confortável.")
            elif odds_radiant < 2.0:
                explicacoes.append(f"{dados_partida['time_radiant']} tem vantagem moderada, mas o {dados_partida['time_dire']} pode oferecer resistência.")
        else:
            # Dire é favorito
            explicacoes.append(f"{dados_partida['time_dire']} é favorito com odds de {odds_dire} contra {odds_radiant} do {dados_partida['time_radiant']}.")
            
            if odds_dire < 1.5:
                explicacoes.append(f"{dados_partida['time_dire']} é fortemente favorito, o que sugere uma vitória confortável.")
            elif odds_dire < 2.0:
                explicacoes.append(f"{dados_partida['time_dire']} tem vantagem moderada, mas o {dados_partida['time_radiant']} pode oferecer resistência.")
        
        # Explicações baseadas nas previsões
        if previsoes["total_kills"]["valor"] > 50:
            explicacoes.append(f"A previsão de {previsoes['total_kills']['valor']} kills totais sugere uma partida muito agressiva.")
        elif previsoes["total_kills"]["valor"] < 40:
            explicacoes.append(f"A previsão de apenas {previsoes['total_kills']['valor']} kills totais sugere uma partida mais estratégica e menos agressiva.")
        else:
            explicacoes.append(f"A previsão de {previsoes['total_kills']['valor']} kills totais está dentro da média para partidas deste nível.")
        
        if abs(previsoes["diferenca_kills"]["valor"]) > 10:
            time_dominante = dados_partida["time_radiant"] if previsoes["diferenca_kills"]["valor"] > 0 else dados_partida["time_dire"]
            explicacoes.append(f"A diferença prevista de {abs(previsoes['diferenca_kills']['valor'])} kills sugere dominância do {time_dominante}.")
        
        if previsoes["duracao_partida"]["valor"] < 30:
            explicacoes.append(f"A duração prevista de {previsoes['duracao_partida']['valor']} minutos sugere uma partida rápida, possivelmente com estratégia de push early.")
        elif previsoes["duracao_partida"]["valor"] > 45:
            explicacoes.append(f"A duração prevista de {previsoes['duracao_partida']['valor']} minutos sugere uma partida longa, possivelmente com foco em late game.")
        
        # Explicações baseadas na composição, se disponível
        if "composicao" in dados_partida:
            self.adicionar_explicacoes_composicao(explicacoes, dados_partida)
        
        return explicacoes
    
    def adicionar_explicacoes_composicao(self, explicacoes: List[str], dados_partida: Dict[str, Any]):
        """
        Adiciona explicações específicas com base na composição
        
        Args:
            explicacoes: Lista de explicações
            dados_partida: Dicionário com dados da partida
        """
        composicao = dados_partida["composicao"]
        
        # Explicações baseadas no estilo de jogo
        if composicao["estilo_radiant"] == "agressivo":
            explicacoes.append(f"A composição do {dados_partida['time_radiant']} é agressiva, favorecendo engajamentos e lutas frequentes.")
        elif composicao["estilo_radiant"] == "defensivo":
            explicacoes.append(f"A composição do {dados_partida['time_radiant']} é defensiva, favorecendo um jogo mais cauteloso e focado em farm.")
        
        if composicao["estilo_dire"] == "agressivo":
            explicacoes.append(f"A composição do {dados_partida['time_dire']} é agressiva, favorecendo engajamentos e lutas frequentes.")
        elif composicao["estilo_dire"] == "defensivo":
            explicacoes.append(f"A composição do {dados_partida['time_dire']} é defensiva, favorecendo um jogo mais cauteloso e focado em farm.")
        
        # Explicações baseadas nas vantagens por fase
        if composicao["vantagem_early"] == "radiant":
            explicacoes.append(f"{dados_partida['time_radiant']} tem vantagem no early game, o que pode resultar em controle de mapa inicial.")
        elif composicao["vantagem_early"] == "dire":
            explicacoes.append(f"{dados_partida['time_dire']} tem vantagem no early game, o que pode resultar em controle de mapa inicial.")
        
        if composicao["vantagem_mid"] == "radiant":
            explicacoes.append(f"{dados_partida['time_radiant']} tem vantagem no mid game, período crítico para estabelecer controle de objetivos.")
        elif composicao["vantagem_mid"] == "dire":
            explicacoes.append(f"{dados_partida['time_dire']} tem vantagem no mid game, período crítico para estabelecer controle de objetivos.")
        
        if composicao["vantagem_late"] == "radiant":
            explicacoes.append(f"{dados_partida['time_radiant']} tem vantagem no late game, o que pode ser decisivo em partidas prolongadas.")
        elif composicao["vantagem_late"] == "dire":
            explicacoes.append(f"{dados_partida['time_dire']} tem vantagem no late game, o que pode ser decisivo em partidas prolongadas.")
    
    def formatar_analise(self, resultado: Dict[str, Any]) -> str:
        """
        Formata os resultados da análise para exibição
        
        Args:
            resultado: Dicionário com resultados da análise
            
        Returns:
            Texto formatado para exibição
        """
        match_data = resultado["match_data"]
        predictions = resultado["predictions"]
        
        # Formatar cabeçalho
        header = f"# Análise: {match_data['time_radiant']} vs {match_data['time_dire']}\n\n"
        
        if "composicao" in match_data:
            header += "## Análise com Composições Incluídas\n\n"
        else:
            header += "## Análise Baseada em Odds (Sem Composições)\n\n"
        
        # Formatar previsões
        prev_section = "## Previsões\n\n"
        
        previsoes = predictions["previsoes"]
        if previsoes:
            # Duração
            duracao = previsoes.get("duracao_partida", {})
            if duracao:
                prev_section += f"### Duração da Partida\n"
                prev_section += f"- **Previsão**: {duracao.get('valor', 'N/A')} minutos\n"
                range_val = duracao.get('range', [0, 0])
                prev_section += f"- **Range**: {range_val[0]} - {range_val[1]} minutos\n"
                confianca = duracao.get('confianca', 0)
                prev_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
            
            # Total de kills
            kills = previsoes.get("total_kills", {})
            if kills:
                prev_section += f"### Total de Abates\n"
                prev_section += f"- **Previsão**: {kills.get('valor', 'N/A')} kills\n"
                range_val = kills.get('range', [0, 0])
                prev_section += f"- **Range**: {range_val[0]} - {range_val[1]} kills\n"
                confianca = kills.get('confianca', 0)
                prev_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
            
            # Diferença de kills
            diff = previsoes.get("diferenca_kills", {})
            if diff:
                prev_section += f"### Diferença de Abates\n"
                valor = diff.get('valor', 0)
                time_favorecido = match_data['time_radiant'] if valor > 0 else match_data['time_dire']
                prev_section += f"- **Previsão**: {abs(valor)} kills a favor de {time_favorecido}\n"
                range_val = diff.get('range', [0, 0])
                prev_section += f"- **Range**: {range_val[0]} - {range_val[1]} kills\n"
                confianca = diff.get('confianca', 0)
                prev_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
        
        # Formatar valuebets
        vb_section = "## Valuebets Recomendadas\n\n"
        
        valuebets = predictions.get("valuebets", [])
        if not valuebets:
            vb_section += "Nenhuma valuebet identificada para esta partida.\n\n"
        else:
            for i, vb in enumerate(valuebets, 1):
                vb_section += f"### Valuebet {i}: {vb.get('mercado', 'N/A')}\n"
                vb_section += f"- **Recomendação**: {vb.get('recomendacao', 'N/A')}\n"
                vb_section += f"- **Odds**: {vb.get('odds', 'N/A')}\n"
                valor_esperado = vb.get('valor_esperado', 0)
                vb_section += f"- **Valor Esperado**: +{(valor_esperado*100):.1f}%\n"
                confianca = vb.get('confianca', 0)
                vb_section += f"- **Confiança**: {int(confianca*100)}%\n\n"
        
        # Formatar explicações
        exp_section = "## Análise Detalhada\n\n"
        
        explicacao = predictions.get("explicacao", {})
        fatores_chave = explicacao.get("fatores_chave", [])
        if not fatores_chave:
            exp_section += "Sem análise detalhada disponível para esta partida.\n"
        else:
            for exp in fatores_chave:
                exp_section += f"- {exp}\n"
        
        # Adicionar seção sobre composições futuras se não houver composição
        if "composicao" not in match_data:
            future_section = "\n## Análise Futura com Composições\n\n"
            future_section += "Quando as composições (drafts) das equipes estiverem disponíveis, a análise será atualizada com:\n\n"
            future_section += "- Avaliação da sinergia entre os heróis de cada equipe\n"
            future_section += "- Análise de timings de poder para cada composição\n"
            future_section += "- Previsões mais precisas baseadas no estilo de jogo de cada herói\n"
            future_section += "- Valuebets específicas considerando as interações entre composições\n"
            future_section += "- Confiança aumentada nas previsões devido aos dados adicionais\n\n"
            future_section += "Para obter esta análise atualizada, envie as informações de draft assim que estiverem disponíveis."
        else:
            future_section = ""
        
        # Combinar tudo
        return header + prev_section + vb_section + exp_section + future_section
