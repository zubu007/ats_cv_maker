# ATS CV Maker SaaS - API Documentation

## Overview

This guide explains how to use the ATS CV Maker REST API for your SaaS frontend. The API exposes core CV analysis, improvement, and skill matching functions as simple HTTP endpoints.

## Quick Start

### 1. Start the API Server

**Option A: Direct Python**
```bash
# Install dependencies
pip install -e .

# Start the API
python -m uvicorn src.ats_cv_maker.api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Option B: Docker**
```bash
# Build and run with Docker Compose
docker-compose up
```

The API will be available at: `http://localhost:8000`

### 2. Access Documentation

- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative Docs (ReDoc)**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## API Endpoints

### 1. CV Analysis

**Endpoint**: `POST /api/v1/analyze`

Analyzes a CV against a job description and returns ATS scores, keyword matches, and optional skill/experience analysis.

**Request Body**:
```json
{
  "cv_content": "Your full CV text here...",
  "job_description": "Full job description text here...",
  "use_spacy": true,
  "include_skills": true,
  "include_experience": true,
  "max_keywords": 50
}
```

**Request Parameters**:
- `cv_content` (string, required): The full text content of the CV
- `job_description` (string, required): The full text content of the job description
- `use_spacy` (boolean, default: true): Enable spaCy NLP for better keyword extraction
- `include_skills` (boolean, default: true): Include skill matching analysis
- `include_experience` (boolean, default: true): Include experience relevance analysis
- `max_keywords` (integer, default: 50): Maximum keywords to extract

**Response**:
```json
{
  "cv_keywords": [
    {
      "keyword": "Python",
      "frequency": 5,
      "relevance_score": 0.85
    }
  ],
  "jd_keywords": [
    {
      "keyword": "Python",
      "frequency": 3,
      "relevance_score": 0.9
    }
  ],
  "rated_keywords": {
    "required": ["Python", "FastAPI", "AWS"],
    "optional": ["Docker", "Redis"]
  },
  "ats_score": {
    "score": 78.5,
    "percentage": 78.5,
    "matched_required": 2,
    "total_required": 3,
    "matched_optional": 1,
    "total_optional": 2
  },
  "skill_score": {
    "matched_skills": ["Python", "FastAPI"],
    "missing_skills": ["AWS"],
    "skill_match_percentage": 66.7
  },
  "experience_score": {
    "experience_relevance_score": 75.0,
    "experience_count": 3,
    "relevant_experiences": ["Senior Engineer", "Tech Lead"]
  },
  "analysis_summary": "CV Analysis Complete: 78.5% match with 2/3 required keywords."
}
```

**Status Codes**:
- `200 OK`: Analysis completed successfully
- `422 Unprocessable Entity`: Invalid request data
- `500 Internal Server Error`: Server-side error

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_content": "John Doe...",
    "job_description": "We are looking for...",
    "use_spacy": true
  }'
```

**Example JavaScript/Fetch**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cv_content: cvText,
    job_description: jdText,
    use_spacy: true
  })
});

const data = await response.json();
console.log(`ATS Score: ${data.ats_score.percentage}%`);
```

---

### 2. CV Improvement

**Endpoint**: `POST /api/v1/improve`

Identifies missing keywords and suggests placements to improve your ATS score.

**Request Body**:
```json
{
  "cv_content": "Your full CV text here...",
  "job_description": "Full job description text here...",
  "max_keywords_to_add": 10,
  "use_spacy": true,
  "include_experience": true
}
```

**Request Parameters**:
- `cv_content` (string, required): The full text content of the CV
- `job_description` (string, required): The full text content of the job description
- `max_keywords_to_add` (integer, default: 10): Maximum keywords to suggest adding
- `use_spacy` (boolean, default: true): Enable spaCy NLP processing
- `include_experience` (boolean, default: true): Include experience relevance analysis

**Response**:
```json
{
  "original_score": {
    "score": 60.0,
    "percentage": 60.0,
    "matched_required": 2,
    "total_required": 5,
    "matched_optional": 1,
    "total_optional": 4
  },
  "keywords_to_add": [
    "AWS",
    "Docker",
    "Kubernetes",
    "CI/CD"
  ],
  "keyword_placements": [
    {
      "keyword": "AWS",
      "section": "professional_summary",
      "suggestion": "Add to your professional summary or relevant project descriptions",
      "priority": "high"
    },
    {
      "keyword": "Docker",
      "section": "work_experience",
      "suggestion": "Include in your work experience descriptions",
      "priority": "high"
    }
  ],
  "improvement_summary": "Found 4 keywords to add that could improve your score to 80.0%",
  "estimated_new_score": {
    "score": 80.0,
    "percentage": 80.0,
    "matched_required": 4,
    "total_required": 5,
    "matched_optional": 3,
    "total_optional": 4
  }
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/improve \
  -H "Content-Type: application/json" \
  -d '{
    "cv_content": "John Doe...",
    "job_description": "We are looking for...",
    "max_keywords_to_add": 10
  }'
```

---

### 3. Skill Matching

**Endpoint**: `POST /api/v1/match-skills`

Extracts and matches technical and soft skills between CV and job description.

**Request Body**:
```json
{
  "cv_content": "Your full CV text here...",
  "job_description": "Full job description text here...",
  "normalize_skills": true
}
```

**Request Parameters**:
- `cv_content` (string, required): The full text content of the CV
- `job_description` (string, required): The full text content of the job description
- `normalize_skills` (boolean, default: true): Normalize skills for better matching

