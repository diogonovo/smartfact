import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
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
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'performance_optimizer.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("PerformanceOptimizer")

class PerformanceOptimizer:
    """
    Classe para otimização de desempenho de máquinas industriais
    utilizando técnicas de clustering e análise de dados
    """
    
    def __init__(self, model_dir='../models/saved'):
        """
        Inicializa o otimizador de desempenho
        
        Args:
            model_dir: Diretório para salvar os modelos treinados
        """
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.optimal_params = {}
        
        # Criar diretório para modelos se não existir
        os.makedirs(model_dir, exist_ok=True)
        
        logger.info(f"PerformanceOptimizer inicializado com diretório de modelos: {model_dir}")
    
    def preprocess_data(self, df, machine_type=None, target_column='efficiency'):
        """
        Pré-processa os dados para análise
        
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
    
    def identify_optimal_clusters(self, df, machine_type=None, max_clusters=10):
        """
        Identifica clusters ótimos de operação
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            max_clusters: Número máximo de clusters a considerar
            
        Returns:
            Modelo de clustering e métricas
        """
        logger.info(f"Identificando clusters ótimos para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Pré-processar dados
        X, _, feature_names = self.preprocess_data(df, machine_type)
        
        # Determinar número ótimo de clusters usando silhouette score
        silhouette_scores = []
        kmeans_models = {}
        
        # Testar diferentes números de clusters
        for n_clusters in range(2, min(max_clusters + 1, X.shape[0])):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X)
            
            # Calcular silhouette score
            if len(np.unique(cluster_labels)) > 1:  # Verificar se há mais de um cluster
                score = silhouette_score(X, cluster_labels)
                silhouette_scores.append(score)
                kmeans_models[n_clusters] = kmeans
                logger.info(f"Clusters: {n_clusters}, Silhouette Score: {score:.4f}")
            else:
                logger.warning(f"Apenas um cluster encontrado para n_clusters={n_clusters}")
        
        if not silhouette_scores:
            raise ValueError("Não foi possível determinar clusters ótimos")
        
        # Selecionar número ótimo de clusters
        optimal_n_clusters = list(kmeans_models.keys())[np.argmax(silhouette_scores)]
        optimal_model = kmeans_models[optimal_n_clusters]
        
        # Armazenar o modelo
        model_key = f"{machine_type if machine_type is not None else 'all'}_clustering"
        self.models[model_key] = optimal_model
        
        # Salvar o modelo
        self.save_model(model_key)
        
        logger.info(f"Número ótimo de clusters: {optimal_n_clusters}, Silhouette Score: {max(silhouette_scores):.4f}")
        
        return {
            'model_key': model_key,
            'optimal_n_clusters': optimal_n_clusters,
            'silhouette_score': max(silhouette_scores),
            'silhouette_scores': dict(zip(range(2, 2 + len(silhouette_scores)), silhouette_scores))
        }
    
    def analyze_clusters(self, df, machine_type=None):
        """
        Analisa os clusters para identificar parâmetros ótimos
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            DataFrame com análise dos clusters
        """
        logger.info(f"Analisando clusters para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Pré-processar dados
        X, y, feature_names = self.preprocess_data(df, machine_type)
        
        # Verificar se o modelo existe
        model_key = f"{machine_type if machine_type is not None else 'all'}_clustering"
        if model_key not in self.models:
            try:
                self.load_model(model_key)
            except:
                logger.info("Modelo de clustering não encontrado, treinando novo modelo")
                self.identify_optimal_clusters(df, machine_type)
        
        # Obter clusters
        cluster_labels = self.models[model_key].predict(X)
        
        # Adicionar labels ao DataFrame original
        result_df = df.copy()
        result_df['cluster'] = cluster_labels
        
        # Analisar cada cluster
        cluster_analysis = []
        
        for cluster_id in range(self.models[model_key].n_clusters):
            cluster_data = result_df[result_df['cluster'] == cluster_id]
            
            # Calcular estatísticas para cada feature
            stats = {}
            
            for feature in feature_names:
                if feature in cluster_data.columns:
                    stats[feature] = {
                        'mean': cluster_data[feature].mean(),
                        'std': cluster_data[feature].std(),
                        'min': cluster_data[feature].min(),
                        'max': cluster_data[feature].max()
                    }
            
            # Calcular eficiência média se disponível
            if 'efficiency' in cluster_data.columns:
                efficiency = cluster_data['efficiency'].mean()
            else:
                efficiency = None
            
            # Calcular consumo de energia médio se disponível
            if 'energy_consumption' in cluster_data.columns:
                energy_consumption = cluster_data['energy_consumption'].mean()
            else:
                energy_consumption = None
            
            # Adicionar análise do cluster
            cluster_analysis.append({
                'cluster_id': cluster_id,
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(result_df) * 100,
                'efficiency': efficiency,
                'energy_consumption': energy_consumption,
                'stats': stats
            })
        
        # Identificar cluster ótimo com base na eficiência ou consumo de energia
        if any(c['efficiency'] is not None for c in cluster_analysis):
            optimal_cluster = max(cluster_analysis, key=lambda x: x['efficiency'] if x['efficiency'] is not None else float('-inf'))
            optimization_metric = 'efficiency'
        elif any(c['energy_consumption'] is not None for c in cluster_analysis):
            optimal_cluster = min(cluster_analysis, key=lambda x: x['energy_consumption'] if x['energy_consumption'] is not None else float('inf'))
            optimization_metric = 'energy_consumption'
        else:
            # Se não houver métricas de eficiência, usar o cluster mais comum
            optimal_cluster = max(cluster_analysis, key=lambda x: x['size'])
            optimization_metric = 'size'
        
        # Extrair parâmetros ótimos
        optimal_params = {}
        
        for feature, stats in optimal_cluster['stats'].items():
            optimal_params[feature] = stats['mean']
        
        # Armazenar parâmetros ótimos
        self.optimal_params[machine_type if machine_type is not None else 'all'] = {
            'cluster_id': optimal_cluster['cluster_id'],
            'optimization_metric': optimization_metric,
            'params': optimal_params
        }
        
        logger.info(f"Cluster ótimo identificado: {optimal_cluster['cluster_id']}, "
                   f"Métrica: {optimization_metric}, "
                   f"Valor: {optimal_cluster.get(optimization_metric)}")
        
        return {
            'clusters': cluster_analysis,
            'optimal_cluster': optimal_cluster,
            'optimization_metric': optimization_metric,
            'optimal_params': optimal_params
        }
    
    def recommend_optimal_parameters(self, machine_type=None):
        """
        Recomenda parâmetros ótimos para operação
        
        Args:
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com parâmetros ótimos
        """
        key = machine_type if machine_type is not None else 'all'
        
        if key not in self.optimal_params:
            raise ValueError(f"Parâmetros ótimos não disponíveis para {key}. Execute analyze_clusters primeiro.")
        
        return self.optimal_params[key]
    
    def calculate_optimization_potential(self, df, machine_type=None):
        """
        Calcula o potencial de otimização para cada máquina
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            DataFrame com potencial de otimização
        """
        logger.info(f"Calculando potencial de otimização para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Filtrar por tipo de máquina se especificado
        if machine_type is not None:
            filtered_df = df[df['machine_type'] == machine_type].copy()
        else:
            filtered_df = df.copy()
        
        if filtered_df.empty:
            raise ValueError(f"Não há dados para o tipo de máquina: {machine_type}")
        
        # Obter parâmetros ótimos
        try:
            optimal_params_data = self.recommend_optimal_parameters(machine_type)
            optimal_params = optimal_params_data['params']
            optimization_metric = optimal_params_data['optimization_metric']
        except ValueError:
            logger.info("Parâmetros ótimos não disponíveis, analisando clusters")
            analysis = self.analyze_clusters(filtered_df, machine_type)
            optimal_params = analysis['optimal_params']
            optimization_metric = analysis['optimization_metric']
        
        # Calcular desvio dos parâmetros ótimos
        result_df = filtered_df.copy()
        
        # Adicionar colunas de desvio
        for param, optimal_value in optimal_params.items():
            if param in result_df.columns:
                result_df[f"{param}_deviation"] = (result_df[param] - optimal_value) / optimal_value * 100
        
        # Calcular desvio médio
        deviation_columns = [col for col in result_df.columns if col.endswith('_deviation')]
        if deviation_columns:
            result_df['mean_deviation'] = result_df[deviation_columns].abs().mean(axis=1)
        
        # Calcular potencial de otimização
        if optimization_metric == 'efficiency' and 'efficiency' in result_df.columns:
            # Para eficiência, potencial é quanto pode melhorar
            optimal_efficiency = optimal_params_data.get('efficiency', result_df['efficiency'].max())
            result_df['optimization_potential'] = (optimal_efficiency - result_df['efficiency']) / result_df['efficiency'] * 100
        elif optimization_metric == 'energy_consumption' and 'energy_consumption' in result_df.columns:
            # Para consumo de energia, potencial é quanto pode reduzir
            optimal_consumption = optimal_params_data.get('energy_consumption', result_df['energy_consumption'].min())
            result_df['optimization_potential'] = (result_df['energy_consumption'] - optimal_consumption) / result_df['energy_consumption'] * 100
        elif 'mean_deviation' in result_df.columns:
            # Se não houver métricas específicas, usar desvio médio
            result_df['optimization_potential'] = result_df['mean_deviation']
        
        logger.info(f"Potencial de otimização calculado para {len(result_df)} registros")
        
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
        
        # Salvar parâmetros ótimos
        if scaler_key in self.optimal_params:
            params_path = os.path.join(self.model_dir, f"{scaler_key}_optimal_params.joblib")
            joblib.dump(self.optimal_params[scaler_key], params_path)
        
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
        
        # Carregar parâmetros ótimos
        params_path = os.path.join(self.model_dir, f"{scaler_key}_optimal_params.joblib")
        if os.path.exists(params_path):
            self.optimal_params[scaler_key] = joblib.load(params_path)
        
        logger.info(f"Modelo carregado de: {model_path}")
        
        return self.models[model_key]
    
    def generate_optimization_data(self, num_samples=1000, num_machines=10, random_state=42):
        """
        Gera dados sintéticos para otimização
        
        Args:
            num_samples: Número de amostras a gerar
            num_machines: Número de máquinas
            random_state: Semente para reprodutibilidade
            
        Returns:
            DataFrame com dados sintéticos
        """
        logger.info(f"Gerando {num_samples} amostras de dados sintéticos para otimização")
        
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
            
            # Gerar dados de operação
            for i in range(samples_per_machine):
                # Parâmetros comuns
                temperature = np.random.uniform(50, 90)
                vibration = np.random.uniform(0.1, 2.0)
                energy_consumption = np.random.uniform(10, 50)
                
                # Parâmetros específicos por tipo de máquina
                if machine_type == 'torno_cnc':
                    speed = np.random.uniform(1000, 3000)
                    torque = np.random.uniform(20, 80)
                    specific_param = speed
                elif machine_type == 'fresadora':
                    speed = np.random.uniform(800, 2500)
                    hydraulic_pressure = np.random.uniform(70, 150)
                    specific_param = hydraulic_pressure
                elif machine_type == 'injetora_plastico':
                    pressure = np.random.uniform(80, 180)
                    cycle_time = np.random.uniform(20, 50)
                    specific_param = pressure
                elif machine_type == 'robo_industrial':
                    precision = np.random.uniform(0.05, 0.3)
                    load = np.random.uniform(20, 80)
                    specific_param = precision
                else:  # compressor
                    pressure = np.random.uniform(8, 15)
                    flow_rate = np.random.uniform(200, 400)
                    specific_param = pressure
                
                # Calcular eficiência com base nos parâmetros
                # Cada tipo de máquina tem uma função de eficiência diferente
                if machine_type == 'torno_cnc':
                    # Eficiência ótima em temperatura média, vibração baixa, velocidade alta
                    efficiency = 90 - 0.5 * abs(temperature - 70) - 20 * vibration + 0.01 * speed - 0.1 * energy_consumption
                elif machine_type == 'fresadora':
                    # Eficiência ótima em temperatura baixa, pressão média
                    efficiency = 85 - 0.3 * temperature - 15 * vibration + 0.1 * abs(hydraulic_pressure - 110) - 0.2 * energy_consumption
                elif machine_type == 'injetora_plastico':
                    # Eficiência ótima em pressão alta, tempo de ciclo baixo
                    efficiency = 80 + 0.1 * pressure - 0.5 * cycle_time - 0.2 * temperature - 10 * vibration - 0.1 * energy_consumption
                elif machine_type == 'robo_industrial':
                    # Eficiência ótima em precisão alta, carga média
                    efficiency = 95 - 100 * precision - 0.1 * abs(load - 50) - 0.3 * temperature - 5 * vibration - 0.2 * energy_consumption
                else:  # compressor
                    # Eficiência ótima em pressão média, fluxo alto
                    efficiency = 88 - 2 * abs(pressure - 10) + 0.05 * flow_rate - 0.2 * temperature - 10 * vibration - 0.15 * energy_consumption
                
                # Adicionar ruído à eficiência
                efficiency += np.random.normal(0, 3)
                efficiency = max(0, min(100, efficiency))
                
                # Adicionar registro
                data.append({
                    'machine_id': machine_id,
                    'machine_type': machine_type,
                    'temperature': temperature,
                    'vibration': vibration,
                    'energy_consumption': energy_consumption,
                    'specific_param': specific_param,
                    'efficiency': efficiency,
                    'timestamp': datetime.now() - timedelta(hours=i)
                })
        
        # Converter para DataFrame
        df = pd.DataFrame(data)
        
        logger.info(f"Gerados {len(df)} registros de dados sintéticos para otimização")
        
        return df

# Exemplo de uso
if __name__ == "__main__":
    # Criar otimizador de desempenho
    optimizer = PerformanceOptimizer()
    
    # Gerar dados sintéticos para otimização
    optimization_data = optimizer.generate_optimization_data(num_samples=5000)
    
    # Identificar clusters ótimos
    clustering_results = optimizer.identify_optimal_clusters(optimization_data)
    print(f"Resultados do clustering: {clustering_results}")
    
    # Analisar clusters
    analysis = optimizer.analyze_clusters(optimization_data)
    print(f"Cluster ótimo: {analysis['optimal_cluster']['cluster_id']}")
    print(f"Parâmetros ótimos: {analysis['optimal_params']}")
    
    # Calcular potencial de otimização
    optimization_potential = optimizer.calculate_optimization_potential(optimization_data)
    print(f"Potencial médio de otimização: {optimization_potential['optimization_potential'].mean():.2f}%")
