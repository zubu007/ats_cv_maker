# SaaS Setup Guide - ATS CV Maker

Complete guide for building a SaaS product using the ATS CV Maker API.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React/Vue/Next.js)                 │
│                                                                  │
│  - CV Upload/Paste                                              │
│  - Job Description Upload/Paste                                 │
│  - Results Dashboard                                            │
│  - User Dashboard                                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend (API Layer)                   │
│                                                                  │
│  - Authentication & Authorization                               │
│  - Rate Limiting                                                │
│  - Request Validation                                           │
│  - Response Formatting                                          │
│  - Error Handling                                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────┐   ┌──────────▼────────┐   ┌────▼─────────┐
│  Database  │   │  ATS CV Maker     │   │  Cache Layer │
│ (PostgreSQL)   │  Services         │   │ (Redis)      │
│            │   │ (Core Logic)      │   │              │
└────────────┘   └───────────────────┘   └──────────────┘
```

## Phase 1: Basic SaaS Setup (Weeks 1-2)

### 1.1 Database Setup

#### Install PostgreSQL
```bash
# macOS with Homebrew
brew install postgresql@15

# Or use Docker
docker run --name ats-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=ats_cv_maker \
  -p 5432:5432 \
  -d postgres:15
```

#### Create Database Models

Create `src/ats_cv_maker/models/database.py`:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ats_cv_maker")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

class CVAnalysis(Base):
    __tablename__ = "cv_analyses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    cv_content = Column(Text)
    job_description = Column(Text)
    ats_score = Column(Integer)
    results = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True, unique=True)
    plan = Column(String)  # 'free', 'pro', 'enterprise'
    stripe_customer_id = Column(String)
    status = Column(String)  # 'active', 'cancelled'
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)
```

### 1.2 User Authentication

Install required packages:
```bash
pip install python-jose[cryptography] passlib[bcrypt] 
```

Create `src/ats_cv_maker/auth/auth.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
```

### 1.3 Rate Limiting

Install:
```bash
pip install slowapi
```

Add to API:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/analyze")
@limiter.limit("10/minute")
async def analyze_cv(request: Request, data: CVAnalysisRequest):
    # Your endpoint code
    pass
```

### 1.4 API Keys (Alternative to Database Auth)

For quick MVP:

```python
from fastapi import APIKey, HTTPException, Depends
from fastapi.security import APIKeyCookie

api_keys = {
    "sk_demo_12345": {"name": "Demo Account", "tier": "free"},
    "sk_pro_67890": {"name": "Pro Account", "tier": "pro"}
}

def verify_api_key(api_key: str) -> dict:
    if api_key not in api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_keys[api_key]

@app.post("/api/v1/analyze")
async def analyze_cv(request: CVAnalysisRequest, api_key: str = Header(...)):
    account = verify_api_key(api_key)
    # Your endpoint code
    pass
```

## Phase 2: Enhanced Features (Weeks 3-4)

### 2.1 File Upload Support

Install:
```bash
pip install python-multipart pdf2image PyPDF2
```

Create upload endpoint:

```python
from fastapi import UploadFile, File
import PyPDF2

@app.post("/api/v1/upload-analyze")
async def upload_and_analyze(
    cv_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    api_key: str = Header(...)
):
    account = verify_api_key(api_key)
    
    # Read CV
    cv_content = await cv_file.read()
    if cv_file.content_type == "application/pdf":
        cv_content = extract_pdf_text(cv_content)
    else:
        cv_content = cv_content.decode()
    
    # Read JD
    jd_content = await jd_file.read()
    if jd_file.content_type == "application/pdf":
        jd_content = extract_pdf_text(jd_content)
    else:
        jd_content = jd_content.decode()
    
    # Call existing analyze function
    return await analyze_cv(CVAnalysisRequest(
        cv_content=cv_content,
        job_description=jd_content
    ))

def extract_pdf_text(pdf_bytes: bytes) -> str:
    pdf = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text
```

### 2.2 Result Caching

Install:
```bash
pip install redis
```

Add Redis caching:

```python
import redis
import json
from hashlib import sha256

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cache_key(cv_content: str, jd_content: str) -> str:
    combined = cv_content + jd_content
    return f"analysis:{sha256(combined.encode()).hexdigest()}"

@app.post("/api/v1/analyze")
async def analyze_cv(request: CVAnalysisRequest, api_key: str = Header(...)):
    account = verify_api_key(api_key)
    cache_key = get_cache_key(request.cv_content, request.job_description)
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Run analysis
    result = service.analyze_cv(...)
    
    # Cache for 7 days
    redis_client.setex(cache_key, 604800, json.dumps(result))
    
    return result
```

### 2.3 Usage Tracking

Add usage logging to database:

```python
from src.ats_cv_maker.models.database import SessionLocal, UserUsage

def log_usage(user_id: int, endpoint: str, tokens_used: int = 0):
    db = SessionLocal()
    usage = UserUsage(
        user_id=user_id,
        endpoint=endpoint,
        tokens_used=tokens_used,
        timestamp=datetime.utcnow()
    )
    db.add(usage)
    db.commit()
