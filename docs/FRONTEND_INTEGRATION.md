# Frontend Integration Guide

Complete guide for building a frontend that uses the ATS CV Maker API.

## Frontend Architecture Recommendation

```
Frontend (React/Next.js/Vue)
├── Components
│   ├── CVUpload          # Upload/paste CV
│   ├── JobDescription    # Upload/paste JD
│   ├── AnalysisResults   # Display analysis
│   ├── Improvements      # Show recommendations
│   └── SkillMatcher      # Skill analysis
├── Services
│   └── atsApi.js         # API client
├── State Management      # Redux, Zustand, or Context
└── Pages
    ├── Dashboard
    ├── Analyzer
    └── Results
```

## 1. API Client Service

### React/JavaScript (`src/services/atsApi.js`)

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ATSCVMakerAPI {
  constructor(apiKey = null) {
    this.apiKey = apiKey;
    this.headers = {
      'Content-Type': 'application/json',
    };
    if (apiKey) {
      this.headers['X-API-Key'] = apiKey;
    }
  }

  async request(endpoint, method = 'GET', data = null) {
    const options = {
      method,
      headers: this.headers,
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
      }
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Analyze CV
  async analyzeCv(cvContent, jobDescription, options = {}) {
    return this.request('/api/v1/analyze', 'POST', {
      cv_content: cvContent,
      job_description: jobDescription,
      use_spacy: options.useSpacy !== false,
      include_skills: options.includeSkills !== false,
      include_experience: options.includeExperience !== false,
      max_keywords: options.maxKeywords || 50,
    });
  }

  // Get improvement suggestions
  async improveCv(cvContent, jobDescription, options = {}) {
    return this.request('/api/v1/improve', 'POST', {
      cv_content: cvContent,
      job_description: jobDescription,
      max_keywords_to_add: options.maxKeywordsToAdd || 10,
      use_spacy: options.useSpacy !== false,
      include_experience: options.includeExperience !== false,
    });
  }

  // Match skills
  async matchSkills(cvContent, jobDescription, options = {}) {
    return this.request('/api/v1/match-skills', 'POST', {
      cv_content: cvContent,
      job_description: jobDescription,
      normalize_skills: options.normalizeSkills !== false,
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export default new ATSCVMakerAPI();
```

## 2. React Component Examples

### CV Analysis Component

```javascript
// src/components/CVAnalyzer.jsx
import React, { useState } from 'react';
import atsApi from '../services/atsApi';
import './CVAnalyzer.css';

const CVAnalyzer = () => {
  const [cvContent, setCvContent] = useState('');
  const [jdContent, setJdContent] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('analyze');

  const handleAnalyze = async () => {
    if (!cvContent.trim() || !jdContent.trim()) {
      setError('Please fill in both CV and Job Description');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await atsApi.analyzeCv(cvContent, jdContent);
      setResults({ ...data, type: 'analysis' });
      setActiveTab('results');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleImprove = async () => {
    if (!cvContent.trim() || !jdContent.trim()) {
      setError('Please fill in both CV and Job Description');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await atsApi.improveCv(cvContent, jdContent);
      setResults({ ...data, type: 'improvement' });
      setActiveTab('results');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMatchSkills = async () => {
    if (!cvContent.trim() || !jdContent.trim()) {
      setError('Please fill in both CV and Job Description');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await atsApi.matchSkills(cvContent, jdContent);
      setResults({ ...data, type: 'skills' });
      setActiveTab('results');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cv-analyzer">
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'analyze' ? 'active' : ''}`}
          onClick={() => setActiveTab('analyze')}
        >
          Analyzer
        </button>
        <button 
          className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
          disabled={!results}
        >
          Results
        </button>
      </div>

      {activeTab === 'analyze' && (
        <div className="analyzer-panel">
          <div className="input-section">
            <div className="input-group">
              <label>Your CV</label>
              <textarea
                value={cvContent}
                onChange={(e) => setCvContent(e.target.value)}
                placeholder="Paste your CV text here..."
                rows={12}
              />
            </div>

            <div className="input-group">
              <label>Job Description</label>
              <textarea
                value={jdContent}
                onChange={(e) => setJdContent(e.target.value)}
                placeholder="Paste the job description here..."
                rows={12}
              />
            </div>
          </div>

          <div className="action-buttons">
            <button 
              onClick={handleAnalyze}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Analyzing...' : 'Analyze CV'}
            </button>
            <button 
              onClick={handleImprove}
              disabled={loading}
              className="btn btn-secondary"
            >
              {loading ? 'Improving...' : 'Get Improvements'}
            </button>
            <button 
              onClick={handleMatchSkills}
              disabled={loading}
              className="btn btn-secondary"
            >
              {loading ? 'Matching...' : 'Match Skills'}
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </div>
      )}

      {activeTab === 'results' && results && (
        <div className="results-panel">
          <ResultsDisplay results={results} />
        </div>
      )}
    </div>
  );
};

// Results Display Component
const ResultsDisplay = ({ results }) => {
  if (results.type === 'analysis') {
    return (
      <div className="results">
        <div className="score-card">
          <h2>ATS Score</h2>
          <div className="score-value">
            {results.ats_score.percentage.toFixed(1)}%
          </div>
          <p className="score-details">
            {results.ats_score.matched_required} / {results.ats_score.total_required} required keywords
          </p>
        </div>

        <div className="keywords-section">
          <h3>Required Keywords</h3>
          <div className="keyword-list">
            {results.rated_keywords.required.slice(0, 10).map((kw, i) => (
              <span key={i} className="keyword required">{kw}</span>
            ))}
          </div>
        </div>

        <div className="keywords-section">
          <h3>Optional Keywords</h3>
          <div className="keyword-list">
            {results.rated_keywords.optional.slice(0, 10).map((kw, i) => (
              <span key={i} className="keyword optional">{kw}</span>
            ))}
          </div>
        </div>

        {results.skill_score && (
          <div className="skill-section">
            <h3>Skill Match: {results.skill_score.skill_match_percentage?.toFixed(1) || 'N/A'}%</h3>
            <p className="summary">{results.analysis_summary}</p>
          </div>
        )}
      </div>
    );
  }

  if (results.type === 'improvement') {
    return (
      <div className="results">
        <div className="improvement-card">
          <h2>CV Improvement Analysis</h2>
          <p className="summary">{results.improvement_summary}</p>

          <div className="score-comparison">
            <div className="score-box">
              <h4>Current Score</h4>
              <div className="score">{results.original_score.percentage.toFixed(1)}%</div>
            </div>
            <div className="arrow">→</div>
            <div className="score-box">
              <h4>Potential Score</h4>
              <div className="score">{results.estimated_new_score.percentage.toFixed(1)}%</div>
            </div>
          </div>

          <div className="keywords-to-add">
            <h3>Keywords to Add</h3>
            {results.keywords_to_add.map((kw, i) => (
              <div key={i} className="keyword-suggestion">
                <strong>{kw}</strong>
                <em>High Priority</em>
              </div>
            ))}
          </div>

          <div className="placements">
            <h3>Suggested Placements</h3>
            {results.keyword_placements.slice(0, 5).map((p, i) => (
              <div key={i} className="placement">
                <h4>{p.keyword}</h4>
                <p className="section">Section: {p.section}</p>
                <p className="suggestion">{p.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (results.type === 'skills') {
    return (
      <div className="results">
        <div className="skill-match-card">
          <h2>Skill Matching Analysis</h2>
          <div className="skill-score">
            {results.skill_match_percentage.toFixed(1)}%
            <span className="label">Match</span>
          </div>
          <p className="summary">{results.summary}</p>

          <div className="skills-section">
            <h3>Your Skills ({results.cv_skills.length})</h3>
            <div className="skill-tags">
              {results.cv_skills.slice(0, 15).map((s, i) => (
                <span key={i} className="skill-tag">{s.skill}</span>
              ))}
            </div>
          </div>

          <div className="skills-section">
            <h3>Required Skills ({results.jd_skills.length})</h3>
            <div className="skill-tags">
              {results.jd_skills.slice(0, 15).map((s, i) => (
                <span key={i} className="skill-tag required">{s.skill}</span>
              ))}
            </div>
          </div>

          {results.missing_skills.length > 0 && (
            <div className="missing-skills">
              <h3>Missing Skills</h3>
              <div className="skill-tags">
                {results.missing_skills.map((s, i) => (
                  <span key={i} className="skill-tag missing">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }
};

export default CVAnalyzer;
```

### Styling (`src/components/CVAnalyzer.css`)

```css
.cv-analyzer {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.tabs {
  display: flex;
  gap: 10px;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 20px;
}

.tab {
  padding: 12px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.tab.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

.tab:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.analyzer-panel {
  display: grid;
  gap: 20px;
}

.input-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-weight: 600;
  color: #333;
}

.input-group textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
  resize: vertical;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
}

.btn-secondary:hover:not(:disabled) {
  background: #d1d5db;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  padding: 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 4px;
  border-left: 4px solid #dc2626;
}

/* Results Styling */
.results {
  display: grid;
  gap: 20px;
}

.score-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 8px;
  text-align: center;
}

.score-card h2 {
  margin-top: 0;
  font-size: 14px;
  opacity: 0.9;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  margin: 10px 0;
}

.score-details {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.keywords-section {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
}

.keywords-section h3 {
  margin-top: 0;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.keyword {
  display: inline-block;
  padding: 8px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 14px;
}

.keyword.required {
  background: #dbeafe;
  border-color: #2563eb;
  color: #1e40af;
}

.keyword.optional {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

/* Improvement Styling */
.improvement-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.score-comparison {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin: 30px 0;
}

.score-box {
  background: #f9fafb;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  min-width: 150px;
}

.score-box h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.score-box .score {
  font-size: 32px;
  font-weight: bold;
  color: #2563eb;
}

.arrow {
  font-size: 24px;
  color: #999;
}

.keywords-to-add {
  margin-top: 30px;
}

.keyword-suggestion {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f0fdf4;
  border-left: 4px solid #16a34a;
  margin-bottom: 8px;
  border-radius: 4px;
}

.keyword-suggestion strong {
  color: #15803d;
}

.keyword-suggestion em {
  color: #16a34a;
  font-style: normal;
  font-weight: 600;
  font-size: 12px;
}

/* Skill Matching Styling */
.skill-score {
  font-size: 48px;
  font-weight: bold;
  color: #2563eb;
  text-align: center;
  margin: 20px 0;
}

.skill-score .label {
  display: block;
  font-size: 14px;
  color: #666;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 15px 0;
}

.skill-tag {
  display: inline-block;
  padding: 8px 12px;
  background: #e0e7ff;
  color: #3730a3;
  border-radius: 4px;
  font-size: 13px;
}

.skill-tag.required {
  background: #dbeafe;
  color: #0c4a6e;
}

.skill-tag.missing {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 768px) {
  .input-section {
    grid-template-columns: 1fr;
  }

  .score-comparison {
    flex-direction: column;
  }
}
```

## 3. Next.js Example

If using Next.js, create an API route wrapper:

```javascript
// pages/api/analyze.js
import atsApi from '../../services/atsApi';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const result = await atsApi.analyzeCv(
      req.body.cvContent,
      req.body.jobDescription
    );
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

## 4. Vue.js Example

```javascript
// src/services/atsApi.js (Vue)
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  analyzeCv(cvContent, jobDescription, options = {}) {
    return apiClient.post('/api/v1/analyze', {
      cv_content: cvContent,
      job_description: jobDescription,
      ...options,
    });
  },

  improveCv(cvContent, jobDescription, options = {}) {
    return apiClient.post('/api/v1/improve', {
      cv_content: cvContent,
      job_description: jobDescription,
      ...options,
    });
  },

  matchSkills(cvContent, jobDescription, options = {}) {
    return apiClient.post('/api/v1/match-skills', {
      cv_content: cvContent,
      job_description: jobDescription,
      ...options,
    });
  },
};
```

## 5. Testing

### Unit Tests (Jest + React Testing Library)

```javascript
// src/components/__tests__/CVAnalyzer.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CVAnalyzer from '../CVAnalyzer';
import atsApi from '../../services/atsApi';

jest.mock('../../services/atsApi');

describe('CVAnalyzer', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders analyzer form', () => {
    render(<CVAnalyzer />);
    expect(screen.getByPlaceholderText(/paste your cv/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/paste the job description/i)).toBeInTheDocument();
  });

  test('handles CV analysis', async () => {
    atsApi.analyzeCv.mockResolvedValue({
      ats_score: { percentage: 80 },
      rated_keywords: { required: [], optional: [] },
      analysis_summary: 'Good match',
    });

    render(<CVAnalyzer />);

    fireEvent.change(screen.getByPlaceholderText(/paste your cv/i), {
      target: { value: 'Sample CV' },
    });
    fireEvent.change(screen.getByPlaceholderText(/paste the job description/i), {
      target: { value: 'Sample JD' },
    });

    fireEvent.click(screen.getByText(/analyze cv/i));

    await waitFor(() => {
      expect(screen.getByText(/80/)).toBeInTheDocument();
    });
  });
});
```

## Configuration

### `.env.local` for React/Next.js

```
REACT_APP_API_URL=http://localhost:8000
# or
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### `.env` for Vue

```
VUE_APP_API_URL=http://localhost:8000
```

## Deployment Checklist

- [ ] API running in production
- [ ] Frontend environment variables configured
- [ ] CORS properly set up
- [ ] SSL/HTTPS enabled
- [ ] API key or auth tokens configured
- [ ] Error handling and logging
- [ ] Loading states
- [ ] Empty states
- [ ] Mobile responsive design
- [ ] Accessibility (a11y)
- [ ] Performance optimized
- [ ] Analytics integrated

## Next Steps

1. Choose your frontend framework (React, Vue, Next.js, etc.)
2. Copy the API client code for your framework
3. Build components using the examples above
4. Test with your API server running locally
5. Deploy frontend and API

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for more API details.
