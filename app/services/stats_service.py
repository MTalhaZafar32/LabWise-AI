"""
Statistics Service - Query knowledge base metrics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Test, Source, Range, Synonym
import logging

logger = logging.getLogger(__name__)

class StatsService:
    """Service for querying knowledge base statistics"""
    
    def get_statistics(self, db: Session) -> dict:
        """
        Get comprehensive statistics about the knowledge base
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with all statistics
        """
        try:
            # Total counts
            total_tests = db.query(func.count(Test.test_id)).scalar()
            total_sources = db.query(func.count(Source.source_id)).scalar()
            total_ranges = db.query(func.count(Range.range_id)).scalar()
            total_synonyms = db.query(func.count(Synonym.synonym_id)).scalar()
            
            # Test distribution by category
            category_dist = db.query(
                Test.category,
                func.count(Test.test_id).label('count')
            ).filter(
                Test.category.isnot(None),
                Test.category != ''
            ).group_by(Test.category).all()
            
            # Test distribution by panel
            panel_dist = db.query(
                Test.panel_name,
                func.count(Test.test_id).label('count')
            ).filter(
                Test.panel_name.isnot(None),
                Test.panel_name != ''
            ).group_by(Test.panel_name).order_by(func.count(Test.test_id).desc()).limit(10).all()
            
            # Source distribution by type
            source_type_dist = db.query(
                Source.type,
                func.count(Source.source_id).label('count')
            ).filter(
                Source.type.isnot(None),
                Source.type != ''
            ).group_by(Source.type).all()
            
            # Top sources by range count
            top_sources = db.query(
                Source.name,
                Source.type,
                func.count(Range.range_id).label('range_count')
            ).join(Range, Source.source_id == Range.source_id)\
             .group_by(Source.source_id, Source.name, Source.type)\
             .order_by(func.count(Range.range_id).desc())\
             .limit(10).all()
            
            # Range distribution by sex
            sex_dist = db.query(
                Range.sex,
                func.count(Range.range_id).label('count')
            ).filter(
                Range.sex.isnot(None),
                Range.sex != ''
            ).group_by(Range.sex).all()
            
            # Specimen type distribution
            specimen_dist = db.query(
                Test.specimen_type,
                func.count(Test.test_id).label('count')
            ).filter(
                Test.specimen_type.isnot(None),
                Test.specimen_type != ''
            ).group_by(Test.specimen_type).all()
            
            # Average synonyms per test
            avg_synonyms = db.query(
                func.avg(
                    db.query(func.count(Synonym.synonym_id))
                    .filter(Synonym.test_id == Test.test_id)
                    .correlate(Test)
                    .scalar_subquery()
                )
            ).scalar() or 0
            
            # Tests with LOINC codes
            tests_with_loinc = db.query(func.count(Test.test_id)).filter(
                Test.loinc_code.isnot(None),
                Test.loinc_code != ''
            ).scalar()
            
            return {
                'overview': {
                    'total_tests': total_tests,
                    'total_sources': total_sources,
                    'total_ranges': total_ranges,
                    'total_synonyms': total_synonyms,
                    'avg_synonyms_per_test': round(avg_synonyms, 2),
                    'tests_with_loinc': tests_with_loinc,
                    'loinc_coverage': round((tests_with_loinc / total_tests * 100), 1) if total_tests > 0 else 0
                },
                'distributions': {
                    'by_category': [
                        {'name': cat or 'Unknown', 'count': count}
                        for cat, count in category_dist
                    ],
                    'by_panel': [
                        {'name': panel or 'Unknown', 'count': count}
                        for panel, count in panel_dist
                    ],
                    'by_source_type': [
                        {'name': stype or 'Unknown', 'count': count}
                        for stype, count in source_type_dist
                    ],
                    'by_sex': [
                        {'name': sex or 'Unspecified', 'count': count}
                        for sex, count in sex_dist
                    ],
                    'by_specimen': [
                        {'name': spec or 'Unknown', 'count': count}
                        for spec, count in specimen_dist
                    ]
                },
                'top_sources': [
                    {
                        'name': name,
                        'type': stype or 'Unknown',
                        'range_count': count
                    }
                    for name, stype, count in top_sources
                ]
            }
            
        except Exception as e:
            logger.error(f"Error fetching statistics: {str(e)}", exc_info=True)
            raise

# Global instance
stats_service = StatsService()
