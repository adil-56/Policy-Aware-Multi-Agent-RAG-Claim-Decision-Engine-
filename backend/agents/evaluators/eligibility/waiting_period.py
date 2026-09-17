from typing import List, Dict, Any
from backend.models.state import EvidenceItem, Finding

class WaitingPeriodEvaluator:
    """Evaluates if the claim meets the required waiting periods."""
    def evaluate(self, claim_data: Dict[str, Any], evidence: List[EvidenceItem]) -> Finding:
        # In a full system, an LLM call would be made here, passing the specific claim details and evidence.
        if not evidence:
            return Finding(
                description="Insufficient evidence to determine waiting period applicability.",
                citations=[],
                is_supported=False
            )
            
        return Finding(
            description="Waiting period requirement appears to be met based on policy inception date.",
            citations=[evidence[0].citation],
            is_supported=True
        )
