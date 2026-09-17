def calculate_recall_at_k(retrieved_chunks, relevant_chunks, k=5):
    """
    Calculates Recall@K: the proportion of relevant chunks that appear in the top K retrieved chunks.
    """
    top_k = retrieved_chunks[:k]
    if not relevant_chunks:
        return 1.0
    
    hits = sum(1 for rc in relevant_chunks if any(rc in tc for tc in top_k))
    return hits / len(relevant_chunks)
