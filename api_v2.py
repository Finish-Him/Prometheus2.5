"""
API para o Oráculo 4.0 com suporte a processamento de texto, imagens e histórico
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Importar módulo de processamento de dados
import process_data

# Configuração do aplicativo FastAPI
app = FastAPI(
    title="Oráculo 4.0 API",
    description="API para processamento de dados e previsões para apostas em Dota 2",
    version="2.0.0"
)

# Configurar CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Classes para requisições e respostas
class TextRequest(BaseModel):
    text: str

class ImageRequest(BaseModel):
    image_base64: str

class FormDataRequest(BaseModel):
    timeRadiant: str
    timeDire: str
    torneio: Optional[str] = None
    oddsRadiant: float
    oddsDire: float
    handicapKills: Optional[float] = None
    oddsOverKills: Optional[float] = None
    oddsUnderKills: Optional[float] = None
    handicapDuration: Optional[float] = None
    oddsOverDuration: Optional[float] = None
    oddsUnderDuration: Optional[float] = None
    totalKills: Optional[float] = None
    oddsOverTotal: Optional[float] = None
    oddsUnderTotal: Optional[float] = None

class SaveRequest(BaseModel):
    match_data: Dict[str, Any]
    predictions: Dict[str, Any]

class HistoryResponse(BaseModel):
    records: List[Dict[str, Any]]

# Endpoints
@app.get("/")
async def root():
    return {"message": "Bem-vindo à API do Oráculo 4.0"}

@app.post("/process/text")
async def process_text_data(request: TextRequest):
    """
    Processa dados de texto para extrair informações da partida e gerar previsões
    """
    try:
        result = process_data.process_text(request.text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar texto: {str(e)}")

@app.post("/process/image")
async def process_image_data(request: ImageRequest):
    """
    Processa dados de imagem para extrair informações da partida e gerar previsões
    """
    try:
        # Remover prefixo de data URL se presente
        image_base64 = request.image_base64
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]
            
        result = process_data.process_image(image_base64)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@app.post("/process/form")
async def process_form_data(request: FormDataRequest):
    """
    Processa dados de formulário para gerar previsões
    """
    try:
        form_data = request.dict()
        result = process_data.process_form(form_data)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar formulário: {str(e)}")

@app.post("/history/save")
async def save_to_history(request: SaveRequest):
    """
    Salva dados da partida e previsões no histórico
    """
    try:
        record_id = process_data.save_prediction(request.match_data, request.predictions)
        return {"record_id": record_id, "message": "Registro salvo com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no histórico: {str(e)}")

@app.get("/history/list", response_model=HistoryResponse)
async def get_history_list(limit: int = Query(20, ge=1, le=100)):
    """
    Obtém lista de registros do histórico
    """
    try:
        records = process_data.get_history_list(limit)
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico: {str(e)}")

@app.get("/history/{record_id}")
async def get_history_item(record_id: str):
    """
    Obtém um registro específico do histórico
    """
    try:
        record = process_data.get_history_item(record_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Registro {record_id} não encontrado")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter registro: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# Iniciar o servidor se executado diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
