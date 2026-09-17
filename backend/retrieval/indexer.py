import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional
from backend.models.policy import PolicyRule, PolicyRuleType
from backend.core.exceptions import ParsingException
import json
import logging

logger = logging.getLogger(__name__)

class PolicyIndexer:
    """
    Handles extracting raw text chunks and structured PolicyRules 
    from the insurance policy PDF.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_text_chunks(self) -> List[Dict[str, Any]]:
        """
        Extracts text blocks from the PDF while attempting to preserve page numbers
        and structure. Returns a list of chunks ready for vector indexing.
        """
        try:
            doc = fitz.open(self.pdf_path)
            chunks = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Extract blocks (text blocks usually have type 0)
                blocks = page.get_text("blocks")
                for idx, b in enumerate(blocks):
                    text = b[4].strip()
                    # Filter out very small artifacts or empty blocks
                    if len(text) > 20:
                        chunks.append({
                            "chunk_id": f"p{page_num+1}_b{idx}",
                            "page": str(page_num + 1),
                            "text": text,
                            "source": self.pdf_path.split("/")[-1]
                        })
            return chunks
        except Exception as e:
            logger.error(f"Failed to parse PDF {self.pdf_path}: {e}")
            raise ParsingException(f"Failed to parse PDF {self.pdf_path}: {str(e)}")

    def extract_structured_rules(self, text: str, llm=None) -> List[PolicyRule]:
        """
        Uses an LLM to extract formal policy rules from raw text chunks.
        This provides the structured knowledge base needed for reliable evaluators.
        """
        if not llm:
            logger.warning("No LLM provided to extract_structured_rules. Returning empty.")
            return []
            
        prompt = f"""
        Extract any formal policy rules from the following text. 
        Respond in pure JSON format: a list of objects with 'rule_type' and 'content'.
        Valid rule_types: PolicyDefinition, CoverageClause, ExclusionClause, WaitingPeriodRule, LimitRule, BenefitRule
        
        Text: {text}
        """
        try:
            # Assumes a Langchain-compatible chat model
            response = llm.invoke(prompt)
            # Very basic cleanup for raw JSON string parsing
            raw_content = response.content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:-3]
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:-3]
                
            data = json.loads(raw_content)
            rules = []
            for item in data:
                rules.append(PolicyRule(
                    rule_type=item["rule_type"],
                    content=item["content"],
                    metadata={"source": "extracted_from_chunk"}
                ))
            return rules
        except Exception as e:
            logger.error(f"Failed to extract structured rules: {e}")
            return []
