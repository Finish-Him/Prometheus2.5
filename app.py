"""
Servidor para integração do Oráculo 4.0 com ChatGPT
"""

import os
import json
import base64
from typing import Dict, Any, List, Optional, Union
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import requests
import uvicorn

# Importar o módulo de integração existente
import sys
sys.path.append('/home/ubuntu/upload')
import chatgpt_integration

# Configuração da API
API_KEY = os.environ.get("ORACULO_API_KEY", "oraculo_v4_api_key_manus_integration_2025_04_24_8f7d3e1a9b2c5d6e")

# Criar aplicação FastAPI
app = FastAPI(
    title="Oráculo 4.0 API",
    description="API para processamento de dados e previsões para apostas em Dota 2",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para validação de dados
class ProcessTextRequest(BaseModel):
    text: str = Field(..., description="Texto contendo informações da partida")

class ProcessImageRequest(BaseModel):
    image_base64: str = Field(..., description="Imagem em base64")

class ProcessFormRequest(BaseModel):
    form_data: Dict[str, Any] = Field(..., description="Dados do formulário")

class SaveHistoryRequest(BaseModel):
    match_data: Dict[str, Any] = Field(..., description="Dados da partida")
    predictions: Dict[str, Any] = Field(..., description="Previsões geradas")

# Função para verificar autenticação
async def verify_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticação ausente ou inválido")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Token de autenticação inválido")
    
    return token

# Servir arquivos estáticos
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota para o logo
@app.get("/logo.png")
async def get_logo():
    # Criar um logo padrão se não existir
    if not os.path.exists("static/logo.png"):
        # Aqui você pode adicionar código para criar um logo padrão
        # Por enquanto, vamos apenas retornar um erro 404
        raise HTTPException(status_code=404, detail="Logo não encontrado")
    
    return FileResponse("static/logo.png")

# Rota para os termos
@app.get("/termos")
async def get_termos():
    return {"message": "Termos de uso do Oráculo 4.0"}

# Rota para o arquivo OpenAPI
@app.get("/openapi.yaml")
async def get_openapi_yaml():
    return FileResponse("/home/ubuntu/projeto_integracao_manus/openapi.yaml")

# Rota para o arquivo ai-plugin.json
@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    return FileResponse("/home/ubuntu/projeto_integracao_manus/.well-known/ai-plugin.json")

# Rotas da API
@app.post("/process/text", response_model=Dict[str, Any])
async def process_text(request: ProcessTextRequest, token: str = Depends(verify_token)):
    try:
        result = chatgpt_integration.process_text(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar texto: {str(e)}")

@app.post("/process/image", response_model=Dict[str, Any])
async def process_image(request: ProcessImageRequest, token: str = Depends(verify_token)):
    try:
        # Salvar a imagem temporariamente
        image_data = base64.b64decode(request.image_base64)
        temp_image_path = "temp_image.jpg"
        with open(temp_image_path, "wb") as f:
            f.write(image_data)
        
        # Processar a imagem
        result = chatgpt_integration.process_image(temp_image_path)
        
        # Remover o arquivo temporário
        os.remove(temp_image_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@app.post("/process/form", response_model=Dict[str, Any])
async def process_form(request: ProcessFormRequest, token: str = Depends(verify_token)):
    try:
        result = chatgpt_integration.process_form(request.form_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar formulário: {str(e)}")

@app.get("/history/list", response_model=Dict[str, List[Dict[str, Any]]])
async def get_history_list(limit: int = 20, token: str = Depends(verify_token)):
    try:
        records = chatgpt_integration.get_history_list(limit)
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico: {str(e)}")

@app.get("/history/{record_id}", response_model=Dict[str, Any])
async def get_history_item(record_id: str, token: str = Depends(verify_token)):
    try:
        record = chatgpt_integration.get_history_item(record_id)
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter registro: {str(e)}")

@app.post("/history/save", response_model=Dict[str, str])
async def save_to_history(request: SaveHistoryRequest, token: str = Depends(verify_token)):
    try:
        record_id = chatgpt_integration.save_to_history(request.match_data, request.predictions)
        return {"record_id": record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no histórico: {str(e)}")

# Rota para verificar se o servidor está funcionando
@app.get("/")
async def root():
    return {"message": "API do Oráculo 4.0 está funcionando"}

if __name__ == "__main__":
    # Criar diretório para arquivos estáticos
    os.makedirs("static", exist_ok=True)
    
    # Iniciar o servidor
    uvicorn.run(app, host="0.0.0.0", port=8000)
