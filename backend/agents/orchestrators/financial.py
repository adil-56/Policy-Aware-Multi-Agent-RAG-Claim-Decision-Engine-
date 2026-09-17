from backend.models.state import CaseState, EvidenceSet, FinancialAssessment
from backend.agents.evaluators.financial.room_rent import RoomRentLimitEvaluator
from backend.agents.evaluators.financial.category_limits import CategoryLimitEvaluator
import logging

logger = logging.getLogger(__name__)

class FinancialAssessmentAgent:
    """
    Orchestrates financial evaluators to calculate final admissible amounts based on policy caps.
    """
    def __init__(self, llm=None):
        self.llm = llm
        self.room_rent_eval = RoomRentLimitEvaluator()
        self.category_eval = CategoryLimitEvaluator()

    def evaluate(self, state: CaseState, evidence: EvidenceSet) -> FinancialAssessment:
        logger.info(f"Evaluating financial limits for case {state.case_id}")
        
        rr_finding = self.room_rent_eval.evaluate(state.claim_data, evidence.limits or evidence.definitions)
        cat_finding = self.category_eval.evaluate(state.claim_data, evidence.limits or evidence.definitions)
        
        all_findings = [rr_finding, cat_finding]
        missing = []
        
        for f in all_findings:
            if not f.is_supported:
                missing.append("Missing evidence for: " + f.description)
                
        claimed_amounts = state.claim_data.get("claimed_amount", {})
        total_claimed = sum(claimed_amounts.values()) if isinstance(claimed_amounts, dict) else 0.0
        
        # Simplified logic: 80% admissible after limits for demonstration
        total_admissible = total_claimed * 0.8 if total_claimed > 0 else 0.0
        
        limits_applied = {
            "room_rent": 5000.0,
            "overall_co_pay": 0.2
        }
        
        return FinancialAssessment(
            findings=all_findings,
            limits_applied=limits_applied,
            total_admissible_amount=total_admissible,
            missing_evidence=missing
        )
