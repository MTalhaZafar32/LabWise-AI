"""
Parsing service for extracting structured data from OCR text
"""
import re
from typing import List, Dict, Optional
from app.utils.medical_utils import MedicalUtils
import logging

logger = logging.getLogger(__name__)

class ParsingService:
    """Service for parsing OCR text into structured lab results"""
    
    def __init__(self):
        self.medical_utils = MedicalUtils()
    
    def parse_lab_report(self, ocr_text: str) -> List[Dict[str, any]]:
        """
        Parse OCR text to extract lab test results
        
        Args:
            ocr_text: Raw text from OCR
            
        Returns:
            List of dictionaries containing test results
        """
        results = []
        lines = ocr_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Try to parse the line
            parsed = self._parse_line(line)
            if parsed:
                results.append(parsed)
        
        logger.info(f"Parsed {len(results)} test results from OCR text")
        return results
    
    def _parse_line(self, line: str) -> Optional[Dict[str, any]]:
        """
        Parse a single line to extract test information
        
        Args:
            line: Single line of text
            
        Returns:
            Dictionary with test info or None
        """
        # Multiple patterns to handle different formats
        patterns = [
            # Pattern 1: "Test Name: 12.5 g/dL"
            r'([A-Za-z][A-Za-z\s\-()]+?)\s*[:=]\s*([\d.]+)\s*([A-Za-z/μ%°×\^0-9]+)',
            # Pattern 2: "Test Name 12.5 g/dL"
            r'([A-Za-z][A-Za-z\s\-()]+?)\s+([\d.]+)\s+([A-Za-z/μ%°×\^0-9]+)',
            # Pattern 3: "Test Name    12.5    g/dL" (multiple spaces)
            r'([A-Za-z][A-Za-z\s\-()]+?)\s{2,}([\d.]+)\s+([A-Za-z/μ%°×\^0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                test_name = match.group(1).strip()
                value_str = match.group(2).strip()
                unit = match.group(3).strip()
                
                # Skip if test name is too short or looks invalid
                if len(test_name) < 2 or test_name.isdigit():
                    continue
                
                # Extract numeric value
                try:
                    value = float(value_str)
                except ValueError:
                    continue
                
                # Normalize
                normalized_name = self.medical_utils.normalize_test_name(test_name)
                normalized_unit = self.medical_utils.normalize_unit(unit)
                
                return {
                    'test_name': test_name,
                    'normalized_name': normalized_name,
                    'value': value,
                    'unit': normalized_unit,
                    'raw_line': line
                }
        
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
