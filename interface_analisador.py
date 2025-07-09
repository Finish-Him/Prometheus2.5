"""
Interface do Analisador/Preditor de Partidas de Dota 2

Este módulo implementa uma interface gráfica para o analisador/preditor de duração
de partidas de Dota 2, permitindo ao usuário inserir dados de uma partida e obter
previsões sobre sua duração.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import joblib
from datetime import datetime

# Importar a função de predição
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from predict_duration import predict_match_duration

class DotaAnalyzerApp:
    """Aplicação principal do analisador de partidas de Dota 2"""
    
    def __init__(self, root):
        """Inicializa a interface gráfica"""
        self.root = root
        self.root.title("Analisador de Partidas de Dota 2 - Oráculo 3.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 11))
        self.style.configure("TButton", font=("Arial", 11))
        self.style.configure("TEntry", font=("Arial", 11))
        self.style.configure("Header.TLabel", font=("Arial", 14, "bold"))
        
        # Criar notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Criar abas
        self.tab_predicao = ttk.Frame(self.notebook)
        self.tab_historico = ttk.Frame(self.notebook)
        self.tab_sobre = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_predicao, text="Predição de Duração")
        self.notebook.add(self.tab_historico, text="Histórico de Análises")
        self.notebook.add(self.tab_sobre, text="Sobre")
        
        # Configurar as abas
        self.setup_tab_predicao()
        self.setup_tab_historico()
        self.setup_tab_sobre()
        
        # Histórico de análises
        self.historico = []
        self.carregar_historico()
    
    def setup_tab_predicao(self):
        """Configura a aba de predição de duração"""
        # Frame principal
        main_frame = ttk.Frame(self.tab_predicao, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Predição de Duração de Partidas", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Frame para entrada de dados
        input_frame = ttk.LabelFrame(main_frame, text="Dados da Partida", padding=10)
        input_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Variáveis para armazenar os valores dos campos
        self.var_times = tk.StringVar()
        self.var_torneio = tk.StringVar()
        self.var_total_kills = tk.StringVar(value="0")
        self.var_radiant_score = tk.StringVar(value="0")
        self.var_dire_score = tk.StringVar(value="0")
        self.var_first_blood_time = tk.StringVar(value="0")
        self.var_tower_status_radiant = tk.StringVar(value="0")
        self.var_tower_status_dire = tk.StringVar(value="0")
        self.var_barracks_status_radiant = tk.StringVar(value="0")
        self.var_barracks_status_dire = tk.StringVar(value="0")
        
        # Campos de entrada
        ttk.Label(input_frame, text="Times (ex: Team A vs Team B):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_times, width=40).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Torneio:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_torneio, width=40).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Total de Kills:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_total_kills, width=10).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Score Radiant:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_radiant_score, width=10).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Score Dire:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_dire_score, width=10).grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Tempo do First Blood (segundos):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_first_blood_time, width=10).grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Status das Torres Radiant:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_tower_status_radiant, width=10).grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Status das Torres Dire:").grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_tower_status_dire, width=10).grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Status dos Barracks Radiant:").grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_barracks_status_radiant, width=10).grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Status dos Barracks Dire:").grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.var_barracks_status_dire, width=10).grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Botões
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Prever Duração", command=self.prever_duracao).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Limpar Campos", command=self.limpar_campos).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Carregar Exemplo", command=self.carregar_exemplo).grid(row=0, column=2, padx=5)
        
        # Frame para resultados
        self.result_frame = ttk.LabelFrame(main_frame, text="Resultados da Análise", padding=10)
        self.result_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        # Configurar o frame de resultados
        self.setup_result_frame()
        
        # Configurar pesos das linhas e colunas
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def setup_result_frame(self):
        """Configura o frame de resultados"""
        # Limpar o frame
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # Adicionar labels para os resultados
        ttk.Label(self.result_frame, text="Aguardando análise...", style="Header.TLabel").pack(pady=10)
        
        # Adicionar botão para salvar análise
        ttk.Button(self.result_frame, text="Salvar Análise", command=self.salvar_analise, state=tk.DISABLED).pack(pady=10)
    
    def setup_tab_historico(self):
        """Configura a aba de histórico de análises"""
        # Frame principal
        main_frame = ttk.Frame(self.tab_historico, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Histórico de Análises", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Frame para lista de análises
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox para análises
        self.analises_listbox = tk.Listbox(list_frame, width=50, height=20, font=("Arial", 11))
        self.analises_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar scrollbar
        self.analises_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.analises_listbox.yview)
        
        # Frame para detalhes da análise
        self.detalhes_frame = ttk.LabelFrame(main_frame, text="Detalhes da Análise", padding=10)
        self.detalhes_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Ver Detalhes", command=self.ver_detalhes).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Excluir Análise", command=self.excluir_analise).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Exportar Histórico", command=self.exportar_historico).grid(row=0, column=2, padx=5)
        
        # Configurar pesos das linhas e colunas
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Vincular evento de seleção
        self.analises_listbox.bind('<<ListboxSelect>>', self.on_analise_select)
    
    def setup_tab_sobre(self):
        """Configura a aba sobre o analisador"""
        # Frame principal
        main_frame = ttk.Frame(self.tab_sobre, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Sobre o Analisador de Partidas de Dota 2", style="Header.TLabel").pack(pady=10)
        
        # Informações
        info_text = """
        Analisador/Preditor de Partidas de Dota 2 - Oráculo 3.0
        
        Este aplicativo permite analisar partidas de Dota 2 e prever sua duração com base em
        diversos fatores como total de kills, scores das equipes, status de torres e barracks.
        
        Desenvolvido com base na base de dados Oráculo 3.0, o analisador utiliza modelos de
        machine learning para fazer previsões precisas sobre a duração das partidas.
        
        Funcionalidades:
        - Previsão de duração de partidas
        - Histórico de análises
        - Exportação de resultados
        
        O modelo utilizado para previsão é o Ridge Regression, treinado com dados históricos
        de partidas de Dota 2. O modelo apresenta um erro médio quadrático (RMSE) de aproximadamente
        7.24 minutos nas previsões.
        
        Versão: 1.0
        Data: Abril de 2025
        """
        
        text_widget = tk.Text(main_frame, wrap=tk.WORD, width=80, height=20, font=("Arial", 11))
        text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
    
    def prever_duracao(self):
        """Realiza a previsão de duração da partida"""
        try:
            # Obter os valores dos campos
            features = {
                'total_kills': int(self.var_total_kills.get()),
                'radiant_score': int(self.var_radiant_score.get()),
                'dire_score': int(self.var_dire_score.get()),
                'first_blood_time': int(self.var_first_blood_time.get()),
                'tower_status_radiant': int(self.var_tower_status_radiant.get()),
                'tower_status_dire': int(self.var_tower_status_dire.get()),
                'barracks_status_radiant': int(self.var_barracks_status_radiant.get()),
                'barracks_status_dire': int(self.var_barracks_status_dire.get())
            }
            
            # Fazer a previsão
            duracao_prevista = predict_match_duration(features)
            
            # Atualizar o frame de resultados
            self.mostrar_resultados(duracao_prevista, features)
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro ao processar os dados: {str(e)}\n\nCertifique-se de que todos os campos numéricos contêm valores válidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def mostrar_resultados(self, duracao_prevista, features):
        """Mostra os resultados da previsão"""
        # Limpar o frame
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # Adicionar resultados
        ttk.Label(self.result_frame, text="Resultados da Análise", style="Header.TLabel").pack(pady=10)
        
        # Duração prevista
        result_frame = ttk.Frame(self.result_frame)
        result_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(result_frame, text="Duração Prevista:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(result_frame, text=f"{duracao_prevista:.2f} minutos", font=("Arial", 12)).grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Converter para horas e minutos
        horas = int(duracao_prevista // 60)
        minutos = int(duracao_prevista % 60)
        segundos = int((duracao_prevista * 60) % 60)
        
        if horas > 0:
            tempo_formatado = f"{horas}h {minutos}m {segundos}s"
        else:
            tempo_formatado = f"{minutos}m {segundos}s"
        
        ttk.Label(result_frame, text="Tempo Formatado:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(result_frame, text=tempo_formatado, font=("Arial", 12)).grid(row=1, column=1, padx=5, sticky=tk.W)
        
        # Informações adicionais
        ttk.Label(self.result_frame, text="Fatores Considerados:", font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        info_text = f"""
        • Total de Kills: {features['total_kills']}
        • Score Radiant: {features['radiant_score']}
        • Score Dire: {features['dire_score']}
        • Tempo do First Blood: {features['first_blood_time']} segundos
        • Status das Torres Radiant: {features['tower_status_radiant']}
        • Status das Torres Dire: {features['tower_status_dire']}
        • Status dos Barracks Radiant: {features['barracks_status_radiant']}
        • Status dos Barracks Dire: {features['barracks_status_dire']}
        """
        
        info_label = ttk.Label(self.result_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W, padx=5)
        
        # Adicionar botão para salvar análise
        ttk.Button(self.result_frame, text="Salvar Análise", command=lambda: self.salvar_analise(duracao_prevista, features)).pack(pady=10)
    
    def salvar_analise(self, duracao_prevista=None, features=None):
        """Salva a análise no histórico"""
        if duracao_prevista is None or features is None:
            messagebox.showinfo("Informação", "Nenhuma análise para salvar.")
            return
        
        # Criar registro da análise
        analise = {
            'data': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'times': self.var_times.get(),
            'torneio': self.var_torneio.get(),
            'features': features,
            'duracao_prevista': duracao_prevista
        }
        
        # Adicionar ao histórico
        self.historico.append(analise)
        
        # Salvar histórico
        self.salvar_historico()
        
        # Atualizar listbox
        self.atualizar_listbox_historico()
        
        messagebox.showinfo("Sucesso", "Análise salva com sucesso!")
    
    def carregar_historico(self):
        """Carrega o histórico de análises"""
        try:
            if os.path.exists("historico_analises.json"):
                self.historico = pd.read_json("historico_analises.json").to_dict('records')
                self.atualizar_listbox_historico()
        except Exception as e:
            print(f"Erro ao carregar histórico: {str(e)}")
            self.historico = []
    
    def salvar_historico(self):
        """Salva o histórico de análises"""
        try:
            pd.DataFrame(self.historico).to_json("historico_analises.json", orient='records')
        except Exception as e:
            print(f"Erro ao salvar histórico: {str(e)}")
    
    def atualizar_listbox_historico(self):
        """Atualiza a listbox com o histórico de análises"""
        self.analises_listbox.delete(0, tk.END)
        
        for i, analise in enumerate(self.historico):
            times = analise['times'] if analise['times'] else "Times não especificados"
            data = analise['data']
            duracao = f"{analise['duracao_prevista']:.2f} min"
            
            self.analises_listbox.insert(tk.END, f"{data} - {times} - {duracao}")
    
    def on_analise_select(self, event):
        """Manipula a seleção de uma análise no histórico"""
        if not self.analises_listbox.curselection():
            return
        
        index = self.analises_listbox.curselection()[0]
        self.mostrar_detalhes_analise(index)
    
    def ver_detalhes(self):
        """Mostra os detalhes da análise selecionada"""
        if not self.analises_listbox.curselection():
            messagebox.showinfo("Informação", "Selecione uma análise para ver os detalhes.")
            return
        
        index = self.analises_listbox.curselection()[0]
        self.mostrar_detalhes_analise(index)
    
    def mostrar_detalhes_analise(self, index):
        """Mostra os detalhes de uma análise específica"""
        # Limpar o frame
        for widget in self.detalhes_frame.winfo_children():
            widget.destroy()
        
        # Obter a análise
        analise = self.historico[index]
        
        # Adicionar detalhes
        ttk.Label(self.detalhes_frame, text="Detalhes da Análise", style="Header.TLabel").pack(pady=10)
        
        # Data e times
        info_frame = ttk.Frame(self.detalhes_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="Data:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=analise['data'], font=("Arial", 11)).grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(info_frame, text="Times:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=analise['times'], font=("Arial", 11)).grid(row=1, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(info_frame, text="Torneio:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=analise['torneio'], font=("Arial", 11)).grid(row=2, column=1, padx=5, sticky=tk.W)
        
        # Duração prevista
        result_frame = ttk.Frame(self.detalhes_frame)
        result_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(result_frame, text="Duração Prevista:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(result_frame, text=f"{analise['duracao_prevista']:.2f} minutos", font=("Arial", 12)).grid(row=0, column=1, padx=5, sticky=tk.W)
        
        # Converter para horas e minutos
        duracao = analise['duracao_prevista']
        horas = int(duracao // 60)
        minutos = int(duracao % 60)
        segundos = int((duracao * 60) % 60)
        
        if horas > 0:
            tempo_formatado = f"{horas}h {minutos}m {segundos}s"
        else:
            tempo_formatado = f"{minutos}m {segundos}s"
        
        ttk.Label(result_frame, text="Tempo Formatado:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(result_frame, text=tempo_formatado, font=("Arial", 12)).grid(row=1, column=1, padx=5, sticky=tk.W)
        
        # Fatores considerados
        ttk.Label(self.detalhes_frame, text="Fatores Considerados:", font=("Arial", 11, "bold")).pack(anchor=tk.W, padx=5, pady=5)
        
        features = analise['features']
        info_text = f"""
        • Total de Kills: {features['total_kills']}
        • Score Radiant: {features['radiant_score']}
        • Score Dire: {features['dire_score']}
        • Tempo do First Blood: {features['first_blood_time']} segundos
        • Status das Torres Radiant: {features['tower_status_radiant']}
        • Status das Torres Dire: {features['tower_status_dire']}
        • Status dos Barracks Radiant: {features['barracks_status_radiant']}
        • Status dos Barracks Dire: {features['barracks_status_dire']}
        """
        
        info_label = ttk.Label(self.detalhes_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W, padx=5)
        
        # Botão para carregar dados na aba de predição
        ttk.Button(self.detalhes_frame, text="Usar Estes Dados", command=lambda: self.carregar_dados_analise(analise)).pack(pady=10)
    
    def carregar_dados_analise(self, analise):
        """Carrega os dados de uma análise na aba de predição"""
        # Mudar para a aba de predição
        self.notebook.select(0)
        
        # Preencher os campos
        self.var_times.set(analise['times'])
        self.var_torneio.set(analise['torneio'])
        
        features = analise['features']
        self.var_total_kills.set(str(features['total_kills']))
        self.var_radiant_score.set(str(features['radiant_score']))
        self.var_dire_score.set(str(features['dire_score']))
        self.var_first_blood_time.set(str(features['first_blood_time']))
        self.var_tower_status_radiant.set(str(features['tower_status_radiant']))
        self.var_tower_status_dire.set(str(features['tower_status_dire']))
        self.var_barracks_status_radiant.set(str(features['barracks_status_radiant']))
        self.var_barracks_status_dire.set(str(features['barracks_status_dire']))
    
    def excluir_analise(self):
        """Exclui a análise selecionada do histórico"""
        if not self.analises_listbox.curselection():
            messagebox.showinfo("Informação", "Selecione uma análise para excluir.")
            return
        
        index = self.analises_listbox.curselection()[0]
        
        # Confirmar exclusão
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir esta análise?"):
            # Remover do histórico
            del self.historico[index]
            
            # Salvar histórico
            self.salvar_historico()
            
            # Atualizar listbox
            self.atualizar_listbox_historico()
            
            # Limpar detalhes
            for widget in self.detalhes_frame.winfo_children():
                widget.destroy()
            
            messagebox.showinfo("Sucesso", "Análise excluída com sucesso!")
    
    def exportar_historico(self):
        """Exporta o histórico de análises para um arquivo"""
        if not self.historico:
            messagebox.showinfo("Informação", "Não há análises para exportar.")
            return
        
        # Solicitar local para salvar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx"), ("JSON Files", "*.json")],
            title="Exportar Histórico"
        )
        
        if not file_path:
            return
        
        try:
            # Criar DataFrame
            df = pd.DataFrame(self.historico)
            
            # Expandir features
            features_df = pd.json_normalize(df['features'])
            df = pd.concat([df.drop('features', axis=1), features_df], axis=1)
            
            # Exportar de acordo com a extensão
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            elif file_path.endswith('.json'):
                df.to_json(file_path, orient='records')
            
            messagebox.showinfo("Sucesso", f"Histórico exportado com sucesso para {file_path}!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar histórico: {str(e)}")
    
    def limpar_campos(self):
        """Limpa todos os campos de entrada"""
        self.var_times.set("")
        self.var_torneio.set("")
        self.var_total_kills.set("0")
        self.var_radiant_score.set("0")
        self.var_dire_score.set("0")
        self.var_first_blood_time.set("0")
        self.var_tower_status_radiant.set("0")
        self.var_tower_status_dire.set("0")
        self.var_barracks_status_radiant.set("0")
        self.var_barracks_status_dire.set("0")
        
        # Resetar o frame de resultados
        self.setup_result_frame()
    
    def carregar_exemplo(self):
        """Carrega dados de exemplo nos campos"""
        self.var_times.set("Team Liquid vs Tundra")
        self.var_torneio.set("DPC Western Europe Division 1")
        self.var_total_kills.set("50")
        self.var_radiant_score.set("30")
        self.var_dire_score.set("20")
        self.var_first_blood_time.set("120")
        self.var_tower_status_radiant.set("1500")
        self.var_tower_status_dire.set("500")
        self.var_barracks_status_radiant.set("60")
        self.var_barracks_status_dire.set("10")

def main():
    """Função principal para iniciar a aplicação"""
    root = tk.Tk()
    app = DotaAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
