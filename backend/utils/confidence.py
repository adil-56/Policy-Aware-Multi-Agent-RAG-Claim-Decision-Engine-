from typing import List
from backend.models.state import Finding

def compute_confidence(
    findings: List[Finding], 
    missing_docs: List[str], 
    avg_relevance: float
) -> float:
    """
    Deterministic confidence scoring based on the architecture constraints.
    Formula:
    confidence = 0.35 retrieval_quality + 0.25 citation_coverage + 0.25 evidence_agreement + 0.15 completeness
    """
    # 1. Retrieval Quality (0.35)
    # Assumes relevance_score from reranker is roughly 0.0 to 1.0 (or normalized)
    retrieval_quality = min(max(avg_relevance, 0.0), 1.0) * 0.35
    
    # 2. Citation Coverage (0.25)
    # Percentage of findings that have a valid citation attached
    total_findings = len(findings)
    if total_findings == 0:
        citation_coverage = 0.0
    else:
        cited_findings = sum(1 for f in findings if len(f.citations) > 0)
        citation_coverage = (cited_findings / total_findings) * 0.25
        
    # 3. Evidence Agreement (0.25)
    # In a full system, we test if findings explicitly contradict each other.
    # Here we base it on whether findings are marked as strictly supported.
    if total_findings == 0:
        evidence_agreement = 0.0
    else:
        supported_findings = sum(1 for f in findings if f.is_supported)
        evidence_agreement = (supported_findings / total_findings) * 0.25
        
    # 4. Completeness (0.15)
    # Penalty for explicitly missing initial claim documents
    completeness = 0.15 if len(missing_docs) == 0 else max(0.15 - (len(missing_docs) * 0.05), 0.0)
    
    total_confidence = retrieval_quality + citation_coverage + evidence_agreement + completeness
    return round(min(total_confidence, 1.0), 3)
