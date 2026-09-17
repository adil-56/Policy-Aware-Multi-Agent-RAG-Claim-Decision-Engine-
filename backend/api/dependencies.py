from fastapi import Request
from backend.retrieval.hybrid import HybridRetriever
from backend.agents.graph import create_claim_workflow

# In a real app, these would be initialized on startup
# and accessed via app.state or dependency injection.
_retriever = None
_workflow = None

def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever

def get_workflow():
    global _workflow
    if _workflow is None:
        # Assuming no real LLM is connected yet for the mock test
        _workflow = create_claim_workflow(get_retriever(), llm=None)
    return _workflow
