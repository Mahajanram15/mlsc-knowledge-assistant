# Technical Decisions Document

This document outlines the core technical decisions made while building the MLSC Knowledge Assistant RAG system.

### Why this embedding model?
**Model:** `sentence-transformers/all-MiniLM-L6-v2`
**Reason:** It is lightweight, fast, and extremely cost-effective as it runs locally without calling external APIs. For a scoped knowledge base like the MLSC documents, MiniLM provides excellent semantic representations without the latency and cost of OpenAI/Google embeddings.

### Why this vector store?
**Store:** FAISS (Facebook AI Similarity Search)
**Reason:** FAISS runs entirely in-memory/locally and requires zero setup overhead compared to dedicated vector databases like Pinecone or Weaviate. For a small set of 6 documents, FAISS is incredibly fast and perfectly suits the local execution environment.

### Why this chunk size?
**Chunk Size:** 500 characters with 50 character overlap.
**Reason:** The MLSC documents contain specific rules, domains, and responsibilities. A chunk size of 500 keeps the context tightly focused, preventing the retrieval of overly broad sections, while the 50 overlap ensures no context is lost at boundaries.

### Why this retrieval strategy?
**Strategy:** Top-K Semantic Search with Confidence Thresholding
**Reason:** We first retrieve the top K most semantically similar chunks. We then apply a confidence threshold on the similarity score. If the best match does not meet the threshold, the system flags the query as unsupported. This acts as our primary defense against hallucinations.

### Why this LLM?
**Model:** Google Gemini (`gemini-2.5-flash`) via `langchain-google-genai`
**Reason:** It is incredibly fast, offers a large context window, and strictly follows system prompts.

### How is hallucination controlled?
Hallucination is controlled at two levels:
1. **Retrieval Level:** The confidence threshold prevents irrelevant context from even reaching the LLM.
2. **Generation Level:** The LLM is given a strict system prompt forbidding the use of outside knowledge and instructing it to output a specific fallback string if the answer cannot be deduced from the provided context.

### How is unsupported information detected?
If the query falls below the vector similarity threshold, or if the LLM cannot find the answer in the context, it outputs the fallback string. The backend detects this and sets the `grounded` flag to `false`.

### How does multi-document retrieval work?
FAISS retrieves the top K chunks globally across all indexed documents. These chunks are appended together in the prompt with their source metadata. The LLM synthesizes the answer by reasoning across all provided chunks.

### How are sources attached to answers?
The generator function extracts the `document` and `chunk_id` metadata from the retrieved chunks. The LLM is forced to output a JSON object containing the `sources` array, ensuring only the chunks actually utilized are cited.

### How are evaluation metrics calculated?
An evaluation dataset (`dataset.json`) is processed through the pipeline. RAGAS (or manual heuristics) is used to calculate:
- **Context Precision/Recall:** Based on the expected vs retrieved chunks.
- **Answer Relevancy & Faithfulness:** Based on the generated answer vs ground truth.
A manual fallback calculates the Retrieval Success Rate and Unsupported Detection Rate.
