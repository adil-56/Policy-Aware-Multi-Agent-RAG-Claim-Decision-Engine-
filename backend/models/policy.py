from pydantic import BaseModel, Field
from typing import Dict, Any, Literal

PolicyRuleType = Literal[
    "PolicyDefinition", 
    "CoverageClause", 
    "ExclusionClause", 
    "WaitingPeriodRule", 
    "LimitRule", 
    "BenefitRule"
]

class PolicyRule(BaseModel):
    """
    Represents a structured rule extracted from the policy document.
    Stored alongside raw vector chunks to ensure precise reasoning.
    """
    rule_type: PolicyRuleType
    content: str = Field(..., description="The exact text or summarized structured logic of the rule")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Metadata including source page, section, and original chunk ID"
    )
