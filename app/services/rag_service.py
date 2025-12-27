"""
RAG Service for knowledge base retrieval
"""
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.db.models import Test, Range, Synonym, Source
from app.utils.medical_utils import MedicalUtils
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """Service for retrieving information from knowledge base"""
    
    def __init__(self):
        self.medical_utils = MedicalUtils()
    
    def find_test(self, db: Session, test_name: str) -> Optional[Test]:
        """
        Find test in knowledge base by name or synonym
        
        Args:
            db: Database session
            test_name: Test name to search for
            
        Returns:
            Test object or None
        """
        # Normalize test name
        normalized = self.medical_utils.normalize_test_name(test_name)
        
        # Search by canonical name (case-insensitive)
        test = db.query(Test).filter(
            Test.canonical_name.ilike(f"%{normalized}%")
        ).first()
        
        if test:
            logger.info(f"Found test by canonical name: {test.canonical_name}")
            return test
        
        # Search by short name
        test = db.query(Test).filter(
            Test.short_name.ilike(f"%{normalized}%")
        ).first()
        
        if test:
            logger.info(f"Found test by short name: {test.canonical_name}")
            return test
        
        # Search by synonym
        synonym = db.query(Synonym).filter(
            Synonym.synonym.ilike(f"%{normalized}%")
        ).first()
        
        if synonym:
            test = db.query(Test).filter(Test.test_id == synonym.test_id).first()
            if test:
                logger.info(f"Found test by synonym: {test.canonical_name}")
                return test
        
        logger.warning(f"Test not found in KB: {test_name}")
        return None
    
    def get_reference_range(
        self,
        db: Session,
        test_id: int,
        sex: str = "Any",
        age: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Get reference range for a test
        
        Args:
            db: Database session
            test_id: Test ID
            sex: Patient sex (Male/Female/Any)
            age: Patient age in years
            
        Returns:
            Dictionary with reference range info or None
        """
        # Query ranges for this test
        query = db.query(Range).filter(Range.test_id == test_id)
        
        # Filter by sex
        query = query.filter(or_(Range.sex == sex, Range.sex == "Any"))
        
        # Filter by age if provided
        if age is not None:
            query = query.filter(
                or_(
                    Range.age_min.is_(None),
                    Range.age_min <= age
                )
            ).filter(
                or_(
                    Range.age_max.is_(None),
                    Range.age_max >= age
                )
            )
        
        # Order by source priority (lower is better) and trust level (higher is better)
        ranges = query.join(Source).order_by(
            Range.source_priority.asc(),
            Source.trust_level.desc()
        ).all()
        
        if not ranges:
            logger.warning(f"No reference range found for test_id: {test_id}")
            return None
        
        # Take the first (highest priority) range
        best_range = ranges[0]
        
        # Get source trust level
        source = db.query(Source).filter(Source.source_id == best_range.source_id).first()
        trust_level = source.trust_level if source else 3
        
        return {
            'ref_low': best_range.ref_low,
            'ref_high': best_range.ref_high,
            'ref_text': best_range.ref_text,
            'unit': best_range.unit,
            'value_type': best_range.value_type,
            'source_id': best_range.source_id,
            'source_priority': best_range.source_priority,
            'trust_level': trust_level,
            'sex': best_range.sex,
            'condition': best_range.condition
        }
    
    def get_test_info(self, db: Session, test_name: str) -> Optional[Dict]:
        """
        Get complete test information including reference range
        
        Args:
            db: Database session
            test_name: Test name
            
        Returns:
            Dictionary with test info and reference range or None
        """
        # Find test
        test = self.find_test(db, test_name)
        if not test:
            return None
        
        # Get reference range
        ref_range = self.get_reference_range(db, test.test_id)
        
        # Extract trust level and source priority for confidence calculation
        trust_level = ref_range.get('trust_level', 3) if ref_range else 3
        source_priority = ref_range.get('source_priority', 3) if ref_range else 3
        
        return {
            'test_id': test.test_id,
            'canonical_name': test.canonical_name,
            'short_name': test.short_name,
            'panel_name': test.panel_name,
            'category': test.category,
            'description': test.description,
            'reference_range': ref_range,
            'trust_level': trust_level,
            'source_priority': source_priority,
            'kb_found': True
        }
    
    def get_all_test_names(self, db: Session) -> List[str]:
        """
        Get list of all standard test names from KB
        Used for helping LLM extraction
        """
        try:
            tests = db.query(Test.canonical_name).all()
            return [t[0] for t in tests]
        except Exception as e:
            logger.error(f"Failed to fetch test names: {e}")
            return []

    def batch_lookup(self, db: Session, test_results: List[Dict]) -> List[Dict]:
        """
        Lookup multiple tests in knowledge base
        
        Args:
            db: Database session
            test_results: List of parsed test results
            
        Returns:
            List of enriched test results with KB info
        """
        enriched_results = []
        
        for result in test_results:
            test_name = result.get('normalized_name') or result.get('test_name')
            
            # Get KB info
            kb_info = self.get_test_info(db, test_name)
            
            # Merge with parsed result
            enriched = {**result}
            
            if kb_info:
                enriched['kb_info'] = kb_info
                enriched['kb_found'] = True
            else:
                enriched['kb_found'] = False
            
            enriched_results.append(enriched)
        
        return enriched_results

# Global instance
rag_service = RAGService()
