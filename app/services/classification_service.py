"""
Classification service for rule-based test result classification
"""
from typing import Dict, Optional
from app.utils.medical_utils import MedicalUtils
import logging

logger = logging.getLogger(__name__)

class ClassificationService:
    """Service for classifying test results as LOW/NORMAL/HIGH"""
    
    def __init__(self):
        self.medical_utils = MedicalUtils()
    
    def classify_result(self, result: Dict) -> Dict:
        """
        Classify a test result based on reference range
        
        Args:
            result: Dictionary containing test result and KB info
            
        Returns:
            Result dictionary with classification added
        """
        classified = {**result}
        
        # Check if KB info is available
        if not result.get('kb_found') or not result.get('kb_info'):
            classified['classification'] = 'UNKNOWN'
            classified['classification_reason'] = 'Test not found in knowledge base'
            return classified
        
        kb_info = result['kb_info']
        ref_range = kb_info.get('reference_range')
        
        if not ref_range:
            classified['classification'] = 'UNKNOWN'
            classified['classification_reason'] = 'No reference range available'
            return classified
        
        # Get test value
        value = result.get('value')
        if value is None:
            classified['classification'] = 'UNKNOWN'
            classified['classification_reason'] = 'No numeric value available'
            return classified
        
        # Get reference bounds
        ref_low = ref_range.get('ref_low')
        ref_high = ref_range.get('ref_high')
        
        # Classify using rule-based logic
        classification = self.medical_utils.classify_value(value, ref_low, ref_high)
        
        classified['classification'] = classification
        classified['ref_low'] = ref_low
        classified['ref_high'] = ref_high
        classified['ref_unit'] = ref_range.get('unit')
        
        # Create reference range string
        if ref_low is not None and ref_high is not None:
            classified['reference_range'] = f"{ref_low} - {ref_high} {ref_range.get('unit', '')}"
        elif ref_low is not None:
            classified['reference_range'] = f"> {ref_low} {ref_range.get('unit', '')}"
        elif ref_high is not None:
            classified['reference_range'] = f"< {ref_high} {ref_range.get('unit', '')}"
        else:
            classified['reference_range'] = ref_range.get('ref_text', 'N/A')
        
        logger.info(
            f"Classified {result.get('test_name')}: "
            f"{value} {result.get('unit')} -> {classification}"
        )
        
        return classified
    
    def classify_batch(self, results: list) -> list:
        """
        Classify multiple test results
        
        Args:
            results: List of test result dictionaries
            
        Returns:
            List of classified results
        """
        return [self.classify_result(result) for result in results]

# Global instance
classification_service = ClassificationService()
