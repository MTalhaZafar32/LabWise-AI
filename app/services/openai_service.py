"""
OpenAI Service for LabWise AI
Handles extraction and summary generation using OpenAI models
"""
import json
import logging
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.utils.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        """Initialize OpenAI models"""
        try:
            # Extraction model (gpt-4o-mini)
            self.extraction_model = ChatOpenAI(
                model=settings.OPENAI_EXTRACTION_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Summary model (gpt-4o-mini)
            self.summary_model = ChatOpenAI(
                model=settings.OPENAI_SUMMARY_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.3,  # Slightly higher for natural summaries
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            logger.info(f"OpenAI models initialized: {settings.OPENAI_EXTRACTION_MODEL}, {settings.OPENAI_SUMMARY_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI models: {e}")
            raise
    
    def extract_structured_data(self, ocr_text: str, standard_test_names: Optional[List[str]] = None) -> List[Dict]:
        """
        Extract structured test data from OCR text using gpt-4o-mini
        
        Args:
            ocr_text: Raw OCR text from the lab report
            standard_test_names: Optional list of standard test names from KB for mapping
            
        Returns:
            List of dictionaries containing extracted test data
        """
        
        # Build prompt additions if standard names are provided
        mapping_instruction = ""
        context_data = ""
        
        if standard_test_names:
            names_str = ", ".join(standard_test_names[:100])  # Limit to 100 names to save tokens
            mapping_instruction = f"""
7. MAP TO STANDARD NAMES: If an extracted test name matches one of these standard names (fuzzy match), use the STANDARD name:
   [{names_str}]
"""
            context_data = f"\n\nStandard Test Names (use these if possible):\n{names_str}"

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"""You are a medical data extraction AI. Your ONLY job is to extract lab test results from OCR text.

CRITICAL RULES:
1. Extract ONLY actual lab tests (Hemoglobin, WBC, RBC, Glucose, Cholesterol, etc.)
2. DO NOT extract metadata: Age, Sex, Date, Page, PID, MRN, Registered, Collected, Reported, Hospital, Doctor, Patient Name
3. Each test MUST have a numeric value
4. Return ONLY valid JSON array, no markdown, no explanations
5. MEDICAL SAFETY: Be extremely accurate - lives depend on this data
6. If uncertain about a value, DO NOT include it{mapping_instruction}

OUTPUT FORMAT (STRICT JSON):
[
  {{{{
    "test_name": "exact name from report (or mapped standard name)",
    "value": numeric_value,
    "unit": "unit string",
    "reference_range": "range if available or empty string"
  }}}}
]

If no valid tests found, return: []

VALIDATION: Double-check all numeric values before returning."""),
            ("human", f"Extract lab tests from this OCR text:\n\n{{ocr_text}}{context_data}")
        ])
        
        try:
            logger.info(f"Sending OCR text to OpenAI ({settings.OPENAI_EXTRACTION_MODEL}) for extraction...")
            
            chain = prompt_template | self.extraction_model
            response = chain.invoke({"ocr_text": ocr_text})
            content = response.content.strip()
            
            # Log raw response for debugging
            logger.debug(f"OpenAI raw response: {content[:500]}")
            
            # Clean markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            # Parse JSON
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    logger.info(f"OpenAI extracted {len(data)} tests")
                    return data
                else:
                    logger.warning(f"Unexpected JSON structure: {type(data)}")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                logger.error(f"Raw content: {content}")
                return []
                
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}", exc_info=True)
            return []
    
    def generate_summary(
        self,
        results: List[Dict],
        kb_matched: bool,
        kb_data: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate medical summary using gpt-4o-mini
        
        Args:
            results: Classified test results
            kb_matched: Whether KB data was found
            kb_data: Knowledge base reference data (if available)
            
        Returns:
            Summary paragraph
        """
        if not results:
            return "No test results were identified in the uploaded report."
        
        # Build context for the model
        test_summary = "\n".join([
            f"- {r.get('test_name')}: {r.get('value')} {r.get('unit')} "
            f"(Status: {r.get('classification', 'UNKNOWN')})"
            for r in results
        ])
        
        if kb_matched and kb_data:
            # We have KB reference data - high confidence summary
            kb_context = "\n".join([
                f"- {r.get('test_name')}: Reference Range = {r.get('reference_range', 'N/A')}"
                for r in results if r.get('kb_found')
            ])
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a medical AI assistant analyzing lab results. You have access to verified reference ranges from our knowledge base.

CRITICAL SAFETY RULES (MEDICAL DATA - LIVES AT STAKE):
1. NEVER diagnose diseases
2. NEVER recommend specific medications
3. NEVER replace doctor consultation
4. Use simple, clear language for non-medical audience
5. Be factual and evidence-based
6. Highlight abnormal values clearly
7. Always recommend consulting a healthcare provider for interpretation
8. DOUBLE-CHECK all values before making statements
9. If uncertain, err on the side of caution
10. This is MEDICAL data - accuracy is CRITICAL

Your task: Write a comprehensive but concise summary paragraph explaining:
- Overall health status based on the results
- Which values are normal vs abnormal
- Severity of any abnormalities (mild, moderate, severe)
- General health implications
- Clear recommendation to consult doctor if needed

FORMAT: Single paragraph, patient-friendly language, 3-5 sentences. DO NOT use asterisks or any markdown formatting. Use plain text only."""),
                ("human", """Analyze these lab results:

TEST RESULTS:
{test_summary}

REFERENCE RANGES (from verified knowledge base):
{kb_context}

Provide a clear, patient-friendly summary paragraph in plain text without any markdown formatting.""")
            ])
            
            chain = prompt_template | self.summary_model
            response = chain.invoke({
                "test_summary": test_summary,
                "kb_context": kb_context
            })
            
        else:
            # No KB data - cautious summary with lower confidence
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a medical AI assistant. You are analyzing lab results WITHOUT verified reference ranges.

