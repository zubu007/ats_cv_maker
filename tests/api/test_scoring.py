import pytest
from fastapi.testclient import TestClient
import base64
import os

# Add the project root to the path so we can import the app
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.main import app  # Assuming your FastAPI app instance is in backend/src.main

client = TestClient(app)

# --- Test Data ---
CV_PATH = os.path.join(os.path.dirname(__file__), '..', 'cv.pdf')
JOB_DESCRIPTION = """
Job Title: Senior Python Developer

We are looking for an experienced Python Developer to join our team.

Responsibilities:
- Design and develop high-quality software solutions.
- Collaborate with cross-functional teams.
- Write clean, maintainable, and efficient code.

Required Skills:
- 5+ years of experience with Python.
- Strong knowledge of FastAPI and Django.
- Experience with PostgreSQL and Docker.
- Excellent problem-solving skills.

Preferred Skills:
- Experience with React.
- Knowledge of AWS.
"""

def get_base64_encoded_file(file_path):
    if not os.path.exists(file_path):
        # Create a dummy file if it doesn't exist
        with open(file_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /MediaBox [0 0 612 792] /Parent 2 0 R /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 53 >>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello, World!) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000118 00000 n \n0000000213 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n309\n%%EOF")

    with open(file_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

# --- Test Cases ---

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_score_cv_endpoint_success():
    """
    Tests the /api/v1/score endpoint with valid inputs.
    """
    cv_base64 = get_base64_encoded_file(CV_PATH)
    
    request_payload = {
        "cv_content": cv_base64,
        "job_description": JOB_DESCRIPTION
    }
    
    response = client.post("/api/v1/score", json=request_payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "jd_summary" in data
    assert "score" in data
    assert isinstance(data["score"], float)
    assert 0 <= data["score"] <= 100
    
    assert "task_description" in data["jd_summary"]
    assert "candidate_requirements" in data["jd_summary"]
    assert isinstance(data["jd_summary"]["task_description"], list)
    assert isinstance(data["jd_summary"]["candidate_requirements"], list)

def test_score_cv_endpoint_no_cv():
    """
    Tests the /api/v1/score endpoint with missing CV content.
    """
    request_payload = {
        "cv_content": "",
        "job_description": JOB_DESCRIPTION
    }
    
    response = client.post("/api/v1/score", json=request_payload)
    
    # Based on the current implementation, this will likely raise an exception
    # that is caught and returned as a 500 error.
    # A more robust implementation would have specific validation and a 4xx error.
    assert response.status_code != 200

def test_score_cv_endpoint_no_jd():
    """
    Tests the /api/v1/score endpoint with missing job description.
    """
    cv_base64 = get_base64_encoded_file(CV_PATH)
    
    request_payload = {
        "cv_content": cv_base64,
        "job_description": ""
    }
    
    response = client.post("/api/v1/score", json=request_payload)
    assert response.status_code != 200

def test_analyze_endpoint():
    """
    Basic test for the analyze endpoint to ensure it still functions.
    """
    cv_base64 = get_base64_encoded_file(CV_PATH)
    
    request_payload = {
        "cv_content": cv_base64,
        "job_description": JOB_DESCRIPTION,
        "include_skills": True,
        "include_experience": True,
        "max_keywords": 20
    }
    
    response = client.post("/api/v1/analyze", json=request_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "ats_score" in data
    assert "section_comparisons" in data

# To run this test:
# 1. Make sure you have pytest and httpx installed:
#    pip install pytest httpx
# 2. Run pytest from the root of the project:
#    pytest
