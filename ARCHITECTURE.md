# Architecture & Design Note

## 1. Agent Boundaries and Responsibilities
The system rejects the pattern of a single "omniscient" LLM prompt. Instead, we implement a genuine multi-agent workflow where responsibilities are strictly separated to mirror a real-world claims adjudication floor.

1. **Case Analysis Agent (The Triage Nurse):** Responsible solely for parsing the raw JSON, validating required fields, and initializing the `CaseState`. It does not retrieve policy data or make coverage decisions.
2. **Policy Evidence Agent (The Researcher):** Acts as the interface to the Vector/BM25 database. It converts the CaseState into highly specific query vectors (e.g., "room rent limits", "waiting periods for pre-existing diseases") and retrieves relevant chunks.
3. **Specialized Orchestrators (Eligibility, Coverage, Financial):** These agents do not evaluate policy themselves. Instead, they instantiate highly specific "Evaluators" (e.g., `RoomRentEvaluator`). They pass the evidence to the evaluator and aggregate the resulting `Findings`.
4. **Decision Agent (The Adjudicator):** Consumes the aggregated findings and applies rigid business logic to formulate a `DecisionResult`.
5. **Validation Agent (The Auditor):** The final safety mechanism. It intercepts the `DecisionResult` and asserts that every material finding possesses a valid policy citation. If citations are missing, it overrides the decision to `NEEDS_REVIEW`.

## 2. State Flow
Agents do not communicate via free-form conversational text. They strictly exchange instances of Pydantic models (e.g., `CaseState`, `EligibilityFindings`). This guarantees type safety and ensures that downstream agents always receive the necessary context (like `sum_insured_inr` or `admission_hours`) without relying on the LLM's memory.

The flow is orchestrated using **LangGraph**, formulated as a strictly directed acyclic graph (DAG) to ensure execution predictability.

## 3. Retrieval Design (Hybrid RRF)
Semantic search (Dense vectors via Chroma/FAISS) excels at conceptual matching (e.g., matching "heart attack" to "myocardial infarction"). However, insurance policies heavily rely on exact lexical matches (e.g., "Section 3.1.b", "30 days"). 

Therefore, we implement:
- **BM25 (Sparse Retrieval):** To capture exact keyword and section number matches.
- **ChromaDB (Dense Retrieval):** To capture semantic intent.
- **Reciprocal Rank Fusion (RRF):** To mathematically merge the rankings from both sparse and dense retrievers.
- **Cross-Encoder Reranking (BAAI/bge-reranker-base):** A final, computationally heavier pass to ensure the top-K chunks strictly entail the query intent before passing them to the reasoning agents.

## 4. Important Trade-offs
- **Latency vs. Accuracy:** The pipeline executes in series through multiple agents and a cross-encoder reranking step. This results in higher latency per claim compared to a standard naive RAG approach, but it is necessary to achieve the extreme accuracy required for automated financial adjudication.
- **Abstention Priority:** The system is biased heavily toward returning `NEEDS_REVIEW`. In production, this means a higher volume of claims will fall out to manual human review. While this lowers straight-through processing (STP) rates, it prevents catastrophic financial liabilities caused by LLM hallucinations.
