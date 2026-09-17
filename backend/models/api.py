from pydantic import BaseModel
from typing import List, Dict, Any
from backend.models.state import DecisionStatus, Finding, Citation, ValidationResult, ExecutionTraceStep

class AnalyzeClaimRequest(BaseModel):
    case_id: str
    claim_data: Dict[str, Any]

class AnalyzeClaimResponse(BaseModel):
    case_id: str
    decision: DecisionStatus
    confidence: float
    key_findings: List[Finding]
    applicable_limits: List[Dict[str, Any]]
    missing_evidence: List[str]
    citations: List[Citation]
    validation: ValidationResult
    trace: List[ExecutionTraceStep]
