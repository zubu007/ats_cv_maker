#!/usr/bin/env python3
"""
Test script for ATS CV Maker API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def test_health():
    """Test the health check endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("✓ Health endpoint working!")
            return True
        else:
            print(f"✗ Health endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("✓ Root endpoint working!")
            return True
        else:
            print(f"✗ Root endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_analyze():
    """Test the analyze endpoint"""
    print("\n=== Testing Analyze Endpoint ===")
    
    sample_cv = """
    John Smith
    Email: john@example.com | Phone: (123) 456-7890
    
    PROFESSIONAL SUMMARY
    Experienced Software Engineer with 5 years of experience in Python, JavaScript, and cloud technologies.
    
    SKILLS
    Python, JavaScript, AWS, Docker, PostgreSQL, React, REST APIs, Agile
    
    WORK EXPERIENCE
    Senior Software Engineer - Tech Corp (2022-Present)
    - Led development of microservices using Python and Docker
    - Improved API performance by 40%
    
    Software Engineer - StartUp Inc (2019-2022)
    - Developed web applications using React and Node.js
    - Built REST APIs for mobile clients
    """
    
    sample_jd = """
    Senior Python Developer
    
    Required Skills:
    - 5+ years Python development
    - AWS or GCP experience
    - Docker and Kubernetes
    - REST API design
    - PostgreSQL
    
    Preferred Skills:
    - React or Vue.js
    - Microservices architecture
    - CI/CD pipelines
    """
    
    payload = {
        "cv_content": sample_cv,
        "job_description": sample_jd,
        "use_spacy": True,
        "include_skills": True,
        "include_experience": True,
        "max_keywords": 50
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Analysis Results:")
            print(f"  - ATS Score: {data.get('ats_score', {}).get('percentage', 'N/A')}%")
            print(f"  - Matched Required: {data.get('ats_score', {}).get('matched_required', 0)}/{data.get('ats_score', {}).get('total_required', 0)}")
            print(f"  - CV Keywords Found: {len(data.get('cv_keywords', []))}")
            print(f"  - JD Keywords Found: {len(data.get('jd_keywords', []))}")
            print(f"  - Summary: {data.get('analysis_summary', 'N/A')}")
            print("✓ Analyze endpoint working!")
            return True
        else:
            print(f"✗ Analyze endpoint returned {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_improve():
    """Test the improve endpoint"""
    print("\n=== Testing Improve Endpoint ===")
    
    sample_cv = """
    Jane Doe
    jane@example.com
    
    EXPERIENCE
    Software Engineer at Tech Inc (2020-Present)
    - Worked on backend systems
    - Used Python and SQL
    """
    
    sample_jd = """
    Senior Full Stack Developer
    Required: Python, JavaScript, React, AWS, Docker, Kubernetes, microservices
    """
    
    payload = {
        "cv_content": sample_cv,
        "job_description": sample_jd,
        "max_keywords_to_add": 10,
        "use_spacy": True,
        "include_experience": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/improve", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Improvement Results:")
            print(f"  - Original Score: {data.get('original_score', {}).get('percentage', 'N/A')}%")
            print(f"  - Keywords to Add: {len(data.get('keywords_to_add', []))}")
            print(f"  - Keyword Placements: {len(data.get('keyword_placements', []))}")
            print(f"  - Summary: {data.get('improvement_summary', 'N/A')}")
            print("✓ Improve endpoint working!")
            return True
        else:
            print(f"✗ Improve endpoint returned {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_match_skills():
    """Test the match-skills endpoint"""
    print("\n=== Testing Match Skills Endpoint ===")
    
    sample_cv = """
    SKILLS
    - Python
    - JavaScript
    - React
    - Docker
    - PostgreSQL
    """
    
    sample_jd = """
    Required: Python, Go, Kubernetes, PostgreSQL, AWS
    Preferred: React, Docker, GraphQL
    """
    
    payload = {
        "cv_content": sample_cv,
        "job_description": sample_jd,
        "normalize_skills": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/match-skills", json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Skill Matching Results:")
            print(f"  - CV Skills Found: {len(data.get('cv_skills', []))}")
            print(f"  - JD Skills Required: {len(data.get('jd_skills', []))}")
            print(f"  - Matched Skills: {len(data.get('matched_skills', []))}")
            print(f"  - Skill Match Percentage: {data.get('skill_match_percentage', 0):.1f}%")
            print(f"  - Missing Skills: {len(data.get('missing_skills', []))}")
            print(f"  - Summary: {data.get('summary', 'N/A')}")
            print("✓ Match Skills endpoint working!")
            return True
        else:
            print(f"✗ Match Skills endpoint returned {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ATS CV Maker API Endpoint Testing")
    print("=" * 60)
    
    results = {
        "Health": test_health(),
        "Root": test_root(),
        "Analyze": test_analyze(),
        "Improve": test_improve(),
        "Match Skills": test_match_skills(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for endpoint, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{endpoint}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} endpoints working")
    
    if passed == total:
        print("\n🎉 All endpoints are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} endpoint(s) failed")

if __name__ == "__main__":
    main()
