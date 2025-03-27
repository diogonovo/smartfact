import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o gerador de dados
from models.data_generator import IndustrialDataGenerator

# Configurar logging
# Criar diretório de logs se não existir
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'data_collector.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DataCollector")

class DataCollector:
    """
    Classe para coleta e armazenamento de dados de máquinas industriais
    """
    
    def __init__(self, data_dir='../data', collection_interval=5):
        """
        Inicializa o coletor de dados
        
        Args:
            data_dir: Diretório onde os dados serão salvos
            collection_interval: Intervalo de coleta em segundos
        """
        self.data_dir = data_dir
        self.collection_interval = collection_interval
        self.generator = IndustrialDataGenerator(output_dir=data_dir)
        
        # Criar diretórios necessários
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'processed'), exist_ok=True)
        os.makedirs('../logs', exist_ok=True)
        
        # Inicializar dicionário para armazenar dados em memória
        self.current_data = {}
        
        logger.info(f"DataCollector inicializado com intervalo de coleta de {collection_interval} segundos")
    
    def collect_data_once(self, num_machines=10):
        """
        Coleta dados uma única vez para todas as máquinas
        
        Args:
            num_machines: Número de máquinas a serem simuladas
            
        Returns:
            DataFrame com os dados coletados
        """
        logger.info(f"Coletando dados para {num_machines} máquinas")
        
        # Gerar dados para uma única leitura (1 ponto por parâmetro por máquina)
        factory_data = self.generator.generate_factory_dataset(
            num_machines=num_machines, 
            num_points=1,
            anomaly_percent=0.05
        )
        
        # Adicionar timestamp atual
        factory_data['collection_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Atualizar dados em memória
        for _, row in factory_data.iterrows():
            machine_id = row['machine_id']
            machine_type = row['machine_type']
            parameter = row['parameter']
            value = row['value']
            
            if machine_id not in self.current_data:
                self.current_data[machine_id] = {
                    'machine_type': machine_type,
                    'parameters': {}
                }
            
            self.current_data[machine_id]['parameters'][parameter] = {
                'value': value,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        return factory_data
    
    def save_raw_data(self, df, timestamp=None):
        """
        Salva os dados brutos em um arquivo CSV
        
        Args:
            df: DataFrame com os dados
            timestamp: Timestamp para o nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo salvo
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filepath = os.path.join(self.data_dir, 'raw', f"raw_data_{timestamp}.csv")
        df.to_csv(filepath, index=False)
        logger.info(f"Dados brutos salvos em: {filepath}")
        
        return filepath
    
    def process_data(self, df):
        """
        Processa os dados brutos
        
        Args:
            df: DataFrame com os dados brutos
            
        Returns:
            DataFrame com os dados processados
        """
        logger.info("Processando dados brutos")
        
        # Cópia para não modificar o original
        processed_df = df.copy()
        
        # Converter timestamp para datetime
        if 'timestamp' in processed_df.columns:
            processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'])
        
        # Adicionar colunas calculadas
        if 'machine_type' in processed_df.columns and 'parameter' in processed_df.columns:
            # Calcular limites com base no tipo de máquina e parâmetro
            for machine_type in processed_df['machine_type'].unique():
                for param in processed_df[processed_df['machine_type'] == machine_type]['parameter'].unique():
                    if machine_type in self.generator.machine_types and param in self.generator.machine_types[machine_type]['ranges']:
                        min_val, max_val, mean, std = self.generator.machine_types[machine_type]['ranges'][param]
                        
                        # Filtrar para o tipo de máquina e parâmetro específicos
                        mask = (processed_df['machine_type'] == machine_type) & (processed_df['parameter'] == param)
                        
                        # Adicionar colunas de limites
                        processed_df.loc[mask, 'min_limit'] = min_val
                        processed_df.loc[mask, 'max_limit'] = max_val
                        processed_df.loc[mask, 'mean_value'] = mean
                        
                        # Calcular desvio em relação à média
                        processed_df.loc[mask, 'deviation'] = (processed_df.loc[mask, 'value'] - mean) / std
                        
                        # Marcar valores fora dos limites
                        processed_df.loc[mask, 'out_of_limits'] = (
                            (processed_df.loc[mask, 'value'] < min_val) | 
                            (processed_df.loc[mask, 'value'] > max_val)
                        )
        
        return processed_df
    
    def save_processed_data(self, df, timestamp=None):
        """
        Salva os dados processados em um arquivo CSV
        
        Args:
            df: DataFrame com os dados processados
            timestamp: Timestamp para o nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo salvo
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filepath = os.path.join(self.data_dir, 'processed', f"processed_data_{timestamp}.csv")
        df.to_csv(filepath, index=False)
        logger.info(f"Dados processados salvos em: {filepath}")
        
        return filepath
    
    def get_current_state(self):
        """
        Retorna o estado atual de todas as máquinas
        
        Returns:
            Dicionário com o estado atual
        """
        return self.current_data
    
    def save_current_state(self):
        """
        Salva o estado atual em um arquivo JSON
        
        Returns:
            Caminho do arquivo salvo
        """
        filepath = os.path.join(self.data_dir, 'current_state.json')
        
        with open(filepath, 'w') as f:
            json.dump(self.current_data, f, indent=4)
        
        logger.info(f"Estado atual salvo em: {filepath}")
        
        return filepath
    
    def collect_continuously(self, duration=60, num_machines=10):
        """
        Coleta dados continuamente por um período determinado
        
        Args:
            duration: Duração da coleta em segundos
            num_machines: Número de máquinas a serem simuladas
            
        Returns:
            Lista de caminhos dos arquivos salvos
        """
        logger.info(f"Iniciando coleta contínua por {duration} segundos")
        
        start_time = time.time()
        end_time = start_time + duration
        saved_files = []
        
        try:
            while time.time() < end_time:
                # Coletar dados
                df = self.collect_data_once(num_machines)
                
                # Obter timestamp atual
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Salvar dados brutos
                raw_file = self.save_raw_data(df, timestamp)
                saved_files.append(raw_file)
                
                # Processar dados
                processed_df = self.process_data(df)
                
                # Salvar dados processados
                processed_file = self.save_processed_data(processed_df, timestamp)
                saved_files.append(processed_file)
                
                # Salvar estado atual
                self.save_current_state()
                
                # Aguardar próximo intervalo
                time.sleep(self.collection_interval)
        
        except KeyboardInterrupt:
            logger.info("Coleta interrompida pelo usuário")
        except Exception as e:
            logger.error(f"Erro durante a coleta: {e}")
        
        logger.info(f"Coleta contínua finalizada. {len(saved_files)} arquivos salvos.")
        
        return saved_files
    
    def load_data(self, start_date=None, end_date=None, processed=True):
        """
        Carrega dados históricos de um período específico
        
        Args:
            start_date: Data inicial (formato: YYYYMMDD)
            end_date: Data final (formato: YYYYMMDD)
            processed: Se True, carrega dados processados, senão dados brutos
            
        Returns:
            DataFrame com os dados carregados
        """
        # Determinar diretório de dados
        data_subdir = 'processed' if processed else 'raw'
        data_dir = os.path.join(self.data_dir, data_subdir)
        
        # Listar todos os arquivos
        all_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        # Filtrar por data se especificado
        if start_date or end_date:
            filtered_files = []
            for file in all_files:
                # Extrair data do nome do arquivo (formato: data_YYYYMMDD_HHMMSS.csv)
                try:
                    file_date = file.split('_')[2][:8]  # Extrair YYYYMMDD
                    
                    if start_date and file_date < start_date:
                        continue
                    
                    if end_date and file_date > end_date:
                        continue
                    
                    filtered_files.append(file)
                except:
                    # Ignorar arquivos com formato de nome diferente
                    continue
            
            files_to_load = filtered_files
        else:
            files_to_load = all_files
        
        # Carregar dados
        dfs = []
        for file in files_to_load:
            filepath = os.path.join(data_dir, file)
            try:
                df = pd.read_csv(filepath)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Erro ao carregar arquivo {filepath}: {e}")
        
        # Concatenar DataFrames
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Carregados {len(dfs)} arquivos, total de {len(combined_df)} registros")
            return combined_df
        else:
            logger.warning("Nenhum dado encontrado para o período especificado")
            return pd.DataFrame()

# Exemplo de uso
if __name__ == "__main__":
    # Criar coletor de dados
    collector = DataCollector(collection_interval=5)
    
    # Coletar dados continuamente por 30 segundos
    collector.collect_continuously(duration=30, num_machines=5)
    
    # Carregar dados históricos
    historical_data = collector.load_data()
    print(f"Dados históricos carregados: {len(historical_data)} registros")
