from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar utilitários de dados
from utils.data_collector import DataCollector
from utils.data_processor import DataProcessor
from utils.data_storage import DataStorage

# Criar um router para as rotas de dados
router = APIRouter(
    prefix="/data",
    tags=["data"],
    responses={404: {"description": "Dados não encontrados"}},
)

# Instanciar classes de dados
data_collector = DataCollector()
data_processor = DataProcessor()
data_storage = DataStorage()

@router.get("/collect")
async def collect_data(num_machines: int = Query(5, description="Número de máquinas para coletar dados")):
    """
    Coleta dados simulados de máquinas industriais
    """
    try:
        # Coletar dados
        df = data_collector.collect_data_once(num_machines=num_machines)
        
        # Processar dados
        processed_df = data_processor.process_data(df)
        
        # Armazenar dados
        stored_count = data_storage.store_dataframe(processed_df)
        
        return {
            "status": "success",
            "message": f"Dados coletados com sucesso para {num_machines} máquinas",
            "records_collected": len(df),
            "records_stored": stored_count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao coletar dados: {str(e)}")

@router.get("/readings")
async def get_readings(
    machine_id: Optional[int] = Query(None, description="ID da máquina"),
    parameter: Optional[str] = Query(None, description="Nome do parâmetro"),
    start_time: Optional[str] = Query(None, description="Timestamp inicial (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="Timestamp final (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(100, description="Limite de registros a retornar")
):
    """
    Obtém leituras de dados das máquinas
    """
    try:
        # Consultar leituras no banco de dados
        readings = data_storage.query_readings(
            machine_id=machine_id,
            parameter_name=parameter,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        if readings.empty:
            return {
                "status": "success",
                "message": "Nenhum dado encontrado para os critérios especificados",
                "data": []
            }
        
        # Converter DataFrame para lista de dicionários
        readings_list = readings.to_dict(orient='records')
        
        return {
            "status": "success",
            "message": f"Encontrados {len(readings)} registros",
            "count": len(readings),
            "data": readings_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter leituras: {str(e)}")

@router.get("/anomalies")
async def get_anomalies(
    machine_id: Optional[int] = Query(None, description="ID da máquina"),
    parameter: Optional[str] = Query(None, description="Nome do parâmetro"),
    start_time: Optional[str] = Query(None, description="Timestamp inicial (YYYY-MM-DD HH:MM:SS)"),
    end_time: Optional[str] = Query(None, description="Timestamp final (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(100, description="Limite de registros a retornar")
):
    """
    Obtém anomalias detectadas nas máquinas
    """
    try:
        # Consultar anomalias no banco de dados
        anomalies = data_storage.query_anomalies(
            machine_id=machine_id,
            parameter_name=parameter,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        if anomalies.empty:
            return {
                "status": "success",
                "message": "Nenhuma anomalia encontrada para os critérios especificados",
                "data": []
            }
        
        # Converter DataFrame para lista de dicionários
        anomalies_list = anomalies.to_dict(orient='records')
        
        return {
            "status": "success",
            "message": f"Encontradas {len(anomalies)} anomalias",
            "count": len(anomalies),
            "data": anomalies_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter anomalias: {str(e)}")

@router.get("/machines")
async def get_machines():
    """
    Obtém lista de máquinas e suas estatísticas
    """
    try:
        # Obter estatísticas das máquinas
        machines = data_storage.get_machine_stats()
        
        if machines.empty:
            return {
                "status": "success",
                "message": "Nenhuma máquina encontrada",
                "data": []
            }
        
        # Converter DataFrame para lista de dicionários
        machines_list = machines.to_dict(orient='records')
        
        return {
            "status": "success",
            "message": f"Encontradas {len(machines)} máquinas",
            "count": len(machines),
            "data": machines_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter máquinas: {str(e)}")

@router.get("/simulate")
async def simulate_data_collection(
    duration: int = Query(30, description="Duração da simulação em segundos"),
    num_machines: int = Query(5, description="Número de máquinas para simular"),
    interval: int = Query(5, description="Intervalo de coleta em segundos")
):
    """
    Simula coleta de dados em tempo real
    """
    try:
        # Iniciar processador de dados
        processor = DataProcessor()
        
        # Simular processamento em tempo real
        stats = processor.simulate_realtime_processing(
            duration=duration,
            num_machines=num_machines,
            collection_interval=interval
        )
        
        return {
            "status": "success",
            "message": f"Simulação concluída com sucesso",
            "duration": duration,
            "num_machines": num_machines,
            "interval": interval,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao simular coleta de dados: {str(e)}")

@router.get("/current-state")
async def get_current_state():
    """
    Obtém o estado atual de todas as máquinas
    """
    try:
        # Obter estado atual
        current_state = data_collector.get_current_state()
        
        return {
            "status": "success",
            "message": f"Estado atual obtido com sucesso",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": current_state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estado atual: {str(e)}")
