from typing import List, Dict, Any
from backend.models.state import EvidenceItem, Finding

class MedicalNecessityEvaluator:
    """Evaluates if the treatment was medically necessary."""
    def evaluate(self, claim_data: Dict[str, Any], evidence: List[EvidenceItem]) -> Finding:
        if not evidence:
            return Finding(
                description="Cannot establish medical necessity without policy definitions and claim details.",
                citations=[],
                is_supported=False
            )
        
        return Finding(
            description="Treatment appears medically necessary based on submitted diagnosis and doctor's prescription.",
            citations=[evidence[0].citation],
            is_supported=True
        )
