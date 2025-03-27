from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import random
import time
from datetime import datetime, timedelta

# Criar um router para as rotas de análise
router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Dados não encontrados"}},
)

@router.get("/kpis")
async def get_kpis():
    """
    Retorna KPIs gerais do sistema
    """
    return {
        "oee": round(random.uniform(75, 95), 2),  # Overall Equipment Effectiveness
        "mtbf": round(random.uniform(100, 500), 2),  # Mean Time Between Failures
        "mttr": round(random.uniform(1, 24), 2),  # Mean Time To Repair
        "energy_efficiency": round(random.uniform(80, 98), 2),  # Eficiência energética
        "quality_rate": round(random.uniform(90, 99.9), 2),  # Taxa de qualidade
        "production_volume": random.randint(5000, 15000),  # Volume de produção
        "active_machines": random.randint(8, 10),  # Máquinas ativas
        "machines_in_maintenance": random.randint(0, 2),  # Máquinas em manutenção
        "anomalies_detected": random.randint(0, 10),  # Anomalias detectadas
    }

@router.get("/production-trends")
async def get_production_trends():
    """
    Retorna tendências de produção para análise
    """
    # Gerar dados simulados para os últimos 30 dias
    days = 30
    current_date = datetime.now()
    dates = [(current_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    dates.reverse()  # Ordenar cronologicamente
    
    # Gerar dados de produção com tendência crescente
    base_production = 1000
    production_data = []
    for i in range(days):
        # Adicionar tendência crescente com alguma variação aleatória
        daily_production = base_production + (i * 10) + random.randint(-50, 50)
        production_data.append(daily_production)
    
    # Gerar dados de eficiência com pequenas variações
    efficiency_data = [round(random.uniform(85, 95), 2) for _ in range(days)]
    
    # Gerar dados de qualidade com pequenas variações
    quality_data = [round(random.uniform(92, 99), 2) for _ in range(days)]
    
    return {
        "dates": dates,
        "production": production_data,
        "efficiency": efficiency_data,
        "quality": quality_data
    }

@router.get("/energy-consumption")
async def get_energy_consumption():
    """
    Retorna dados de consumo energético
    """
    # Gerar dados simulados para os últimos 30 dias
    days = 30
    current_date = datetime.now()
    dates = [(current_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
    dates.reverse()  # Ordenar cronologicamente
    
    # Gerar dados de consumo energético por setor
    sectors = ["Setor A", "Setor B", "Setor C", "Setor D"]
    consumption_by_sector = {}
    
    for sector in sectors:
        # Base de consumo diferente para cada setor
        base_consumption = random.randint(500, 1000)
        sector_data = []
        
        for i in range(days):
            # Adicionar padrão de consumo com variação aleatória
            daily_consumption = base_consumption + random.randint(-50, 50)
            # Adicionar padrão semanal (menos consumo nos fins de semana)
            day_of_week = (current_date - timedelta(days=i)).weekday()
            if day_of_week >= 5:  # Sábado e domingo
                daily_consumption *= 0.7
            
            sector_data.append(round(daily_consumption, 2))
        
        consumption_by_sector[sector] = sector_data
    
    return {
        "dates": dates,
        "consumption_by_sector": consumption_by_sector,
        "total_consumption": [sum(consumption_by_sector[sector][i] for sector in sectors) for i in range(days)]
    }

@router.get("/maintenance-analysis")
async def get_maintenance_analysis():
    """
    Retorna análise de manutenção
    """
    # Tipos de manutenção
    maintenance_types = ["Preventiva", "Corretiva", "Preditiva"]
    
    # Gerar dados simulados para os últimos 12 meses
    months = 12
    current_date = datetime.now()
    month_labels = []
    
    for i in range(months):
        month_date = current_date - timedelta(days=30*i)
        month_labels.append(month_date.strftime("%b/%Y"))
    
    month_labels.reverse()  # Ordenar cronologicamente
    
    # Gerar dados de manutenção por tipo
    maintenance_data = {}
    
    for mtype in maintenance_types:
        # Base de ocorrências diferente para cada tipo
        if mtype == "Preventiva":
            base_count = random.randint(8, 12)
        elif mtype == "Corretiva":
            base_count = random.randint(3, 7)
        else:  # Preditiva
            base_count = random.randint(5, 10)
        
        monthly_data = []
        
        for i in range(months):
            # Adicionar variação aleatória
            monthly_count = max(0, base_count + random.randint(-2, 2))
            monthly_data.append(monthly_count)
        
        maintenance_data[mtype] = monthly_data
    
    # Calcular custos de manutenção
    maintenance_costs = []
    for i in range(months):
        # Custo base mensal
        base_cost = 5000
        # Adicionar custo por tipo de manutenção
        preventive_cost = maintenance_data["Preventiva"][i] * 500
        corrective_cost = maintenance_data["Corretiva"][i] * 2000
        predictive_cost = maintenance_data["Preditiva"][i] * 300
        
        total_cost = base_cost + preventive_cost + corrective_cost + predictive_cost
        maintenance_costs.append(total_cost)
    
    return {
        "months": month_labels,
        "maintenance_by_type": maintenance_data,
        "maintenance_costs": maintenance_costs,
        "mtbf_trend": [round(random.uniform(100, 500), 2) for _ in range(months)],
        "mttr_trend": [round(random.uniform(1, 24), 2) for _ in range(months)]
    }

@router.get("/anomaly-distribution")
async def get_anomaly_distribution():
    """
    Retorna distribuição de anomalias por tipo e máquina
    """
    # Tipos de anomalias
    anomaly_types = ["Temperatura", "Vibração", "Pressão", "Ruído", "Consumo Energético"]
    
    # Gerar distribuição de anomalias por tipo
    anomalies_by_type = {}
    total_anomalies = random.randint(50, 100)
    
    remaining = total_anomalies
    for i, atype in enumerate(anomaly_types):
        if i == len(anomaly_types) - 1:
            anomalies_by_type[atype] = remaining
        else:
            count = random.randint(5, remaining - (len(anomaly_types) - i - 1) * 5)
            anomalies_by_type[atype] = count
            remaining -= count
    
    # Gerar distribuição de anomalias por máquina
    machine_types = ["Torno CNC", "Fresadora", "Injetora de Plástico", "Robô Industrial", "Compressor"]
    anomalies_by_machine = {}
    
    remaining = total_anomalies
    for i, mtype in enumerate(machine_types):
        if i == len(machine_types) - 1:
            anomalies_by_machine[mtype] = remaining
        else:
            count = random.randint(5, remaining - (len(machine_types) - i - 1) * 5)
            anomalies_by_machine[mtype] = count
            remaining -= count
    
    # Gerar distribuição de anomalias por severidade
    severity_levels = ["Baixa", "Média", "Alta", "Crítica"]
    anomalies_by_severity = {}
    
    remaining = total_anomalies
    for i, level in enumerate(severity_levels):
        if i == len(severity_levels) - 1:
            anomalies_by_severity[level] = remaining
        else:
            count = random.randint(5, remaining - (len(severity_levels) - i - 1) * 5)
            anomalies_by_severity[level] = count
            remaining -= count
    
    return {
        "total_anomalies": total_anomalies,
        "anomalies_by_type": anomalies_by_type,
        "anomalies_by_machine": anomalies_by_machine,
        "anomalies_by_severity": anomalies_by_severity
    }
