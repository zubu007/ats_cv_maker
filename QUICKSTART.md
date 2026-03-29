# Quick Start Guide

## Starting the Application

### Method 1: Using Shell Scripts (Recommended)

**Terminal 1 - Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start_frontend.sh
```

---

### Method 2: Using Python/NPM Directly

**Terminal 1 - Backend:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Start backend
python start_backend.py
```

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend
cd frontend

# Start frontend
npm run dev
```

---

### Method 3: Using Uvicorn Directly

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
uvicorn backend.src.api.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## Access URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API Alternative Docs:** http://localhost:8000/redoc

---

## Troubleshooting

### Backend won't start
1. Ensure virtual environment is activated: `source .venv/bin/activate`
2. Check if dependencies are installed: `pip install -e .`
3. Verify .env file exists with OPENAI_API_KEY

### Frontend won't start
1. Ensure you're in the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Check if port 5173 is available

### API Key Issues
1. Check .env file has OPENAI_API_KEY set
2. Verify the API key is valid
3. Check console for authentication errors

---

## First Time Setup

If this is your first time running the project:

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate it
source .venv/bin/activate

# 3. Install Python dependencies
pip install -e .

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 6. Install frontend dependencies
cd frontend
npm install
cd ..

# 7. Start backend (in terminal 1)
./start_backend.sh

# 8. Start frontend (in terminal 2)
./start_frontend.sh
```
