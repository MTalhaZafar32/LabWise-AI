"""
Database models for LabWise AI Knowledge Base
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Test(Base):
    """Master test catalog"""
    __tablename__ = "tests"
    
    test_id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String, nullable=False, index=True)
    short_name = Column(String)
    panel_name = Column(String)
    specimen_type = Column(String)
    category = Column(String)
    loinc_code = Column(String)
    description = Column(Text)
    
    # Relationships
    ranges = relationship("Range", back_populates="test")
    synonyms = relationship("Synonym", back_populates="test")

class Source(Base):
    """Reference sources and trust levels"""
    __tablename__ = "sources"
    
    source_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    url = Column(String)
    year = Column(Integer)
    trust_level = Column(Integer)
    
    # Relationships
    ranges = relationship("Range", back_populates="source")

class Range(Base):
    """Reference ranges for tests"""
    __tablename__ = "ranges"
    
    range_id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.test_id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.source_id"), nullable=False)
    canonical_name = Column(String)
    unit = Column(String)
    value_type = Column(String)
    ref_low = Column(Float)
    ref_high = Column(Float)
    ref_text = Column(String)
    sex = Column(String)
    age_min = Column(Float)
    age_max = Column(Float)
    condition = Column(String)
    source_priority = Column(Integer)
    effective_year = Column(Integer)
    
    # Relationships
    test = relationship("Test", back_populates="ranges")
    source = relationship("Source", back_populates="ranges")

class Synonym(Base):
    """Test name synonyms and aliases"""
    __tablename__ = "synonyms"
    
    synonym_id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.test_id"), nullable=False, index=True)
    synonym = Column(String, nullable=False, index=True)
    source_id = Column(Integer)
    
    # Relationships
    test = relationship("Test", back_populates="synonyms")
