import unittest
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar os módulos a serem testados
from models.data_generator import IndustrialDataGenerator
from backend.utils.data_collector import DataCollector
from backend.utils.data_processor import DataProcessor
from backend.utils.data_storage import DataStorage

class TestDataSystem(unittest.TestCase):
    """
    Testes para o sistema de coleta e processamento de dados
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes
        """
        # Criar diretório temporário para testes
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Inicializar componentes
        self.generator = IndustrialDataGenerator(output_dir=self.test_dir)
        self.collector = DataCollector(data_dir=self.test_dir)
        self.processor = DataProcessor(data_dir=self.test_dir)
        self.storage = DataStorage(data_dir=self.test_dir, db_name='test_industrial_data.db')
        
        logging.info("Configuração de teste inicializada")
    
    def tearDown(self):
        """
        Limpeza após os testes
        """
        # Remover arquivos de teste
        for root, dirs, files in os.walk(self.test_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        
        logging.info("Limpeza de teste concluída")
    
    def test_data_generator(self):
        """
        Testa o gerador de dados
        """
        logging.info("Testando gerador de dados...")
        
        # Gerar dados para uma máquina
        machine_type = "torno_cnc"
        param = "temperatura"
        num_points = 10
        
        df = self.generator.generate_normal_data(machine_type, param, num_points)
        
        # Verificar se o DataFrame foi criado corretamente
        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertEqual(len(df), num_points)
        self.assertIn('timestamp', df.columns)
        self.assertIn('machine_type', df.columns)
        self.assertIn('parameter', df.columns)
        self.assertIn('value', df.columns)
        
        # Verificar valores
        self.assertEqual(df['machine_type'].iloc[0], machine_type)
        self.assertEqual(df['parameter'].iloc[0], param)
        
        logging.info("Teste do gerador de dados concluído com sucesso")
    
    def test_data_collector(self):
        """
        Testa o coletor de dados
        """
        logging.info("Testando coletor de dados...")
        
        # Coletar dados uma vez
        num_machines = 3
        df = self.collector.collect_data_once(num_machines=num_machines)
        
        # Verificar se o DataFrame foi criado corretamente
        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertIn('machine_id', df.columns)
        self.assertIn('machine_type', df.columns)
        self.assertIn('parameter', df.columns)
        self.assertIn('value', df.columns)
        self.assertIn('collection_timestamp', df.columns)
        
        # Verificar se há dados para todas as máquinas
        unique_machines = df['machine_id'].unique()
        self.assertEqual(len(unique_machines), num_machines)
        
        # Testar processamento de dados
        processed_df = self.collector.process_data(df)
        
        # Verificar se o processamento adicionou colunas
        self.assertIn('min_limit', processed_df.columns)
        self.assertIn('max_limit', processed_df.columns)
        self.assertIn('deviation', processed_df.columns)
        
        # Salvar dados
        raw_file = self.collector.save_raw_data(df)
        processed_file = self.collector.save_processed_data(processed_df)
        
        # Verificar se os arquivos foram criados
        self.assertTrue(os.path.exists(raw_file))
        self.assertTrue(os.path.exists(processed_file))
        
        logging.info("Teste do coletor de dados concluído com sucesso")
    
    def test_data_processor(self):
        """
        Testa o processador de dados
        """
        logging.info("Testando processador de dados...")
        
        # Gerar dados para teste
        num_machines = 3
        df = self.collector.collect_data_once(num_machines=num_machines)
        
        # Adicionar ao buffer do processador
        success = self.processor.add_to_buffer(df)
        self.assertTrue(success)
        
        # Processar buffer
        processed_df = self.processor.process_buffer()
        
        # Verificar se o processamento foi bem-sucedido
        self.assertIsNotNone(processed_df)
        self.assertFalse(processed_df.empty)
        
        # Verificar estatísticas
        stats = self.processor.get_stats()
        self.assertGreater(stats['processed_records'], 0)
        
        logging.info("Teste do processador de dados concluído com sucesso")
    
    def test_data_storage(self):
        """
        Testa o armazenamento de dados
        """
        logging.info("Testando armazenamento de dados...")
        
        # Gerar dados para teste
        num_machines = 3
        df = self.collector.collect_data_once(num_machines=num_machines)
        processed_df = self.collector.process_data(df)
        
        # Armazenar dados
        stored_count = self.storage.store_dataframe(processed_df)
        
        # Verificar se os dados foram armazenados
        self.assertGreater(stored_count, 0)
        
        # Consultar leituras
        readings = self.storage.query_readings(limit=100)
        
        # Verificar se as leituras foram recuperadas
        self.assertIsNotNone(readings)
        self.assertFalse(readings.empty)
        self.assertEqual(len(readings), stored_count)
        
        # Consultar estatísticas das máquinas
        stats = self.storage.get_machine_stats()
        
        # Verificar se as estatísticas foram recuperadas
        self.assertIsNotNone(stats)
        self.assertFalse(stats.empty)
        self.assertEqual(len(stats), num_machines)
        
        logging.info("Teste do armazenamento de dados concluído com sucesso")
    
    def test_end_to_end(self):
        """
        Teste de ponta a ponta do sistema
        """
        logging.info("Executando teste de ponta a ponta...")
        
        # Simular coleta e processamento de dados
        num_machines = 3
        collection_interval = 1
        duration = 5
        
        # Iniciar processamento
        self.processor.start_processing()
        
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            while time.time() < end_time:
                # Coletar dados
                df = self.collector.collect_data_once(num_machines=num_machines)
                
                # Adicionar ao buffer de processamento
                self.processor.add_to_buffer(df)
                
                # Aguardar próximo intervalo
                time.sleep(collection_interval)
        
        finally:
            # Parar processamento
            self.processor.stop_processing()
        
        # Verificar estatísticas
        stats = self.processor.get_stats()
        self.assertGreater(stats['processed_records'], 0)
        
        # Armazenar dados no banco de dados
        for i in range(5):
            # Coletar dados
            df = self.collector.collect_data_once(num_machines=num_machines)
            processed_df = self.collector.process_data(df)
            self.storage.store_dataframe(processed_df)
            
        # Consultar dados armazenados
        readings = self.storage.query_readings(limit=100)
        self.assertFalse(readings.empty)
        
        logging.info("Teste de ponta a ponta concluído com sucesso")

if __name__ == '__main__':
    unittest.main()
