# LabWise AI - System Architecture

## Overview

LabWise AI is a medical lab report interpretation system that combines OCR, AI-powered analysis, and a comprehensive knowledge base to provide accurate, confidence-scored interpretations of laboratory test results.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (React + Vite Frontend)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                               │
│                      (FastAPI Backend)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   /analyze   │  │   /health    │  │    /stats    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING PIPELINE                          │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │   OCR    │──▶│   LLM    │──▶│   RAG    │──▶│  Class.  │   │
│  │ EasyOCR  │   │  OpenAI  │   │    KB    │   │  Rules   │   │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   │
│                                                                 │
│                         ┌──────────┐                           │
│                         │   LLM    │                           │
│                         │ Summary  │                           │
│                         └──────────┘                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              SQLite Knowledge Base                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │  Tests   │  │  Ranges  │  │ Synonyms │  │ Sources  │ │  │
│  │  │  1000+   │  │  10000+  │  │  5000+   │  │   50+    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI 0.109 | REST API, async support |
| **Server** | Uvicorn | ASGI server |
| **Database** | SQLite + SQLAlchemy | Knowledge base storage |
| **OCR** | EasyOCR 1.7 | Text extraction from images/PDFs |
| **LLM** | OpenAI GPT-4o-mini | Data extraction & summarization |
| **LLM Framework** | Langchain | LLM integration |
| **PDF Processing** | pdf2image + Pillow | PDF to image conversion |
| **Image Processing** | OpenCV | Image preprocessing |
| **Data Processing** | Pandas + NumPy | Data manipulation |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | React 18 | UI components |
| **Build Tool** | Vite | Fast development & bundling |
| **Styling** | Vanilla CSS | Custom styling |
| **HTTP Client** | Axios | API communication |

---

## Core Services

### 1. OCR Service (`ocr_service.py`)

**Purpose**: Extract text from uploaded PDF/image files

**Technology**: EasyOCR

**Process**:
1. Convert PDF to images (if needed)
2. Preprocess images (resize, enhance)
3. Run EasyOCR text detection
4. Calculate confidence score
5. Return extracted text + confidence

**Output**:
```python
{
    "text": "COMPLETE BLOOD COUNT\nWBC: 7.5...",
    "confidence": 0.91
}
```

---

### 2. Parsing Service (`parsing_service.py`)

**Purpose**: Extract structured test data from OCR text

**Technology**: OpenAI GPT-4o-mini via Langchain

**Process**:
1. Receive OCR text + KB test names
2. Send to OpenAI with structured extraction prompt
3. LLM identifies test names, values, units, ranges
4. Parse JSON response
5. Return structured test list

**Input Prompt**:
```
Extract lab tests from this OCR text:
- Test name, value, unit, reference range
- Map to standard names if possible: [Hemoglobin, WBC, RBC...]
- Return JSON array
```

**Output**:
```python
[
    {
        "test_name": "Hemoglobin",
        "value": 14.5,
        "unit": "g/dL",
        "reference_range": "13.5-17.5"
    },
    ...
]
```

---

### 3. RAG Service (`rag_service.py`)

**Purpose**: Retrieve reference ranges from knowledge base

**Technology**: SQLAlchemy + SQLite

**Process**:
1. Normalize test name
2. Search KB by canonical name, short name, or synonym
3. Retrieve best reference range (by source priority & trust level)
4. Return KB info with trust_level and source_priority

**Search Strategy**:
```python
1. Exact match on canonical_name
2. Fuzzy match on short_name
3. Synonym lookup
4. Return None if not found
```

**Output**:
```python
{
    "test_id": 123,
    "canonical_name": "Hemoglobin A1c",
    "reference_range": {
        "ref_low": 4.0,
        "ref_high": 5.6,
        "unit": "%",
        "trust_level": 5,
        "source_priority": 1
    },
    "kb_found": True
}
```

---

### 4. Classification Service (`classification_service.py`)

**Purpose**: Classify test results as LOW/NORMAL/HIGH

**Technology**: Rule-based logic

**Process**:
1. Check if KB reference range exists
2. Compare value to ref_low and ref_high
3. Assign classification
4. Return enriched result

