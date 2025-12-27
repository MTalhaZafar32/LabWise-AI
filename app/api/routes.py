"""
API routes for LabWise AI
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.models import AnalysisResponse, HealthResponse, ErrorResponse, StatsResponse
from app.services.lab_service import lab_service
from app.services.stats_service import stats_service
from app.db.database import get_db
from app.utils.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.API_PREFIX)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_lab_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Analyze a lab report (PDF or image)
    
    Args:
        file: Uploaded lab report file
        db: Database session
        
    Returns:
        Analysis results with test classifications and explanations
    """
    try:
        logger.info(f"Received file: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        
        # Process the report
        result = await lab_service.process_report(
            filename=file.filename,
            file_content=file_content,
            db=db
        )
        
        return AnalysisResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the report: {str(e)}"
        )

@router.get("/stats", response_model=StatsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get knowledge base statistics
    
    Args:
        db: Database session
        
    Returns:
        Statistics about tests, sources, ranges, and distributions
    """
    try:
        stats = stats_service.get_statistics(db)
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching statistics: {str(e)}"
        )

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LabWise AI API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
