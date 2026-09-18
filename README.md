# Policy-Aware Multi-Agent RAG Claim Decision Engine

## Executive Summary
Health insurance claims processing is traditionally a manual, time-intensive operation that requires extensive cross-referencing between patient data, medical invoices, and complex, 100+ page policy documents. This manual review cycle introduces significant operational bottlenecks and human error.

This repository contains a production-style, multi-agent artificial intelligence system designed to autonomously adjudicate health insurance claims using Retrieval-Augmented Generation (RAG). By grounding every decision in explicit policy citations and strictly enforcing deterministic financial rules over LLM hallucinations, the system ensures highly accurate, auditable outcomes. Crucially, the system is designed with a strict escalation protocol: if evidence is lacking, it abstains from guessing and safely routes the claim for human intervention (`NEEDS_REVIEW`).

## Live Application Links

You can test and interact with the deployed application via the following environments:

* **User Interface (Streamlit):** [https://policy-aware-multi-agent-rag-claim-decision.streamlit.app/](https://policy-aware-multi-agent-rag-claim-decision.streamlit.app/)
  * Use this interface to interactively evaluate claim cases, view citations, and inspect the system's execution trace without exposing the raw underlying chain-of-thought.
* **Backend API Documentation (FastAPI / Swagger UI):** [https://policy-aware-multi-agent-rag-claim.onrender.com/docs](https://policy-aware-multi-agent-rag-claim.onrender.com/docs)
  * Interactive API documentation. Use the `/analyze` POST endpoint to programmatically submit claim JSON data, or the `/health` GET endpoint to verify infrastructure readiness.

## System Architecture & Workflow

The architecture leverages **LangGraph** to pass a strongly-typed, verifiable state object through a genuine multi-agent workflow. Responsibilities are strictly separated into domain-specific agents to prevent prompt engineering bleed and ensure highly focused reasoning.

```mermaid
graph TD
    User([User / API Request]) --> CA[Case Analysis Agent]
    
    subgraph Multi-Agent RAG Workflow
        CA -->|Analyzes Claim & Identifies Needs| PE[Policy Evidence Agent]
        
        subgraph Hybrid Retrieval Engine
            PE --> DB[(ChromaDB: Dense Search)]
            PE --> BM[(BM25: Sparse Search)]
            DB --> FUSE(Reciprocal Rank Fusion)
            BM --> FUSE
            FUSE --> RR[FlashRank Cross-Encoder]
        end
        
        RR -->|Highly Ranked Metadata Citations| CE[Coverage & Exclusion Agent]
        CE -->|Evaluates Medical Necessity & Exclusions| DA[Decision Agent]
        DA -->|Calculates Limits & Final Decision| VA[Validation Agent]
    end
    
    VA -->|Validates Evidence Support| API[FastAPI Response]
    API --> User
```

### Specialized Agent Responsibilities
1. **Case Analysis Agent:** Extracts material facts from the raw claim JSON, identifies missing initial evidence (e.g., missing claim forms), and outlines the investigation scope.
2. **Policy Evidence Agent:** Orchestrates the Hybrid Retrieval Engine to pull the most relevant policy clauses regarding room rent limits, waiting periods, and specific exclusions.
3. **Coverage & Exclusion Agent:** Cross-references the retrieved policy evidence with the claim treatment to flag pre-existing conditions, waiting period breaches, or categorical exclusions.
4. **Decision Agent:** Aggregates all findings, calculates strict financial limits (e.g., enforcing a 1% of Sum Insured room rent cap), and issues the final determination (`ADMISSIBLE`, `NOT_ADMISSIBLE`, `ADMISSIBLE_WITH_LIMITS`, or `NEEDS_REVIEW`).
5. **Validation Agent:** Acts as the final safety net and compliance check. It inspects the decision to ensure every material claim is backed by a verifiable policy citation. If evidence is lacking, it forcefully overrides the status to `NEEDS_REVIEW`.

## Core Engineering & Design Trade-offs

* **Hybrid Retrieval with CPU Reranking:** Instead of relying on latency-heavy and costly commercial embedding APIs, the system utilizes `FastEmbed` (Dense Semantic Search) and `BM25` (Sparse Keyword Search), fused via Reciprocal Rank Fusion (RRF). Because standard vector search struggles with nuanced legal/insurance terminology, the results are passed through **FlashRank** (`ms-marco-TinyBERT`), a CPU-optimized cross-encoder. This guarantees high-accuracy evidence retrieval without exceeding free-tier cloud memory constraints (512MB RAM).
* **Section Metadata Extraction:** Arbitrary character splitting destroys policy context. The indexing engine parses PDF text blocks using heuristics to detect and persist hierarchical PDF headers (e.g., `(C) Claims Processing`) alongside the page number and chunk ID, preserving the legal context for citations.
* **Deterministic Rules over Generative Math:** Generative AI is prone to hallucinating mathematical calculations and specific insurance caps. Confidence scoring and financial sub-limit logic are extracted into deterministic Python functions, ensuring the system calculates payouts reliably rather than attempting to generate them via prompt.

## Evaluation & Performance Metrics

The system was evaluated against a suite of 17 test cases, consisting of 12 public baseline cases and 5 custom-designed edge cases (testing missing documentation and pre-existing condition wait periods). 

* **Overall Accuracy:** 100% on valid, known outcomes.
* **Abstention Target:** Achieved. The system correctly identifies missing critical documents (e.g., missing discharge summaries) and defaults to `NEEDS_REVIEW` to prompt human intervention, fulfilling the primary safety requirement.
* A detailed breakdown of the evaluation pipeline and failure analysis methodology is documented inside the repository's `evaluation_report.md`.

## Setup & Local Execution

### Prerequisites
* Python 3.10+
* `pip` package manager

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/adil-56/Policy-Aware-Multi-Agent-RAG-Claim-Decision-Engine-.git
   cd Policy-Aware-Multi-Agent-RAG-Claim-Decision-Engine-
   ```
2. Install the lightweight dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. *(Optional)* If you wish to rebuild the vector database from the source PDF:
   ```bash
   python build_db.py
   ```

### Running the API (Backend)
Launch the FastAPI backend server:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
The interactive API documentation will be available at `http://localhost:8000/docs`.

### Running the UI (Frontend)
In a separate terminal window, launch the Streamlit interface:
```bash
streamlit run frontend/app.py
```
The user interface will be available at `http://localhost:8501`.
