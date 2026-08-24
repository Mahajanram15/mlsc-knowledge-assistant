from typing import List, Tuple
from langchain_core.documents import Document

def retrieve_context(query: str, vector_store, top_k: int = 5, confidence_threshold: float = 0.5) -> Tuple[List[Document], bool]:
    if not vector_store:
        return [], False

    # Get results with relevance scores (FAISS returns L2 distance, lower is better)
    # Using similarity_search_with_score returns (doc, l2_dist)
    # Alternatively, similarity_search_with_relevance_scores returns scores between 0 and 1
    results = vector_store.similarity_search_with_relevance_scores(query, k=top_k)
    
    selected_docs = []
    has_confident_results = False
    
    for doc, score in results:
        selected_docs.append(doc)
        if score >= confidence_threshold:
            has_confident_results = True
            
    # If using similarity_search_with_relevance_scores is not properly normalized by default in faiss,
    # we might need to adjust the threshold. But we'll rely on it returning normalized scores if configured,
    # or just use standard similarity search and basic heuristics if not.
    # For now, let's assume relevance_scores returns standard 0-1 scores.
    
    return selected_docs, has_confident_results
