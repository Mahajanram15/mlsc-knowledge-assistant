import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document

def load_and_chunk_documents(knowledge_base_path: str) -> List[Document]:
    documents = []
    
    if not os.path.exists(knowledge_base_path):
        print(f"Warning: Knowledge base path {knowledge_base_path} does not exist.")
        return documents

    # Get all .txt files
    txt_files = glob.glob(os.path.join(knowledge_base_path, "*.txt"))
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        loader = TextLoader(file_path, encoding='utf-8')
        try:
            docs = loader.load()
            for doc in docs:
                # Add metadata
                doc.metadata["document"] = filename
                doc.metadata["source"] = filename
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Assign chunk_id
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{chunk.metadata['document']}_chunk_{i}"
        
    return chunks
