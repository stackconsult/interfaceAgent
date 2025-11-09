"""
PII Detection and Redaction service.
"""
from typing import Dict, Any, List
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from app.core.config import get_settings

settings = get_settings()


class PIIRedactionService:
    """Service for detecting and redacting PII from data."""
    
    def __init__(self):
        if settings.enable_pii_redaction:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
        else:
            self.analyzer = None
            self.anonymizer = None
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII entities in text."""
        if not settings.enable_pii_redaction or not text:
            return []
        
        results = self.analyzer.analyze(
            text=text,
            entities=settings.pii_entities_list,
            language="en",
        )
        
        return [
            {
                "entity_type": result.entity_type,
                "start": result.start,
                "end": result.end,
                "score": result.score,
                "text": text[result.start:result.end],
            }
            for result in results
        ]
    
    def redact_pii(self, text: str) -> str:
        """Redact PII from text."""
        if not settings.enable_pii_redaction or not text:
            return text
        
        # Analyze text for PII
        analyzer_results = self.analyzer.analyze(
            text=text,
            entities=settings.pii_entities_list,
            language="en",
        )
        
        # Anonymize detected PII
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": {"type": "mask", "masking_char": settings.pii_redaction_char}},
        )
        
        return anonymized_result.text
    
    def redact_dict(self, data: Dict[str, Any], fields_to_check: List[str] = None) -> Dict[str, Any]:
        """Redact PII from dictionary fields."""
        if not settings.enable_pii_redaction:
            return data
        
        result = data.copy()
        
        # If no specific fields specified, check all string fields
        if fields_to_check is None:
            fields_to_check = [k for k, v in data.items() if isinstance(v, str)]
        
        for field in fields_to_check:
            if field in result and isinstance(result[field], str):
                result[field] = self.redact_pii(result[field])
        
        return result


# Global PII redaction service instance
pii_service = PIIRedactionService()
