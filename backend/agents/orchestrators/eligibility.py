from backend.models.state import CaseState, EvidenceSet, EligibilityFindings
from backend.agents.evaluators.eligibility.waiting_period import WaitingPeriodEvaluator
from backend.agents.evaluators.eligibility.hospital_definition import HospitalDefinitionEvaluator
import logging

logger = logging.getLogger(__name__)

class EligibilityAgent:
    """
    Orchestrates eligibility evaluators to determine if a claim is structurally eligible.
    """
    def __init__(self, llm=None):
        self.llm = llm
        self.wp_evaluator = WaitingPeriodEvaluator()
        self.hd_evaluator = HospitalDefinitionEvaluator()

    def evaluate(self, state: CaseState, evidence: EvidenceSet) -> EligibilityFindings:
        logger.info(f"Evaluating eligibility for case {state.case_id}")
        
        # Run evaluators
        wp_finding = self.wp_evaluator.evaluate(state.claim_data, evidence.definitions)
        hd_finding = self.hd_evaluator.evaluate(state.claim_data, evidence.definitions)
        
        all_findings = [wp_finding, hd_finding]
        missing = []
        
        # Check if evaluators failed due to missing evidence
        for f in all_findings:
            if not f.is_supported:
                missing.append("Missing evidence for: " + f.description)
                
        is_eligible = len(missing) == 0 and "does not meet" not in hd_finding.description
        
        return EligibilityFindings(
            findings=all_findings,
            hospitalization_eligible=is_eligible,
            waiting_period_met="met" in wp_finding.description,
            hospital_definition_met="meets standard" in hd_finding.description,
            missing_evidence=missing
        )
