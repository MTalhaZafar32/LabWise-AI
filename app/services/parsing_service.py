"""
Parsing service for extracting structured data from OCR text
"""
import re
from typing import List, Dict, Optional
from app.utils.medical_utils import MedicalUtils
import logging

logger = logging.getLogger(__name__)

from app.services.llm_service import llm_service

class ParsingService:
    """Service for parsing OCR text into structured lab results"""
    
    def __init__(self):
        self.medical_utils = MedicalUtils()
    
    def parse_lab_report(self, ocr_text: str) -> List[Dict[str, any]]:
        """
        Parse OCR text to extract lab test results using LLM
        """
        results = []
        
        # Step 1: Use LLM to extract structured data
        logger.info("Sending OCR text to LLM for extraction...")
        llm_data = llm_service.extract_structured_data(ocr_text)
        
        if not llm_data:
            logger.warning("LLM returned no structured data")
            return []

        # Step 2: Normalize and validate extracted data
        for item in llm_data:
            try:
                test_name = item.get('test_name')
                value = item.get('value')
                unit = item.get('unit', '')
                ref_range = item.get('ref_range', '')
                
                if not test_name or value is None:
                    continue
                
                # Filter out obvious metadata that LLM might have extracted
                lower_name = test_name.lower()
                blocklist = [
                    'age', 'sex', 'gender', 'page', 'date', 'time',
                    'registered', 'collected', 'reported', 'generated', 'received',
                    'pid', 'patient', 'name', 'mrn', 'dob', 'ref', 'dr', 'doctor',
                    'hospital', 'lab', 'location', 'phone', 'fax', 'email'
                ]
                
                # Check if any blocklist word is the ENTIRE name or if the name starts with it
                if any(lower_name == blocked or lower_name.startswith(f"{blocked} ") for blocked in blocklist):
                    continue
                
                # Ensure value is numeric
                if isinstance(value, str):
                    try:
                        # Handle ranges or "<" symbols if LLM extracted them as value
                        clean_val = re.sub(r'[^\d.]', '', value)
                        value = float(clean_val)
                    except ValueError:
                        continue
                
                # Normalize
                normalized_name = self.medical_utils.normalize_test_name(test_name)
                normalized_unit = self.medical_utils.normalize_unit(unit)
                
                results.append({
                    'test_name': test_name,
                    'normalized_name': normalized_name,
                    'value': value,
                    'unit': normalized_unit,
                    'reference_range': ref_range
                })
                
            except Exception as e:
                logger.warning(f"Error normalizing item {item}: {e}")
                continue
        
        logger.info(f"LLM extracted and parsed {len(results)} test results")
        return results

    def _parse_line(self, line: str) -> Optional[Dict[str, any]]:
        """Deprecated: Regex parsing (kept for reference or fallback if needed in future)"""
        return None
    
    def clean_test_name(self, test_name: str) -> str:
        """
        Clean and normalize test name
        
        Args:
            test_name: Raw test name
            
        Returns:
            Cleaned test name
        """
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', test_name.strip())
        
        # Remove trailing punctuation
        cleaned = cleaned.rstrip('.:,;')
        
        return cleaned

# Global instance
parsing_service = ParsingService()
