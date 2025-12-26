# LabWise AI 🧬

**Autonomous Medical Lab Report Interpretation Agent**

LabWise AI is an offline, privacy-preserving AI system that interprets medical laboratory reports and generates human-readable explanations for non-technical users.

## 🌟 Features

- **OCR Extraction**: Converts PDF and image lab reports to structured data using PaddleOCR
- **Knowledge Base Integration**: Matches tests against a comprehensive medical reference database
- **Rule-Based Classification**: Deterministic LOW/NORMAL/HIGH classification for medical safety
- **AI Explanations**: Local LLM (Phi-3 Mini via Ollama) generates clear, non-technical explanations
- **Privacy-First**: All processing happens locally - no data leaves your device
- **Confidence Scoring**: Transparent OCR confidence and KB matching indicators
- **Modern UI**: Beautiful, responsive React interface with real-time analysis

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **API Layer**: REST endpoints for file upload and analysis
- **Service Layer**: OCR, Parsing, RAG, Classification, LLM services
- **Database Layer**: SQLite with medical knowledge base
- **Clean Architecture**: Separation of concerns, modular components

### Frontend (React + Vite)
- **File Upload**: Drag-and-drop interface for PDF/images
- **Results Display**: Interactive cards showing test results and explanations
- **Real-time Progress**: Upload and processing status indicators

### Knowledge Base
- **Tests**: 200+ laboratory tests with canonical definitions
- **Reference Ranges**: Multi-source, sex/age-specific ranges
- **Synonyms**: Alternate test names for robust matching
- **Sources**: Trust-level based reference prioritization

## 📋 Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 16 or higher
- **Ollama**: For local LLM (optional but recommended)
- **Poppler**: For PDF processing (required for PDF support)

## 🚀 Installation

### 1. Clone the Repository

```bash
cd Labwise-ai
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m app.db.init_db
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Install Ollama (Optional but Recommended)

Download and install Ollama from [https://ollama.ai](https://ollama.ai)

```bash
# Pull Phi-3 Mini model
ollama pull phi3:mini
```

### 5. Install Poppler (For PDF Support)

**Windows:**
- Download from: https://github.com/oschwartz10612/poppler-windows/releases
- Add to PATH

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**Mac:**
```bash
brew install poppler
```

## 🎯 Usage

### Start Backend Server

```bash
# From project root
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
# From frontend directory
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### Using the Application

1. Open `http://localhost:5173` in your browser
2. Upload a lab report (PDF or image)
3. Wait for analysis to complete
4. View results with classifications and AI explanations

## 📁 Project Structure

```
labwise-ai/
├── app/                      # Backend application
│   ├── api/                  # API routes and models
│   ├── services/             # Business logic services
│   │   ├── ocr_service.py    # OCR extraction
│   │   ├── parsing_service.py # Text parsing
│   │   ├── rag_service.py    # Knowledge base retrieval
│   │   ├── classification_service.py # Rule-based classification
│   │   ├── llm_service.py    # LLM explanation generation
│   │   └── lab_service.py    # Main orchestration
│   ├── db/                   # Database models and initialization
│   ├── utils/                # Utilities and configuration
│   └── main.py               # FastAPI application
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   ├── App.jsx           # Main app component
│   │   └── main.jsx          # Entry point
│   └── package.json
├── Knowladge-base/           # Medical reference data (CSV files)
├── data/                     # SQLite database (generated)
├── requirements.txt          # Python dependencies
└── README.md
```

## 🔧 Configuration

Create a `.env` file in the project root (optional):

```env
# LLM Settings
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=phi3:mini

# OCR Settings
OCR_CONFIDENCE_THRESHOLD=0.7
USE_GPU=False

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## 🧪 API Endpoints

### Health Check
```
GET /api/health
```

### Analyze Lab Report
```
POST /api/analyze
Content-Type: multipart/form-data
Body: file (PDF or image)
```

Response:
```json
{
  "success": true,
  "summary": {
    "total_tests": 10,
    "kb_matched": 9,
    "normal_results": 7,
    "high_results": 2,
    "low_results": 1
  },
  "confidence": {
    "ocr_confidence": 0.92,
    "confidence_level": "HIGH"
  },
  "tests": [
    {
      "test_name": "Hemoglobin",
      "value": 11.2,
      "unit": "g/dL",
      "classification": "LOW",
      "reference_range": "13.0 - 17.0 g/dL",
      "ai_explanation": "...",
      "kb_found": true
    }
  ],
  "disclaimer": "..."
}
```

## 🔒 Privacy & Security

- **Offline Processing**: All OCR, classification, and LLM processing happens locally
- **No External APIs**: No data is sent to cloud services
- **Local Database**: Knowledge base stored in local SQLite
- **Medical Safety**: Rule-based classification ensures deterministic results
- **Transparency**: Confidence scores and KB matching indicators

## ⚠️ Medical Disclaimer

**IMPORTANT**: LabWise AI is for informational and educational purposes only. It does NOT:
- Provide medical diagnosis
- Replace professional medical advice
- Recommend treatments or medications
- Substitute for consultation with healthcare providers

Always consult qualified healthcare professionals for medical decisions.

## 🛠️ Development

### Run Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black app/

# Lint
flake8 app/
```

### Build Frontend for Production
```bash
cd frontend
npm run build
```

## 📚 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PaddleOCR**: OCR engine
- **OpenCV**: Image preprocessing
- **SQLAlchemy**: ORM for database
- **Ollama**: Local LLM inference
- **pdf2image**: PDF conversion

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **Axios**: HTTP client

## 🤝 Contributing

This is an educational project. Contributions are welcome!

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- Knowledge base compiled from clinical references
- Built with modern AI/ML technologies
- Designed for privacy and medical safety

## 📞 Support

For issues or questions, please check:
- API Documentation: `http://localhost:8000/docs`
- Project structure and code comments
- Architecture documentation

---

**Built with ❤️ for safer, more accessible healthcare information**
