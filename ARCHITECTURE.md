# LabWise AI  
## An Autonomous Medical Lab Report Interpretation Agent  
**End-to-End Technical Documentation (GenAI + AI Agents)**

---

## 1. Introduction

LabWise AI is an **offline, privacy-preserving, autonomous AI agent system** designed to interpret medical laboratory reports (PDF or images) and generate **human-readable explanations** for non-technical users.

The system integrates:
- OCR
- Rule-based medical logic
- Retrieval-Augmented Generation (RAG)
- Local Generative AI
- Agent-based orchestration

This document explains **every architectural layer, workflow, decision, and implementation responsibility in depth**, following **industry standards**.

---

## 2. Design Goals

- Offline-first (no cloud dependency)
- Privacy-safe (medical data never leaves the device)
- Deterministic medical reasoning
- Transparent confidence & knowledge usage
- Modular & replaceable components
- Industry-grade backend & frontend separation

---

## 3. High-Level System Overview

LabWise AI transforms **raw lab reports** into **clear health explanations** through a **multi-stage AI agent pipeline**.

### Supported Inputs
- PDF lab reports
- Image-based lab reports (`.png`, `.jpg`, `.jpeg`)

### Final Outputs
- Structured lab result table
- LOW / NORMAL / HIGH classification
- AI-generated explanation
- Confidence score
- Knowledge Base usage indicator
- Medical safety disclaimer

---

## 4. High-Level Architecture

```
User (React UI)
↓
FastAPI Backend
↓
Agent-Orchestrated Pipeline
↓
OCR → Parsing → KB Lookup → Classification → LLM Explanation
↓
Structured + Explained Medical Report
```

The system is **agent-driven**, meaning each step is planned, validated, and executed autonomously.

---

## 5. Three-Layer Backend Architecture

### 5.1 API Layer (FastAPI)

**Purpose:**  
Expose REST endpoints only.  
❌ No business logic  
❌ No OCR  
❌ No LLM calls  

Example:
```python
@router.post("/analyze")
def analyze_lab_report(file: UploadFile):
    return lab_service.process_report(file)
```

---

### 5.2 Service Layer (Business & AI Logic)

**Purpose:**
Contains **all application logic**.

Responsibilities:

* OCR execution
* Parsing
* Classification
* RAG retrieval
* LLM prompting
* Confidence scoring

Example flow:

```python
def process_report(file):
    text, conf = ocr_service.extract_text(file)
    structured = parsing_service.parse(text)
    classified = classification_service.classify(structured)
    explanation = explanation_service.generate(classified)
    return explanation
```

---

### 5.3 Core / Infrastructure Layer

**Purpose:**
Implements reusable, replaceable system components.

Includes:

* OCR engines
* LLM clients
* Databases
* RAG retrievers
* Agent planners

---

## 6. Complete Backend Folder Structure

```
labwise-ai/
├── app/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── agents/
│   ├── models/
│   ├── db/
│   ├── rag/
│   ├── llm/
│   ├── ocr/
│   └── utils/
├── data/
│   └── labqar/
├── tests/
└── docker-compose.yml
```

Each folder has **one responsibility only**, following Clean Architecture.

---

## 7. End-to-End Processing Pipeline (Detailed)

### Step 1: File Upload (React UI)

* User uploads PDF or image
* Client-side validation (type, size)
* File sent to FastAPI via multipart/form-data

---

### Step 2: File Validation (Backend)

* MIME type validation
* File integrity check
* Unsupported formats rejected

---

### Step 3: PDF to Image Conversion (If PDF)

**Why:** OCR performs better on images.

Process:

* Convert each PDF page → image
* Normalize resolution
* Temporary in-memory storage

---

### Step 4: Image Preprocessing

Using OpenCV:

* Grayscale conversion
* Noise removal
* Contrast enhancement
* Table boundary improvement

Goal: maximize OCR accuracy.

---

### Step 5: OCR Extraction + Confidence Scoring

**Tool:** PaddleOCR (CPU)

Output:

```json
{
  "text": "Hemoglobin 11.2 g/dL",
  "confidence": 0.92
}
```

* Average confidence computed
* If below threshold → retry or warn user

---

### Step 6: Parsing & Normalization

Extracts:

* Test name
* Numeric value
* Unit

Techniques:

