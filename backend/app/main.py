import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.config import settings
from app.rag.pipeline import initialize_pipeline

app = FastAPI(title="MLSC Knowledge Assistant API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173", "*"],  # * for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # Initialize the vector store if it doesn't exist
    print("Starting up MLSC Knowledge Assistant...")
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your-google-api-key-here":
        print("WARNING: GOOGLE_API_KEY is not set correctly. The assistant will fail to generate answers.")
        
    try:
        initialize_pipeline()
        print("RAG pipeline initialized.")
    except Exception as e:
        print(f"Failed to initialize RAG pipeline: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
