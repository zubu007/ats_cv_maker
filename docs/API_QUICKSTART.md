# API Quick Start Guide

Get the ATS CV Maker API running in 5 minutes.

## Prerequisites

- Python 3.11+
- pip or poetry

## Installation

### 1. Install Dependencies

```bash
# Navigate to project directory
cd /path/to/ats_cv_maker

# Install the project with API dependencies
pip install -e .

# Download required spaCy model
python -m spacy download en_core_web_sm
```

### 2. Configure Environment (Optional)

Create a `.env` file with your settings:

```bash
cp .env.example .env
```

Edit `.env` and update values as needed. The defaults should work for local development.

### 3. Start the API Server

```bash
# Option A: Development mode with auto-reload
python api_server.py

# Option B: Using uvicorn directly
uvicorn src.ats_cv_maker.api.app:app --reload --port 8000

# Option C: Docker
docker-compose up
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Verify Installation

### Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "api_ready": true
}
```

### Access Documentation

Open your browser to `http://localhost:8000/docs` to see interactive API documentation (Swagger UI).

## First API Call

### Using cURL

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_content": "John Doe\nSoftware Engineer\nPython, JavaScript, AWS\n\nExperience:\nSenior Engineer at TechCorp (2020-2024)\n- Built scalable microservices using Python and FastAPI\n- Deployed applications on AWS\n- Managed CI/CD pipelines with Docker",
    "job_description": "We are looking for a Senior Software Engineer with Python and AWS experience. Required: Python, AWS, FastAPI. Nice to have: Docker, Kubernetes"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/analyze',
    json={
        'cv_content': 'John Doe\nSoftware Engineer\nPython, JavaScript, AWS',
        'job_description': 'Required: Python, AWS, FastAPI'
    }
)

print(f"ATS Score: {response.json()['ats_score']['percentage']}%")
```

### Using JavaScript/Fetch

```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cv_content: 'John Doe\nSoftware Engineer\nPython, AWS',
    job_description: 'Required: Python, AWS, FastAPI'
  })
});

const data = await response.json();
console.log(`ATS Score: ${data.ats_score.percentage}%`);
```

## Available Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/analyze` | Analyze CV against job description |
| `POST` | `/api/v1/improve` | Get CV improvement recommendations |
| `POST` | `/api/v1/match-skills` | Analyze skill matching |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/redoc` | Alternative API documentation |

## Common Parameters

All endpoints require:
- `cv_content` (string): Full CV text
- `job_description` (string): Full job description text

Optional parameters vary by endpoint. See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for details.

## Troubleshooting

### Port 8000 already in use
```bash
# Use a different port
python -m uvicorn src.ats_cv_maker.api.app:app --port 8001
```

### Module not found errors
```bash
# Make sure you're in the project root and installed in development mode
pip install -e .
```

### spaCy model errors
```bash
# Download the English model
python -m spacy download en_core_web_sm
```

### CORS errors in browser
- Update `CORS_ORIGINS` in `.env` to include your frontend URL
- Restart the API server

## Next Steps

1. Read the [full API documentation](./API_DOCUMENTATION.md)
2. Explore the endpoints in the interactive docs: `http://localhost:8000/docs`
3. Build your frontend to connect to these endpoints
4. Deploy to production when ready

## Example Frontend Integration

See examples in [API_DOCUMENTATION.md](./API_DOCUMENTATION.md#integration-examples) for:
- React integration
- Python client
- JavaScript/Fetch examples
