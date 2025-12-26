"""
Medical utilities for unit conversion and term normalization
"""
from typing import Dict, Optional
import re

class MedicalUtils:
    """Utilities for medical data processing"""
    
    # Common unit conversions
    UNIT_CONVERSIONS = {
        'g/dl': 'g/dL',
        'g/l': 'g/L',
        'mg/dl': 'mg/dL',
        'mmol/l': 'mmol/L',
        'umol/l': 'μmol/L',
        'iu/l': 'IU/L',
        'u/l': 'U/L',
        'pg/ml': 'pg/mL',
        'ng/ml': 'ng/mL',
        'ng/dl': 'ng/dL',
    }
    
    # Medical term synonyms
    TERM_SYNONYMS = {
        'hb': 'hemoglobin',
        'hgb': 'hemoglobin',
        'wbc': 'white blood cell count',
        'rbc': 'red blood cell count',
        'plt': 'platelet count',
        'mcv': 'mean corpuscular volume',
        'mch': 'mean corpuscular hemoglobin',
        'mchc': 'mean corpuscular hemoglobin concentration',
        'esr': 'erythrocyte sedimentation rate',
        'crp': 'c-reactive protein',
        'alt': 'alanine aminotransferase',
        'ast': 'aspartate aminotransferase',
        'alp': 'alkaline phosphatase',
        'ggt': 'gamma-glutamyl transferase',
        'ldl': 'ldl cholesterol',
        'hdl': 'hdl cholesterol',
        'tsh': 'thyroid stimulating hormone',
        'ft4': 'free thyroxine',
        'ft3': 'free triiodothyronine',
        'hba1c': 'hemoglobin a1c',
        'a1c': 'hemoglobin a1c',
    }
    
    @staticmethod
    def normalize_unit(unit: str) -> str:
        """
        Normalize unit to standard format
        
        Args:
            unit: Unit string
            
        Returns:
            Normalized unit string
        """
        unit_lower = unit.lower().strip()
        return MedicalUtils.UNIT_CONVERSIONS.get(unit_lower, unit)
    
    @staticmethod
    def normalize_test_name(test_name: str) -> str:
        """
        Normalize test name for matching
        
        Args:
            test_name: Test name string
            
        Returns:
            Normalized test name
        """
        # Convert to lowercase and remove extra spaces
        normalized = test_name.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Check for synonyms
        return MedicalUtils.TERM_SYNONYMS.get(normalized, normalized)
    
    @staticmethod
    def extract_numeric_value(value_str: str) -> Optional[float]:
        """
        Extract numeric value from string
        
        Args:
            value_str: String containing numeric value
            
        Returns:
            Extracted float value or None
        """
        # Remove common non-numeric characters
        cleaned = re.sub(r'[^\d.\-+]', '', value_str)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def parse_test_line(line: str) -> Optional[Dict[str, str]]:
        """
        Parse a line from OCR output to extract test information
        
        Args:
            line: OCR text line
            
        Returns:
            Dictionary with test_name, value, unit or None
        """
        # Common patterns for lab results
        # Example: "Hemoglobin 12.5 g/dL"
        # Example: "WBC: 8.5 x10^3/μL"
        
        patterns = [
            r'([A-Za-z\s]+?)\s*[:=]?\s*([\d.]+)\s*([A-Za-z/μ%°]+)',
            r'([A-Za-z\s]+?)\s+([\d.]+)\s+([A-Za-z/μ%°]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return {
                    'test_name': match.group(1).strip(),
                    'value': match.group(2).strip(),
                    'unit': match.group(3).strip()
                }
        
        return None
    
    @staticmethod
    def classify_value(value: float, ref_low: Optional[float], ref_high: Optional[float]) -> str:
        """
        Classify a test value as LOW, NORMAL, or HIGH
        
        Args:
            value: Test value
            ref_low: Reference range lower bound
            ref_high: Reference range upper bound
            
        Returns:
            Classification string: 'LOW', 'NORMAL', or 'HIGH'
        """
        if ref_low is not None and value < ref_low:
            return 'LOW'
        elif ref_high is not None and value > ref_high:
            return 'HIGH'
        else:
            return 'NORMAL'
