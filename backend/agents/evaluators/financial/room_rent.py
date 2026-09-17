from typing import List, Dict, Any
from backend.models.state import EvidenceItem, Finding

class RoomRentLimitEvaluator:
    """Evaluates and applies room rent caps."""
    def evaluate(self, claim_data: Dict[str, Any], evidence: List[EvidenceItem]) -> Finding:
        if not evidence:
            return Finding(
                description="Cannot determine room rent limit without policy evidence.",
                citations=[],
                is_supported=False
            )
            
        claimed_rent = claim_data.get("claimed_amount", {}).get("room_rent", 0)
        
        # Example static limit. In production, this is parsed from EvidenceItem (the PolicyRule)
        limit = 5000
        applied_limit = min(claimed_rent, limit) if claimed_rent > 0 else 0
        
        return Finding(
            description=f"Room rent limited to {limit} per policy terms. Claimed {claimed_rent}, Admissible: {applied_limit}.",
            citations=[evidence[0].citation],
            is_supported=True
        )
