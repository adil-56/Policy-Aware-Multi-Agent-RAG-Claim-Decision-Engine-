from typing import List, Dict, Any
from backend.models.state import EvidenceItem, Finding

class HospitalDefinitionEvaluator:
    """Evaluates if the hospital meets the policy definition."""
    def evaluate(self, claim_data: Dict[str, Any], evidence: List[EvidenceItem]) -> Finding:
        hospital_info = claim_data.get("hospital", {})
        beds = hospital_info.get("beds", 0)
        
        if not evidence:
            return Finding(
                description="Cannot verify hospital definition without policy evidence.",
                citations=[],
                is_supported=False
            )
            
        if beds > 0 and beds < 10:
            return Finding(
                description=f"Hospital does not meet minimum bed requirements (has {beds} beds).",
                citations=[evidence[0].citation],
                is_supported=True
            )
            
        return Finding(
            description="Hospital meets standard policy definition requirements.",
            citations=[evidence[0].citation],
            is_supported=True
        )
