# ATS CV Maker SaaS - Complete Getting Started Guide

Your ATS CV Maker has been transformed into a production-ready REST API for building a SaaS platform.

## 📚 Documentation Overview

### Quick Reference
| Document | Purpose | Read Time |
|----------|---------|-----------|
| [API_QUICKSTART.md](./API_QUICKSTART.md) | Get API running in 5 minutes | 5 min |
| [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) | Complete API reference with examples | 15 min |
| [API_CONVERSION_SUMMARY.md](./API_CONVERSION_SUMMARY.md) | What changed and why | 10 min |
| [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) | Build React/Vue/Next.js frontend | 20 min |
| [SAAS_SETUP.md](./SAAS_SETUP.md) | Full SaaS implementation (DB, Auth, Payments) | 30 min |

## 🚀 Quick Start (5 minutes)

### 1. Install & Run API

```bash
# Install dependencies
pip install -e .
python -m spacy download en_core_web_sm

# Start API
python api_server.py

# API is now at: http://localhost:8000
```

### 2. Access Documentation

Open your browser:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 3. Test the API

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_content": "John Doe\nSoftware Engineer\nPython, AWS",
    "job_description": "Senior Engineer with Python and AWS"
  }'
```

## 📁 New Files Created

```
src/ats_cv_maker/api/
├── __init__.py        # API package
├── app.py             # FastAPI application
├── routes.py          # API endpoints (/analyze, /improve, /match-skills)
├── models.py          # Request/Response Pydantic models
├── core.py            # Business logic services
└── config.py          # Configuration management

Root:
├── api_server.py      # Start the API: python api_server.py
├── Dockerfile         # Docker build file
└── docker-compose.yml # Docker Compose for easy setup

Documentation:
├── API_QUICKSTART.md
├── API_DOCUMENTATION.md
├── API_CONVERSION_SUMMARY.md
├── FRONTEND_INTEGRATION.md
└── SAAS_SETUP.md
```

## 🔌 API Endpoints

### Analyze CV
**POST** `/api/v1/analyze`

Analyze CV against job description.

```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cv_content: 'Your CV text...',
    job_description: 'Job description text...'
  })
});
const data = await response.json();
console.log(`ATS Score: ${data.ats_score.percentage}%`);
```

**Response:**
```json
{
  "ats_score": {
    "score": 78.5,
    "percentage": 78.5,
    "matched_required": 2,
    "total_required": 3
  },
  "rated_keywords": {
    "required": ["Python", "FastAPI"],
    "optional": ["Docker"]
  },
  "analysis_summary": "CV Analysis Complete: 78.5% match..."
}
```

### Improve CV
**POST** `/api/v1/improve`

Get recommendations to improve CV score.

```javascript
const response = await fetch('http://localhost:8000/api/v1/improve', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cv_content: 'Your CV text...',
    job_description: 'Job description text...',
    max_keywords_to_add: 10
  })
});
const data = await response.json();
console.log(`Keywords to add: ${data.keywords_to_add.join(', ')}`);
```

### Match Skills
**POST** `/api/v1/match-skills`

Analyze skill matching.

```javascript
const response = await fetch('http://localhost:8000/api/v1/match-skills', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cv_content: 'Your CV text...',
    job_description: 'Job description text...'
  })
});
const data = await response.json();
console.log(`Skill match: ${data.skill_match_percentage}%`);
console.log(`Missing: ${data.missing_skills.join(', ')}`);
```

### Health Check
**GET** `/health`

```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "version": "1.0.0", "api_ready": true}
```

## 🛠️ Development Options

### Option 1: Local Development
```bash
python api_server.py
# API runs at http://localhost:8000
# Development mode with auto-reload
```

### Option 2: Docker (Recommended)
```bash
docker-compose up
# API runs at http://localhost:8000
# Production-like environment
```

### Option 3: Uvicorn Directly
```bash
uvicorn src.ats_cv_maker.api.app:app --reload --port 8000
```

## 🎨 Build Your Frontend

### React Example
```javascript
// 1. Create React app
npx create-react-app ats-frontend
cd ats-frontend

