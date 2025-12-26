
# 🧪 Unified Clinical Laboratory Reference Dataset

## 📌 Overview

This repository contains a **normalized, source-aware, clinically structured laboratory reference dataset** designed for:

- Clinical decision support systems
- Laboratory Information Systems (LIS)
- Health screening & diagnostic packages
- AI/ML medical interpretation engines
- Patient-facing lab report explanations

The dataset consolidates **hundreds of laboratory tests** with:
- Canonical test definitions
- Multi-source reference ranges
- Sex- and condition-specific values
- Calculated vs measured test handling
- Source trust & priority resolution

It is **adult-focused**, clinically validated, and scalable to pediatric and pregnancy-specific extensions.

---

## 📂 Dataset Structure (4 Core Files)

```

/dataset
│
├── tests.csv           # Master test catalog (canonical definitions)
├── ranges.csv          # Reference ranges (multi-source, conditional)
├── sources.csv         # Reference source metadata & trust levels
└── synonyms.csv        # Alternate test names & aliases

```

Each file serves a **distinct, non-overlapping responsibility**.

---

## 1️⃣ `tests.csv` — Canonical Test Definitions

This is the **master registry** of all laboratory tests.

### Purpose
- Ensures **one test = one canonical identity**
- Normalizes naming across labs, reports, and sources
- Acts as the anchor for ranges, synonyms, and packages

### Columns

| Column Name | Description |
|------------|-------------|
| `test_id` | **Primary key**. Unique integer identifier for each test |
| `canonical_name` | Official standardized test name |
| `short_name` | Common abbreviated name (e.g., ALT, TSH) |
| `panel_name` | Logical grouping (CBC, LFT, Renal, Cardiac, etc.) |
| `specimen_type` | Sample type (blood, serum, plasma, urine, stool, CSF) |
| `category` | Broad classification (chemistry, hematology, serology, calculated, endocrinology, etc.) |
| `loinc_code` | Standard LOINC identifier (or `NA` if unavailable) |
| `description` | Clinical purpose and interpretation summary |

### Key Design Rules
- **No duplicates** of canonical tests
- Calculated tests (e.g., eGFR, LDL, FAI) are explicitly labeled
- LOINC codes are included when confidently mapped

---

## 2️⃣ `ranges.csv` — Reference Ranges

This file defines **all numeric and textual reference values**.

### Purpose
- Supports **multiple sources per test**
- Handles sex-specific, condition-specific, and contextual ranges
- Enables intelligent range resolution via priority rules

### Columns

| Column Name | Description |
|------------|-------------|
| `range_id` | **Primary key** for the range record |
| `test_id` | Foreign key → `tests.test_id` |
| `source_id` | Foreign key → `sources.source_id` |
| `canonical_name` | Redundant safety column for validation |
| `unit` | Measurement unit (mg/dL, mmol/L, %, IU/L, etc.) |
| `value_type` | `numeric` or `text` |
| `ref_low` | Lower reference limit (nullable) |
| `ref_high` | Upper reference limit (nullable) |
| `ref_text` | Text-based interpretation (e.g., "<200", "Negative") |
| `sex` | `Male`, `Female`, or `Any` |
| `age_min` | Minimum age (years, nullable) |
| `age_max` | Maximum age (years, nullable) |
| `condition` | Context (fasting, pregnancy, AM, PM, postmenopausal, etc.) |
| `source_priority` | Numeric priority for conflict resolution |
| `effective_year` | Year the range is valid or published |

### Range Resolution Logic

When **multiple ranges exist** for a test:
1. Match **sex**
2. Match **age**
3. Match **condition**
4. Select **highest trust source**
5. Use **lowest `source_priority` value**

---

## 3️⃣ `sources.csv` — Reference Sources & Trust Model

This file defines **where ranges come from** and how reliable they are.

### Purpose
- Enables **transparent clinical provenance**
- Allows intelligent conflict resolution
- Supports auditability and regulatory review

### Columns

| Column Name | Description |
|------------|-------------|
| `source_id` | **Primary key** |
| `name` | Name of the source |
| `type` | Dataset, clinical reference, guideline, educational |
| `url` | Public reference link |
| `year` | Publication or revision year |
| `trust_level` | Reliability score (1–5) |

### Trust Level Definition

| Trust Level | Meaning |
|------------|--------|
| **5** | Authoritative clinical bodies (WHO, NIH, CDC, ACP) |
| **4** | Peer-reviewed clinical references (ABIM, Medscape) |
| **3** | Academic or institutional datasets |
| **2** | Educational compilations |
| **1** | Legacy or low-confidence references |

### Priority vs Trust
- **Trust level** reflects *quality*
- **Source priority** controls *which range wins*

This allows newer or region-specific sources to override older ones **without deleting data**.

---

## 4️⃣ `synonyms.csv` — Test Name Normalization

This file maps **alternate names → canonical tests**.

### Purpose
- Handles lab-to-lab naming differences
- Supports search, ingestion, and NLP pipelines
- Prevents duplicate test creation

### Columns

| Column Name | Description |
|------------|-------------|
| `synonym_id` | **Primary key** |
| `test_id` | Foreign key → `tests.test_id` |
| `synonym` | Alternate or colloquial test name |
| `source_id` | Origin of the synonym |

### Examples
- SGPT → ALT  
- A1C → Hemoglobin A1c  
- HBsAg → Hepatitis B Surface Antigen  
- DAT → Direct Coombs Test  

---

## 🔄 Calculated vs Measured Tests

Some tests are **derived**, not directly measured:

Examples:
- LDL Cholesterol (calculated)
- Estimated GFR
- Corrected Calcium
- Free Androgen Index

These are:
- Marked with `category = calculated`
- Still assigned reference ranges
- Intended to be computed externally using defined formulas

---

## 🧠 Clinical Scope & Coverage

### Fully Covered Domains
- CBC & Differential
- Renal Function (RFT)
- Liver Function (LFT)
- Lipid Profile
- Cardiac Markers
- Endocrine & Hormonal Tests
- Iron Studies
- Coagulation & Hematology
- Autoimmune & Immunology
- Antenatal Screening
- Stool & Urine Analysis

### Current Focus
- Adult reference ranges
- General population screening
- Hospital & outpatient diagnostics

---

## ⚠️ Important Notes

- This dataset **does not replace clinical judgment**
- Ranges may vary by:
  - Geography
  - Laboratory methodology
  - Instrumentation
- Always pair with **lab-specific flags** when used clinically

---

## 🚀 Extensibility

Designed to support:
- Pediatric ranges
- Trimester-specific pregnancy ranges
- Disease-specific targets
- Unit conversion tables
- AI interpretation layers

No schema changes required.

---

## 📜 License & Usage

This dataset is intended for:
- Research
- Education
- Health technology development

Clinical use should comply with **local regulations and validation requirements**.

---

## 👏 Final Note

This dataset is structured to **professional clinical standards** and is suitable as a **core knowledge base** for modern health applications.


