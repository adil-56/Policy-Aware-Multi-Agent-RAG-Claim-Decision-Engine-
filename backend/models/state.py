from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal

class Citation(BaseModel):
    page: str
    section: str
    chunk_id: str
    source: str
    text: str

class Finding(BaseModel):
    description: str
    citations: List[Citation]
    is_supported: bool = True

class EvidenceItem(BaseModel):
    category: str
    content: str
    citation: Citation
    relevance_score: float
    is_structured_rule: bool = False

class CaseState(BaseModel):
    case_id: str
    claim_data: Dict[str, Any]
    decision_dimensions: List[str] = Field(default_factory=list)
    missing_initial_evidence: List[str] = Field(default_factory=list)
    investigation_plan: List[str] = Field(default_factory=list)

class EvidenceSet(BaseModel):
    definitions: List[EvidenceItem] = Field(default_factory=list)
    coverage_clauses: List[EvidenceItem] = Field(default_factory=list)
    exclusions: List[EvidenceItem] = Field(default_factory=list)
    limits: List[EvidenceItem] = Field(default_factory=list)

class EligibilityFindings(BaseModel):
    findings: List[Finding] = Field(default_factory=list)
    hospitalization_eligible: bool = False
    waiting_period_met: bool = False
    portability_adjustments: bool = False
    hospital_definition_met: bool = False
    domiciliary_eligible: bool = False
    day_care_eligible: bool = False
    missing_evidence: List[str] = Field(default_factory=list)

class CoverageFindings(BaseModel):
    findings: List[Finding] = Field(default_factory=list)
    covered_benefits: List[str] = Field(default_factory=list)
    applied_exclusions: List[str] = Field(default_factory=list)
    is_experimental: bool = False
    medical_necessity_established: bool = False
    missing_evidence: List[str] = Field(default_factory=list)

class FinancialAssessment(BaseModel):
    findings: List[Finding] = Field(default_factory=list)
    limits_applied: Dict[str, float] = Field(default_factory=dict)
    total_admissible_amount: float = 0.0
    missing_evidence: List[str] = Field(default_factory=list)

DecisionStatus = Literal[
    "ADMISSIBLE", 
    "ADMISSIBLE_WITH_LIMITS", 
    "PARTIALLY_ADMISSIBLE", 
    "NOT_ADMISSIBLE", 
    "NEEDS_REVIEW", 
    "INSUFFICIENT_EVIDENCE"
]

class ValidationResult(BaseModel):
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)

class ExecutionTraceStep(BaseModel):
    agent: str
    action: str
    timestamp: str
    retrieval_time_ms: Optional[int] = None
    rerank_time_ms: Optional[int] = None
    llm_time_ms: Optional[int] = None
    total_latency_ms: int
    token_usage: Optional[Dict[str, int]] = None
    retrieval_count: Optional[int] = None
    citation_count: Optional[int] = None

class DecisionResult(BaseModel):
    status: DecisionStatus
    confidence: float
    reasoning: str
    key_findings: List[Finding] = Field(default_factory=list)
    validation: Optional[ValidationResult] = None