```

## Phase 3: Monetization (Weeks 5-6)

### 3.1 Stripe Integration

Install:
```bash
pip install stripe
```

Create subscription management:

```python
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.post("/api/v1/subscribe")
async def create_subscription(
    plan: str,  # 'pro' or 'enterprise'
    user_id: int,
    api_key: str = Header(...)
):
    account = verify_api_key(api_key)
    
    # Create Stripe customer
    customer = stripe.Customer.create(
        email=account.email,
        metadata={"user_id": user_id}
    )
    
    # Create subscription
    subscription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": STRIPE_PRICE_IDS[plan]}]
    )
    
    # Save to database
    db.query(Subscription).filter(...).update({
        "stripe_customer_id": customer.id,
        "stripe_subscription_id": subscription.id,
        "plan": plan,
        "status": "active"
    })
    
    return {
        "subscription_id": subscription.id,
        "status": subscription.status,
        "customer_id": customer.id
    }
```

### 3.2 Plan Limits

```python
PLAN_LIMITS = {
    "free": {
        "analyses_per_month": 5,
        "cv_size_mb": 2,
        "features": ["basic_analysis"]
    },
    "pro": {
        "analyses_per_month": 100,
        "cv_size_mb": 10,
        "features": ["basic_analysis", "skill_matching", "improvement_suggestions"]
    },
    "enterprise": {
        "analyses_per_month": float('inf'),
        "cv_size_mb": 50,
        "features": ["*"]
    }
}

async def check_plan_limits(user_id: int, endpoint: str):
    user = db.query(User).filter(User.id == user_id).first()
    subscription = db.query(Subscription).filter(...).first()
    plan = subscription.plan if subscription else "free"
    limits = PLAN_LIMITS[plan]
    
    if endpoint == "analyze":
        usage = get_monthly_usage(user_id)
        if usage >= limits["analyses_per_month"]:
            raise HTTPException(status_code=429, detail="Plan limit reached")
```

## Phase 4: Deployment (Weeks 7-8)

### 4.1 Production Environment Setup

Create `.env.production`:

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@prod-db.example.com/ats_cv_maker

# Redis
REDIS_URL=redis://prod-redis.example.com:6379

# Security
SECRET_KEY=generate-with-openssl-rand-hex-32
CORS_ORIGINS=https://yourdomain.com

# LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### 4.2 Docker Production Build

Update `Dockerfile`:

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --user --no-cache-dir -e .

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
RUN python -m spacy download en_core_web_sm
CMD ["uvicorn", "src.ats_cv_maker.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3 Deploy to Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create ats-cv-maker

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Set config
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set OPENAI_API_KEY=your_key

# Deploy
git push heroku main

# Monitor
heroku logs --tail
```

### 4.4 AWS Deployment (Alternative)

```bash
# Create EC2 instance
aws ec2 run-instances \
  --image-id ami-0c94855ba95c574c8 \
  --instance-type t3.medium \
  --key-name your-key

# SSH into instance
ssh -i your-key.pem ec2-user@your-instance

# Setup
sudo yum update
sudo yum install python3.11 docker git
sudo usermod -aG docker ec2-user

# Clone and run
git clone your-repo
cd ats_cv_maker
docker-compose -f docker-compose.prod.yml up -d
```

### 4.5 Monitoring & Logging

Install:
```bash
pip install sentry-sdk
```

Add to app:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0
)
```

## Frontend Setup Examples

### React + Vite Template

```bash
npm create vite@latest ats-frontend -- --template react
cd ats-frontend
npm install axios react-router-dom zustand

# Create .env
echo "VITE_API_URL=http://localhost:8000" > .env
```

### Next.js Template

```bash
npx create-next-app@latest ats-frontend
cd ats-frontend
npm install stripe @stripe/react-js swr

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_STRIPE_KEY=pk_test_..." >> .env.local
```

## Testing Before Launch

### Load Testing

```bash
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, constant

class CVAnalysisUser(HttpUser):
    wait_time = constant(1)
    
    @task
    def analyze_cv(self):
        self.client.post("/api/v1/analyze", json={
            "cv_content": "Sample CV...",
            "job_description": "Sample JD..."
        })

# Run: locust -f locustfile.py --host=http://localhost:8000
EOF
```

### Security Checklist

- [ ] HTTPS enabled in production
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] API key rotation enabled
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] CSRF protection
- [ ] Data encryption at rest
- [ ] Regular backups
- [ ] Error messages don't leak sensitive info
- [ ] Security headers configured

## Monitoring & Metrics

Key metrics to track:

1. **API Performance**
   - Response time by endpoint
   - Error rates
   - Uptime %

2. **Business Metrics**
   - Monthly active users (MAU)
   - Conversion rate (free → paid)
   - Monthly recurring revenue (MRR)
   - Churn rate

3. **Technical Metrics**
   - Database query performance
   - Cache hit rate
   - Infrastructure costs
   - Token usage (LLM calls)

## Scaling Checklist

As you grow:

- [ ] Implement database connection pooling
- [ ] Add CDN for static assets
- [ ] Horizontal scaling for API servers
- [ ] Database read replicas
- [ ] Message queue (Celery) for async tasks
- [ ] ML model optimization
- [ ] Batch processing for large analyses

## Conclusion

You now have a complete SaaS platform! The key is to:

1. Start with Phase 1 (API + Basic Auth)
2. Get paying customers early
3. Iterate based on feedback
4. Scale as revenue grows

Good luck! 🚀