**Classification Logic**:
```python
if value < ref_low:
    classification = "LOW"
elif value > ref_high:
    classification = "HIGH"
else:
    classification = "NORMAL"
```

**Output**:
```python
{
    "test_name": "Hemoglobin",
    "value": 14.5,
    "unit": "g/dL",
    "classification": "NORMAL",
    "reference_range": "13.5-17.5",
    "kb_found": True
}
```

---

### 5. OpenAI Service (`openai_service.py`)

**Purpose**: LLM-powered extraction and summarization

**Technology**: OpenAI GPT-4o-mini via Langchain

**Functions**:

#### A. Data Extraction
- Extract structured test data from OCR text
- Map to standard test names using KB guidance
- Return JSON array of tests

#### B. Summary Generation
- Generate patient-friendly summary
- Two modes:
  - **With KB data**: Comprehensive summary with classifications
  - **Without KB data**: Cautious summary emphasizing professional review
- Plain text output (no markdown)

#### C. Confidence Calculation
- **With KB matches**: 
  - Calculate from trust_level (1-5) and source_priority (1-5)
  - Normalize to 0-1 scale
  - Add randomization (±5%)
  - Blend KB match rate with quality score
- **Without KB matches**:
  - Randomized base score (0.40-0.50)

**Confidence Formula**:
```python
# Normalize trust level (1-5 → 0-1)
trust_score = (trust_level - 1) / 4.0

# Normalize source priority (1-5 → 0-1, inverted)
priority_score = (6 - source_priority) / 5.0

# Weighted combination
test_score = (trust_score * 0.6) + (priority_score * 0.4)

# Add randomization
test_score += random.uniform(-0.05, 0.05)

# Final score
final_score = (kb_match_rate * 0.4) + (avg_score * 0.6)
final_score = max(0.20, final_score)  # Minimum 20%
```

---

### 6. Lab Service (`lab_service.py`)

**Purpose**: Orchestrate the entire processing pipeline

**Process**:
```
1. Validate file (size, format)
2. Convert PDF to images
3. Extract text via OCR
4. Parse text via LLM
5. Lookup tests in KB (RAG)
6. Classify results
7. Generate summary via LLM
8. Calculate confidence
9. Format and return results
```

**Pipeline Timing** (typical):
- Validation: <0.01s
- Image preparation: 2-5s
- OCR: 60-80s (first run), 20-30s (cached)
- Parsing: 3-7s
- RAG lookup: <0.1s
- Classification: <0.01s
- Summarization: 3-6s
- **Total**: ~70-90s (first run), ~30-45s (subsequent)

---

### 7. Stats Service (`stats_service.py`)

**Purpose**: Generate knowledge base statistics

**Metrics**:
- Total tests, sources, ranges, synonyms
- Distribution by category, panel, source type
- Top sources by range count
- LOINC coverage percentage
- Average synonyms per test

---

## Database Schema

### Tables

#### 1. `tests`
```sql
test_id          INTEGER PRIMARY KEY
canonical_name   STRING (indexed)
short_name       STRING
panel_name       STRING
specimen_type    STRING
category         STRING
loinc_code       STRING
description      TEXT
```

#### 2. `sources`
```sql
source_id     INTEGER PRIMARY KEY
name          STRING
type          STRING
url           STRING
year          INTEGER
trust_level   INTEGER  -- 1-5 (5 = highest trust)
```

#### 3. `ranges`
```sql
range_id         INTEGER PRIMARY KEY
test_id          INTEGER (FK → tests)
source_id        INTEGER (FK → sources)
canonical_name   STRING
unit             STRING
value_type       STRING
ref_low          FLOAT
ref_high         FLOAT
ref_text         STRING
sex              STRING
age_min          FLOAT
age_max          FLOAT
condition        STRING
source_priority  INTEGER  -- 1-5 (1 = highest priority)
effective_year   INTEGER
```

#### 4. `synonyms`
```sql
synonym_id   INTEGER PRIMARY KEY
test_id      INTEGER (FK → tests)
synonym      STRING (indexed)
source_id    INTEGER
```

---

## API Endpoints

### 1. `GET /api/health`

**Purpose**: Health check

**Response**:
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

---

### 2. `POST /api/analyze`

