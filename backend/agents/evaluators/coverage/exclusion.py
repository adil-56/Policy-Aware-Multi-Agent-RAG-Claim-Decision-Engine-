from typing import List, Dict, Any
from backend.models.state import EvidenceItem, Finding

class ExclusionEvaluator:
    """Evaluates if the claim triggers any specific policy exclusions."""
    def evaluate(self, claim_data: Dict[str, Any], evidence: List[EvidenceItem]) -> Finding:
        if not evidence:
            return Finding(
                description="Unable to verify policy exclusions without sufficient evidence.",
                citations=[],
                is_supported=False
            )
            
        diagnosis = claim_data.get("diagnosis", "").lower()
        if "cosmetic" in diagnosis or "experimental" in diagnosis:
            return Finding(
                description=f"Treatment '{diagnosis}' is specifically excluded under standard policy terms.",
                citations=[evidence[0].citation],
                is_supported=True
            )
            
        return Finding(
            description="No specific policy exclusions apply to this diagnosis/procedure.",
            citations=[evidence[0].citation],
            is_supported=True
        )
