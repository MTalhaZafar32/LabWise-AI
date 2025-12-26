"""
Main Lab Service - Orchestrates the entire pipeline
"""
from typing import Dict, List
from sqlalchemy.orm import Session
from PIL import Image
import logging

from app.services.ocr_service import ocr_service
from app.services.parsing_service import parsing_service
from app.services.rag_service import rag_service
from app.services.classification_service import classification_service
from app.services.llm_service import llm_service
from app.utils.file_utils import FileUtils
from app.utils.config import settings

logger = logging.getLogger(__name__)

class LabService:
    """Main service for processing lab reports"""
    
    def __init__(self):
        self.file_utils = FileUtils()
    
    async def process_report(
        self,
        filename: str,
        file_content: bytes,
        db: Session
    ) -> Dict:
        """
        Process a lab report through the complete pipeline
        
        Args:
            filename: Name of uploaded file
            file_content: File content in bytes
            db: Database session
            
        Returns:
            Dictionary with processed results
        """
        logger.info(f"Processing lab report: {filename}")
        
        # Step 1: Validate file
        is_valid, error_msg = self.file_utils.validate_file(
            filename,
            file_content,
            settings.MAX_UPLOAD_SIZE
        )
        
        if not is_valid:
            raise ValueError(error_msg)
        
        # Step 2: Convert to images
        images = self._prepare_images(filename, file_content)
        logger.info(f"Prepared {len(images)} image(s) for processing")
        
        # Step 3: OCR Extraction
        ocr_text, ocr_confidence = self._extract_text(images)
        logger.info(f"OCR completed with confidence: {ocr_confidence:.2f}")
        
        # Step 4: Parse text to extract test results
        parsed_results = parsing_service.parse_lab_report(ocr_text)
        logger.info(f"Parsed {len(parsed_results)} test results")
        
        if not parsed_results:
            return {
                'success': False,
                'error': 'No test results could be extracted from the document',
                'ocr_confidence': ocr_confidence
            }
        
        # Step 5: RAG - Lookup in knowledge base
        enriched_results = rag_service.batch_lookup(db, parsed_results)
        logger.info("Knowledge base lookup completed")
        
        # Step 6: Rule-based classification
        classified_results = classification_service.classify_batch(enriched_results)
        logger.info("Classification completed")
        
        # Step 7: LLM explanation generation
        explained_results = llm_service.generate_batch_explanations(classified_results)
        logger.info("Explanation generation completed")
        
        # Step 8: Aggregate and format results
        final_results = self._format_results(
            explained_results,
            ocr_confidence,
            ocr_text
        )
        
        logger.info("Lab report processing completed successfully")
        return final_results
    
    def _prepare_images(self, filename: str, file_content: bytes) -> List[Image.Image]:
        """Convert file to list of images"""
        if self.file_utils.is_pdf(filename):
            # Convert PDF to images
            images = self.file_utils.pdf_to_images(file_content)
        else:
            # Load single image
            image = self.file_utils.bytes_to_image(file_content)
            images = [image]
        
        return images
    
    def _extract_text(self, images: List[Image.Image]) -> tuple:
        """Extract text from images using OCR"""
        if len(images) == 1:
            return ocr_service.extract_text(images[0])
        else:
            return ocr_service.extract_from_multiple_images(images)
    
    def _format_results(
        self,
        results: List[Dict],
        ocr_confidence: float,
        ocr_text: str
    ) -> Dict:
        """Format final results for API response"""
        
        # Calculate statistics
        total_tests = len(results)
        kb_found_count = sum(1 for r in results if r.get('kb_found'))
        
        # Categorize by classification
        low_count = sum(1 for r in results if r.get('classification') == 'LOW')
        normal_count = sum(1 for r in results if r.get('classification') == 'NORMAL')
        high_count = sum(1 for r in results if r.get('classification') == 'HIGH')
        unknown_count = sum(1 for r in results if r.get('classification') == 'UNKNOWN')
        
        # Format individual results
        formatted_tests = []
        for result in results:
            formatted_tests.append({
                'test_name': result.get('test_name'),
                'value': result.get('value'),
                'unit': result.get('unit'),
                'classification': result.get('classification'),
                'reference_range': result.get('reference_range', 'N/A'),
                'ai_explanation': result.get('ai_explanation', ''),
                'kb_found': result.get('kb_found', False),
                'canonical_name': result.get('kb_info', {}).get('canonical_name', ''),
                'panel_name': result.get('kb_info', {}).get('panel_name', '')
            })
        
        # Determine overall confidence level
        if ocr_confidence >= settings.CONFIDENCE_MEDIUM_THRESHOLD:
            confidence_level = 'HIGH'
        elif ocr_confidence >= settings.CONFIDENCE_LOW_THRESHOLD:
            confidence_level = 'MEDIUM'
        else:
            confidence_level = 'LOW'
        
        return {
            'success': True,
            'summary': {
                'total_tests': total_tests,
                'kb_matched': kb_found_count,
                'kb_match_rate': f"{(kb_found_count/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                'low_results': low_count,
                'normal_results': normal_count,
                'high_results': high_count,
                'unknown_results': unknown_count
            },
            'confidence': {
                'ocr_confidence': round(ocr_confidence, 2),
                'confidence_level': confidence_level
            },
            'tests': formatted_tests,
            'disclaimer': (
                "⚠️ MEDICAL DISCLAIMER: This analysis is for informational purposes only. "
                "It does NOT constitute medical advice, diagnosis, or treatment. "
                "Always consult a qualified healthcare professional for medical decisions."
            ),
            'raw_ocr_text': ocr_text if settings.DEBUG else None
        }

# Global instance
lab_service = LabService()
