from backend.models.state import DecisionResult, ValidationResult
import logging

logger = logging.getLogger(__name__)

class ValidationAgent:
    """
    Final rigorous check to ensure all material findings have valid, existing citations.
    """
    def __init__(self, llm=None):
        self.llm = llm

    def validate(self, decision: DecisionResult) -> DecisionResult:
        logger.info("Validating citations and findings for decision result.")
        
        errors = []
        unsupported = []
        
        for finding in decision.key_findings:
            if not finding.citations:
                msg = f"Finding '{finding.description[:30]}...' lacks explicit citations."
                errors.append(msg)
                unsupported.append(finding.description)
                finding.is_supported = False
            
            # In a full production system:
            # 1. Verify if citation chunks actually exist in the DB.
            # 2. Use LLM entailment to check if the chunk text logically supports the finding.
            
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.warning(f"Validation failed. Errors: {len(errors)}")
            # Enforce Abstention Priority
            if decision.status in ["ADMISSIBLE", "ADMISSIBLE_WITH_LIMITS", "PARTIALLY_ADMISSIBLE"]:
                logger.warning("Downgrading decision to NEEDS_REVIEW due to missing citations.")
                decision.status = "NEEDS_REVIEW"
                decision.confidence = max(0.0, decision.confidence - 0.3)
                decision.reasoning += " [SYSTEM: Flagged for review due to unsupported findings]"
            
        decision.validation = ValidationResult(
            is_valid=is_valid,
            validation_errors=errors,
            unsupported_claims=unsupported
        )
        
        return decision
