def calculate_precision_at_k(retrieved_chunks, relevant_chunks, k=5):
    """
    Calculates Precision@K: the proportion of top K retrieved chunks that are relevant.
    """
    top_k = retrieved_chunks[:k]
    if not top_k:
        return 0.0
        
    hits = sum(1 for tc in top_k if any(tc in rc for rc in relevant_chunks))
    return hits / k
