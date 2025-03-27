from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Adicionar o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar routers
from api.machines import router as machines_router
from api.analytics import router as analytics_router

# Inicializar a aplicação FastAPI
app = FastAPI(
    title="API de Análise de Máquinas Industriais",
    description="API para coleta, processamento e análise de dados de máquinas industriais com Indústria 4.0",
    version="0.1.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens exatas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(machines_router)
app.include_router(analytics_router)

# Rota raiz
@app.get("/")
async def root():
    return {"message": "API de Análise de Máquinas Industriais com Indústria 4.0"}

# Iniciar o servidor se executado diretamente
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
