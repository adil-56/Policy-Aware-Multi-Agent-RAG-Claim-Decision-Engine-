from backend.models.state import CaseState, EvidenceSet
from backend.retrieval.hybrid import HybridRetriever
import logging

logger = logging.getLogger(__name__)

class PolicyEvidenceAgent:
    """
    Retrieves necessary policy evidence for a given claim.
    """
    def __init__(self, retriever: HybridRetriever, llm=None):
        self.retriever = retriever
        self.llm = llm

    def gather_evidence(self, state: CaseState) -> EvidenceSet:
        logger.info(f"Gathering evidence for case {state.case_id}")
        
        diagnosis = state.claim_data.get("diagnosis", "")
        procedure = state.claim_data.get("procedure", "")
        
        # Craft targeted queries based on claim data
        queries = [
            f"Waiting period for {diagnosis}",
            f"Exclusion for {diagnosis} or {procedure}",
            "Hospital definition requirements",
            "Room rent and ICU limits"
        ]
        
        all_evidence = []
        for q in queries:
            try:
                items = self.retriever.retrieve(query=q, top_k=3)
                all_evidence.extend(items)
            except Exception as e:
                logger.warning(f"Retrieval failed for query '{q}': {e}")
            
        # Deduplicate evidence based on chunk_id
        seen = set()
        unique_evidence = []
        for e in all_evidence:
            if e.citation.chunk_id not in seen:
                seen.add(e.citation.chunk_id)
                unique_evidence.append(e)
                
        # In a real system, we'd classify the chunks into definitions, coverage_clauses, etc.
        # Here we just dump them into definitions for downstream evaluators to parse.
        return EvidenceSet(
            definitions=unique_evidence,
            coverage_clauses=[],
            exclusions=[],
            limits=[]
        )
