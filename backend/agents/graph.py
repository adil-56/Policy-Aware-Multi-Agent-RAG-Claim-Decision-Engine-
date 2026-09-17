from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from backend.models.state import (
    CaseState, EvidenceSet, EligibilityFindings, 
    CoverageFindings, FinancialAssessment, DecisionResult, ExecutionTraceStep
)
from backend.agents.case_analysis import CaseAnalysisAgent
from backend.agents.policy_evidence import PolicyEvidenceAgent
from backend.agents.orchestrators.eligibility import EligibilityAgent
from backend.agents.orchestrators.coverage import CoverageExclusionAgent
from backend.agents.orchestrators.financial import FinancialAssessmentAgent
from backend.agents.decision import DecisionAgent
from backend.agents.validation import ValidationAgent
import time

class GraphState(TypedDict):
    request: Dict[str, Any]
    case_state: CaseState
    evidence: EvidenceSet
    eligibility: EligibilityFindings
    coverage: CoverageFindings
    financial: FinancialAssessment
    decision: DecisionResult
    trace: list[ExecutionTraceStep]

def create_claim_workflow(retriever, llm=None):
    """
    Compiles the directed LangGraph workflow mapping the Multi-Agent architecture.
    """
    workflow = StateGraph(GraphState)
    
    # Initialize agents
    case_agent = CaseAnalysisAgent(llm)
    evidence_agent = PolicyEvidenceAgent(retriever, llm)
    eligibility_agent = EligibilityAgent(llm)
    coverage_agent = CoverageExclusionAgent(llm)
    financial_agent = FinancialAssessmentAgent(llm)
    decision_agent = DecisionAgent(llm)
    validation_agent = ValidationAgent(llm)

    # Nodes
    def analyze_case(state: GraphState):
        start = time.time()
        req = state["request"]
        case_state = case_agent.analyze(req["case_id"], req["claim_data"])
        trace = state.get("trace", [])
        trace.append(ExecutionTraceStep(
            agent="CaseAnalysisAgent", action="analyze", timestamp=str(time.time()), total_latency_ms=int((time.time()-start)*1000)
        ))
        return {"case_state": case_state, "trace": trace}

    def gather_evidence(state: GraphState):
        start = time.time()
        evidence = evidence_agent.gather_evidence(state["case_state"])
        trace = state.get("trace", [])
        trace.append(ExecutionTraceStep(
            agent="PolicyEvidenceAgent", action="retrieve_evidence", timestamp=str(time.time()), total_latency_ms=int((time.time()-start)*1000)
        ))
        return {"evidence": evidence, "trace": trace}

    def evaluate_eligibility(state: GraphState):
        start = time.time()
        elig = eligibility_agent.evaluate(state["case_state"], state["evidence"])
        trace = state.get("trace", [])
        trace.append(ExecutionTraceStep(
            agent="EligibilityAgent", action="evaluate", timestamp=str(time.time()), total_latency_ms=int((time.time()-start)*1000)
        ))
        return {"eligibility": elig, "trace": trace}

    def evaluate_coverage(state: GraphState):
        start = time.time()
        cov = coverage_agent.evaluate(state["case_state"], state["evidence"])
        trace = state.get("trace", [])
        trace.append(ExecutionTraceStep(
            agent="CoverageExclusionAgent", action="evaluate", timestamp=str(time.time()), total_latency_ms=int((time.time()-start)*1000)
        ))
        return {"coverage": cov, "trace": trace}

    def evaluate_financial(state: GraphState):
        start = time.time()
        fin = financial_agent.evaluate(state["case_state"], state["evidence"])
        trace = state.get("trace", [])
        trace.append(ExecutionTraceStep(
            agent="FinancialAssessmentAgent", action="evaluate", timestamp=str(time.time()), total_latency_ms=int((time.time()-start)*1000)
        ))
        return {"financial": fin, "trace": trace}

    def make_decision(state: GraphState):
        start = time.time()
        dec = decision_agent.evaluate(
            state["case_state"], state["eligibility"], state["coverage"], state["financial"], state["evidence"]
        )
        trace = state.get("trace", [])
        trace.append(ExecutionTraceStep(
            agent="DecisionAgent", action="evaluate", timestamp=str(time.time()), total_latency_ms=int((time.time()-start)*1000)
        ))
        return {"decision": dec, "trace": trace}
        
    def validate_decision(state: GraphState):
        start = time.time()
        dec = validation_agent.validate(state["decision"])
        trace = state.get("trace", [])
        trace.append(ExecutionTraceStep(
            agent="ValidationAgent", action="validate", timestamp=str(time.time()), total_latency_ms=int((time.time()-start)*1000)
        ))
        return {"decision": dec, "trace": trace}

    # Build Graph topology
    workflow.add_node("analyze_case", analyze_case)
    workflow.add_node("gather_evidence", gather_evidence)
    workflow.add_node("evaluate_eligibility", evaluate_eligibility)
    workflow.add_node("evaluate_coverage", evaluate_coverage)
    workflow.add_node("evaluate_financial", evaluate_financial)
    workflow.add_node("make_decision", make_decision)
    workflow.add_node("validate_decision", validate_decision)

    # Define edges (Sequential Pipeline)
    workflow.set_entry_point("analyze_case")
    workflow.add_edge("analyze_case", "gather_evidence")
    workflow.add_edge("gather_evidence", "evaluate_eligibility")
    workflow.add_edge("evaluate_eligibility", "evaluate_coverage")
    workflow.add_edge("evaluate_coverage", "evaluate_financial")
    workflow.add_edge("evaluate_financial", "make_decision")
    workflow.add_edge("make_decision", "validate_decision")
    workflow.add_edge("validate_decision", END)

    return workflow.compile()
