import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
import sqlite3
from pathlib import Path

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
# Criar diretório de logs se não existir
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'data_storage.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DataStorage")

class DataStorage:
    """
    Classe para armazenamento de dados históricos de máquinas industriais
    """
    
    def __init__(self, data_dir='../data', db_name='industrial_data.db'):
        """
        Inicializa o sistema de armazenamento de dados
        
        Args:
            data_dir: Diretório onde os dados serão salvos
            db_name: Nome do banco de dados SQLite
        """
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, db_name)
        
        # Criar diretórios necessários
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs('../logs', exist_ok=True)
        
        # Inicializar banco de dados
        self._init_database()
        
        logger.info(f"DataStorage inicializado com banco de dados em: {self.db_path}")
    
    def _init_database(self):
        """
        Inicializa o banco de dados SQLite
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Criar tabela de máquinas
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS machines (
                machine_id INTEGER PRIMARY KEY,
                machine_type TEXT NOT NULL,
                location TEXT,
                installation_date TEXT,
                status TEXT
            )
            ''')
            
            # Criar tabela de parâmetros
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS parameters (
                parameter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id INTEGER,
                parameter_name TEXT NOT NULL,
                unit TEXT,
                min_limit REAL,
                max_limit REAL,
                FOREIGN KEY (machine_id) REFERENCES machines (machine_id)
            )
            ''')
            
            # Criar tabela de leituras
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id INTEGER,
                parameter_id INTEGER,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                is_anomaly INTEGER DEFAULT 0,
                FOREIGN KEY (machine_id) REFERENCES machines (machine_id),
                FOREIGN KEY (parameter_id) REFERENCES parameters (parameter_id)
            )
            ''')
            
            # Criar tabela de anomalias
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
                reading_id INTEGER,
                machine_id INTEGER,
                parameter_id INTEGER,
                timestamp TEXT NOT NULL,
                value REAL NOT NULL,
                severity TEXT,
                description TEXT,
                FOREIGN KEY (reading_id) REFERENCES readings (reading_id),
                FOREIGN KEY (machine_id) REFERENCES machines (machine_id),
                FOREIGN KEY (parameter_id) REFERENCES parameters (parameter_id)
            )
            ''')
            
            # Criar índices para melhorar performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_machine_id ON readings (machine_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_parameter_id ON readings (parameter_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_machine_id ON anomalies (machine_id)')
            
            conn.commit()
            conn.close()
            
            logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
    
    def store_machine_data(self, machine_id, machine_type, location=None, installation_date=None, status=None):
        """
        Armazena informações de uma máquina
        
        Args:
            machine_id: ID da máquina
            machine_type: Tipo da máquina
            location: Localização da máquina
            installation_date: Data de instalação
            status: Status atual
            
        Returns:
            ID da máquina inserida/atualizada
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se a máquina já existe
            cursor.execute('SELECT machine_id FROM machines WHERE machine_id = ?', (machine_id,))
            result = cursor.fetchone()
            
            if result:
                # Atualizar máquina existente
                cursor.execute('''
                UPDATE machines 
                SET machine_type = ?, location = ?, installation_date = ?, status = ?
                WHERE machine_id = ?
                ''', (machine_type, location, installation_date, status, machine_id))
                logger.info(f"Máquina ID {machine_id} atualizada")
            else:
                # Inserir nova máquina
                cursor.execute('''
                INSERT INTO machines (machine_id, machine_type, location, installation_date, status)
                VALUES (?, ?, ?, ?, ?)
                ''', (machine_id, machine_type, location, installation_date, status))
                logger.info(f"Máquina ID {machine_id} inserida")
            
            conn.commit()
            conn.close()
            
            return machine_id
        except Exception as e:
            logger.error(f"Erro ao armazenar dados da máquina: {e}")
            return None
    
    def store_parameter(self, machine_id, parameter_name, unit=None, min_limit=None, max_limit=None):
        """
        Armazena informações de um parâmetro
        
        Args:
            machine_id: ID da máquina
            parameter_name: Nome do parâmetro
            unit: Unidade de medida
            min_limit: Limite mínimo
            max_limit: Limite máximo
            
        Returns:
            ID do parâmetro inserido/atualizado
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se o parâmetro já existe
            cursor.execute('''
            SELECT parameter_id FROM parameters 
            WHERE machine_id = ? AND parameter_name = ?
            ''', (machine_id, parameter_name))
            result = cursor.fetchone()
            
            if result:
                # Atualizar parâmetro existente
                parameter_id = result[0]
                cursor.execute('''
                UPDATE parameters 
                SET unit = ?, min_limit = ?, max_limit = ?
                WHERE parameter_id = ?
                ''', (unit, min_limit, max_limit, parameter_id))
                logger.info(f"Parâmetro ID {parameter_id} atualizado")
            else:
                # Inserir novo parâmetro
                cursor.execute('''
                INSERT INTO parameters (machine_id, parameter_name, unit, min_limit, max_limit)
                VALUES (?, ?, ?, ?, ?)
                ''', (machine_id, parameter_name, unit, min_limit, max_limit))
                parameter_id = cursor.lastrowid
                logger.info(f"Parâmetro ID {parameter_id} inserido")
            
            conn.commit()
            conn.close()
            
            return parameter_id
        except Exception as e:
            logger.error(f"Erro ao armazenar parâmetro: {e}")
            return None
    
    def store_reading(self, machine_id, parameter_name, timestamp, value, is_anomaly=0):
        """
        Armazena uma leitura de parâmetro
        
        Args:
            machine_id: ID da máquina
            parameter_name: Nome do parâmetro
            timestamp: Timestamp da leitura
            value: Valor da leitura
            is_anomaly: Se a leitura é uma anomalia (0 ou 1)
            
        Returns:
            ID da leitura inserida
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obter ID do parâmetro
            cursor.execute('''
            SELECT parameter_id FROM parameters 
            WHERE machine_id = ? AND parameter_name = ?
            ''', (machine_id, parameter_name))
            result = cursor.fetchone()
            
            if result:
                parameter_id = result[0]
            else:
                # Criar parâmetro se não existir
                parameter_id = self.store_parameter(machine_id, parameter_name)
            
            # Inserir leitura
            cursor.execute('''
            INSERT INTO readings (machine_id, parameter_id, timestamp, value, is_anomaly)
            VALUES (?, ?, ?, ?, ?)
            ''', (machine_id, parameter_id, timestamp, value, is_anomaly))
            reading_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return reading_id
        except Exception as e:
            logger.error(f"Erro ao armazenar leitura: {e}")
            return None
    
    def store_anomaly(self, reading_id, machine_id, parameter_name, timestamp, value, severity='Medium', description=None):
        """
        Armazena uma anomalia detectada
        
        Args:
            reading_id: ID da leitura associada
            machine_id: ID da máquina
            parameter_name: Nome do parâmetro
            timestamp: Timestamp da anomalia
            value: Valor anômalo
            severity: Severidade da anomalia
            description: Descrição da anomalia
            
        Returns:
            ID da anomalia inserida
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obter ID do parâmetro
            cursor.execute('''
            SELECT parameter_id FROM parameters 
            WHERE machine_id = ? AND parameter_name = ?
            ''', (machine_id, parameter_name))
            result = cursor.fetchone()
            
            if result:
                parameter_id = result[0]
            else:
                # Criar parâmetro se não existir
                parameter_id = self.store_parameter(machine_id, parameter_name)
            
            # Inserir anomalia
            cursor.execute('''
            INSERT INTO anomalies (reading_id, machine_id, parameter_id, timestamp, value, severity, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (reading_id, machine_id, parameter_id, timestamp, value, severity, description))
            anomaly_id = cursor.lastrowid
            
            # Marcar a leitura como anomalia
            if reading_id:
                cursor.execute('''
                UPDATE readings SET is_anomaly = 1 WHERE reading_id = ?
                ''', (reading_id,))
            
            conn.commit()
            conn.close()
            
            return anomaly_id
        except Exception as e:
            logger.error(f"Erro ao armazenar anomalia: {e}")
            return None
    
    def store_dataframe(self, df):
        """
        Armazena dados de um DataFrame
        
        Args:
            df: DataFrame com os dados a serem armazenados
            
        Returns:
            Número de registros armazenados
        """
        if df is None or df.empty:
            logger.warning("DataFrame vazio, nada para armazenar")
            return 0
        
        stored_count = 0
        
        try:
            # Verificar colunas necessárias
            required_columns = ['machine_id', 'machine_type', 'parameter', 'value']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                logger.error(f"Colunas obrigatórias ausentes no DataFrame: {missing}")
                return 0
            
            # Processar cada linha do DataFrame
            for _, row in df.iterrows():
                machine_id = row['machine_id']
                machine_type = row['machine_type']
                parameter = row['parameter']
                value = row['value']
                
                if 'timestamp' in row:
                    timestamp = row['timestamp']
                elif 'collection_timestamp' in row:
                    timestamp = row['collection_timestamp']
                else:
                    timestamp = datetime.now()

                # Converter sempre para string compatível com SQLite
                if isinstance(timestamp, pd.Timestamp):
                    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(timestamp, datetime):
                    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                
                # Obter outros campos opcionais
                location = row.get('location', None)
                status = row.get('status', 'Operational')
                
                # Obter limites do parâmetro
                min_limit = row.get('min_limit', None)
                max_limit = row.get('max_limit', None)
                
                # Verificar se é anomalia
                is_anomaly = 0
                if 'out_of_limits' in row and row['out_of_limits']:
                    is_anomaly = 1
                elif 'anomaly' in row and row['anomaly']:
                    is_anomaly = 1
                
                # Armazenar dados da máquina
                self.store_machine_data(machine_id, machine_type, location, None, status)
                
                # Armazenar parâmetro
                self.store_parameter(machine_id, parameter, None, min_limit, max_limit)
                
                # Armazenar leitura
                reading_id = self.store_reading(machine_id, parameter, timestamp, value, is_anomaly)
                
                # Armazenar anomalia se necessário
                if is_anomaly:
                    severity = 'High' if abs(row.get('deviation', 0)) > 3 else 'Medium'
                    description = f"Valor fora dos limites: {value}"
                    self.store_anomaly(reading_id, machine_id, parameter, timestamp, value, severity, description)
                
                stored_count += 1
            
            logger.info(f"Armazenados {stored_count} registros no banco de dados")
            return stored_count
        except Exception as e:
            logger.error(f"Erro ao armazenar DataFrame: {e}")
            return stored_count
    
    def query_readings(self, machine_id=None, parameter_name=None, start_time=None, end_time=None, limit=1000):
        """
        Consulta leituras no banco de dados
        
        Args:
            machine_id: ID da máquina (opcional)
            parameter_name: Nome do parâmetro (opcional)
            start_time: Timestamp inicial (formato: YYYY-MM-DD HH:MM:SS)
            end_time: Timestamp final (formato: YYYY-MM-DD HH:MM:SS)
            limit: Limite de registros a retornar
            
        Returns:
            DataFrame com os resultados
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
            SELECT r.reading_id, r.machine_id, m.machine_type, p.parameter_name, 
                   r.timestamp, r.value, r.is_anomaly, p.min_limit, p.max_limit
            FROM readings r
            JOIN machines m ON r.machine_id = m.machine_id
            JOIN parameters p ON r.parameter_id = p.parameter_id
            WHERE 1=1
            '''
            
            params = []
            
            if machine_id is not None:
                query += " AND r.machine_id = ?"
                params.append(machine_id)
            
            if parameter_name is not None:
                query += " AND p.parameter_name = ?"
                params.append(parameter_name)
            
            if start_time is not None:
                query += " AND r.timestamp >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND r.timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY r.timestamp DESC LIMIT ?"
            params.append(limit)
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            logger.info(f"Consulta retornou {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"Erro ao consultar leituras: {e}")
            return pd.DataFrame()
    
    def query_anomalies(self, machine_id=None, parameter_name=None, start_time=None, end_time=None, limit=1000):
        """
        Consulta anomalias no banco de dados
        
        Args:
            machine_id: ID da máquina (opcional)
            parameter_name: Nome do parâmetro (opcional)
            start_time: Timestamp inicial (formato: YYYY-MM-DD HH:MM:SS)
            end_time: Timestamp final (formato: YYYY-MM-DD HH:MM:SS)
            limit: Limite de registros a retornar
            
        Returns:
            DataFrame com os resultados
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
            SELECT a.anomaly_id, a.machine_id, m.machine_type, p.parameter_name, 
                   a.timestamp, a.value, a.severity, a.description
            FROM anomalies a
            JOIN machines m ON a.machine_id = m.machine_id
            JOIN parameters p ON a.parameter_id = p.parameter_id
            WHERE 1=1
            '''
            
            params = []
            
            if machine_id is not None:
                query += " AND a.machine_id = ?"
                params.append(machine_id)
            
            if parameter_name is not None:
                query += " AND p.parameter_name = ?"
                params.append(parameter_name)
            
            if start_time is not None:
                query += " AND a.timestamp >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND a.timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY a.timestamp DESC LIMIT ?"
            params.append(limit)
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            logger.info(f"Consulta de anomalias retornou {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"Erro ao consultar anomalias: {e}")
            return pd.DataFrame()
    
    def get_machine_stats(self, machine_id=None):
        """
        Obtém estatísticas das máquinas
        
        Args:
            machine_id: ID da máquina (opcional)
            
        Returns:
            DataFrame com estatísticas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
            SELECT m.machine_id, m.machine_type, m.location, m.status,
                   COUNT(DISTINCT p.parameter_id) as num_parameters,
                   COUNT(r.reading_id) as num_readings,
                   COUNT(DISTINCT CASE WHEN r.is_anomaly = 1 THEN r.reading_id END) as num_anomalies,
                   MIN(r.timestamp) as first_reading,
                   MAX(r.timestamp) as last_reading
            FROM machines m
            LEFT JOIN parameters p ON m.machine_id = p.machine_id
            LEFT JOIN readings r ON m.machine_id = r.machine_id
            '''
            
            params = []
            
            if machine_id is not None:
                query += " WHERE m.machine_id = ?"
                params.append(machine_id)
            
            query += " GROUP BY m.machine_id"
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            logger.info(f"Consulta de estatísticas retornou {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas das máquinas: {e}")
            return pd.DataFrame()
    
    def export_to_csv(self, query_result, filename):
        """
        Exporta resultados de consulta para CSV
        
        Args:
            query_result: DataFrame com resultados
            filename: Nome do arquivo (sem extensão)
            
        Returns:
            Caminho do arquivo salvo
        """
        if query_result is None or query_result.empty:
            logger.warning("Nenhum dado para exportar")
            return None
        
        filepath = os.path.join(self.data_dir, f"{filename}.csv")
        query_result.to_csv(filepath, index=False)
        logger.info(f"Dados exportados para: {filepath}")
        
        return filepath

# Exemplo de uso
if __name__ == "__main__":
    # Importar o gerador de dados
    from models.data_generator import IndustrialDataGenerator
    
    # Gerar dados simulados
    generator = IndustrialDataGenerator()
    factory_data = generator.generate_factory_dataset(num_machines=3, num_points=10)
    
    # Criar armazenamento de dados
    storage = DataStorage()
    
    # Armazenar dados
    storage.store_dataframe(factory_data)
    
    # Consultar leituras
    readings = storage.query_readings(limit=20)
    print(f"Leituras: {len(readings)}")
    
    # Consultar anomalias
    anomalies = storage.query_anomalies()
    print(f"Anomalias: {len(anomalies)}")
    
    # Obter estatísticas
    stats = storage.get_machine_stats()
    print("Estatísticas das máquinas:")
    print(stats)
