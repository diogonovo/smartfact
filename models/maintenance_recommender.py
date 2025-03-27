import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys
import logging
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar outros modelos
from models.anomaly_detector import AnomalyDetector
from models.failure_predictor import FailurePredictor
from models.performance_optimizer import PerformanceOptimizer

# Configurar logging
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'maintenance_recommender.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MaintenanceRecommender")

class MaintenanceRecommender:
    """
    Classe para recomendação de manutenção preditiva para máquinas industriais
    integrando resultados de detecção de anomalias, previsão de falhas e otimização de desempenho
    """
    
    def __init__(self, model_dir='../models/saved'):
        """
        Inicializa o recomendador de manutenção
        
        Args:
            model_dir: Diretório para salvar os modelos treinados
        """
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        
        # Criar diretório para modelos se não existir
        os.makedirs(model_dir, exist_ok=True)
        
        # Inicializar outros modelos
        self.anomaly_detector = AnomalyDetector(model_dir=model_dir)
        self.failure_predictor = FailurePredictor(model_dir=model_dir)
        self.performance_optimizer = PerformanceOptimizer(model_dir=model_dir)
        
        logger.info(f"MaintenanceRecommender inicializado com diretório de modelos: {model_dir}")
    
    def preprocess_data(self, df, machine_type=None):
        """
        Pré-processa os dados para análise
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            X: Features pré-processadas
            feature_names: Nomes das features
        """
        logger.info(f"Pré-processando dados para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Filtrar por tipo de máquina se especificado
        if machine_type is not None:
            df = df[df['machine_type'] == machine_type].copy()
        
        if df.empty:
            raise ValueError(f"Não há dados para o tipo de máquina: {machine_type}")
        
        # Remover colunas não numéricas e não relevantes
        exclude_columns = ['timestamp', 'collection_timestamp']
        feature_columns = [col for col in df.columns if col not in exclude_columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if not feature_columns:
            raise ValueError("Não há colunas numéricas para usar como features")
        
        # Extrair features
        X = df[feature_columns].copy()
        
        # Lidar com valores ausentes
        X.fillna(X.mean(), inplace=True)
        
        # Criar e ajustar o scaler
        scaler_key = machine_type if machine_type is not None else 'all'
        if scaler_key not in self.scalers:
            self.scalers[scaler_key] = StandardScaler()
            X_scaled = self.scalers[scaler_key].fit_transform(X)
        else:
            X_scaled = self.scalers[scaler_key].transform(X)
        
        return X_scaled, feature_columns
    
    def generate_maintenance_recommendations(self, df, machine_type=None):
        """
        Gera recomendações de manutenção com base em múltiplos modelos
        
        Args:
            df: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            DataFrame com recomendações de manutenção
        """
        logger.info(f"Gerando recomendações de manutenção para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Filtrar por tipo de máquina se especificado
        if machine_type is not None:
            filtered_df = df[df['machine_type'] == machine_type].copy()
        else:
            filtered_df = df.copy()
        
        if filtered_df.empty:
            raise ValueError(f"Não há dados para o tipo de máquina: {machine_type}")
        
        # Criar DataFrame de resultado
        result_df = filtered_df.copy()
        
        # 1. Detectar anomalias
        try:
            anomalies_df = self.anomaly_detector.detect_anomalies_all_parameters(filtered_df, machine_type)
            if not anomalies_df.empty:
                # Marcar anomalias no DataFrame de resultado
                for _, row in anomalies_df[anomalies_df['anomaly']].iterrows():
                    mask = (result_df['machine_id'] == row['machine_id']) & (result_df['parameter'] == row['parameter'])
                    result_df.loc[mask, 'has_anomaly'] = True
                    result_df.loc[mask, 'anomaly_score'] = row['anomaly_score']
        except Exception as e:
            logger.warning(f"Erro ao detectar anomalias: {e}")
            result_df['has_anomaly'] = False
            result_df['anomaly_score'] = 0
        
        # 2. Prever falhas
        try:
            failure_df = self.failure_predictor.predict_failure_probability(filtered_df, machine_type)
            if not failure_df.empty:
                # Adicionar probabilidade de falha ao DataFrame de resultado
                for col in ['failure_probability', 'predicted_failure', 'predicted_rul']:
                    if col in failure_df.columns:
                        result_df[col] = failure_df[col]
        except Exception as e:
            logger.warning(f"Erro ao prever falhas: {e}")
            result_df['failure_probability'] = 0
            result_df['predicted_failure'] = 0
            result_df['predicted_rul'] = 10000  # Valor alto para indicar sem previsão
        
        # 3. Calcular potencial de otimização
        try:
            optimization_df = self.performance_optimizer.calculate_optimization_potential(filtered_df, machine_type)
            if not optimization_df.empty:
                # Adicionar potencial de otimização ao DataFrame de resultado
                for col in ['optimization_potential', 'mean_deviation']:
                    if col in optimization_df.columns:
                        result_df[col] = optimization_df[col]
        except Exception as e:
            logger.warning(f"Erro ao calcular potencial de otimização: {e}")
            result_df['optimization_potential'] = 0
            result_df['mean_deviation'] = 0
        
        # 4. Gerar recomendações de manutenção
        self._generate_recommendations(result_df)
        
        logger.info(f"Geradas recomendações para {len(result_df)} registros")
        
        return result_df
    
    def _generate_recommendations(self, df):
        """
        Gera recomendações específicas com base nos resultados dos modelos
        
        Args:
            df: DataFrame com resultados dos modelos
            
        Returns:
            DataFrame atualizado com recomendações
        """
        # Inicializar colunas de recomendação
        df['maintenance_priority'] = 0  # 0-10, onde 10 é mais urgente
        df['recommended_action'] = 'Nenhuma ação necessária'
        df['recommended_timeframe'] = 'Nenhum'
        df['recommendation_details'] = ''
        
        # Processar cada linha
        for idx, row in df.iterrows():
            priority = 0
            actions = []
            timeframe = 'Nenhum'
            details = []
            
            # 1. Verificar anomalias
            if 'has_anomaly' in row and row['has_anomaly']:
                priority += 3
                actions.append('Investigar anomalia')
                if timeframe == 'Nenhum' or timeframe == 'Próxima manutenção programada':
                    timeframe = 'Próximos dias'
                details.append(f"Anomalia detectada em {row['parameter']} com score {row.get('anomaly_score', 'N/A')}")
            
            # 2. Verificar probabilidade de falha
            if 'failure_probability' in row:
                if row['failure_probability'] > 0.7:
                    priority += 5
                    actions.append('Manutenção corretiva urgente')
                    timeframe = 'Imediato'
                    details.append(f"Alta probabilidade de falha: {row['failure_probability']:.2f}")
                elif row['failure_probability'] > 0.4:
                    priority += 3
                    actions.append('Manutenção preventiva')
                    if timeframe == 'Nenhum' or timeframe == 'Próxima manutenção programada':
                        timeframe = 'Próxima semana'
                    details.append(f"Média probabilidade de falha: {row['failure_probability']:.2f}")
                elif row['failure_probability'] > 0.2:
                    priority += 1
                    actions.append('Monitoramento intensivo')
                    if timeframe == 'Nenhum':
                        timeframe = 'Próxima manutenção programada'
                    details.append(f"Baixa probabilidade de falha: {row['failure_probability']:.2f}")
            
            # 3. Verificar vida útil restante
            if 'predicted_rul' in row:
                if row['predicted_rul'] < 100:
                    priority += 4
                    actions.append('Planejar substituição')
                    if timeframe == 'Nenhum' or timeframe == 'Próxima manutenção programada':
                        timeframe = 'Próxima semana'
                    details.append(f"Vida útil restante baixa: {row['predicted_rul']:.0f} horas")
                elif row['predicted_rul'] < 500:
                    priority += 2
                    actions.append('Agendar manutenção preventiva')
                    if timeframe == 'Nenhum':
                        timeframe = 'Próxima manutenção programada'
                    details.append(f"Vida útil restante média: {row['predicted_rul']:.0f} horas")
            
            # 4. Verificar potencial de otimização
            if 'optimization_potential' in row and row['optimization_potential'] > 10:
                priority += 1
                actions.append('Ajustar parâmetros operacionais')
                if timeframe == 'Nenhum':
                    timeframe = 'Próxima manutenção programada'
                details.append(f"Potencial de otimização: {row['optimization_potential']:.2f}%")
            
            # Limitar prioridade a 10
            priority = min(10, priority)
            
            # Atualizar DataFrame
            df.at[idx, 'maintenance_priority'] = priority
            df.at[idx, 'recommended_action'] = ', '.join(actions) if actions else 'Nenhuma ação necessária'
            df.at[idx, 'recommended_timeframe'] = timeframe
            df.at[idx, 'recommendation_details'] = '; '.join(details) if details else 'Operação normal'
        
        return df
    
    def get_maintenance_schedule(self, df, days_ahead=30):
        """
        Gera um cronograma de manutenção para os próximos dias
        
        Args:
            df: DataFrame com recomendações de manutenção
            days_ahead: Número de dias para planejar
            
        Returns:
            DataFrame com cronograma de manutenção
        """
        logger.info(f"Gerando cronograma de manutenção para os próximos {days_ahead} dias")
        
        # Verificar se há recomendações
        if 'maintenance_priority' not in df.columns:
            raise ValueError("DataFrame não contém recomendações de manutenção. Execute generate_maintenance_recommendations primeiro.")
        
        # Filtrar apenas máquinas que precisam de manutenção
        maintenance_df = df[df['maintenance_priority'] > 0].copy()
        
        if maintenance_df.empty:
            logger.info("Nenhuma manutenção necessária")
            return pd.DataFrame()
        
        # Agrupar por máquina e obter a maior prioridade
        machine_priorities = maintenance_df.groupby('machine_id')['maintenance_priority'].max().reset_index()
        
        # Ordenar por prioridade
        machine_priorities = machine_priorities.sort_values('maintenance_priority', ascending=False)
        
        # Criar cronograma
        schedule = []
        today = datetime.now()
        
        # Distribuir manutenções ao longo dos dias com base na prioridade
        for idx, row in machine_priorities.iterrows():
            machine_id = row['machine_id']
            priority = row['maintenance_priority']
            
            # Obter detalhes da máquina
            machine_data = maintenance_df[maintenance_df['machine_id'] == machine_id].iloc[0]
            machine_type = machine_data.get('machine_type', 'Desconhecido')
            
            # Determinar prazo com base na prioridade
            if priority >= 8:  # Urgente
                days_until_maintenance = 1
            elif priority >= 5:  # Alta prioridade
                days_until_maintenance = 3
            elif priority >= 3:  # Média prioridade
                days_until_maintenance = 7
            else:  # Baixa prioridade
                days_until_maintenance = 14
            
            # Calcular data de manutenção
            maintenance_date = today + timedelta(days=days_until_maintenance)
            
            # Obter ações recomendadas
            actions = []
            for _, m_row in maintenance_df[maintenance_df['machine_id'] == machine_id].iterrows():
                if 'recommended_action' in m_row and m_row['recommended_action'] != 'Nenhuma ação necessária':
                    actions.append(m_row['recommended_action'])
            
            # Adicionar ao cronograma
            schedule.append({
                'machine_id': machine_id,
                'machine_type': machine_type,
                'priority': priority,
                'maintenance_date': maintenance_date.strftime("%Y-%m-%d"),
                'days_until_maintenance': days_until_maintenance,
                'recommended_actions': ', '.join(set(actions)),
                'estimated_duration': self._estimate_maintenance_duration(priority, actions)
            })
        
        # Converter para DataFrame
        schedule_df = pd.DataFrame(schedule)
        
        logger.info(f"Gerado cronograma com {len(schedule_df)} manutenções")
        
        return schedule_df
    
    def _estimate_maintenance_duration(self, priority, actions):
        """
        Estima a duração da manutenção com base na prioridade e ações
        
        Args:
            priority: Prioridade da manutenção
            actions: Lista de ações recomendadas
            
        Returns:
            Duração estimada em horas
        """
        # Duração base com base na prioridade
        if priority >= 8:
            base_duration = 4  # Manutenção urgente e complexa
        elif priority >= 5:
            base_duration = 3  # Manutenção significativa
        elif priority >= 3:
            base_duration = 2  # Manutenção média
        else:
            base_duration = 1  # Manutenção simples
        
        # Ajustar com base nas ações
        action_str = ', '.join(actions) if isinstance(actions, list) else actions
        
        if 'substituição' in action_str.lower():
            base_duration += 2
        if 'corretiva' in action_str.lower():
            base_duration += 1
        if 'preventiva' in action_str.lower():
            base_duration += 0.5
        
        return base_duration
    
    def get_optimization_recommendations(self, df, machine_type=None):
        """
        Obtém recomendações de otimização para parâmetros operacionais
        
        Args:
            df: DataFrame com dados das máquinas
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            DataFrame com recomendações de otimização
        """
        logger.info(f"Obtendo recomendações de otimização para {'todos os tipos' if machine_type is None else machine_type}")
        
        try:
            # Analisar clusters para identificar parâmetros ótimos
            analysis = self.performance_optimizer.analyze_clusters(df, machine_type)
            
            # Obter parâmetros ótimos
            optimal_params = analysis['optimal_params']
            
            # Criar DataFrame de recomendações
            recommendations = []
            
            # Filtrar por tipo de máquina se especificado
            if machine_type is not None:
                filtered_df = df[df['machine_type'] == machine_type].copy()
            else:
                filtered_df = df.copy()
            
            # Agrupar por máquina
            for machine_id, machine_data in filtered_df.groupby('machine_id'):
                machine_type = machine_data['machine_type'].iloc[0]
                
                # Calcular desvios dos parâmetros ótimos
                param_deviations = {}
                
                for param, optimal_value in optimal_params.items():
                    if param in machine_data.columns:
                        current_value = machine_data[param].mean()
                        deviation = (current_value - optimal_value) / optimal_value * 100
                        param_deviations[param] = {
                            'current_value': current_value,
                            'optimal_value': optimal_value,
                            'deviation': deviation,
                            'adjustment_needed': abs(deviation) > 10  # Ajuste necessário se desvio > 10%
                        }
                
                # Adicionar recomendação
                recommendations.append({
                    'machine_id': machine_id,
                    'machine_type': machine_type,
                    'parameter_deviations': param_deviations,
                    'optimization_potential': machine_data.get('optimization_potential', pd.Series([0])).mean(),
                    'recommendations': self._generate_optimization_recommendations(param_deviations)
                })
            
            logger.info(f"Geradas {len(recommendations)} recomendações de otimização")
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações de otimização: {e}")
            return []
    
    def _generate_optimization_recommendations(self, param_deviations):
        """
        Gera recomendações específicas para otimização de parâmetros
        
        Args:
            param_deviations: Dicionário com desvios dos parâmetros
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        for param, data in param_deviations.items():
            if data['adjustment_needed']:
                direction = "aumentar" if data['deviation'] < 0 else "reduzir"
                adjustment = abs(data['deviation'])
                
                if adjustment > 30:
                    urgency = "urgentemente"
                elif adjustment > 15:
                    urgency = "significativamente"
                else:
                    urgency = "ligeiramente"
                
                recommendations.append(
                    f"{param}: {direction} {urgency} de {data['current_value']:.2f} para {data['optimal_value']:.2f} "
                    f"(ajuste de {adjustment:.1f}%)"
                )
        
        return recommendations
    
    def generate_training_data(self, num_samples=1000, num_machines=10, random_state=42):
        """
        Gera dados sintéticos para treinamento dos modelos
        
        Args:
            num_samples: Número de amostras a gerar
            num_machines: Número de máquinas
            random_state: Semente para reprodutibilidade
            
        Returns:
            DataFrame com dados sintéticos
        """
        # Usar o gerador de dados do FailurePredictor
        return self.failure_predictor.generate_training_data(
            num_samples=num_samples,
            num_machines=num_machines,
            failure_rate=0.2,
            random_state=random_state
        )

# Exemplo de uso
if __name__ == "__main__":
    # Criar recomendador de manutenção
    recommender = MaintenanceRecommender()
    
    # Gerar dados sintéticos para teste
    test_data = recommender.generate_training_data(num_samples=1000, num_machines=5)
    
    # Gerar recomendações de manutenção
    recommendations = recommender.generate_maintenance_recommendations(test_data)
    
    # Mostrar estatísticas
    print(f"Total de registros: {len(recommendations)}")
    print(f"Registros com recomendações: {len(recommendations[recommendations['maintenance_priority'] > 0])}")
    
    # Gerar cronograma de manutenção
    schedule = recommender.get_maintenance_schedule(recommendations)
    
    if not schedule.empty:
        print("\nCronograma de manutenção:")
        print(schedule[['machine_id', 'priority', 'maintenance_date', 'recommended_actions']])
    
    # Obter recomendações de otimização
    optimization_recommendations = recommender.get_optimization_recommendations(test_data)
    
    if optimization_recommendations:
        print("\nRecomendações de otimização:")
        for rec in optimization_recommendations[:2]:  # Mostrar apenas as primeiras recomendações
            print(f"Máquina {rec['machine_id']} ({rec['machine_type']}):")
            for r in rec['recommendations']:
                print(f"  - {r}")
