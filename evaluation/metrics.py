class EvaluationMetrics:
    def __init__(self):
        self.total_cases = 0
        self.correct_decisions = 0
        self.abstentions = 0
        self.hallucinations = 0
        self.total_citations = 0
        self.valid_citations = 0
        
    def add_case_result(self, is_correct: bool, is_abstention: bool, has_hallucination: bool, valid_cites: int, total_cites: int):
        self.total_cases += 1
        if is_correct: self.correct_decisions += 1
        if is_abstention: self.abstentions += 1
        if has_hallucination: self.hallucinations += 1
        self.valid_citations += valid_cites
        self.total_citations += total_cites
        
    def get_summary(self):
        return {
            "decision_accuracy": self.correct_decisions / max(self.total_cases, 1),
            "abstention_rate": self.abstentions / max(self.total_cases, 1),
            "hallucination_rate": self.hallucinations / max(self.total_cases, 1),
            "citation_accuracy": self.valid_citations / max(self.total_citations, 1)
        }