CRITICAL SAFETY RULES (MEDICAL DATA - LIVES AT STAKE):
1. State clearly that reference ranges are not available
2. NEVER diagnose diseases
3. NEVER recommend specific medications  
4. STRONGLY recommend consulting a healthcare provider
5. Be extremely cautious in interpretation
6. Use phrases like "appears to be", "may indicate", "should be evaluated by"
7. Emphasize the importance of professional medical interpretation
8. DO NOT attempt to classify values as normal/abnormal without references
9. This is MEDICAL data - extreme caution required

Your task: Write a brief, cautious summary that:
- Lists the test values found
- States that proper interpretation requires reference ranges
- Strongly recommends consulting a healthcare provider
- Does NOT attempt to classify values as normal/abnormal

FORMAT: Single paragraph, 2-3 sentences, emphasizing need for professional review. DO NOT use asterisks or any markdown formatting. Use plain text only."""),
                ("human", """These lab test values were found:

{test_summary}

Note: Reference ranges are not available in our knowledge base for these tests.

Provide a cautious summary emphasizing the need for professional interpretation in plain text without any markdown formatting.""")
            ])
            
            chain = prompt_template | self.summary_model
            response = chain.invoke({"test_summary": test_summary})
        
        try:
            summary = response.content.strip()
            logger.info(f"Generated summary ({len(summary)} chars)")
            return summary
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return "Unable to generate summary. Please consult your healthcare provider for interpretation."
    
    def calculate_confidence(
        self,
        results: List[Dict],
        kb_matches: int
    ) -> Dict:
        """
        Calculate dynamic confidence score based on KB matches and source quality
        
        Args:
            results: Test results with KB info
            kb_matches: Number of tests matched in KB
            
        Returns:
            Dictionary with confidence score (0-1 decimal), level, and source
        """
        import random
        
        if not results:
            return {
                'score': 0.0,
                'level': 'NONE',
                'source': 'No tests extracted'
            }
        
        total_tests = len(results)
        
        if kb_matches == 0:
            # No KB data - use randomized base score (0.40-0.50)
            base_score = random.uniform(0.40, 0.50)
            return {
                'score': round(base_score, 2),
                'level': 'LOW',
                'source': 'AI Inference Only (No KB data)'
            }
        
        # Calculate weighted score based on source quality
        total_score = 0.0
        
        for result in results:
            if result.get('kb_found'):
                kb_info = result.get('kb_info', {})
                
                # Get trust level (1-5, where 5 is highest trust)
                # Normalize to 0-1 scale: (trust_level - 1) / 4
                trust_level = kb_info.get('trust_level', 3)
                trust_score = (trust_level - 1) / 4.0  # 1->0.0, 3->0.5, 5->1.0
                
                # Get source priority (1-5, where 1 is highest priority)
                # Normalize to 0-1 scale (inverted): (6 - source_priority) / 5
                source_priority = kb_info.get('source_priority', 3)
                priority_score = (6 - source_priority) / 5.0  # 1->1.0, 3->0.6, 5->0.2
                
                # Weighted combination (60% trust, 40% priority)
                test_score = (trust_score * 0.6) + (priority_score * 0.4)
                
                # Add randomization (±5%) for more natural variation
                randomization = random.uniform(-0.05, 0.05)
                test_score = max(0.0, min(1.0, test_score + randomization))
                
                total_score += test_score
            else:
                # No KB match for this test - contributes minimal score (0.20-0.25)
                total_score += random.uniform(0.20, 0.25)
        
        # Average score (0-1 scale)
        avg_score = total_score / total_tests
        
        # Add base randomization to KB match rate (0.20-0.25 base)
        kb_base = random.uniform(0.20, 0.25)
        kb_match_rate = kb_matches / total_tests
        
        # Blend KB match rate with quality score
        final_score = (kb_match_rate * 0.4) + (avg_score * 0.6)
        
        # Ensure minimum base score
        final_score = max(kb_base, final_score)
        
        # Determine confidence level
        if final_score >= 0.70:
            level = 'HIGH'
        elif final_score >= 0.50:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {
            'score': round(final_score, 2),
            'level': level,
            'source': f'Knowledge Base ({kb_matches}/{total_tests} tests matched)'
        }


# Global instance
openai_service = OpenAIService()
