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
        
        # Load ranges
        print("Loading reference ranges...")
        ranges_df = pd.read_csv(kb_path / "LabWise AI KB - test_ranges.csv")
        for _, row in ranges_df.iterrows():
            range_obj = Range(
                range_id=row['range_id'],
                test_id=row['test_id'],
                source_id=row['source_id'],
                canonical_name=row.get('canonical_name', ''),
                unit=row.get('unit', ''),
                value_type=row.get('value_type', 'numeric'),
                ref_low=float(row['ref_low']) if pd.notna(row.get('ref_low')) else None,
                ref_high=float(row['ref_high']) if pd.notna(row.get('ref_high')) else None,
                ref_text=row.get('ref_text', ''),
                sex=row.get('sex', 'Any'),
                age_min=float(row['age_min']) if pd.notna(row.get('age_min')) else None,
                age_max=float(row['age_max']) if pd.notna(row.get('age_max')) else None,
                condition=row.get('condition', ''),
                source_priority=int(row['source_priority']) if pd.notna(row.get('source_priority')) else 1,
                effective_year=int(row['effective_year']) if pd.notna(row.get('effective_year')) else None
            )
            db.add(range_obj)
        db.commit()
        print(f"Loaded {len(ranges_df)} reference ranges")
        
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
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_csv_data()
