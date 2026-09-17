def calculate_citation_accuracy(findings):
    """
    Evaluates if every finding has at least one valid citation attached.
    Returns (valid_citations, total_citations, has_hallucination_flag)
    """
    total = len(findings)
    if total == 0:
        return 0, 0, False
        
    valid = sum(1 for f in findings if len(f.citations) > 0 and getattr(f, 'is_supported', True))
    has_hallucination = any(len(f.citations) == 0 for f in findings)
    
    return valid, total, has_hallucination
