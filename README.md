# Multimodal AI Analysis & Model Evaluation Platform

A FastAPI + SQLite + HTML/CSS/JavaScript platform for text, image, PDF analysis and AI model evaluation.

## 1. Folder structure

multimodal-ai-evaluation-platform/
- app.py
- ai_service.py
- database.py
- requirements.txt
- .env
- .env.example
- .gitignore
- frontend/
  - index.html
  - style.css
  - script.js

## 2. Create the virtual environment

Windows PowerShell:

python -m venv venv

## 3. Install packages

.\venv\Scripts\python.exe -m pip install -r requirements.txt

## 4. Configure Gemini

Copy `.env.example` to `.env`.

Put your new Gemini key in `.env`:

GEMINI_API_KEY=YOUR_KEY
GEMINI_MODEL=gemini-2.5-flash
DEMO_MODE=false

Never upload `.env` to GitHub.

If you do not have a key yet, use:

DEMO_MODE=true

The platform will still start and local analysis/history features will work.

## 5. Start the server

.\venv\Scripts\python.exe -m uvicorn app:app --reload

Open:

http://127.0.0.1:8000/

Do not use Live Server for this project.

## 6. Main features

- Dashboard
- Text analysis
- Image analysis
- PDF extraction and analysis
- Automatic model evaluation
- Manual model comparison
- Accuracy/relevance/quality/safety/hallucination signals
- SQLite history
- Delete one history item
- Clear all history
- Gemini integration with local/demo fallback
