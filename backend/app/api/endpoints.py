from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import os
import glob
from app.models.schema import ChatRequest, ChatResponse, EvaluateResponse
from app.rag.pipeline import process_query, initialize_pipeline
from app.config import settings

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        response = process_query(request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex")
async def reindex():
    try:
        success = initialize_pipeline(force_reindex=True)
        if success:
            return {"status": "success", "message": "Knowledge base reindexed successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to reindex knowledge base.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def get_documents():
    if not os.path.exists(settings.KNOWLEDGE_BASE_PATH):
        return {"documents": []}
        
    txt_files = glob.glob(os.path.join(settings.KNOWLEDGE_BASE_PATH, "*.txt"))
    documents = [os.path.basename(f) for f in txt_files]
    return {"documents": documents}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
