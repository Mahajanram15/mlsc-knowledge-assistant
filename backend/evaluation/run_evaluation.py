import os
import json
import time
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    answer_relevancy,
    faithfulness,
)
import sys

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.pipeline import process_query, initialize_pipeline

def run_evaluation(dataset_path: str = "dataset.json"):
    print("Initializing pipeline for evaluation...")
    success = initialize_pipeline()
    if not success:
        print("Failed to initialize pipeline.")
        return

    with open(dataset_path, "r") as f:
        eval_data = json.load(f)

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    results = []

    print(f"Running queries for {len(eval_data)} test cases...")
    for idx, item in enumerate(eval_data):
        q = item["question"]
        print(f"[{idx+1}/{len(eval_data)}] Testing: {q}")
        
        # Add slight delay to avoid rate limits
        time.sleep(1)
        
        res = process_query(q)
        
        # Prepare for Ragas
        questions.append(q)
        answers.append(res.answer)
        
        # Extract contexts
        ctx_list = [chunk.content for chunk in res.retrieval.chunks if chunk.content]
        contexts.append(ctx_list)
        
        # Ragas expects a list of ground truths for each question
        ground_truths.append([item["reference_answer"]])
        
        results.append({
            "question": q,
            "generated_answer": res.answer,
            "reference_answer": item["reference_answer"],
            "expected_sources": item["expected_sources"],
            "retrieved_sources": [s.document for s in res.sources],
            "grounded": res.grounded
        })

    print("Building HuggingFace Dataset for Ragas...")
    
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }

    dataset = Dataset.from_dict(data)

    print("Running RAGAS evaluation (this requires OpenAI/Google API key configured for Ragas)...")
    # Ragas by default uses OpenAI. Since we only have Gemini, we might need to configure Ragas to use Gemini.
    # We will try to use the default or just skip the exact metric computation if it fails due to missing OpenAI key,
    # and instead print manual retrieval stats.
    
    metrics_result = None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        # Override ragas llm/embeddings if possible
        gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # For simplicity, we just run evaluate and catch errors if they happen.
        # If it fails, we will calculate standard retrieval metrics manually.
        metrics_result = evaluate(
            dataset,
            metrics=[context_precision, context_recall, answer_relevancy, faithfulness],
            llm=gemini_llm,
            embeddings=gemini_embeddings
        )
        print("Ragas evaluation successful.")
        print(metrics_result)
    except Exception as e:
        print(f"Could not complete RAGAS evaluation automatically (possibly due to API or model constraints): {e}")
        print("Proceeding with manual retrieval metrics...")
        
    # Manual Retrieval Stats
    total_q = len(eval_data)
    unsupported_q = sum(1 for item in eval_data if len(item["expected_sources"]) == 0)
    supported_q = total_q - unsupported_q
    
    retrieval_successes = 0
    unsupported_successes = 0
    
    for r in results:
        expected = set(r["expected_sources"])
        actual = set(r["retrieved_sources"])
        
        if len(expected) == 0:
            if not r["grounded"]:
                unsupported_successes += 1
        else:
            # Check if all expected sources were retrieved
            if expected.issubset(actual):
                retrieval_successes += 1
                
    retrieval_success_rate = retrieval_successes / supported_q if supported_q > 0 else 0
    unsupported_detection_rate = unsupported_successes / unsupported_q if unsupported_q > 0 else 0
    
    print("\n--- Manual Evaluation Stats ---")
    print(f"Total Questions: {total_q}")
    print(f"Retrieval Success Rate: {retrieval_success_rate*100:.2f}%")
    print(f"Unsupported Detection Rate: {unsupported_detection_rate*100:.2f}%")
    
    # Save results
    with open("evaluation_results.json", "w") as f:
        json.dump({
            "manual_stats": {
                "total_questions": total_q,
                "retrieval_success_rate": retrieval_success_rate,
                "unsupported_detection_rate": unsupported_detection_rate
            },
            "ragas_metrics": metrics_result if metrics_result else None,
            "detailed_results": results
        }, f, indent=2)
        
    print("Evaluation results saved to evaluation_results.json")

if __name__ == "__main__":
    run_evaluation()
