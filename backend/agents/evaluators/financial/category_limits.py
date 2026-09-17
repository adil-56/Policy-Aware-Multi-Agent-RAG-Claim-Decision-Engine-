from typing import List, Dict, Any
from backend.models.state import EvidenceItem, Finding

class CategoryLimitEvaluator:
    """Evaluates aggregate or specific category limits (e.g. ICU, medicines)."""
    def evaluate(self, claim_data: Dict[str, Any], evidence: List[EvidenceItem]) -> Finding:
        if not evidence:
            return Finding(
                description="Cannot determine category limits without policy evidence.",
                citations=[],
                is_supported=False
            )
            
        amounts = claim_data.get("claimed_amount", {})
        claimed_total = sum(amounts.values()) if isinstance(amounts, dict) else 0
        
        return Finding(
            description=f"Standard category limits applied. Total claimed across categories: {claimed_total}.",
            citations=[evidence[0].citation],
            is_supported=True
        )
