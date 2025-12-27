# LabWise AI 🧬

**Autonomous Medical Lab Report Interpreter**

LabWise AI is an offline, privacy-preserving AI system that interprets medical laboratory reports (PDF or images) and generates human-readable explanations with confidence scoring based on a comprehensive knowledge base.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 🌟 Features

- **📄 Multi-Format Support**: Process PDFs and images (PNG, JPG, JPEG)
- **🔍 OCR Extraction**: EasyOCR for accurate text extraction
- **🧠 AI-Powered Analysis**: OpenAI GPT-4o-mini for intelligent interpretation
- **📊 Knowledge Base**: 1000+ medical tests with reference ranges from trusted sources
- **🎯 Smart Classification**: Automatic LOW/NORMAL/HIGH classification
- **💯 Confidence Scoring**: Dynamic confidence based on KB data quality
- **🔒 Privacy-First**: All processing happens locally (except OpenAI API calls)
- **📈 Statistics Dashboard**: View comprehensive KB statistics

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework**: FastAPI + Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **OCR**: EasyOCR
- **LLM**: OpenAI GPT-4o-mini (via Langchain)
- **PDF Processing**: pdf2image + Pillow

**Frontend:**
- **Framework**: React 18 + Vite
- **Styling**: Vanilla CSS with modern design
- **HTTP Client**: Axios

### Processing Pipeline

```
PDF/Image → OCR (EasyOCR) → LLM Extraction (OpenAI) → RAG Lookup (KB) 
→ Classification (Rule-based) → Summary Generation (OpenAI) → Results
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **OpenAI API Key** (GitHub Models or OpenAI)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/labwise-ai.git
cd labwise-ai
```

### 2. Backend Setup

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Initialize Database

```powershell
# Load knowledge base data
python -m app.db.init_db
```

### 4. Frontend Setup

```powershell
cd frontend
npm install
cd ..
```

### 5. Run Application

**Option A: Run All (Recommended)**
```powershell
.\run-all.ps1
```

**Option B: Run Separately**
```powershell
# Terminal 1: Backend
.\run-backend.ps1

# Terminal 2: Frontend
.\run-frontend.ps1
```

### 6. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
labwise-ai/
├── app/                        # Backend application
│   ├── api/                    # API routes and models
│   ├── db/                     # Database models and initialization
│   ├── services/               # Core services
│   │   ├── ocr_service.py      # EasyOCR integration
│   │   ├── openai_service.py   # OpenAI/LLM integration
│   │   ├── parsing_service.py  # Data extraction
│   │   ├── rag_service.py      # Knowledge base retrieval
│   │   ├── classification_service.py  # Result classification
│   │   └── stats_service.py    # Statistics generation
│   ├── utils/                  # Utilities
│   └── main.py                 # FastAPI application
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client
│   │   └── App.jsx             # Main app component
│   └── package.json
├── Knowladge-base/             # KB source data (CSV files)
├── data/                       # SQLite database
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://models.inference.ai.azure.com  # Or https://api.openai.com/v1
OPENAI_EXTRACTION_MODEL=gpt-4o-mini
OPENAI_SUMMARY_MODEL=gpt-4o-mini

# Application Settings
APP_VERSION=1.0.0
DEBUG=False
MAX_UPLOAD_SIZE=10485760  # 10MB

# Database
DATABASE_URL=sqlite:///./data/labwise.db

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### OpenAI API Key Options

1. **GitHub Models** (Free for development):
   - Get token from: https://github.com/settings/tokens
   - Set `OPENAI_BASE_URL=https://models.inference.ai.azure.com`

2. **OpenAI** (Paid):
   - Get API key from: https://platform.openai.com/api-keys
   - Set `OPENAI_BASE_URL=https://api.openai.com/v1`

---

## 📊 Knowledge Base

The system includes a comprehensive medical knowledge base with:

- **1,000+ Medical Tests**: Complete Blood Count, Metabolic Panels, Lipid Profiles, etc.
- **10,000+ Reference Ranges**: Age, sex, and condition-specific ranges
- **5,000+ Test Synonyms**: Alternative names and abbreviations
- **Trusted Sources**: Mayo Clinic, LabCorp, Quest Diagnostics, WHO, NIH

### KB Statistics

View real-time statistics at: http://localhost:5173/ → "View KB Statistics"

---

## 🔬 How It Works

### 1. OCR Extraction
- **EasyOCR** extracts text from uploaded PDF/image
- Confidence score calculated based on OCR quality

### 2. LLM-Based Parsing
- **OpenAI GPT-4o-mini** extracts structured test data
- Guided by KB test names for accurate mapping

### 3. Knowledge Base Lookup (RAG)
- Searches KB for each test by canonical name or synonym
- Retrieves reference ranges with source trust levels

### 4. Classification
- Rule-based classification: LOW/NORMAL/HIGH/UNKNOWN
- Based on KB reference ranges

### 5. Confidence Scoring
- **With KB Data**: Calculated from source trust_level (1-5) and source_priority (1-5)
- **Without KB Data**: Randomized base score (40-50%)
- **Dynamic**: Varies with each request based on data quality

### 6. Summary Generation
- **OpenAI GPT-4o-mini** generates patient-friendly summary
- Different prompts for KB-matched vs non-matched tests
- Plain text output (no markdown formatting)

---

## 🧪 Testing

### Test with Sample Report

1. Navigate to http://localhost:5173
2. Upload a lab report (PDF or image)
3. Wait for analysis (~60-90 seconds for first run)
4. View results with confidence scores

### API Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Get KB statistics
curl http://localhost:8000/api/stats

# Analyze report
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@path/to/report.pdf"
```

---

## 📈 Performance

- **OCR Processing**: 60-80 seconds (first run), 20-30 seconds (subsequent)
- **LLM Extraction**: 3-7 seconds
- **KB Lookup**: <0.1 seconds
- **Summary Generation**: 3-6 seconds
- **Total**: ~70-90 seconds (first run), ~30-45 seconds (subsequent)

---

## 🛡️ Privacy & Security

- **Local Processing**: OCR and classification happen locally
- **API Calls**: Only OpenAI API calls leave your system
- **No Data Storage**: Uploaded files are not stored permanently
- **Medical Disclaimer**: Always included in results

---

## ⚠️ Medical Disclaimer

**IMPORTANT**: This tool is for informational purposes only and does NOT constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical decisions.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **Knowledge Base Sources**: Mayo Clinic, LabCorp, Quest Diagnostics, WHO, NIH
- **OCR**: EasyOCR team
- **LLM**: OpenAI GPT-4o-mini
- **Framework**: FastAPI and React communities

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`

---

**Built with ❤️ for better healthcare accessibility**
