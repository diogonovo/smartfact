import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, GridSearchCV
import os
import sys
import logging
import joblib
from datetime import datetime

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar os modelos
from models.anomaly_detector import AnomalyDetector
from models.failure_predictor import FailurePredictor
from models.performance_optimizer import PerformanceOptimizer
from models.maintenance_recommender import MaintenanceRecommender

# Configurar logging
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'model_evaluator.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ModelEvaluator")

class ModelEvaluator:
    """
    Classe para avaliação e otimização dos modelos de Machine Learning
    """
    
    def __init__(self, model_dir='../models/saved', results_dir='../models/evaluation'):
        """
        Inicializa o avaliador de modelos
        
        Args:
            model_dir: Diretório onde os modelos estão salvos
            results_dir: Diretório para salvar os resultados da avaliação
        """
        self.model_dir = model_dir
        self.results_dir = results_dir
        
        # Criar diretórios se não existirem
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        os.makedirs(os.path.join(results_dir, 'plots'), exist_ok=True)
        
        # Inicializar modelos
        self.anomaly_detector = AnomalyDetector(model_dir=model_dir)
        self.failure_predictor = FailurePredictor(model_dir=model_dir)
        self.performance_optimizer = PerformanceOptimizer(model_dir=model_dir)
        self.maintenance_recommender = MaintenanceRecommender(model_dir=model_dir)
        
        logger.info(f"ModelEvaluator inicializado com diretório de modelos: {model_dir}")
    
    def generate_evaluation_data(self, num_samples=2000, num_machines=10, random_state=42):
        """
        Gera dados sintéticos para avaliação dos modelos
        
        Args:
            num_samples: Número de amostras a gerar
            num_machines: Número de máquinas
            random_state: Semente para reprodutibilidade
            
        Returns:
            DataFrame com dados sintéticos
        """
        logger.info(f"Gerando {num_samples} amostras de dados sintéticos para avaliação")
        
        # Usar o gerador de dados do FailurePredictor
        return self.failure_predictor.generate_training_data(
            num_samples=num_samples,
            num_machines=num_machines,
            failure_rate=0.3,  # Taxa de falha maior para avaliação
            random_state=random_state
        )
    
    def evaluate_anomaly_detector(self, data, machine_type=None):
        """
        Avalia o detector de anomalias
        
        Args:
            data: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com métricas de avaliação
        """
        logger.info(f"Avaliando detector de anomalias para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Detectar anomalias
        anomalies_df = self.anomaly_detector.detect_anomalies_all_parameters(data, machine_type)
        
        # Calcular métricas
        metrics = {}
        
        # Verificar se há coluna de falha para comparar
        if 'failure' in data.columns:
            # Agrupar por máquina e verificar se há falha
            machine_failures = data.groupby('machine_id')['failure'].max().reset_index()
            machine_failures.rename(columns={'failure': 'actual_failure'}, inplace=True)
            
            # Agrupar anomalias por máquina
            if not anomalies_df.empty and 'anomaly' in anomalies_df.columns:
                machine_anomalies = anomalies_df.groupby('machine_id')['anomaly'].max().reset_index()
                machine_anomalies.rename(columns={'anomaly': 'detected_anomaly'}, inplace=True)
                
                # Mesclar resultados
                evaluation_df = pd.merge(machine_failures, machine_anomalies, on='machine_id', how='left')
                evaluation_df['detected_anomaly'].fillna(0, inplace=True)
                
                # Calcular matriz de confusão
                y_true = evaluation_df['actual_failure'].astype(int)
                y_pred = evaluation_df['detected_anomaly'].astype(int)
                
                tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                
                # Calcular métricas
                accuracy = (tp + tn) / (tp + tn + fp + fn)
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                
                metrics = {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'true_positives': tp,
                    'false_positives': fp,
                    'true_negatives': tn,
                    'false_negatives': fn
                }
                
                # Gerar relatório de classificação
                report = classification_report(y_true, y_pred, output_dict=True)
                metrics['classification_report'] = report
                
                # Plotar matriz de confusão
                plt.figure(figsize=(8, 6))
                sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, fmt='d', cmap='Blues',
                           xticklabels=['Normal', 'Anomalia'], yticklabels=['Normal', 'Falha'])
                plt.xlabel('Previsto')
                plt.ylabel('Real')
                plt.title('Matriz de Confusão - Detector de Anomalias')
                
                # Salvar plot
                plot_path = os.path.join(self.results_dir, 'plots', f"anomaly_detector_cm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(plot_path)
                plt.close()
                
                metrics['confusion_matrix_plot'] = plot_path
        
        # Calcular distribuição de scores de anomalia
        if not anomalies_df.empty and 'anomaly_score' in anomalies_df.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(anomalies_df['anomaly_score'], bins=50, kde=True)
            plt.axvline(x=self.anomaly_detector.threshold, color='r', linestyle='--', label=f'Limiar ({self.anomaly_detector.threshold})')
            plt.xlabel('Score de Anomalia')
            plt.ylabel('Frequência')
            plt.title('Distribuição de Scores de Anomalia')
            plt.legend()
            
            # Salvar plot
            plot_path = os.path.join(self.results_dir, 'plots', f"anomaly_score_dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_path)
            plt.close()
            
            metrics['anomaly_score_distribution_plot'] = plot_path
            metrics['anomaly_score_mean'] = anomalies_df['anomaly_score'].mean()
            metrics['anomaly_score_std'] = anomalies_df['anomaly_score'].std()
            metrics['anomaly_score_min'] = anomalies_df['anomaly_score'].min()
            metrics['anomaly_score_max'] = anomalies_df['anomaly_score'].max()
        
        # Salvar métricas
        metrics_path = os.path.join(self.results_dir, f"anomaly_detector_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        joblib.dump(metrics, metrics_path)
        
        logger.info(f"Avaliação do detector de anomalias concluída e salva em: {metrics_path}")
        
        return metrics
    
    def evaluate_failure_predictor(self, data, machine_type=None):
        """
        Avalia o preditor de falhas
        
        Args:
            data: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com métricas de avaliação
        """
        logger.info(f"Avaliando preditor de falhas para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Dividir dados em treino e teste
        from sklearn.model_selection import train_test_split
        
        train_data, test_data = train_test_split(data, test_size=0.3, random_state=42)
        
        # Treinar modelo de classificação
        classification_metrics = self.failure_predictor.train_classification_model(
            train_data, machine_type, target_column='failure'
        )
        
        # Treinar modelo de regressão
        regression_metrics = self.failure_predictor.train_regression_model(
            train_data, machine_type, target_column='remaining_useful_life'
        )
        
        # Fazer previsões no conjunto de teste
        failure_predictions = self.failure_predictor.predict_failure_probability(test_data, machine_type)
        rul_predictions = self.failure_predictor.predict_remaining_useful_life(test_data, machine_type)
        
        # Avaliar modelo de classificação
        if 'failure' in test_data.columns and 'predicted_failure' in failure_predictions.columns:
            y_true = test_data['failure'].astype(int)
            y_pred = failure_predictions['predicted_failure'].astype(int)
            
            # Calcular matriz de confusão
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            
            # Calcular métricas
            accuracy = (tp + tn) / (tp + tn + fp + fn)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            classification_metrics.update({
                'test_accuracy': accuracy,
                'test_precision': precision,
                'test_recall': recall,
                'test_f1_score': f1,
                'test_true_positives': tp,
                'test_false_positives': fp,
                'test_true_negatives': tn,
                'test_false_negatives': fn
            })
            
            # Gerar relatório de classificação
            report = classification_report(y_true, y_pred, output_dict=True)
            classification_metrics['test_classification_report'] = report
            
            # Plotar matriz de confusão
            plt.figure(figsize=(8, 6))
            sns.heatmap(confusion_matrix(y_true, y_pred), annot=True, fmt='d', cmap='Blues',
                       xticklabels=['Normal', 'Falha'], yticklabels=['Normal', 'Falha'])
            plt.xlabel('Previsto')
            plt.ylabel('Real')
            plt.title('Matriz de Confusão - Preditor de Falhas')
            
            # Salvar plot
            plot_path = os.path.join(self.results_dir, 'plots', f"failure_predictor_cm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_path)
            plt.close()
            
            classification_metrics['confusion_matrix_plot'] = plot_path
            
            # Plotar distribuição de probabilidades de falha
            if 'failure_probability' in failure_predictions.columns:
                plt.figure(figsize=(10, 6))
                sns.histplot(failure_predictions['failure_probability'], bins=50, kde=True)
                plt.xlabel('Probabilidade de Falha')
                plt.ylabel('Frequência')
                plt.title('Distribuição de Probabilidades de Falha')
                
                # Salvar plot
                plot_path = os.path.join(self.results_dir, 'plots', f"failure_prob_dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(plot_path)
                plt.close()
                
                classification_metrics['failure_probability_distribution_plot'] = plot_path
        
        # Avaliar modelo de regressão
        if 'remaining_useful_life' in test_data.columns and 'predicted_rul' in rul_predictions.columns:
            y_true = test_data['remaining_useful_life']
            y_pred = rul_predictions['predicted_rul']
            
            # Calcular métricas
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            
            regression_metrics.update({
                'test_mse': mse,
                'test_rmse': rmse,
                'test_r2': r2
            })
            
            # Plotar valores reais vs. previstos
            plt.figure(figsize=(10, 6))
            plt.scatter(y_true, y_pred, alpha=0.5)
            plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
            plt.xlabel('Vida Útil Restante Real')
            plt.ylabel('Vida Útil Restante Prevista')
            plt.title('Valores Reais vs. Previstos - Vida Útil Restante')
            
            # Salvar plot
            plot_path = os.path.join(self.results_dir, 'plots', f"rul_prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_path)
            plt.close()
            
            regression_metrics['rul_prediction_plot'] = plot_path
        
        # Combinar métricas
        metrics = {
            'classification': classification_metrics,
            'regression': regression_metrics
        }
        
        # Salvar métricas
        metrics_path = os.path.join(self.results_dir, f"failure_predictor_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        joblib.dump(metrics, metrics_path)
        
        logger.info(f"Avaliação do preditor de falhas concluída e salva em: {metrics_path}")
        
        return metrics
    
    def evaluate_performance_optimizer(self, data, machine_type=None):
        """
        Avalia o otimizador de desempenho
        
        Args:
            data: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com métricas de avaliação
        """
        logger.info(f"Avaliando otimizador de desempenho para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Identificar clusters ótimos
        clustering_results = self.performance_optimizer.identify_optimal_clusters(data, machine_type)
        
        # Analisar clusters
        analysis = self.performance_optimizer.analyze_clusters(data, machine_type)
        
        # Calcular potencial de otimização
        optimization_potential = self.performance_optimizer.calculate_optimization_potential(data, machine_type)
        
        # Calcular métricas
        metrics = {
            'clustering': clustering_results,
            'cluster_analysis': {
                'optimal_cluster': analysis['optimal_cluster']['cluster_id'],
                'optimization_metric': analysis['optimization_metric'],
                'num_clusters': len(analysis['clusters'])
            },
            'optimization_potential': {
                'mean': optimization_potential['optimization_potential'].mean(),
                'std': optimization_potential['optimization_potential'].std(),
                'min': optimization_potential['optimization_potential'].min(),
                'max': optimization_potential['optimization_potential'].max()
            }
        }
        
        # Plotar distribuição de potencial de otimização
        if 'optimization_potential' in optimization_potential.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(optimization_potential['optimization_potential'], bins=50, kde=True)
            plt.xlabel('Potencial de Otimização (%)')
            plt.ylabel('Frequência')
            plt.title('Distribuição de Potencial de Otimização')
            
            # Salvar plot
            plot_path = os.path.join(self.results_dir, 'plots', f"optimization_potential_dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_path)
            plt.close()
            
            metrics['optimization_potential_distribution_plot'] = plot_path
        
        # Plotar silhouette scores
        if 'silhouette_scores' in clustering_results:
            plt.figure(figsize=(10, 6))
            scores = clustering_results['silhouette_scores']
            plt.plot(list(scores.keys()), list(scores.values()), 'o-')
            plt.axvline(x=clustering_results['optimal_n_clusters'], color='r', linestyle='--', 
                       label=f'Número ótimo de clusters ({clustering_results["optimal_n_clusters"]})')
            plt.xlabel('Número de Clusters')
            plt.ylabel('Silhouette Score')
            plt.title('Silhouette Scores por Número de Clusters')
            plt.legend()
            
            # Salvar plot
            plot_path = os.path.join(self.results_dir, 'plots', f"silhouette_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_path)
            plt.close()
            
            metrics['silhouette_scores_plot'] = plot_path
        
        # Salvar métricas
        metrics_path = os.path.join(self.results_dir, f"performance_optimizer_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        joblib.dump(metrics, metrics_path)
        
        logger.info(f"Avaliação do otimizador de desempenho concluída e salva em: {metrics_path}")
        
        return metrics
    
    def evaluate_maintenance_recommender(self, data, machine_type=None):
        """
        Avalia o recomendador de manutenção
        
        Args:
            data: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com métricas de avaliação
        """
        logger.info(f"Avaliando recomendador de manutenção para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Gerar recomendações de manutenção
        recommendations = self.maintenance_recommender.generate_maintenance_recommendations(data, machine_type)
        
        # Gerar cronograma de manutenção
        schedule = self.maintenance_recommender.get_maintenance_schedule(recommendations)
        
        # Calcular métricas
        metrics = {
            'recommendations': {
                'total_records': len(recommendations),
                'records_with_recommendations': len(recommendations[recommendations['maintenance_priority'] > 0]),
                'priority_distribution': recommendations['maintenance_priority'].value_counts().to_dict(),
                'action_distribution': recommendations['recommended_action'].value_counts().to_dict(),
                'timeframe_distribution': recommendations['recommended_timeframe'].value_counts().to_dict()
            }
        }
        
        if not schedule.empty:
            metrics['schedule'] = {
                'total_maintenance_tasks': len(schedule),
                'priority_distribution': schedule['priority'].value_counts().to_dict(),
                'days_until_maintenance_mean': schedule['days_until_maintenance'].mean(),
                'estimated_duration_mean': schedule['estimated_duration'].mean()
            }
        
        # Plotar distribuição de prioridades
        plt.figure(figsize=(10, 6))
        sns.countplot(x='maintenance_priority', data=recommendations)
        plt.xlabel('Prioridade de Manutenção')
        plt.ylabel('Contagem')
        plt.title('Distribuição de Prioridades de Manutenção')
        
        # Salvar plot
        plot_path = os.path.join(self.results_dir, 'plots', f"maintenance_priority_dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(plot_path)
        plt.close()
        
        metrics['maintenance_priority_distribution_plot'] = plot_path
        
        # Plotar distribuição de prazos
        plt.figure(figsize=(12, 6))
        sns.countplot(y='recommended_timeframe', data=recommendations)
        plt.xlabel('Contagem')
        plt.ylabel('Prazo Recomendado')
        plt.title('Distribuição de Prazos Recomendados')
        
        # Salvar plot
        plot_path = os.path.join(self.results_dir, 'plots', f"timeframe_dist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(plot_path)
        plt.close()
        
        metrics['timeframe_distribution_plot'] = plot_path
        
        # Salvar métricas
        metrics_path = os.path.join(self.results_dir, f"maintenance_recommender_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        joblib.dump(metrics, metrics_path)
        
        logger.info(f"Avaliação do recomendador de manutenção concluída e salva em: {metrics_path}")
        
        return metrics
    
    def optimize_anomaly_detector(self, data, machine_type=None):
        """
        Otimiza o detector de anomalias
        
        Args:
            data: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com parâmetros otimizados
        """
        logger.info(f"Otimizando detector de anomalias para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Testar diferentes limiares
        thresholds = np.linspace(0.01, 0.2, 20)
        results = []
        
        for threshold in thresholds:
            # Configurar detector com novo limiar
            self.anomaly_detector.threshold = threshold
            
            # Detectar anomalias
            anomalies_df = self.anomaly_detector.detect_anomalies_all_parameters(data, machine_type)
            
            # Verificar se há coluna de falha para comparar
            if 'failure' in data.columns:
                # Agrupar por máquina e verificar se há falha
                machine_failures = data.groupby('machine_id')['failure'].max().reset_index()
                machine_failures.rename(columns={'failure': 'actual_failure'}, inplace=True)
                
                # Agrupar anomalias por máquina
                if not anomalies_df.empty and 'anomaly' in anomalies_df.columns:
                    machine_anomalies = anomalies_df.groupby('machine_id')['anomaly'].max().reset_index()
                    machine_anomalies.rename(columns={'anomaly': 'detected_anomaly'}, inplace=True)
                    
                    # Mesclar resultados
                    evaluation_df = pd.merge(machine_failures, machine_anomalies, on='machine_id', how='left')
                    evaluation_df['detected_anomaly'].fillna(0, inplace=True)
                    
                    # Calcular matriz de confusão
                    y_true = evaluation_df['actual_failure'].astype(int)
                    y_pred = evaluation_df['detected_anomaly'].astype(int)
                    
                    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                    
                    # Calcular métricas
                    accuracy = (tp + tn) / (tp + tn + fp + fn)
                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                    
                    results.append({
                        'threshold': threshold,
                        'accuracy': accuracy,
                        'precision': precision,
                        'recall': recall,
                        'f1_score': f1,
                        'true_positives': tp,
                        'false_positives': fp,
                        'true_negatives': tn,
                        'false_negatives': fn
                    })
        
        if results:
            # Converter para DataFrame
            results_df = pd.DataFrame(results)
            
            # Encontrar limiar ótimo com base no F1-score
            optimal_result = results_df.loc[results_df['f1_score'].idxmax()]
            optimal_threshold = optimal_result['threshold']
            
            # Atualizar detector com limiar ótimo
            self.anomaly_detector.threshold = optimal_threshold
            
            # Plotar resultados
            plt.figure(figsize=(12, 8))
            plt.subplot(2, 2, 1)
            plt.plot(results_df['threshold'], results_df['accuracy'], 'o-')
            plt.xlabel('Limiar')
            plt.ylabel('Acurácia')
            plt.title('Acurácia vs. Limiar')
            
            plt.subplot(2, 2, 2)
            plt.plot(results_df['threshold'], results_df['precision'], 'o-')
            plt.xlabel('Limiar')
            plt.ylabel('Precisão')
            plt.title('Precisão vs. Limiar')
            
            plt.subplot(2, 2, 3)
            plt.plot(results_df['threshold'], results_df['recall'], 'o-')
            plt.xlabel('Limiar')
            plt.ylabel('Recall')
            plt.title('Recall vs. Limiar')
            
            plt.subplot(2, 2, 4)
            plt.plot(results_df['threshold'], results_df['f1_score'], 'o-')
            plt.axvline(x=optimal_threshold, color='r', linestyle='--', 
                       label=f'Limiar ótimo ({optimal_threshold:.4f})')
            plt.xlabel('Limiar')
            plt.ylabel('F1-Score')
            plt.title('F1-Score vs. Limiar')
            plt.legend()
            
            plt.tight_layout()
            
            # Salvar plot
            plot_path = os.path.join(self.results_dir, 'plots', f"anomaly_detector_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            plt.savefig(plot_path)
            plt.close()
            
            # Salvar resultados
            optimization_results = {
                'optimal_threshold': optimal_threshold,
                'optimal_metrics': optimal_result.to_dict(),
                'all_results': results_df.to_dict(orient='records'),
                'optimization_plot': plot_path
            }
            
            # Salvar resultados
            results_path = os.path.join(self.results_dir, f"anomaly_detector_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            joblib.dump(optimization_results, results_path)
            
            logger.info(f"Otimização do detector de anomalias concluída. Limiar ótimo: {optimal_threshold:.4f}")
            
            return optimization_results
        
        logger.warning("Não foi possível otimizar o detector de anomalias devido à falta de dados de falha")
        return None
    
    def optimize_failure_predictor(self, data, machine_type=None):
        """
        Otimiza o preditor de falhas
        
        Args:
            data: DataFrame com os dados
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com parâmetros otimizados
        """
        logger.info(f"Otimizando preditor de falhas para {'todos os tipos' if machine_type is None else machine_type}")
        
        # Dividir dados em treino e teste
        from sklearn.model_selection import train_test_split
        
        train_data, test_data = train_test_split(data, test_size=0.3, random_state=42)
        
        # Pré-processar dados para classificação
        X, y, feature_names = self.failure_predictor.preprocess_data(train_data, machine_type, target_column='failure')
        
        if y is None:
            logger.warning("Não foi possível otimizar o preditor de falhas devido à falta de dados de falha")
            return None
        
        # Definir parâmetros para otimização
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # Criar modelo base
        from sklearn.ensemble import RandomForestClassifier
        base_model = RandomForestClassifier(random_state=42, class_weight='balanced')
        
        # Realizar busca em grade
        grid_search = GridSearchCV(
            base_model, param_grid, cv=5, scoring='f1_weighted', n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X, y)
        
        # Obter melhores parâmetros
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_
        
        # Criar modelo com melhores parâmetros
        best_model = RandomForestClassifier(
            n_estimators=best_params['n_estimators'],
            max_depth=best_params['max_depth'],
            min_samples_split=best_params['min_samples_split'],
            min_samples_leaf=best_params['min_samples_leaf'],
            random_state=42,
            class_weight='balanced'
        )
        
        # Treinar modelo com melhores parâmetros
        best_model.fit(X, y)
        
        # Atualizar modelo no preditor de falhas
        model_key = f"{machine_type if machine_type is not None else 'all'}_classification"
        self.failure_predictor.models[model_key] = best_model
        
        # Salvar modelo otimizado
        self.failure_predictor.save_model(model_key)
        
        # Avaliar modelo otimizado no conjunto de teste
        X_test, y_test, _ = self.failure_predictor.preprocess_data(test_data, machine_type, target_column='failure')
        y_pred = best_model.predict(X_test)
        
        # Calcular métricas
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Salvar resultados
        optimization_results = {
            'best_params': best_params,
            'best_cv_score': best_score,
            'test_metrics': {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            },
            'all_results': grid_search.cv_results_
        }
        
        # Plotar importância das features
        feature_importance = best_model.feature_importances_
        indices = np.argsort(feature_importance)[::-1]
        
        plt.figure(figsize=(12, 8))
        plt.bar(range(len(indices)), feature_importance[indices], align='center')
        plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=90)
        plt.xlabel('Features')
        plt.ylabel('Importância')
        plt.title('Importância das Features - Preditor de Falhas Otimizado')
        plt.tight_layout()
        
        # Salvar plot
        plot_path = os.path.join(self.results_dir, 'plots', f"failure_predictor_feature_importance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(plot_path)
        plt.close()
        
        optimization_results['feature_importance_plot'] = plot_path
        
        # Salvar resultados
        results_path = os.path.join(self.results_dir, f"failure_predictor_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        joblib.dump(optimization_results, results_path)
        
        logger.info(f"Otimização do preditor de falhas concluída. Melhores parâmetros: {best_params}")
        
        return optimization_results
    
    def evaluate_all_models(self, data=None, machine_type=None):
        """
        Avalia todos os modelos
        
        Args:
            data: DataFrame com os dados (opcional, gera dados se None)
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com métricas de avaliação para todos os modelos
        """
        logger.info("Iniciando avaliação de todos os modelos")
        
        # Gerar dados se não fornecidos
        if data is None:
            data = self.generate_evaluation_data()
        
        # Avaliar cada modelo
        anomaly_metrics = self.evaluate_anomaly_detector(data, machine_type)
        failure_metrics = self.evaluate_failure_predictor(data, machine_type)
        optimizer_metrics = self.evaluate_performance_optimizer(data, machine_type)
        recommender_metrics = self.evaluate_maintenance_recommender(data, machine_type)
        
        # Combinar métricas
        all_metrics = {
            'anomaly_detector': anomaly_metrics,
            'failure_predictor': failure_metrics,
            'performance_optimizer': optimizer_metrics,
            'maintenance_recommender': recommender_metrics,
            'evaluation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Salvar métricas combinadas
        metrics_path = os.path.join(self.results_dir, f"all_models_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        joblib.dump(all_metrics, metrics_path)
        
        logger.info(f"Avaliação de todos os modelos concluída e salva em: {metrics_path}")
        
        return all_metrics
    
    def optimize_all_models(self, data=None, machine_type=None):
        """
        Otimiza todos os modelos
        
        Args:
            data: DataFrame com os dados (opcional, gera dados se None)
            machine_type: Tipo de máquina (opcional)
            
        Returns:
            Dicionário com parâmetros otimizados para todos os modelos
        """
        logger.info("Iniciando otimização de todos os modelos")
        
        # Gerar dados se não fornecidos
        if data is None:
            data = self.generate_evaluation_data()
        
        # Otimizar cada modelo
        anomaly_optimization = self.optimize_anomaly_detector(data, machine_type)
        failure_optimization = self.optimize_failure_predictor(data, machine_type)
        
        # Combinar resultados
        all_optimizations = {
            'anomaly_detector': anomaly_optimization,
            'failure_predictor': failure_optimization,
            'optimization_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Salvar resultados combinados
        results_path = os.path.join(self.results_dir, f"all_models_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        joblib.dump(all_optimizations, results_path)
        
        logger.info(f"Otimização de todos os modelos concluída e salva em: {results_path}")
        
        return all_optimizations

# Exemplo de uso
if __name__ == "__main__":
    # Criar avaliador de modelos
    evaluator = ModelEvaluator()
    
    # Gerar dados para avaliação
    evaluation_data = evaluator.generate_evaluation_data(num_samples=2000)
    
    # Avaliar todos os modelos
    all_metrics = evaluator.evaluate_all_models(evaluation_data)
    
    # Otimizar todos os modelos
    all_optimizations = evaluator.optimize_all_models(evaluation_data)
    
    print("Avaliação e otimização de modelos concluídas com sucesso!")
