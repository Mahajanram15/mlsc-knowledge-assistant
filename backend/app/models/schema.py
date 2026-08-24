from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str

class Source(BaseModel):
    document: str
    chunk_id: str
    content: Optional[str] = None

class RetrievalInfo(BaseModel):
    chunks: List[Source]

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    grounded: bool
    retrieval: RetrievalInfo

class EvaluateResponse(BaseModel):
    success: bool
    message: str
    metrics: Optional[dict] = None
