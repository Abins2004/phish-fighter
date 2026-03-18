# Phish Fighter

A full-stack AI-powered phishing detection system based on HTML structural analysis, visual features, and semantic content.

## Architecture
- **Frontend**: React + Tailwind CSS (Vite)
- **Backend**: Python (FastAPI)
- **ML Stack**: LightGBM, Scikit-learn (SVM, LogReg), PyTorch (EfficientNet-B0, MiniLM)
- **Web Scraping**: BeautifulSoup, Selenium
- **Database**: SQLite (SQLAlchemy ORM)

## Setup & Execution

### Method 1: Docker (Recommended)
1. Ensure Docker and Docker Compose are installed.
2. Run from the project root:
   ```bash
   docker-compose up --build
   ```
3. Access the Web Interface at `http://localhost`.

### Method 2: Local Development
#### Backend
1. `cd backend`
2. `python -m venv venv`
3. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. `pip install -r requirements.txt`
5. `uvicorn backend.main:app --reload`
*Backend running at http://localhost:8000*

#### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
*Frontend running at http://localhost:5173*

## API Endpoints

### `POST /api/analyze-url`
Analyzes a URL and returns phishing probability and explainability data.
**Request body:**
```json
{ "url": "https://example.com" }
```

### `POST /api/train-model`
Adds a new entry to the active dataset and triggers background retraining.
**Request body:**
```json
{
  "url": "https://suspicious-site.com",
  "label": 1
}
```
*(Label `1` = Phishing, `0` = Safe)*
