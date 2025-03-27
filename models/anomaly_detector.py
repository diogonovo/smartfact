import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

class AnomalyDetector:
    """
    Classe para detecção de anomalias em dados de máquinas industriais
    utilizando o algoritmo Isolation Forest
    """
    
    def __init__(self, contamination=0.05, random_state=42, model_dir='../models/saved'):
        """
        Inicializa o detector de anomalias
        
        Args:
            contamination: Proporção esperada de anomalias nos dados
            random_state: Semente para reprodutibilidade
            model_dir: Diretório para salvar os modelos treinados
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        
        # Criar diretório para modelos se não existir
        os.makedirs(model_dir, exist_ok=True)
    
    def preprocess_data(self, df, machine_type, param):
        """
        Pré-processa os dados para um parâmetro específico de uma máquina
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina
            param: Parâmetro a ser analisado
            
        Returns:
            Dados pré-processados
        """
        # Filtrar dados para o tipo de máquina e parâmetro específicos
        filtered_df = df[(df['machine_type'] == machine_type) & (df['parameter'] == param)]
        
        if filtered_df.empty:
            raise ValueError(f"Não há dados para {machine_type}, parâmetro {param}")
        
        # Extrair valores
        values = filtered_df['value'].values.reshape(-1, 1)
        
        # Criar e ajustar o scaler se não existir
        scaler_key = f"{machine_type}_{param}"
        if scaler_key not in self.scalers:
            self.scalers[scaler_key] = StandardScaler()
            scaled_values = self.scalers[scaler_key].fit_transform(values)
        else:
            scaled_values = self.scalers[scaler_key].transform(values)
        
        return scaled_values, filtered_df
    
    def train(self, df, machine_type, param):
        """
        Treina um modelo de detecção de anomalias para um parâmetro específico de uma máquina
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina
            param: Parâmetro a ser analisado
            
        Returns:
            Modelo treinado
        """
        # Pré-processar os dados
        scaled_values, _ = self.preprocess_data(df, machine_type, param)
        
        # Criar e treinar o modelo
        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples='auto'
        )
        
        model.fit(scaled_values)
        
        # Armazenar o modelo
        model_key = f"{machine_type}_{param}"
        self.models[model_key] = model
        
        return model
    
    def predict(self, df, machine_type, param):
        """
        Detecta anomalias em dados para um parâmetro específico de uma máquina
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina
            param: Parâmetro a ser analisado
            
        Returns:
            DataFrame com os dados originais e as previsões de anomalias
        """
        # Pré-processar os dados
        scaled_values, filtered_df = self.preprocess_data(df, machine_type, param)
        
        # Verificar se o modelo existe
        model_key = f"{machine_type}_{param}"
        if model_key not in self.models:
            raise ValueError(f"Modelo não treinado para {machine_type}, parâmetro {param}")
        
        # Fazer previsões
        # -1 para anomalias, 1 para dados normais
        predictions = self.models[model_key].predict(scaled_values)
        
        # Calcular pontuação de anomalia (quanto menor, mais anômalo)
        scores = self.models[model_key].decision_function(scaled_values)
        
        # Adicionar previsões ao DataFrame
        result_df = filtered_df.copy()
        result_df['anomaly'] = predictions == -1  # True para anomalias
        result_df['anomaly_score'] = scores
        
        return result_df
    
    def save_model(self, machine_type, param):
        """
        Salva o modelo treinado em disco
        
        Args:
            machine_type: Tipo de máquina
            param: Parâmetro do modelo
            
        Returns:
            Caminho do arquivo salvo
        """
        model_key = f"{machine_type}_{param}"
        if model_key not in self.models:
            raise ValueError(f"Modelo não treinado para {machine_type}, parâmetro {param}")
        
        # Salvar modelo
        model_path = os.path.join(self.model_dir, f"{model_key}_model.joblib")
        joblib.dump(self.models[model_key], model_path)
        
        # Salvar scaler
        scaler_path = os.path.join(self.model_dir, f"{model_key}_scaler.joblib")
        joblib.dump(self.scalers[model_key], scaler_path)
        
        print(f"Modelo e scaler salvos em: {model_path} e {scaler_path}")
        
        return model_path, scaler_path
    
    def load_model(self, machine_type, param):
        """
        Carrega um modelo treinado do disco
        
        Args:
            machine_type: Tipo de máquina
            param: Parâmetro do modelo
            
        Returns:
            Modelo carregado
        """
        model_key = f"{machine_type}_{param}"
        
        # Carregar modelo
        model_path = os.path.join(self.model_dir, f"{model_key}_model.joblib")
        self.models[model_key] = joblib.load(model_path)
        
        # Carregar scaler
        scaler_path = os.path.join(self.model_dir, f"{model_key}_scaler.joblib")
        self.scalers[model_key] = joblib.load(scaler_path)
        
        print(f"Modelo e scaler carregados de: {model_path} e {scaler_path}")
        
        return self.models[model_key]
    
    def train_all_parameters(self, df, machine_type):
        """
        Treina modelos para todos os parâmetros de um tipo de máquina
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina
            
        Returns:
            Dicionário com os modelos treinados
        """
        # Obter todos os parâmetros únicos para o tipo de máquina
        params = df[df['machine_type'] == machine_type]['parameter'].unique()
        
        if len(params) == 0:
            raise ValueError(f"Não há dados para o tipo de máquina: {machine_type}")
        
        # Treinar um modelo para cada parâmetro
        for param in params:
            self.train(df, machine_type, param)
            self.save_model(machine_type, param)
        
        return {f"{machine_type}_{param}": self.models[f"{machine_type}_{param}"] for param in params}
    
    def detect_anomalies_all_parameters(self, df, machine_type):
        """
        Detecta anomalias em todos os parâmetros de um tipo de máquina
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina
            
        Returns:
            DataFrame com os dados e as previsões de anomalias
        """
        # Obter todos os parâmetros únicos para o tipo de máquina
        params = df[df['machine_type'] == machine_type]['parameter'].unique()
        
        if len(params) == 0:
            raise ValueError(f"Não há dados para o tipo de máquina: {machine_type}")
        
        # Detectar anomalias para cada parâmetro
        results = []
        for param in params:
            try:
                # Verificar se o modelo existe, se não, treiná-lo
                model_key = f"{machine_type}_{param}"
                if model_key not in self.models:
                    try:
                        self.load_model(machine_type, param)
                    except:
                        self.train(df, machine_type, param)
                
                # Detectar anomalias
                result_df = self.predict(df, machine_type, param)
                results.append(result_df)
            except Exception as e:
                print(f"Erro ao processar {machine_type}, parâmetro {param}: {e}")
        
        # Concatenar resultados
        if results:
            return pd.concat(results, ignore_index=True)
        else:
            return pd.DataFrame()

# Exemplo de uso
if __name__ == "__main__":
    # Importar o gerador de dados
    from data_generator import IndustrialDataGenerator
    
    # Gerar dados simulados
    generator = IndustrialDataGenerator()
    factory_data = generator.generate_factory_dataset(num_machines=5, num_points=1000)
    
    # Criar detector de anomalias
    detector = AnomalyDetector(contamination=0.05)
    
    # Treinar modelos para um tipo de máquina
    machine_type = "torno_cnc"
    detector.train_all_parameters(factory_data, machine_type)
    
    # Detectar anomalias
    anomalies = detector.detect_anomalies_all_parameters(factory_data, machine_type)
    
    # Mostrar estatísticas
    if not anomalies.empty:
        total_points = len(anomalies)
        anomaly_points = anomalies['anomaly'].sum()
        print(f"Total de pontos: {total_points}")
        print(f"Pontos anômalos: {anomaly_points} ({anomaly_points/total_points*100:.2f}%)")
        
        # Mostrar alguns exemplos de anomalias
        print("\nExemplos de anomalias:")
        print(anomalies[anomalies['anomaly']].head())
