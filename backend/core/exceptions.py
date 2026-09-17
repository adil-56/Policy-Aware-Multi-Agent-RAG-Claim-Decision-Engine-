class EngineException(Exception):
    """Base exception for the Claim Decision Engine"""
    pass

class ParsingException(EngineException):
    """Raised when PDF parsing or rule extraction fails"""
    pass

class RetrievalException(EngineException):
    """Raised when vector search or BM25 retrieval fails"""
    pass

class EvaluationException(EngineException):
    """Raised when an internal policy evaluator fails"""
    pass

class MissingEvidenceException(EngineException):
    """Raised when critical evidence is completely missing, forcing an abstention"""
    pass
