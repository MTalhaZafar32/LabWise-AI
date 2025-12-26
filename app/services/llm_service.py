"""
LLM Service for generating explanations using Ollama
"""
import requests
from typing import Dict, Optional, List
import json
import re
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating AI explanations using local LLM"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                return any(self.model in name for name in model_names)
            return False
        except Exception as e:
            logger.error(f"Ollama not available: {str(e)}")
            return False
    
    def generate_explanation(self, result: Dict) -> str:
        """
        Generate human-readable explanation for a test result
        
        Args:
            result: Classified test result dictionary
            
        Returns:
            AI-generated explanation string
        """
        # Build prompt
        prompt = self._build_prompt(result)
        
        # Check if Ollama is available
        if not self.check_ollama_available():
            logger.warning("Ollama not available, using fallback explanation")
            return self._fallback_explanation(result)
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                explanation = response.json().get('response', '').strip()
                logger.info(f"Generated explanation for {result.get('test_name')}")
                return explanation
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._fallback_explanation(result)
                
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return self._fallback_explanation(result)
    
    def _build_prompt(self, result: Dict) -> str:
        """Build prompt for LLM"""
        test_name = result.get('test_name', 'Unknown Test')
        value = result.get('value', 'N/A')
        unit = result.get('unit', '')
        classification = result.get('classification', 'UNKNOWN')
        ref_range = result.get('reference_range', 'N/A')
        
        kb_info = result.get('kb_info', {})
        description = kb_info.get('description', '')
        
        prompt = f"""You are a medical information assistant. Explain the following lab test result in simple, clear language for a non-medical person.

Test: {test_name}
Value: {value} {unit}
Reference Range: {ref_range}
Status: {classification}

{f'Test Description: {description}' if description else ''}

IMPORTANT CONSTRAINTS:
1. Explain what this test measures
2. Explain what the {classification} status means
3. Use simple, non-technical language
4. Do NOT provide medical diagnosis
5. Do NOT recommend medications
6. Do NOT replace doctor consultation
7. Keep explanation under 100 words
8. Be factual and helpful

Provide a clear, concise explanation:"""

        return prompt
    
    def _fallback_explanation(self, result: Dict) -> str:
        """Generate fallback explanation when LLM is not available"""
        test_name = result.get('test_name', 'Unknown Test')
        classification = result.get('classification', 'UNKNOWN')
        ref_range = result.get('reference_range', 'N/A')
        
        if classification == 'NORMAL':
            return f"Your {test_name} level is within the normal reference range ({ref_range}). This is a good result."
        elif classification == 'LOW':
            return f"Your {test_name} level is below the normal reference range ({ref_range}). Please consult your healthcare provider for interpretation."
        elif classification == 'HIGH':
            return f"Your {test_name} level is above the normal reference range ({ref_range}). Please consult your healthcare provider for interpretation."
        else:
            return f"Unable to classify {test_name}. Please consult your healthcare provider for interpretation."
    
    def generate_batch_explanations(self, results: list) -> list:
        """
        Generate explanations for multiple results
        
        Args:
            results: List of classified test results
            
        Returns:
            List of results with explanations added
        """
        explained_results = []
        
        for result in results:
            # Only generate explanation for classified results
            if result.get('classification') in ['LOW', 'NORMAL', 'HIGH']:
                explanation = self.generate_explanation(result)
                result['ai_explanation'] = explanation
            else:
                result['ai_explanation'] = self._fallback_explanation(result)
            
            explained_results.append(result)
        
        return explained_results
    
    def extract_structured_data(self, ocr_text: str) -> List[Dict]:
        """
        Extract structured test results from OCR text using LLM
        """
        prompt = f"""You are a medical data extraction assistant. extracting lab test results from OCR text.
        
        EXTRACT FORMAT (JSON List):
        [{{
            "test_name": "exact test name found",
            "value": numeric_value,
            "unit": "unit string",
            "ref_range": "reference range string"
        }}]

        RULES:
        1. Extract ONLY lab tests (e.g., Hemoglobin, RBC, WBC, Glucose).
        2. DO NOT EXTRACT: Age, Sex, Date, Page Number, PID, MRN, Registered, Collected, Reported.
        3. IGNORE headers like "Test Name", "Result", "Units".
        4. If a value is missing or not numeric, skip the test.
        5. Return ONLY valid JSON. No markdown, no explanations.

        OCR TEXT:
        {ocr_text}
        
        JSON OUTPUT:"""

        try:
            if not self.check_ollama_available():
                logger.error("Ollama not available for extraction")
                return []

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 1000}
                },
                timeout=45
            )
            
            if response.status_code == 200:
                content = response.json().get('response', '')
                print(f"[DEBUG LLM RAW OUTPUT]: {content[:500]}")  # First 500 chars
                # Clean markdown code blocks if present
                content = re.sub(r'```json\s*|\s*```', '', content)
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'results' in data:
                        return data['results']
                    else:
                        logger.warning(f"Unexpected JSON structure: {type(data)}")
                        return []
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse LLM output as JSON: {content}")
                    return []
            return []
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return []

    def generate_final_summary(self, results: List[Dict]) -> str:
        """
        Generate a final summary paragraph based on findings
        """
        if not results:
            return "No test results were identified to summarize."

        # Format findings for prompt
        findings_str = "\n".join([
            f"- {r.get('test_name')}: {r.get('value')} {r.get('unit')} ({r.get('classification')})"
            for r in results
        ])
        
        prompt = f"""You are a medical AI assistant. Write a summary for a patient based on the following lab results.
        
        FINDINGS:
        {findings_str}
        
        INSTRUCTIONS:
        1. Write a cohesive paragraph summarizing the health status.
        2. Highlight any ABNORMAL (High/Low) results.
        3. Use simple, clear language.
        4. Do NOT diagnose diseases.
        5. End with a standard medical disclaimer.
        
        SUMMARY:"""
        
        try:
            if not self.check_ollama_available():
                return "AI Summary unavailable."

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=45
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
            return "Failed to generate summary."
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return "Error generating summary."

# Global instance
llm_service = LLMService()
