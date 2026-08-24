import os
from typing import Dict, Any
from app.rag.embeddings import load_vector_store, create_and_save_vector_store
from app.rag.ingestion import load_and_chunk_documents
from app.rag.retriever import retrieve_context
from app.rag.generator import generate_answer
from app.config import settings
from app.models.schema import ChatResponse, Source, RetrievalInfo

# Global vector store instance
VECTOR_STORE = None

def initialize_pipeline(force_reindex: bool = False):
    global VECTOR_STORE
    
    if force_reindex or not os.path.exists(os.path.join(settings.VECTOR_STORE_PATH, "index.faiss")):
        print("Building vector store...")
        chunks = load_and_chunk_documents(settings.KNOWLEDGE_BASE_PATH)
        VECTOR_STORE = create_and_save_vector_store(chunks, settings.VECTOR_STORE_PATH)
    else:
        print("Loading existing vector store...")
        VECTOR_STORE = load_vector_store(settings.VECTOR_STORE_PATH)
        
    return VECTOR_STORE is not None

def process_query(query: str, top_k: int = 5) -> ChatResponse:
    global VECTOR_STORE
    if VECTOR_STORE is None:
        initialized = initialize_pipeline()
        if not initialized:
            return ChatResponse(
                answer="Error: Vector store is not initialized and could not be built.",
                sources=[],
                grounded=False,
                retrieval=RetrievalInfo(chunks=[])
            )
            
    # 1. Retrieval
    docs, has_confident_results = retrieve_context(
        query=query, 
        vector_store=VECTOR_STORE, 
        top_k=top_k, 
        confidence_threshold=settings.CONFIDENCE_THRESHOLD
    )
    
    # Format retrieved chunks for the response
    retrieved_chunks = []
    for doc in docs:
        retrieved_chunks.append(
            Source(
                document=doc.metadata.get("document", "Unknown"),
                chunk_id=doc.metadata.get("chunk_id", "Unknown"),
                content=doc.page_content
            )
        )
        
    # 2. Generation
    generated = generate_answer(query, docs, has_confident_results)
    
    # 3. Format output
    # The generation step returns sources that were actually used
    used_sources = []
    for src in generated.get("sources", []):
        used_sources.append(
            Source(
                document=src.get("document", "Unknown"),
                chunk_id=src.get("chunk_id", "Unknown")
            )
        )
        
    return ChatResponse(
        answer=generated.get("answer", "Error generating answer."),
        sources=used_sources,
        grounded=generated.get("grounded", False),
        retrieval=RetrievalInfo(chunks=retrieved_chunks)
    )
