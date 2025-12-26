"""
File handling utilities for PDF and image processing
"""
from pathlib import Path
from typing import List, Tuple
import tempfile
from pdf2image import convert_from_bytes
from PIL import Image
import io

class FileUtils:
    """Utilities for file handling and conversion"""
    
    @staticmethod
    def validate_file(filename: str, content: bytes, max_size: int) -> Tuple[bool, str]:
        """
        Validate uploaded file
        
        Args:
            filename: Name of the file
            content: File content in bytes
            max_size: Maximum allowed file size
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(content) > max_size:
            return False, f"File size exceeds maximum allowed size of {max_size / (1024*1024):.1f}MB"
        
        # Check file extension
        ext = Path(filename).suffix.lower()
        allowed = {'.pdf', '.png', '.jpg', '.jpeg'}
        if ext not in allowed:
            return False, f"File type {ext} not allowed. Allowed types: {', '.join(allowed)}"
        
        return True, ""
    
    @staticmethod
    def pdf_to_images(pdf_bytes: bytes, dpi: int = 300) -> List[Image.Image]:
        """
        Convert PDF to list of PIL Images
        
        Args:
            pdf_bytes: PDF file content
            dpi: Resolution for conversion
            
        Returns:
            List of PIL Image objects
        """
        try:
            # Specify poppler path for Windows
            poppler_path = r"C:\poppler\poppler-24.08.0\Library\bin"
            images = convert_from_bytes(
                pdf_bytes, 
                dpi=dpi,
                poppler_path=poppler_path
            )
            return images
        except Exception as e:
            raise ValueError(f"Failed to convert PDF to images: {str(e)}")
    
    @staticmethod
    def bytes_to_image(image_bytes: bytes) -> Image.Image:
        """
        Convert bytes to PIL Image
        
        Args:
            image_bytes: Image file content
            
        Returns:
            PIL Image object
        """
        try:
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"Failed to load image: {str(e)}")
    
    @staticmethod
    def is_pdf(filename: str) -> bool:
        """Check if file is PDF"""
        return Path(filename).suffix.lower() == '.pdf'
    
    @staticmethod
    def save_temp_image(image: Image.Image) -> str:
        """
        Save PIL Image to temporary file
        
        Args:
            image: PIL Image object
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_file.name)
        return temp_file.name
