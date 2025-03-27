import os
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import random

class IndustrialDataGenerator:
    """
    Classe para geração de dados simulados de máquinas industriais
    """
    
    def __init__(self, output_dir='../data'):
        """
        Inicializa o gerador de dados
        
        Args:
            output_dir: Diretório onde os dados serão salvos
        """
        self.output_dir = output_dir
        self.machine_types = {
            "torno_cnc": {
                "params": ["temperatura", "vibracao", "velocidade", "torque", "consumo_energia"],
                "ranges": {
                    "temperatura": (50, 85, 70, 5),  # min, max, média, desvio padrão
                    "vibracao": (0.1, 3.0, 0.8, 0.3),
                    "velocidade": (500, 5000, 2500, 300),
                    "torque": (10, 100, 50, 10),
                    "consumo_energia": (5, 30, 15, 3)
                }
            },
            "fresadora": {
                "params": ["temperatura", "vibracao", "velocidade", "pressao_hidraulica", "consumo_energia"],
                "ranges": {
                    "temperatura": (45, 80, 65, 5),
                    "vibracao": (0.2, 2.5, 0.7, 0.2),
                    "velocidade": (300, 3000, 1500, 200),
                    "pressao_hidraulica": (50, 150, 100, 15),
                    "consumo_energia": (8, 35, 20, 4)
                }
            },
            "injetora_plastico": {
                "params": ["temperatura", "pressao", "tempo_ciclo", "consumo_energia", "temperatura_molde"],
                "ranges": {
                    "temperatura": (150, 300, 220, 15),
                    "pressao": (50, 200, 120, 20),
                    "tempo_ciclo": (10, 60, 30, 5),
                    "consumo_energia": (15, 50, 30, 5),
                    "temperatura_molde": (20, 80, 50, 8)
                }
            },
            "robo_industrial": {
                "params": ["temperatura", "precisao", "velocidade", "consumo_energia", "carga"],
                "ranges": {
                    "temperatura": (30, 70, 45, 5),
                    "precisao": (0.01, 0.5, 0.1, 0.05),
                    "velocidade": (10, 100, 50, 10),
                    "consumo_energia": (2, 20, 10, 2),
                    "carga": (0, 100, 50, 15)
                }
            },
            "compressor": {
                "params": ["temperatura", "pressao", "consumo_energia", "vazao", "vibracao"],
                "ranges": {
                    "temperatura": (40, 90, 65, 8),
                    "pressao": (5, 15, 10, 1),
                    "consumo_energia": (10, 40, 25, 5),
                    "vazao": (100, 500, 300, 50),
                    "vibracao": (0.1, 2.0, 0.5, 0.2)
                }
            }
        }
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_normal_data(self, machine_type, param, num_points, start_time=None):
        """
        Gera dados normais para um parâmetro específico de uma máquina
        
        Args:
            machine_type: Tipo de máquina
            param: Parâmetro a ser gerado
            num_points: Número de pontos a serem gerados
            start_time: Timestamp inicial (opcional)
            
        Returns:
            DataFrame com os dados gerados
        """
        if machine_type not in self.machine_types:
            raise ValueError(f"Tipo de máquina desconhecido: {machine_type}")
        
        if param not in self.machine_types[machine_type]["params"]:
            raise ValueError(f"Parâmetro desconhecido para {machine_type}: {param}")
        
        # Obter os limites para o parâmetro
        min_val, max_val, mean, std = self.machine_types[machine_type]["ranges"][param]
        
        # Gerar timestamps
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=num_points)
        
        timestamps = [start_time + timedelta(hours=i) for i in range(num_points)]
        
        # Gerar valores com distribuição normal
        values = np.random.normal(mean, std, num_points)
        
        # Limitar aos valores mínimos e máximos
        values = np.clip(values, min_val, max_val)
        
        # Criar DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'machine_type': machine_type,
            'parameter': param,
            'value': values
        })
        
        return df
    
    def generate_anomaly_data(self, machine_type, param, num_points, anomaly_percent=0.05, start_time=None):
        """
        Gera dados com anomalias para um parâmetro específico de uma máquina
        
        Args:
            machine_type: Tipo de máquina
            param: Parâmetro a ser gerado
            num_points: Número de pontos a serem gerados
            anomaly_percent: Porcentagem de pontos anômalos
            start_time: Timestamp inicial (opcional)
            
        Returns:
            DataFrame com os dados gerados
        """
        # Gerar dados normais primeiro
        df = self.generate_normal_data(machine_type, param, num_points, start_time)
        
        # Obter os limites para o parâmetro
        min_val, max_val, mean, std = self.machine_types[machine_type]["ranges"][param]
        
        # Calcular número de pontos anômalos
        num_anomalies = int(num_points * anomaly_percent)
        
        if num_anomalies > 0:
            # Selecionar índices aleatórios para anomalias
            anomaly_indices = np.random.choice(num_points, num_anomalies, replace=False)
            
            # Gerar valores anômalos (fora dos limites normais)
            for idx in anomaly_indices:
                # Decidir se a anomalia será acima ou abaixo do normal
                if np.random.random() > 0.5:
                    # Anomalia acima do normal
                    df.loc[idx, 'value'] = max_val + np.random.uniform(0, max_val * 0.2)
                else:
                    # Anomalia abaixo do normal
                    df.loc[idx, 'value'] = min_val - np.random.uniform(0, min_val * 0.2)
        
        return df
    
    def generate_machine_dataset(self, machine_type, num_points=24*30, anomaly_percent=0.05):
        """
        Gera um conjunto completo de dados para uma máquina
        
        Args:
            machine_type: Tipo de máquina
            num_points: Número de pontos a serem gerados
            anomaly_percent: Porcentagem de pontos anômalos
            
        Returns:
            DataFrame com os dados gerados para todos os parâmetros
        """
        if machine_type not in self.machine_types:
            raise ValueError(f"Tipo de máquina desconhecido: {machine_type}")
        
        # Obter a lista de parâmetros para o tipo de máquina
        params = self.machine_types[machine_type]["params"]
        
        # Timestamp inicial comum para todos os parâmetros
        start_time = datetime.now() - timedelta(hours=num_points)
        
        # Gerar dados para cada parâmetro
        all_data = []
        for param in params:
            # Decidir se este parâmetro terá anomalias
            if np.random.random() < 0.3:  # 30% de chance de ter anomalias
                df = self.generate_anomaly_data(machine_type, param, num_points, anomaly_percent, start_time)
            else:
                df = self.generate_normal_data(machine_type, param, num_points, start_time)
            
            all_data.append(df)
        
        # Concatenar todos os DataFrames
        combined_df = pd.concat(all_data, ignore_index=True)
        
        return combined_df
    
    def generate_factory_dataset(self, num_machines=10, num_points=24*30, anomaly_percent=0.05):
        """
        Gera um conjunto completo de dados para uma fábrica com múltiplas máquinas
        
        Args:
            num_machines: Número de máquinas a serem simuladas
            num_points: Número de pontos a serem gerados por máquina
            anomaly_percent: Porcentagem de pontos anômalos
            
        Returns:
            DataFrame com os dados gerados para todas as máquinas
        """
        # Selecionar tipos de máquinas aleatoriamente
        machine_types_list = list(self.machine_types.keys())
        selected_machines = [random.choice(machine_types_list) for _ in range(num_machines)]
        
        # Gerar dados para cada máquina
        all_data = []
        for i, machine_type in enumerate(selected_machines):
            df = self.generate_machine_dataset(machine_type, num_points, anomaly_percent)
            df['machine_id'] = i + 1  # Adicionar ID da máquina
            all_data.append(df)
        
        # Concatenar todos os DataFrames
        combined_df = pd.concat(all_data, ignore_index=True)
        
        return combined_df
    
    def save_dataset(self, df, filename):
        """
        Salva o DataFrame em um arquivo CSV
        
        Args:
            df: DataFrame a ser salvo
            filename: Nome do arquivo (sem extensão)
        """
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        df.to_csv(filepath, index=False)
        print(f"Dataset salvo em: {filepath}")
        
        return filepath

# Exemplo de uso
if __name__ == "__main__":
    generator = IndustrialDataGenerator()
    
    # Gerar dados para uma fábrica com 10 máquinas
    factory_data = generator.generate_factory_dataset(num_machines=10, num_points=24*30)
    
    # Salvar os dados
    generator.save_dataset(factory_data, "factory_data")