// 2. Create API client (src/services/atsApi.js)
const API_URL = 'http://localhost:8000';
export const analyzeCv = async (cv, jd) => {
  const res = await fetch(`${API_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cv_content: cv, job_description: jd })
  });
  return res.json();
};

// 3. Use in component
import { analyzeCv } from './services/atsApi';

function App() {
  const [results, setResults] = useState(null);
  const handleAnalyze = async () => {
    const data = await analyzeCv(cv, jd);
    setResults(data);
  };
  
  return (
    <div>
      <button onClick={handleAnalyze}>Analyze</button>
      {results && <p>Score: {results.ats_score.percentage}%</p>}
    </div>
  );
}
```

See [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) for complete examples with React, Vue, and Next.js.

## 🔐 Configuration

Create `.env` file in project root:

```env
# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS (allow frontend origin)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# LLM Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Environment
ENVIRONMENT=development
```

## 📚 Learning Path

### Day 1: Understand the API
1. Read [API_QUICKSTART.md](./API_QUICKSTART.md) (5 min)
2. Start the API and explore /docs endpoint (15 min)
3. Try some API calls with curl or Postman (15 min)
4. **Checkpoint**: Can you analyze a CV and see the ATS score?

### Day 2: Build Basic Frontend
1. Read [FRONTEND_INTEGRATION.md](./FRONTEND_INTEGRATION.md) (15 min)
2. Create React app with API client (30 min)
3. Build CV input and results display (45 min)
4. **Checkpoint**: Can you analyze CV from your frontend?

### Day 3: Add Advanced Features
1. Read [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) (15 min)
2. Add improvement suggestions feature (30 min)
3. Add skill matching feature (30 min)
4. **Checkpoint**: All 3 endpoints working in frontend

### Day 4-5: SaaS Setup
1. Read [SAAS_SETUP.md](./SAAS_SETUP.md) (30 min)
2. Set up PostgreSQL database (30 min)
3. Implement user authentication (1-2 hours)
4. Add rate limiting and usage tracking (1 hour)
5. **Checkpoint**: Users can sign up and use API with limits

### Day 6: Monetization
1. Integrate Stripe (1-2 hours)
2. Implement subscription plans (1-2 hours)
3. **Checkpoint**: Users can upgrade to pro plan

### Day 7+: Deploy & Scale
1. Set up Docker deployment
2. Deploy to Heroku/AWS/Cloud
3. Configure monitoring and logging
4. Marketing and user acquisition

## 🧪 Testing

### Test in Browser
- API Docs: http://localhost:8000/docs
- Try all endpoints directly in Swagger UI

### Test with Code
```python
import requests

# Test analyze
response = requests.post('http://localhost:8000/api/v1/analyze', json={
    'cv_content': 'John Doe...',
    'job_description': 'Senior Engineer...'
})
print(response.json())
```

## 🐳 Docker Deployment

### Build & Run Locally
```bash
docker-compose up
# API available at http://localhost:8000
```

### Deploy to Heroku
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
heroku open
```

### Deploy to AWS
```bash
# See SAAS_SETUP.md for detailed AWS instructions
```

## 🔗 API Integrations

### JavaScript/Fetch
```javascript
const res = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ cv_content, job_description })
});
const data = await res.json();
```

### Python Requests
```python
import requests
resp = requests.post(
    'http://localhost:8000/api/v1/analyze',
    json={'cv_content': cv, 'job_description': jd}
)
print(resp.json())
```

### cURL
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"cv_content":"...", "job_description":"..."}'
```

## 📊 Success Metrics

Track these as you build:

1. **API Metrics**
   - Response time (target: < 2s)
   - Uptime (target: > 99.9%)
   - Error rate (target: < 0.1%)

2. **Product Metrics**
   - Daily active users
   - Analyses per day
   - Free to paid conversion
   - Monthly recurring revenue (MRR)

3. **Technical Metrics**
   - Cost per analysis
   - Cache hit rate
   - Database performance

## 🆘 Troubleshooting

### Port 8000 already in use
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
python api_server.py --port 8001
```

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### CORS errors
- Update `CORS_ORIGINS` in `.env` to include your frontend URL
- Restart API server

### Module import errors
```bash
# Ensure you're in project root and installed in dev mode
pip install -e .
```

## 📖 Additional Resources

- [API Reference](./API_DOCUMENTATION.md) - Complete endpoint documentation
- [Frontend Guide](./FRONTEND_INTEGRATION.md) - Building frontends with React/Vue/Next.js
- [SaaS Implementation](./SAAS_SETUP.md) - Database, auth, payments, deployment
- [FastAPI Docs](https://fastapi.tiangolo.com/) - FastAPI documentation

## 🎯 Next Immediate Steps

1. **Start the API**: `python api_server.py`
2. **Open the docs**: http://localhost:8000/docs
3. **Try an analysis**: Use the Swagger UI to test
4. **Read API_DOCUMENTATION.md**: Understand all endpoints
5. **Choose a frontend**: React, Vue, or Next.js
6. **Build your first feature**: CV upload and analysis

---

**You now have everything you need to build a SaaS! Start with the API, build a frontend, add authentication and payments, then deploy. 🚀**

Have questions? Check the relevant documentation file above!