**Purpose**: Analyze lab report

**Request**:
```
Content-Type: multipart/form-data
file: <PDF or image file>
```

**Response**:
```json
{
    "success": true,
    "summary": {
        "total_tests": 4,
        "kb_matched": 1,
        "kb_match_rate": "25.0%",
        "low_results": 0,
        "normal_results": 1,
        "high_results": 0,
        "unknown_results": 3
    },
    "overall_summary": "Your lab results show...",
    "confidence": {
        "ocr_confidence": 0.91,
        "ocr_level": "HIGH",
        "response_confidence": 0.32,
        "response_level": "LOW",
        "confidence_source": "Knowledge Base (1/4 tests matched)"
    },
    "tests": [
        {
            "test_name": "Hemoglobin",
            "value": 14.5,
            "unit": "g/dL",
            "classification": "NORMAL",
            "reference_range": "13.5-17.5",
            "ai_explanation": "",
            "kb_found": true,
            "canonical_name": "Hemoglobin A1c",
            "panel_name": "Complete Blood Count"
        }
    ],
    "disclaimer": "⚠️ MEDICAL DISCLAIMER: ..."
}
```

---

### 3. `GET /api/stats`

**Purpose**: Get KB statistics

**Response**:
```json
{
    "overview": {
        "total_tests": 1043,
        "total_sources": 52,
        "total_ranges": 10234,
        "total_synonyms": 5123,
        "loinc_coverage": "45.2%",
        "avg_synonyms_per_test": 4.9
    },
    "distributions": {
        "by_category": [...],
        "by_panel": [...],
        "by_source_type": [...]
    },
    "top_sources": [...]
}
```

---

## Data Flow

### Complete Analysis Flow

```
1. User uploads PDF/image
   ↓
2. Frontend sends to /api/analyze
   ↓
3. Backend validates file
   ↓
4. OCR Service extracts text
   ↓
5. Parsing Service (OpenAI) extracts structured data
   ↓
6. RAG Service looks up each test in KB
   ↓
7. Classification Service classifies results
   ↓
8. OpenAI Service generates summary
   ↓
9. OpenAI Service calculates confidence
   ↓
10. Lab Service formats response
   ↓
11. Frontend displays results
```

---

## Configuration

### Environment Variables

```env
# OpenAI
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://models.inference.ai.azure.com
OPENAI_EXTRACTION_MODEL=gpt-4o-mini
OPENAI_SUMMARY_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# Application
APP_VERSION=1.0.0
DEBUG=False
MAX_UPLOAD_SIZE=10485760

# Database
DATABASE_URL=sqlite:///./data/labwise.db

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Confidence Thresholds
CONFIDENCE_LOW_THRESHOLD=0.5
CONFIDENCE_MEDIUM_THRESHOLD=0.7
```

---

## Security Considerations

1. **File Upload**: Size limits, type validation
2. **API Keys**: Stored in .env, never committed
3. **CORS**: Restricted to specific origins
4. **Input Validation**: Pydantic models
5. **Error Handling**: Generic error messages to users
6. **Medical Disclaimer**: Always included in responses

---

## Performance Optimization

1. **OCR Caching**: EasyOCR models cached after first load
2. **Database Indexing**: Indexed on test names and synonyms
3. **Async Processing**: FastAPI async endpoints
4. **Connection Pooling**: SQLAlchemy connection management
5. **Frontend Bundling**: Vite optimization

---

## Future Enhancements

1. **Multi-page PDF Support**: Process multi-page reports
2. **Batch Processing**: Analyze multiple reports
3. **Export Options**: PDF, CSV export of results
4. **User Accounts**: Save analysis history
5. **Advanced Visualizations**: Trend charts, comparisons
6. **Mobile App**: React Native version
7. **Offline Mode**: Fully offline LLM option

---

## Deployment

### Docker Deployment

```bash
docker-compose up -d
```

### Manual Deployment

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
npm run preview
```

---

## Monitoring & Logging

- **Logging**: Python logging module
- **Log Levels**: INFO, WARNING, ERROR
- **Log Files**: Console output (can be redirected)
- **Metrics**: Processing time per step

---

**Last Updated**: 2025-12-27
**Version**: 1.0.0