**Response**:
```json
{
  "cv_skills": [
    {
      "skill": "Python",
      "normalized_skill": "python",
      "is_technical": true
    }
  ],
  "jd_skills": [
    {
      "skill": "Python",
      "normalized_skill": "python",
      "is_technical": true
    }
  ],
  "matched_skills": [
    {
      "skill": "Python",
      "match_type": "exact",
      "confidence": 0.95
    }
  ],
  "missing_skills": ["Kubernetes", "AWS"],
  "skill_match_percentage": 71.4,
  "summary": "Skill Match: 71.4%. You have 5/7 of the required skills."
}
```

**Example JavaScript**:
```javascript
const response = await fetch('http://localhost:8000/api/v1/match-skills', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    cv_content: cvText,
    job_description: jdText,
    normalize_skills: true
  })
});

const data = await response.json();
console.log(`Skill Match: ${data.skill_match_percentage}%`);
console.log(`Missing Skills: ${data.missing_skills.join(', ')}`);
```

---

### 4. Health Check

**Endpoint**: `GET /health`

Simple health check endpoint for monitoring API availability.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "api_ready": true
}
```

---

## Integration Examples

### React Frontend Example

```javascript
import React, { useState } from 'react';

const CVAnalyzer = () => {
  const [cvContent, setCvContent] = useState('');
  const [jdContent, setJdContent] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeCv = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/analyze`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cv_content: cvContent,
            job_description: jdContent
          })
        }
      );
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error analyzing CV:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea 
        value={cvContent}
        onChange={(e) => setCvContent(e.target.value)}
        placeholder="Paste your CV here..."
      />
      <textarea 
        value={jdContent}
        onChange={(e) => setJdContent(e.target.value)}
        placeholder="Paste job description here..."
      />
      <button onClick={analyzeCv} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze CV'}
      </button>
      
      {results && (
        <div>
          <h2>ATS Score: {results.ats_score.percentage.toFixed(1)}%</h2>
          <p>{results.analysis_summary}</p>
          {/* Display more results */}
        </div>
      )}
    </div>
  );
};

export default CVAnalyzer;
```

### Python Client Example

```python
import requests
import json

class ATSCVMakerClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_cv(self, cv_content, job_description, **kwargs):
        """Analyze CV against job description"""
        response = requests.post(
            f"{self.base_url}/api/v1/analyze",
            json={
                "cv_content": cv_content,
                "job_description": job_description,
                **kwargs
            }
        )
        return response.json()
    
    def improve_cv(self, cv_content, job_description, **kwargs):
        """Get CV improvement recommendations"""
        response = requests.post(
            f"{self.base_url}/api/v1/improve",
            json={
                "cv_content": cv_content,
                "job_description": job_description,
                **kwargs
            }
        )
        return response.json()
    
    def match_skills(self, cv_content, job_description, **kwargs):
        """Analyze skill matching"""
        response = requests.post(
            f"{self.base_url}/api/v1/match-skills",
            json={
                "cv_content": cv_content,
                "job_description": job_description,
                **kwargs
            }
        )
        return response.json()

# Usage
client = ATSCVMakerClient()
with open('cv.txt') as f:
    cv = f.read()
with open('jd.txt') as f:
    jd = f.read()

results = client.analyze_cv(cv, jd)
print(f"ATS Score: {results['ats_score']['percentage']}%")
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: Request successful
- `422 Unprocessable Entity`: Invalid request format
- `500 Internal Server Error`: Server-side error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS (for frontend access)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# LLM Keys (for AI-powered analysis)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Environment
ENVIRONMENT=development
```

### CORS Configuration

By default, CORS is enabled for common development URLs. To allow your frontend:

1. Update `CORS_ORIGINS` in `.env` to include your frontend URL
2. Restart the API server
3. Frontend requests will now be allowed

Example for React on port 3000:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Performance Tips

1. **CV Content**: For best results, use plain text CV content rather than formatted documents
2. **Job Descriptions**: Include full JD content for comprehensive analysis
3. **spaCy Processing**: Set `use_spacy: false` for faster response times on large texts (slightly less accurate)
4. **Caching**: Consider caching results for the same CV/JD combinations on your frontend

---

## Troubleshooting

### API won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use a different port
python -m uvicorn src.ats_cv_maker.api.app:app --port 8001
```

### CORS errors in frontend
- Ensure your frontend URL is in `CORS_ORIGINS` in `.env`
- Restart the API server after changing environment variables
- Check browser console for exact CORS error

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### Memory issues with large CVs
- Process smaller CV sections separately
- Set `use_spacy: false` to reduce memory usage

---

## Next Steps for SaaS

To complete your SaaS setup, consider:

1. **Database**: Add PostgreSQL for storing user CVs, analyses, and usage history
2. **Authentication**: Implement JWT authentication with user accounts
3. **File Upload**: Add PDF/DOC file upload support instead of text input
4. **Caching**: Add Redis for caching common analyses
5. **Rate Limiting**: Implement rate limiting to prevent API abuse
6. **Logging**: Add structured logging for analytics
7. **Monitoring**: Set up health checks and error monitoring (Sentry)
8. **Deployment**: Deploy to cloud (AWS, GCP, Azure, Heroku)

See [SAAS_SETUP.md](./docs/SAAS_SETUP.md) for detailed setup instructions.
