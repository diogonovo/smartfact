from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import random
import time
from datetime import datetime, timedelta

# Criar um router para as rotas de máquinas
router = APIRouter(
    prefix="/machines",
    tags=["machines"],
    responses={404: {"description": "Máquina não encontrada"}},
)

# Dados simulados de máquinas
MACHINE_TYPES = ["Torno CNC", "Fresadora", "Injetora de Plástico", "Robô Industrial", "Compressor"]
LOCATIONS = ["Setor A", "Setor B", "Setor C", "Setor D"]
STATUS = ["Operacional", "Em Manutenção", "Desligada", "Alerta"]

# Lista simulada de máquinas
machines = [
    {
        "id": i,
        "name": f"{MACHINE_TYPES[i % len(MACHINE_TYPES)]} #{i+1}",
        "type": MACHINE_TYPES[i % len(MACHINE_TYPES)],
        "location": LOCATIONS[i % len(LOCATIONS)],
        "installation_date": (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d"),
        "status": STATUS[i % len(STATUS)]
    }
    for i in range(10)
]

@router.get("/")
async def get_machines():
    """
    Retorna a lista de todas as máquinas
    """
    return machines

@router.get("/{machine_id}")
async def get_machine(machine_id: int):
    """
    Retorna informações detalhadas de uma máquina específica
    """
    if machine_id < 0 or machine_id >= len(machines):
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    return machines[machine_id]

@router.get("/{machine_id}/metrics")
async def get_machine_metrics(machine_id: int):
    """
    Retorna métricas simuladas para uma máquina específica
    """
    if machine_id < 0 or machine_id >= len(machines):
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    
    # Gerar dados simulados de métricas
    current_time = time.time()
    time_points = [current_time - i * 3600 for i in range(24)]  # Últimas 24 horas
    
    metrics = {
        "temperature": [round(random.uniform(50, 80), 2) for _ in time_points],
        "vibration": [round(random.uniform(0.1, 2.5), 2) for _ in time_points],
        "pressure": [round(random.uniform(80, 120), 2) for _ in time_points],
        "energy_consumption": [round(random.uniform(10, 50), 2) for _ in time_points],
        "production_rate": [round(random.uniform(80, 100), 2) for _ in time_points],
        "timestamps": [datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S") for t in time_points]
    }
    
    return metrics

@router.get("/{machine_id}/anomalies")
async def get_machine_anomalies(machine_id: int):
    """
    Retorna anomalias detectadas para uma máquina específica
    """
    if machine_id < 0 or machine_id >= len(machines):
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    
    # Gerar dados simulados de anomalias
    anomaly_count = random.randint(0, 5)
    current_time = time.time()
    
    anomalies = [
        {
            "id": i,
            "timestamp": datetime.fromtimestamp(current_time - random.randint(0, 86400)).strftime("%Y-%m-%d %H:%M:%S"),
            "metric": random.choice(["temperature", "vibration", "pressure"]),
            "value": round(random.uniform(0, 100), 2),
            "severity": random.choice(["Low", "Medium", "High"]),
            "description": f"Anomalia detectada em {random.choice(['temperatura', 'vibração', 'pressão'])}"
        }
        for i in range(anomaly_count)
    ]
    
    return anomalies

@router.get("/{machine_id}/predictions")
async def get_machine_predictions(machine_id: int):
    """
    Retorna previsões para uma máquina específica
    """
    if machine_id < 0 or machine_id >= len(machines):
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    
    # Gerar dados simulados de previsões
    current_time = time.time()
    future_points = [current_time + i * 3600 for i in range(1, 25)]  # Próximas 24 horas
    
    predictions = {
        "failure_probability": round(random.uniform(0, 1), 2),
        "estimated_remaining_life": random.randint(100, 5000),
        "maintenance_recommendation": random.choice([
            "Manutenção recomendada em 7 dias",
            "Operação normal, verificar em 30 dias",
            "Atenção: componente X apresenta sinais de desgaste"
        ]),
        "predicted_metrics": {
            "temperature": [round(random.uniform(50, 80), 2) for _ in future_points],
            "vibration": [round(random.uniform(0.1, 2.5), 2) for _ in future_points],
            "timestamps": [datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S") for t in future_points]
        }
    }
    
    return predictions
