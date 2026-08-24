import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List
from langchain_core.documents import Document

def get_embeddings_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def create_and_save_vector_store(chunks: List[Document], vector_store_path: str):
    embeddings = get_embeddings_model()
    if not chunks:
        print("No chunks provided to index.")
        return None
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(vector_store_path)
    return vector_store

def load_vector_store(vector_store_path: str):
    if not os.path.exists(os.path.join(vector_store_path, "index.faiss")):
        return None
    embeddings = get_embeddings_model()
    try:
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        return vector_store
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None
