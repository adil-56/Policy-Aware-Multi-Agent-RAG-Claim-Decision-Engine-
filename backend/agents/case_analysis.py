from typing import Dict, Any, List
from backend.models.state import CaseState
import logging

logger = logging.getLogger(__name__)

class CaseAnalysisAgent:
    """
    Initial entry point for the Multi-Agent workflow.
    Parses claim JSON, flags missing essential documents, and creates the CaseState.
    """
    def __init__(self, llm=None):
        self.llm = llm

    def analyze(self, case_id: str, claim_data: Dict[str, Any]) -> CaseState:
        logger.info(f"Analyzing case {case_id}")
        
        missing_docs = []
        provided_docs = claim_data.get("documents", [])
        if "discharge_summary" not in [d.lower() for d in provided_docs]:
            missing_docs.append("discharge_summary")
        if "itemized_bill" not in [d.lower() for d in provided_docs]:
            missing_docs.append("itemized_bill")
            
        # Determine decision dimensions (e.g. is this a day-care or hospitalization?)
        dimensions = ["eligibility", "coverage", "financial"]
        if claim_data.get("is_day_care", False):
            dimensions.append("day_care")
        
        # Build investigation plan
        plan = [
            "1. Verify waiting periods and policy inception date.",
            "2. Verify hospital registration and definition.",
            "3. Check for specific exclusions based on diagnosis.",
            "4. Apply sub-limits (room rent, etc.) if admissible."
        ]
        
        return CaseState(
            case_id=case_id,
            claim_data=claim_data,
            decision_dimensions=dimensions,
            missing_initial_evidence=missing_docs,
            investigation_plan=plan
        )