* Regex rules
* Medical synonym mapping
* Unit normalization

Example:

```json
{
  "test_name": "Hemoglobin",
  "value": 11.2,
  "unit": "g/dL"
}
```

---

### Step 7: Knowledge Base Lookup (RAG)

**Storage:** SQLite
**Source:** LabQAR dataset + curated medical references

Decision logic:

```
IF test found in KB:
    use verified reference range
    kb_used = true
ELSE:
    kb_used = false
    safe fallback explanation
```

This prevents hallucination.

---

### Step 8: Rule-Based Classification

**Not handled by LLM**

Logic:

```
value < lower_bound → LOW
value > upper_bound → HIGH
else → NORMAL
```

This ensures:

* Deterministic behavior
* Medical safety
* Explainability

---

### Step 9: Prompt Construction

Prompt includes:

* Test name
* Value
* Reference range
* Classification
* OCR confidence
* Safety constraints

Example:

```
Explain in simple language:
Test: Hemoglobin
Value: 11.2 g/dL
Range: 13–17
Status: LOW
Do NOT provide diagnosis.
```

---

### Step 10: LLM Reasoning (Offline)

**Model:** Phi-3 Mini (via Ollama)

Used ONLY for:

* Explanation
* Summarization
* Guidance (non-diagnostic)

Not used for:

* Classification
* Medical decision logic

---

### Step 11: Result Aggregation

Merged output includes:

* Numeric results
* Classification
* AI explanation
* Confidence score
* KB usage flag
* Disclaimer

---

### Step 12: Response to Frontend

```json
{
  "test": "Hemoglobin",
  "value": "11.2 g/dL",
  "status": "LOW",
  "reference_range": "13–17",
  "confidence_score": 0.91,
  "kb_used": true,
  "ai_summary": "Low hemoglobin may indicate...",
  "disclaimer": "This is not a medical diagnosis."
}
```

---

## 8. React Frontend Architecture

### Goals

* Simple for non-technical users
* Transparent results
* Clear confidence indicators

### Structure

```
frontend/
├── api/
├── components/
├── pages/
├── services/
└── App.jsx
```

### UI Responsibilities

* File upload
* Progress display
* Result rendering
* No medical logic

---

## 9. Model Selection Justification

**Recommended Model:** Phi-3 Mini (3.8B)

**Why:**

* Runs on 8 GB RAM
* CPU optimized
* Deterministic outputs
* Excellent for structured explanations
* Offline & privacy-safe

Not recommended:

* LLaMA 8B
* Mistral 7B
* Vision-language models

---

## 10. Safety & Transparency Measures

* Rule-based medical logic
* Knowledge Base grounding
* Confidence scoring
* KB usage indicator
* Mandatory disclaimer
* No diagnosis or medication advice

---

## 11. Why This Architecture Is Industry-Grade

* Clean Architecture
* Separation of concerns
* Replaceable components
* Agent-driven workflows
* Medical AI safety alignment
* Scalable to production systems

---

## 12. Examiner-Ready Summary

LabWise AI is an autonomous, offline medical AI agent that converts lab reports into structured, explained results using OCR, rule-based classification, RAG, and local generative AI. The system ensures safety through deterministic logic, transparency through confidence and KB indicators, and privacy through local execution.

---

## 13. Implementation Details

### Database Schema

**Tests Table:**
- test_id (PK)
- canonical_name
- short_name
- panel_name
- category
- description

**Ranges Table:**
- range_id (PK)
- test_id (FK)
- source_id (FK)
- ref_low, ref_high
- unit
- sex, age_min, age_max
- condition

**Sources Table:**
- source_id (PK)
- name
- trust_level
- year

**Synonyms Table:**
- synonym_id (PK)
- test_id (FK)
- synonym

### Service Layer Components

1. **OCR Service**: PaddleOCR integration with image preprocessing
2. **Parsing Service**: Regex-based extraction of test data
3. **RAG Service**: Knowledge base queries with synonym matching
4. **Classification Service**: Rule-based LOW/NORMAL/HIGH determination
5. **LLM Service**: Ollama client for explanation generation
6. **Lab Service**: Main orchestrator coordinating all services

---

## 14. Conclusion

This document fully defines **what to build, why it is built this way, and how every component interacts**.
A developer can implement the system end-to-end by following this specification without external clarification.

---

**End of Documentation**
