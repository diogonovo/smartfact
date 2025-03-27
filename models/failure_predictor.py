import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
import sys
import logging
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar logging
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'failure_predictor.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("FailurePredictor")

class FailurePredictor:
    """
    Classe para previsão de falhas em máquinas industriais
    utilizando algoritmos de Machine Learning
    """
    
    def __init__(self, model_dir='../models/saved'):
        """
        Inicializa o preditor de falhas
        
        Args:
            model_dir: Diretório para salvar os modelos treinados
        """
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
        # Criar diretório para modelos se não existir
        os.makedirs(model_dir, exist_ok=True)
        
        logger.info(f"FailurePredictor inicializado com diretório de modelos: {model_dir}")
    
    def preprocess_data(self, df, machine_type=None, target_column='failure'):
        """
        Pré-processa os dados para treinamento ou previsão
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            target_column: Nome da coluna alvo
            
        Returns:
            X: Features pré-processadas
            y: Valores alvo (se disponíveis)
            feature_names: Nomes das features
        """
        logger.info(f"Pré-processando dados para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Filtrar por tipo de máquina se especificado
        if machine_type is not None:
            df = df[df['machine_type'] == machine_type].copy()
        
        if df.empty:
            raise ValueError(f"Não há dados para o tipo de máquina: {machine_type}")
        
        # Verificar se o target_column existe
        has_target = target_column in df.columns
        
        # Remover colunas não numéricas e não relevantes
        exclude_columns = ['timestamp', 'collection_timestamp', target_column] if has_target else ['timestamp', 'collection_timestamp']
        feature_columns = [col for col in df.columns if col not in exclude_columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if not feature_columns:
            raise ValueError("Não há colunas numéricas para usar como features")
        
        # Extrair features e target
        X = df[feature_columns].copy()
        y = df[target_column].copy() if has_target else None
        
        # Lidar com valores ausentes
        X.fillna(X.mean(), inplace=True)
        
        # Criar e ajustar o scaler
        scaler_key = machine_type if machine_type is not None else 'all'
        if scaler_key not in self.scalers:
            self.scalers[scaler_key] = StandardScaler()
            X_scaled = self.scalers[scaler_key].fit_transform(X)
        else:
            X_scaled = self.scalers[scaler_key].transform(X)
        
        return X_scaled, y, feature_columns
    
    def train_regression_model(self, df, machine_type=None, target_column='remaining_useful_life', test_size=0.2, random_state=42):
        """
        Treina um modelo de regressão para prever a vida útil restante
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            target_column: Nome da coluna alvo
            test_size: Proporção do conjunto de teste
            random_state: Semente para reprodutibilidade
            
        Returns:
            Métricas de avaliação do modelo
        """
        logger.info(f"Treinando modelo de regressão para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Pré-processar dados
        X, y, feature_names = self.preprocess_data(df, machine_type, target_column)
        
        if y is None:
            raise ValueError(f"Coluna alvo '{target_column}' não encontrada no DataFrame")
        
        # Dividir em conjuntos de treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        
        # Criar e treinar o modelo
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=random_state,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Fazer previsões no conjunto de teste
        y_pred = model.predict(X_test)
        
        # Calcular métricas
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Armazenar o modelo
        model_key = f"{machine_type if machine_type is not None else 'all'}_regression"
        self.models[model_key] = model
        
        # Armazenar importância das features
        self.feature_importance[model_key] = dict(zip(feature_names, model.feature_importances_))
        
        # Salvar o modelo
        self.save_model(model_key)
        
        logger.info(f"Modelo de regressão treinado com RMSE: {rmse:.4f}, R²: {r2:.4f}")
        
        return {
            'model_key': model_key,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'feature_importance': self.feature_importance[model_key]
        }
    
    def train_classification_model(self, df, machine_type=None, target_column='failure', test_size=0.2, random_state=42):
        """
        Treina um modelo de classificação para prever falhas
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            target_column: Nome da coluna alvo
            test_size: Proporção do conjunto de teste
            random_state: Semente para reprodutibilidade
            
        Returns:
            Métricas de avaliação do modelo
        """
        logger.info(f"Treinando modelo de classificação para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Pré-processar dados
        X, y, feature_names = self.preprocess_data(df, machine_type, target_column)
        
        if y is None:
            raise ValueError(f"Coluna alvo '{target_column}' não encontrada no DataFrame")
        
        # Dividir em conjuntos de treino e teste
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        
        # Criar e treinar o modelo
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=random_state,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        model.fit(X_train, y_train)
        
        # Fazer previsões no conjunto de teste
        y_pred = model.predict(X_test)
        
        # Calcular métricas
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Armazenar o modelo
        model_key = f"{machine_type if machine_type is not None else 'all'}_classification"
        self.models[model_key] = model
        
        # Armazenar importância das features
        self.feature_importance[model_key] = dict(zip(feature_names, model.feature_importances_))
        
        # Salvar o modelo
        self.save_model(model_key)
        
        logger.info(f"Modelo de classificação treinado com Acurácia: {accuracy:.4f}, F1: {f1:.4f}")
        
        return {
            'model_key': model_key,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'feature_importance': self.feature_importance[model_key]
        }
    
    def predict_remaining_useful_life(self, df, machine_type=None):
        """
        Prevê a vida útil restante para máquinas
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            DataFrame com os dados originais e as previsões
        """
        logger.info(f"Prevendo vida útil restante para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Pré-processar dados
        X, _, feature_names = self.preprocess_data(df, machine_type, target_column='remaining_useful_life')
        
        # Verificar se o modelo existe
        model_key = f"{machine_type if machine_type is not None else 'all'}_regression"
        if model_key not in self.models:
            try:
                self.load_model(model_key)
            except:
                raise ValueError(f"Modelo não treinado para {model_key}")
        
        # Fazer previsões
        predictions = self.models[model_key].predict(X)
        
        # Adicionar previsões ao DataFrame
        result_df = df.copy()
        result_df['predicted_rul'] = predictions
        
        return result_df
    
    def predict_failure_probability(self, df, machine_type=None):
        """
        Prevê a probabilidade de falha para máquinas
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            DataFrame com os dados originais e as previsões
        """
        logger.info(f"Prevendo probabilidade de falha para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Pré-processar dados
        X, _, feature_names = self.preprocess_data(df, machine_type, target_column='failure')
        
        # Verificar se o modelo existe
        model_key = f"{machine_type if machine_type is not None else 'all'}_classification"
        if model_key not in self.models:
            try:
                self.load_model(model_key)
            except:
                raise ValueError(f"Modelo não treinado para {model_key}")
        
        # Fazer previsões
        probabilities = self.models[model_key].predict_proba(X)
        
        # Adicionar previsões ao DataFrame
        result_df = df.copy()
        
        # Obter índice da classe positiva (falha)
        positive_class_idx = list(self.models[model_key].classes_).index(1) if 1 in self.models[model_key].classes_ else 1
        
        result_df['failure_probability'] = probabilities[:, positive_class_idx]
        result_df['predicted_failure'] = self.models[model_key].predict(X)
        
        return result_df
    
    def save_model(self, model_key):
        """
        Salva o modelo treinado em disco
        
        Args:
            model_key: Chave do modelo
            
        Returns:
            Caminho do arquivo salvo
        """
        if model_key not in self.models:
            raise ValueError(f"Modelo não encontrado: {model_key}")
        
        # Salvar modelo
        model_path = os.path.join(self.model_dir, f"{model_key}_model.joblib")
        joblib.dump(self.models[model_key], model_path)
        
        # Salvar scaler
        scaler_key = model_key.split('_')[0]  # Extrair tipo de máquina ou 'all'
        if scaler_key in self.scalers:
            scaler_path = os.path.join(self.model_dir, f"{scaler_key}_scaler.joblib")
            joblib.dump(self.scalers[scaler_key], scaler_path)
        
        # Salvar importância das features
        if model_key in self.feature_importance:
            importance_path = os.path.join(self.model_dir, f"{model_key}_importance.joblib")
            joblib.dump(self.feature_importance[model_key], importance_path)
        
        logger.info(f"Modelo salvo em: {model_path}")
        
        return model_path
    
    def load_model(self, model_key):
        """
        Carrega um modelo treinado do disco
        
        Args:
            model_key: Chave do modelo
            
        Returns:
            Modelo carregado
        """
        # Carregar modelo
        model_path = os.path.join(self.model_dir, f"{model_key}_model.joblib")
        self.models[model_key] = joblib.load(model_path)
        
        # Carregar scaler
        scaler_key = model_key.split('_')[0]  # Extrair tipo de máquina ou 'all'
        scaler_path = os.path.join(self.model_dir, f"{scaler_key}_scaler.joblib")
        if os.path.exists(scaler_path):
            self.scalers[scaler_key] = joblib.load(scaler_path)
        
        # Carregar importância das features
        importance_path = os.path.join(self.model_dir, f"{model_key}_importance.joblib")
        if os.path.exists(importance_path):
            self.feature_importance[model_key] = joblib.load(importance_path)
        
        logger.info(f"Modelo carregado de: {model_path}")
        
        return self.models[model_key]
    
    def generate_training_data(self, num_samples=1000, num_machines=10, failure_rate=0.2, random_state=42):
        """
        Gera dados sintéticos para treinamento dos modelos
        
        Args:
            num_samples: Número de amostras a gerar
            num_machines: Número de máquinas
            failure_rate: Taxa de falhas
            random_state: Semente para reprodutibilidade
            
        Returns:
            DataFrame com dados sintéticos
        """
        logger.info(f"Gerando {num_samples} amostras de dados sintéticos para treinamento")
        
        np.random.seed(random_state)
        
        # Definir tipos de máquinas
        machine_types = ['torno_cnc', 'fresadora', 'injetora_plastico', 'robo_industrial', 'compressor']
        
        # Criar DataFrame vazio
        data = []
        
        # Gerar dados para cada máquina
        for machine_id in range(1, num_machines + 1):
            machine_type = machine_types[machine_id % len(machine_types)]
            
            # Número de amostras por máquina
            samples_per_machine = num_samples // num_machines
            
            # Gerar dados de operação normal
            for i in range(samples_per_machine):
                # Tempo de operação (horas)
                operation_time = np.random.uniform(0, 10000)
                
                # Parâmetros comuns
                temperature = 60 + 20 * np.random.randn() + operation_time / 1000
                vibration = 0.5 + 0.3 * np.random.randn() + operation_time / 5000
                energy_consumption = 20 + 5 * np.random.randn() + operation_time / 2000
                
                # Parâmetros específicos por tipo de máquina
                if machine_type == 'torno_cnc':
                    speed = 2000 + 200 * np.random.randn() - operation_time / 1000
                    torque = 50 + 10 * np.random.randn() + operation_time / 2000
                    specific_param = speed
                elif machine_type == 'fresadora':
                    speed = 1500 + 150 * np.random.randn() - operation_time / 1000
                    hydraulic_pressure = 100 + 15 * np.random.randn() - operation_time / 3000
                    specific_param = hydraulic_pressure
                elif machine_type == 'injetora_plastico':
                    pressure = 120 + 20 * np.random.randn() - operation_time / 2000
                    cycle_time = 30 + 5 * np.random.randn() + operation_time / 4000
                    specific_param = pressure
                elif machine_type == 'robo_industrial':
                    precision = 0.1 + 0.05 * np.random.randn() + operation_time / 10000
                    load = 50 + 15 * np.random.randn()
                    specific_param = precision
                else:  # compressor
                    pressure = 10 + 1 * np.random.randn() - operation_time / 3000
                    flow_rate = 300 + 50 * np.random.randn() - operation_time / 2000
                    specific_param = pressure
                
                # Calcular vida útil restante (RUL)
                max_life = 10000  # Horas
                remaining_useful_life = max(0, max_life - operation_time)
                
                # Adicionar ruído à RUL
                remaining_useful_life += np.random.normal(0, max_life * 0.05)
                remaining_useful_life = max(0, remaining_useful_life)
                
                # Determinar se há falha
                # Probabilidade de falha aumenta com o tempo de operação
                failure_prob = min(1.0, failure_rate * (operation_time / max_life) ** 2)
                failure = 1 if np.random.random() < failure_prob else 0
                
                # Se há falha, ajustar parâmetros para refletir condição anormal
                if failure:
                    # Aumentar temperatura e vibração
                    temperature += np.random.uniform(10, 30)
                    vibration += np.random.uniform(0.5, 2.0)
                    energy_consumption += np.random.uniform(5, 15)
                    
                    # Reduzir vida útil restante
                    remaining_useful_life = np.random.uniform(0, 100)
                
                # Adicionar registro
                data.append({
                    'machine_id': machine_id,
                    'machine_type': machine_type,
                    'operation_time': operation_time,
                    'temperature': temperature,
                    'vibration': vibration,
                    'energy_consumption': energy_consumption,
                    'specific_param': specific_param,
                    'remaining_useful_life': remaining_useful_life,
                    'failure': failure,
                    'timestamp': datetime.now() - timedelta(hours=int(operation_time))
                })
        
        # Converter para DataFrame
        df = pd.DataFrame(data)
        
        logger.info(f"Gerados {len(df)} registros de dados sintéticos")
        
        return df

# Exemplo de uso
if __name__ == "__main__":
    # Criar preditor de falhas
    predictor = FailurePredictor()
    
    # Gerar dados sintéticos para treinamento
    training_data = predictor.generate_training_data(num_samples=5000, failure_rate=0.2)
    
    # Treinar modelo de regressão para prever vida útil restante
    regression_metrics = predictor.train_regression_model(training_data)
    print(f"Métricas do modelo de regressão: {regression_metrics}")
    
    # Treinar modelo de classificação para prever falhas
    classification_metrics = predictor.train_classification_model(training_data)
    print(f"Métricas do modelo de classificação: {classification_metrics}")
    
    # Gerar dados para teste
    test_data = predictor.generate_training_data(num_samples=100, failure_rate=0.3)
    
    # Prever vida útil restante
    rul_predictions = predictor.predict_remaining_useful_life(test_data)
    print(f"Previsões de vida útil restante: {rul_predictions['predicted_rul'].describe()}")
    
    # Prever probabilidade de falha
    failure_predictions = predictor.predict_failure_probability(test_data)
    print(f"Previsões de probabilidade de falha: {failure_predictions['failure_probability'].describe()}")
