# Tender AI Platform - Python Backend

Backend API for Moroccan Government Tender Analysis.

## Requirements

- Python 3.11+ (also compatible with 3.13 and 3.14)
- PostgreSQL 14+
- Playwright browsers

## Quick Start

### 1. Clone and Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

**Option A: Local PostgreSQL**
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/tender_ai
```

**Option B: Supabase (recommended)**
```
SUPABASE_URL=https://msrgptjqvnvrttvgoxsc.supabase.co
SUPABASE_SERVICE_KEY=<your-service-role-key>
```

Get your service key from the Lovable Cloud backend panel.

### 3. Add DeepSeek API Key

Get your key from https://platform.deepseek.com/

```
DEEPSEEK_API_KEY=sk-...
```

### 4. Run the Server

```bash
python main.py
```

Server runs at http://localhost:8000

## API Endpoints

### Tenders

- `GET /api/tenders/` - List tenders
- `GET /api/tenders/{id}` - Get tender details
- `GET /api/tenders/{id}/documents` - Get tender documents
- `GET /api/tenders/{id}/lots` - Get tender lots

### Scraper

- `POST /api/scraper/run` - Start scraper (optional: `target_date`)
- `GET /api/scraper/status` - Get scraper status
- `POST /api/scraper/stop` - Stop scraper

### AI Analysis

- `POST /api/analysis/avis` - Extract Avis metadata
- `POST /api/analysis/deep` - Run deep analysis
- `POST /api/analysis/ask` - Ask AI a question
- `GET /api/analysis/chats/{tender_id}` - Get chat history

## Architecture

```
backend/
├── main.py                 # FastAPI entry point
├── config.py               # Settings management
├── database.py             # Database connections
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── routers/
│   ├── tenders.py          # Tender CRUD
│   ├── scraper.py          # Scraper control
│   └── analysis.py         # AI analysis
└── services/
    ├── tender_scraper.py   # Playwright scraper
    ├── document_extractor.py # Text extraction
    └── ai_analyzer.py      # DeepSeek integration
```

## Data Flow

1. **Scraping** → Downloads tender ZIP files from marchespublics.gov.ma
2. **Extraction** → Extracts text from PDF/DOCX/XLSX (memory-only)
3. **Classification** → Classifies documents (AVIS, RC, CPS, ANNEXE)
4. **AI Pipeline 1** → Extracts Avis metadata → Status: LISTED
5. **AI Pipeline 2** → Deep analysis (on click) → Status: ANALYZED
6. **AI Pipeline 3** → Ask AI (chat interface)

## Memory-Only Processing

All file processing happens in-memory using `io.BytesIO`. No files are written to disk during extraction.

## Test Mode

Set `TEST_MODE=true` to run the scraper immediately instead of waiting for midnight.

```bash
# In test mode, trigger manually:
curl -X POST http://localhost:8000/api/scraper/run
```
