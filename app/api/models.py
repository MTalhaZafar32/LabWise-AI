"""
API request and response models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    ollama_available: bool

class TestResult(BaseModel):
    """Individual test result"""
    test_name: str
    value: float
    unit: str
    classification: str
    reference_range: str
    ai_explanation: str
    kb_found: bool
    canonical_name: Optional[str] = ""
    panel_name: Optional[str] = ""

class AnalysisResponse(BaseModel):
    """Lab report analysis response"""
    success: bool
    summary: Optional[Dict[str, Any]] = None
    confidence: Optional[Dict[str, Any]] = None
    tests: Optional[List[TestResult]] = None
    disclaimer: Optional[str] = None
    raw_ocr_text: Optional[str] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_type: Optional[str] = None
