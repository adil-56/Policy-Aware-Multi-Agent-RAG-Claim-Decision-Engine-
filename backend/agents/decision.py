from backend.models.state import (
    CaseState, EvidenceSet, EligibilityFindings, CoverageFindings, 
    FinancialAssessment, DecisionResult
)
from backend.utils.confidence import compute_confidence
import logging

logger = logging.getLogger(__name__)

class DecisionAgent:
    """
    Aggregates findings and makes the final determination based on strict rules.
    Prioritizes abstention (NEEDS_REVIEW / INSUFFICIENT_EVIDENCE).
    """
    def __init__(self, llm=None):
        self.llm = llm

    def evaluate(
        self, 
        state: CaseState, 
        eligibility: EligibilityFindings, 
        coverage: CoverageFindings, 
        financial: FinancialAssessment,
        evidence: EvidenceSet
    ) -> DecisionResult:
        logger.info(f"Making final decision for case {state.case_id}")
        
        all_findings = eligibility.findings + coverage.findings + financial.findings
        all_missing = (state.missing_initial_evidence + eligibility.missing_evidence + 
                       coverage.missing_evidence + financial.missing_evidence)
        
        # Calculate deterministic confidence
        avg_relevance = 0.8  # Default high fallback
        if evidence.definitions:
            avg_relevance = sum(e.relevance_score for e in evidence.definitions) / len(evidence.definitions)
            
        confidence = compute_confidence(all_findings, all_missing, avg_relevance)
        
        # Strict Abstention Logic (Rule-based)
        if len(state.missing_initial_evidence) > 0 or not eligibility.hospital_definition_met or not coverage.medical_necessity_established:
            status = "NEEDS_REVIEW"
            reasoning = "Critical evidence missing or fundamental eligibility/necessity criteria could not be established."
        elif not eligibility.hospitalization_eligible:
            status = "NOT_ADMISSIBLE"
            reasoning = "Not eligible for hospitalization under current policy definitions."
        elif len(coverage.applied_exclusions) > 0:
            status = "NOT_ADMISSIBLE"
            reasoning = "Procedure hits specific policy exclusions."
        elif financial.total_admissible_amount < sum(state.claim_data.get("claimed_amount", {}).values()):
            status = "ADMISSIBLE_WITH_LIMITS"
            reasoning = "Admissible but subject to specific policy limits (room rent/category caps)."
        else:
            status = "ADMISSIBLE"
            reasoning = "Claim is fully admissible."
            
        return DecisionResult(
            status=status,
            confidence=confidence,
            reasoning=reasoning,
            key_findings=all_findings
        )
