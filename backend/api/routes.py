from fastapi import APIRouter, Depends, HTTPException
from backend.models.api import AnalyzeClaimRequest, AnalyzeClaimResponse
from backend.api.dependencies import get_workflow
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/analyze", response_model=AnalyzeClaimResponse)
def analyze_claim(
    request: AnalyzeClaimRequest,
    workflow = Depends(get_workflow)
):
    try:
        # Construct initial state
        initial_state = {
            "request": {
                "case_id": request.case_id,
                "claim_data": request.claim_data
            }
        }
        
        # Execute LangGraph workflow
        logger.info(f"Starting workflow for case {request.case_id}")
        final_state = workflow.invoke(initial_state)
        
        decision = final_state.get("decision")
        if not decision:
            raise HTTPException(status_code=500, detail="Workflow failed to produce a decision.")
            
        financial = final_state.get("financial")
        limits = []
        if financial and financial.limits_applied:
            limits = [{"category": k, "limit": v} for k, v in financial.limits_applied.items()]
            
        return AnalyzeClaimResponse(
            case_id=request.case_id,
            decision=decision.status,
            confidence=decision.confidence,
            key_findings=decision.key_findings,
            applicable_limits=limits,
            missing_evidence=final_state.get("case_state").missing_initial_evidence,
            citations=[c for f in decision.key_findings for c in f.citations], # Flatten citations
            validation=decision.validation,
            trace=final_state.get("trace", [])
        )
    except Exception as e:
        logger.error(f"Error processing claim {request.case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
