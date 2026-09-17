from backend.models.state import CaseState, EvidenceSet, CoverageFindings
from backend.agents.evaluators.coverage.medical_necessity import MedicalNecessityEvaluator
from backend.agents.evaluators.coverage.exclusion import ExclusionEvaluator
import logging

logger = logging.getLogger(__name__)

class CoverageExclusionAgent:
    """
    Orchestrates coverage evaluators to determine if the claim falls under valid coverage or hits an exclusion.
    """
    def __init__(self, llm=None):
        self.llm = llm
        self.necessity_eval = MedicalNecessityEvaluator()
        self.exclusion_eval = ExclusionEvaluator()

    def evaluate(self, state: CaseState, evidence: EvidenceSet) -> CoverageFindings:
        logger.info(f"Evaluating coverage for case {state.case_id}")
        
        nec_finding = self.necessity_eval.evaluate(state.claim_data, evidence.definitions)
        excl_finding = self.exclusion_eval.evaluate(state.claim_data, evidence.exclusions or evidence.definitions)
        
        all_findings = [nec_finding, excl_finding]
        missing = []
        
        for f in all_findings:
            if not f.is_supported:
                missing.append("Missing evidence for: " + f.description)
                
        is_necessary = "appears medically necessary" in nec_finding.description
        is_excluded = "specifically excluded" in excl_finding.description
        
        return CoverageFindings(
            findings=all_findings,
            covered_benefits=["in-patient hospitalization"] if is_necessary and not is_excluded else [],
            applied_exclusions=[state.claim_data.get("diagnosis", "Unknown")] if is_excluded else [],
            is_experimental="experimental" in state.claim_data.get("diagnosis", "").lower(),
            medical_necessity_established=is_necessary,
            missing_evidence=missing
        )
