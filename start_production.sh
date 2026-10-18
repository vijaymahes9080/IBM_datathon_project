#!/usr/bin/env bash
set -e

echo "==============================================================================="
echo "Starting SecureAgent AI - Unified Production Server"
echo "==============================================================================="

if [ ! -d "venv" ]; then
    echo "[1/3] Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r backend/requirements.txt
    python -m spacy download en_core_web_sm
else
    source venv/bin/activate
fi

echo "[2/3] Building React Frontend..."
cd frontend
npm run build
cd ..

echo "[3/3] Launching Unified Gateway on http://0.0.0.0:8000 ..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
