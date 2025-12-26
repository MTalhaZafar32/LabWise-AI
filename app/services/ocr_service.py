"""
OCR Service for text extraction from images
"""
from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """Service for OCR text extraction"""
    
    def __init__(self):
        """Initialize PaddleOCR"""
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='en',
            use_gpu=settings.USE_GPU,
            show_log=False
        )
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image as numpy array
        """
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def extract_text(self, image: Image.Image) -> Tuple[str, float]:
        """
        Extract text from image using OCR
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (extracted_text, average_confidence)
        """
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image)
            
            # Perform OCR
            result = self.ocr.ocr(processed_img, cls=True)
            
            if not result or not result[0]:
                logger.warning("No text detected in image")
                return "", 0.0
            
            # Extract text and confidence scores
            lines = []
            confidences = []
            
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                lines.append(text)
                confidences.append(confidence)
            
            # Combine text
            full_text = '\n'.join(lines)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            logger.info(f"OCR extracted {len(lines)} lines with avg confidence: {avg_confidence:.2f}")
            
            return full_text, avg_confidence
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise ValueError(f"OCR extraction failed: {str(e)}")
    
    def extract_from_multiple_images(self, images: List[Image.Image]) -> Tuple[str, float]:
        """
        Extract text from multiple images (e.g., PDF pages)
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Tuple of (combined_text, average_confidence)
        """
        all_text = []
        all_confidences = []
        
        for i, image in enumerate(images):
            logger.info(f"Processing image {i+1}/{len(images)}")
            text, confidence = self.extract_text(image)
            all_text.append(text)
            all_confidences.append(confidence)
        
        combined_text = '\n\n'.join(all_text)
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        return combined_text, avg_confidence

# Global instance
ocr_service = OCRService()
