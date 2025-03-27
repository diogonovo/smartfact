import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import threading
import queue

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o coletor de dados
from utils.data_collector import DataCollector

# Configurar logging
# Criar diretório de logs se não existir
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'data_processor.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DataProcessor")

class DataProcessor:
    """
    Classe para processamento de dados em tempo real de máquinas industriais
    """
    
    def __init__(self, data_dir='../data', buffer_size=100):
        """
        Inicializa o processador de dados
        
        Args:
            data_dir: Diretório onde os dados serão salvos
            buffer_size: Tamanho do buffer para processamento em lote
        """
        self.data_dir = data_dir
        self.buffer_size = buffer_size
        self.collector = DataCollector(data_dir=data_dir)
        
        # Criar diretórios necessários
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'processed'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'analytics'), exist_ok=True)
        os.makedirs('../logs', exist_ok=True)
        
        # Inicializar buffer de dados
        self.data_buffer = queue.Queue(maxsize=buffer_size)
        
        # Inicializar flag para controle de threads
        self.running = False
        
        # Inicializar estatísticas
        self.stats = {
            'processed_records': 0,
            'anomalies_detected': 0,
            'processing_time': 0,
            'last_processed': None
        }
        
        logger.info(f"DataProcessor inicializado com buffer de tamanho {buffer_size}")
    
    def add_to_buffer(self, data):
        """
        Adiciona dados ao buffer de processamento
        
        Args:
            data: DataFrame ou dicionário com dados a serem processados
            
        Returns:
            True se adicionado com sucesso, False se buffer cheio
        """
        try:
            # Converter para DataFrame se for dicionário
            if isinstance(data, dict):
                data_df = pd.DataFrame([data])
            else:
                data_df = data
            
            # Adicionar ao buffer
            self.data_buffer.put(data_df, block=False)
            return True
        except queue.Full:
            logger.warning("Buffer cheio, dados descartados")
            return False
        except Exception as e:
            logger.error(f"Erro ao adicionar dados ao buffer: {e}")
            return False
    
    def process_buffer(self):
        """
        Processa os dados no buffer
        
        Returns:
            DataFrame com os dados processados
        """
        # Coletar todos os dados do buffer
        data_frames = []
        start_time = time.time()
        
        try:
            while not self.data_buffer.empty():
                data_df = self.data_buffer.get(block=False)
                data_frames.append(data_df)
                self.data_buffer.task_done()
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Erro ao obter dados do buffer: {e}")
        
        if not data_frames:
            logger.info("Buffer vazio, nada para processar")
            return None
        
        # Concatenar todos os DataFrames
        combined_df = pd.concat(data_frames, ignore_index=True)
        
        # Processar os dados
        processed_df = self.process_data(combined_df)
        
        # Atualizar estatísticas
        end_time = time.time()
        self.stats['processed_records'] += len(processed_df)
        self.stats['processing_time'] += (end_time - start_time)
        self.stats['last_processed'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return processed_df
    
    def process_data(self, df):
        """
        Processa os dados
        
        Args:
            df: DataFrame com os dados a serem processados
            
        Returns:
            DataFrame com os dados processados
        """
        logger.info(f"Processando {len(df)} registros")
        
        # Usar o processamento do coletor de dados
        processed_df = self.collector.process_data(df)
        
        # Adicionar processamento adicional aqui
        
        # Calcular métricas agregadas
        if 'machine_id' in processed_df.columns and 'parameter' in processed_df.columns and 'value' in processed_df.columns:
            # Calcular estatísticas por máquina e parâmetro
            agg_df = processed_df.groupby(['machine_id', 'parameter']).agg({
                'value': ['mean', 'std', 'min', 'max', 'count']
            }).reset_index()
            
            # Renomear colunas
            agg_df.columns = ['machine_id', 'parameter', 'mean', 'std', 'min', 'max', 'count']
            
            # Salvar métricas agregadas
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.data_dir, 'analytics', f"metrics_{timestamp}.csv")
            agg_df.to_csv(filepath, index=False)
            logger.info(f"Métricas agregadas salvas em: {filepath}")
        
        # Detectar anomalias simples (valores fora dos limites)
        if 'out_of_limits' in processed_df.columns:
            anomalies = processed_df[processed_df['out_of_limits'] == True]
            self.stats['anomalies_detected'] += len(anomalies)
            
            if not anomalies.empty:
                # Salvar anomalias detectadas
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(self.data_dir, 'analytics', f"anomalies_{timestamp}.csv")
                anomalies.to_csv(filepath, index=False)
                logger.info(f"Detectadas {len(anomalies)} anomalias, salvas em: {filepath}")
        
        return processed_df
    
    def save_processed_data(self, df):
        """
        Salva os dados processados
        
        Args:
            df: DataFrame com os dados processados
            
        Returns:
            Caminho do arquivo salvo
        """
        if df is None or df.empty:
            logger.warning("Nenhum dado para salvar")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.data_dir, 'processed', f"realtime_processed_{timestamp}.csv")
        df.to_csv(filepath, index=False)
        logger.info(f"Dados processados salvos em: {filepath}")
        
        return filepath
    
    def processing_thread(self):
        """
        Thread para processamento contínuo dos dados no buffer
        """
        logger.info("Iniciando thread de processamento")
        
        while self.running:
            try:
                # Processar buffer
                processed_df = self.process_buffer()
                
                # Salvar dados processados
                if processed_df is not None and not processed_df.empty:
                    self.save_processed_data(processed_df)
                
                # Aguardar um pouco para não sobrecarregar o sistema
                time.sleep(1)
            except Exception as e:
                logger.error(f"Erro na thread de processamento: {e}")
        
        logger.info("Thread de processamento finalizada")
    
    def start_processing(self):
        """
        Inicia o processamento contínuo em uma thread separada
        """
        if self.running:
            logger.warning("Processamento já está em execução")
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self.processing_thread)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        logger.info("Processamento contínuo iniciado")
    
    def stop_processing(self):
        """
        Para o processamento contínuo
        """
        if not self.running:
            logger.warning("Processamento não está em execução")
            return
        
        self.running = False
        self.processing_thread.join(timeout=5)
        
        logger.info("Processamento contínuo parado")
    
    def get_stats(self):
        """
        Retorna estatísticas do processamento
        
        Returns:
            Dicionário com estatísticas
        """
        return self.stats
    
    def simulate_realtime_processing(self, duration=60, num_machines=10, collection_interval=5):
        """
        Simula processamento em tempo real coletando e processando dados
        
        Args:
            duration: Duração da simulação em segundos
            num_machines: Número de máquinas a serem simuladas
            collection_interval: Intervalo de coleta em segundos
            
        Returns:
            Estatísticas do processamento
        """
        logger.info(f"Iniciando simulação de processamento em tempo real por {duration} segundos")
        
        # Iniciar processamento contínuo
        self.start_processing()
        
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            while time.time() < end_time:
                # Coletar dados
                df = self.collector.collect_data_once(num_machines)
                
                # Adicionar ao buffer de processamento
                self.add_to_buffer(df)
                
                # Aguardar próximo intervalo
                time.sleep(collection_interval)
        
        except KeyboardInterrupt:
            logger.info("Simulação interrompida pelo usuário")
        except Exception as e:
            logger.error(f"Erro durante a simulação: {e}")
        finally:
            # Parar processamento contínuo
            self.stop_processing()
        
        logger.info(f"Simulação finalizada. Estatísticas: {self.stats}")
        
        return self.stats

# Exemplo de uso
if __name__ == "__main__":
    # Criar processador de dados
    processor = DataProcessor()
    
    # Simular processamento em tempo real por 30 segundos
    processor.simulate_realtime_processing(duration=30, num_machines=5, collection_interval=2)
