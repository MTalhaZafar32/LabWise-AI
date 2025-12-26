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
            lang='en'
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
        
        # Convert back to BGR for compatibility with PaddleOCR
        bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        return bgr
    
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
            
            logger.info("Starting OCR processing...")
            try:
                # Perform OCR
                result = self.ocr.ocr(processed_img)
            except Exception as ocr_err:
                logger.error(f"Internal PaddleOCR error: {str(ocr_err)}")
                # Try with original image if preprocessing fails
                logger.info("Retrying with original image...")
                result = self.ocr.ocr(np.array(image))

            # Debug logs to inspect structure
            logger.info(f"OCR Result type: {type(result)}")
            logger.info(f"OCR Result: {result}")
            
            if not result:
                logger.warning("No text detected (empty result)")
                return "", 0.0

            # Handle different result structures
            # PaddleOCR sometimes returns [None] or just None if no text found
            if result[0] is None:
                 logger.warning("No text detected (result[0] is None)")
                 return "", 0.0
            
            # Extract text and confidence scores
            lines = []
            confidences = []
            
            # Iterate through the first element if it's a list (standard structure)
            # Structure usually: [ [[box], (text, score)], ... ]
            ocr_data = result[0] if isinstance(result, list) and len(result) > 0 else result
            
            if not isinstance(ocr_data, list):
                logger.warning(f"Unexpected OCR result format: {type(ocr_data)}")
                return "", 0.0

            for line in ocr_data:
                # Debug line structure
                # logger.info(f"Line data: {line}") 
                pass
            
            for line in ocr_data:
                try:
                    # Expected: line = [box, (text, score)]
                    # box = [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    # text_info = ('text', 0.99)
                    
                    if len(line) >= 2 and isinstance(line[1], (list, tuple)):
                        text = line[1][0]
                        confidence = line[1][1]
                        lines.append(text)
                        confidences.append(confidence)
                    else:
                        logger.warning(f"Unexpected item format in OCR result: {line}")
                except Exception as loop_err:
                     logger.warning(f"Error parsing line: {line} - {loop_err}")
                     continue
            
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
