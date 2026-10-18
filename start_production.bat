@echo off
echo ===============================================================================
echo Starting SecureAgent AI - Unified Production Server
echo ===============================================================================

echo [1/3] Checking dependencies...
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
    python -m spacy download en_core_web_sm
) else (
    call venv\Scripts\activate.bat
)

echo [2/3] Building React Frontend...
cd frontend
call npm run build
cd ..

echo [3/3] Starting Unified Gateway on http://localhost:8000 ...
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
