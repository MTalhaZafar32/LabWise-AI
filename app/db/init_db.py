"""
Initialize database with knowledge base data from CSV files
"""
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.db.models import Base, Test, Source, Range, Synonym
from app.utils.config import settings

def load_csv_data():
    """Load knowledge base CSV files into database"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already loaded
        if db.query(Test).count() > 0:
            print("Database already initialized. Skipping...")
            return
        
        kb_path = settings.KB_DATA_PATH
        
        # Load sources
        print("Loading sources...")
        sources_df = pd.read_csv(kb_path / "LabWise AI KB - sources.csv")
        for _, row in sources_df.iterrows():
            source = Source(
                source_id=row['source_id'],
                name=row['name'],
                type=row['type'],
                url=row.get('url', ''),
                year=int(row['year']) if pd.notna(row.get('year')) else None,
                trust_level=int(row['trust_level']) if pd.notna(row.get('trust_level')) else 3
            )
            db.add(source)
        db.commit()
        print(f"Loaded {len(sources_df)} sources")
        
        # Load tests
        print("Loading tests...")
        tests_df = pd.read_csv(kb_path / "LabWise AI KB - tests.csv")
        for _, row in tests_df.iterrows():
            test = Test(
                test_id=row['test_id'],
                canonical_name=row['canonical_name'],
                short_name=row.get('short_name', ''),
                panel_name=row.get('panel_name', ''),
                specimen_type=row.get('specimen_type', ''),
                category=row.get('category', ''),
                loinc_code=row.get('loinc_code', ''),
                description=row.get('description', '')
            )
            db.add(test)
        db.commit()
        print(f"Loaded {len(tests_df)} tests")
        
        # Create placeholder test for ranges with NA test_id
        PLACEHOLDER_TEST_ID = 999
        placeholder_exists = db.query(Test).filter(Test.test_id == PLACEHOLDER_TEST_ID).first()
        if not placeholder_exists:
            placeholder_test = Test(
                test_id=PLACEHOLDER_TEST_ID,
                canonical_name="Unassigned Test",
                short_name="Unassigned",
                description="Placeholder for reference ranges with missing test_id in source data"
            )
            db.add(placeholder_test)
            db.commit()
            print(f"Created placeholder test (test_id={PLACEHOLDER_TEST_ID})")
        
        # Helper functions to safely convert values
        def safe_float(value):
            """Safely convert value to float, returning None if conversion fails"""
            if pd.isna(value):
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        def safe_int(value, default=None):
            """Safely convert value to int, returning default if conversion fails"""
            if pd.isna(value):
                return default
            try:
                return int(float(value))  # Convert through float first to handle decimals
            except (ValueError, TypeError):
                return default
        
        # Load ranges
        print("Loading reference ranges...")
        ranges_df = pd.read_csv(kb_path / "LabWise AI KB - test_ranges.csv")
        placeholder_count = 0
        for _, row in ranges_df.iterrows():
            # Assign placeholder test_id for ranges with NA test_id
            if pd.isna(row.get('test_id')):
                test_id_value = PLACEHOLDER_TEST_ID
                placeholder_count += 1
            else:
                test_id_value = int(row['test_id'])
                
            range_obj = Range(
                test_id=test_id_value,
                source_id=row['source_id'],
                canonical_name=row.get('canonical_name', ''),
                unit=row.get('unit', ''),
                value_type=row.get('value_type', 'numeric'),
                ref_low=safe_float(row.get('ref_low')),
                ref_high=safe_float(row.get('ref_high')),
                ref_text=row.get('ref_text', ''),
                sex=row.get('sex', 'Any'),
                age_min=safe_float(row.get('age_min')),
                age_max=safe_float(row.get('age_max')),
                condition=row.get('condition', ''),
                source_priority=safe_int(row.get('source_priority'), 1),
                effective_year=safe_int(row.get('effective_year'))
            )
            db.add(range_obj)
        db.commit()
        print(f"Loaded {len(ranges_df)} reference ranges")
        if placeholder_count > 0:
            print(f"Assigned placeholder test_id to {placeholder_count} ranges with missing test_id")
        
        # Load synonyms
        print("Loading test synonyms...")
        synonyms_df = pd.read_csv(kb_path / "LabWise AI KB - test_synonyms.csv")
        for _, row in synonyms_df.iterrows():
            synonym = Synonym(
                synonym_id=row['synonym_id'],
                test_id=row['test_id'],
                synonym=row['synonym'],
                source_id=int(row['source_id']) if pd.notna(row.get('source_id')) else None
            )
            db.add(synonym)
        db.commit()
        print(f"Loaded {len(synonyms_df)} synonyms")
        
        print("\n=== Database initialization complete! ===")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_csv_data()
