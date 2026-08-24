# MLSC Knowledge Assistant

A RAG (Retrieval-Augmented Generation) based web application to answer questions about the MLSC (Microsoft Learn Student Ambassadors) community.

## Overview
This system uses a local FAISS vector store with HuggingFace embeddings to retrieve relevant chunks from a set of knowledge base text files, and then generates grounded answers using the Gemini Generative AI model.

## Folder Structure
- `backend/`: FastAPI application handling the RAG pipeline.
- `frontend/`: React + Vite application for the chat interface.
- `mlsc_knowledge_base/`: Text files acting as the single source of truth.

## Setup Instructions

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows)
4. `pip install -r requirements.txt`
5. Create a `.env` file (copy from `.env.example`) and add your `GOOGLE_API_KEY`.
6. Start server: `uvicorn app.main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

### Running Evaluation
Navigate to `backend/evaluation` and run:
`python run_evaluation.py`
This uses RAGAS metrics and manual checks to evaluate system performance.

## Important Technical Decisions
- **Embeddings:** `all-MiniLM-L6-v2` is used locally via `sentence-transformers` for fast, cost-free vectorization.
- **Vector Store:** FAISS is chosen for its simplicity and local performance.
- **LLM:** Google Gemini via `langchain-google-genai` is used for generation, explicitly prompted to answer ONLY from context.
- **Hallucination Prevention:** We filter chunks below a confidence threshold and provide an explicit fallback response in the LLM prompt.
