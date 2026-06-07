#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all endpoints: /health, /analyze, /improve, /match-skills
"""

import requests
import json
import base64
import time
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

# Sample CV text for testing
SAMPLE_CV_TEXT = """
John Doe
Email: john.doe@example.com | Phone: (555) 123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Senior Software Engineer with 5+ years of experience in full-stack web development.
Proficient in Python, JavaScript, and cloud technologies. Strong background in 
building scalable applications and leading development teams.

SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java
Frameworks: React, Node.js, Django, Flask, Express
Databases: PostgreSQL, MongoDB, Redis
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD
Tools: Git, Jenkins, JIRA

WORK EXPERIENCE
Senior Software Engineer | Tech Company Inc. | 2020 - Present
- Led development of microservices architecture using Python and Django
- Implemented CI/CD pipelines reducing deployment time by 40%
- Mentored junior developers and conducted code reviews
- Built RESTful APIs serving 1M+ requests daily

Software Engineer | StartUp Co. | 2018 - 2020
- Developed React-based frontend applications
- Implemented real-time features using WebSockets
- Collaborated with product team on feature specifications

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2014 - 2018
GPA: 3.8/4.0

PROJECTS
E-commerce Platform
- Built full-stack e-commerce platform using MERN stack
- Integrated Stripe payment processing
- Implemented inventory management system

CERTIFICATIONS
AWS Certified Solutions Architect
Certified Scrum Master (CSM)
"""

# Sample Job Description for testing
SAMPLE_JD_TEXT = """
Senior Full-Stack Engineer

We are seeking a talented Senior Full-Stack Engineer to join our growing team.

REQUIRED QUALIFICATIONS:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with React and Node.js
- Knowledge of Docker and Kubernetes
- Experience with AWS cloud services
- Bachelor's degree in Computer Science or related field
- Excellent problem-solving and communication skills

PREFERRED QUALIFICATIONS:
- Experience with TypeScript
- Knowledge of GraphQL
- Experience with microservices architecture
- Familiarity with CI/CD pipelines
- AWS certifications

RESPONSIBILITIES:
- Design and develop scalable web applications
- Collaborate with cross-functional teams
- Mentor junior developers
- Participate in code reviews
- Contribute to technical architecture decisions

BENEFITS:
- Competitive salary
- Health insurance
- 401(k) matching
- Remote work options
"""

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_health_endpoint():
    """Test /health endpoint"""
    print_section("Testing /health Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Health check successful")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   API Ready: {data.get('api_ready')}")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_root_endpoint():
    """Test / root endpoint"""
    print_section("Testing / Root Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Root endpoint successful")
            print(f"   Message: {data.get('message')}")
            print(f"   Endpoints: {list(data.get('endpoints', {}).keys())}")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_analyze_endpoint():
    """Test /api/v1/analyze endpoint"""
    print_section("Testing /api/v1/analyze Endpoint")
    
    payload = {
        "cv_content": SAMPLE_CV_TEXT,
        "job_description": SAMPLE_JD_TEXT,
        "use_spacy": True,
        "include_skills": True,
        "include_experience": True,
        "max_keywords": 50
    }
    
    try:
        print("Sending request (this may take 10-30 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze",
            json=payload,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Analysis completed in {elapsed:.1f}s")
            
            # Print key results
            if 'ats_score' in data:
                ats = data['ats_score']
                print(f"\n   📊 ATS Score: {ats.get('percentage', 0):.1f}%")
                print(f"   Required: {ats.get('matched_required', 0)}/{ats.get('total_required', 0)}")
                print(f"   Optional: {ats.get('matched_optional', 0)}/{ats.get('total_optional', 0)}")
            
            if 'rated_keywords' in data:
                print(f"\n   🔑 Keywords:")
                print(f"   Required: {len(data['rated_keywords'].get('required', []))} keywords")
                print(f"   Optional: {len(data['rated_keywords'].get('optional', []))} keywords")
            
            if 'skill_score' in data and data['skill_score']:
                skill = data['skill_score']
                print(f"\n   🎯 Skills:")
                print(f"   Match: {skill.get('skill_match_percentage', 0):.1f}%")
                print(f"   Matched: {len(skill.get('matched_skills', []))} skills")
                print(f"   Missing: {len(skill.get('missing_skills', []))} skills")
            
            if 'experience_score' in data and data['experience_score']:
                exp = data['experience_score']
                print(f"\n   💼 Experience:")
                print(f"   Relevance: {exp.get('experience_relevance_score', 0):.1f}%")
                print(f"   Count: {exp.get('experience_count', 0)} positions")
            
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_improve_endpoint():
    """Test /api/v1/improve endpoint"""
    print_section("Testing /api/v1/improve Endpoint")
    
    payload = {
        "cv_content": SAMPLE_CV_TEXT,
        "job_description": SAMPLE_JD_TEXT,
        "max_keywords_to_add": 10,
        "use_spacy": True,
        "include_experience": True
    }
    
    try:
        print("Sending request (this may take 30-60 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/improve",
            json=payload,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Improvement completed in {elapsed:.1f}s")
            
            # Print key results
            if 'original_score' in data:
                orig = data['original_score']
                print(f"\n   📊 Original Score: {orig.get('percentage', 0):.1f}%")
            
            if 'estimated_new_score' in data:
                new = data['estimated_new_score']
                print(f"   📈 Estimated New Score: {new.get('percentage', 0):.1f}%")
            
            if 'keywords_to_add' in data:
                keywords = data['keywords_to_add']
                print(f"\n   ➕ Keywords to Add: {len(keywords)}")
                if keywords:
                    print(f"   {', '.join(keywords[:5])}")
            
            if 'keyword_placements' in data:
                placements = data['keyword_placements']
                print(f"\n   📍 Placement Suggestions: {len(placements)}")
            
            if 'improved_pdf_base64' in data and data['improved_pdf_base64']:
                pdf_size = len(data['improved_pdf_base64'])
                print(f"\n   📄 PDF Generated: {pdf_size:,} bytes (base64)")
            else:
                print(f"\n   📄 PDF: Not generated")
            
            print(f"\n   💡 Summary: {data.get('improvement_summary', 'N/A')}")
            
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_match_skills_endpoint():
    """Test /api/v1/match-skills endpoint"""
    print_section("Testing /api/v1/match-skills Endpoint")
    
    payload = {
        "cv_content": SAMPLE_CV_TEXT,
        "job_description": SAMPLE_JD_TEXT,
        "normalize_skills": True
    }
    
    try:
        print("Sending request (this may take 15-30 seconds)...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/match-skills",
            json=payload,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Skill matching completed in {elapsed:.1f}s")
            
            # Print key results
            print(f"\n   🎯 Match Percentage: {data.get('skill_match_percentage', 0):.1f}%")
            
            if 'cv_skills' in data:
                print(f"   CV Skills: {len(data['cv_skills'])} found")
                
            if 'jd_skills' in data:
                print(f"   JD Skills: {len(data['jd_skills'])} required")
            
            if 'matched_skills' in data:
                matched = data['matched_skills']
                print(f"\n   ✅ Matched Skills: {len(matched)}")
                if matched:
                    print(f"   {', '.join([s.get('cv_skill', '') for s in matched[:5]])}")
            
            if 'missing_skills' in data:
                missing = data['missing_skills']
                print(f"\n   ❌ Missing Skills: {len(missing)}")
                if missing:
                    print(f"   {', '.join(missing[:5])}")
            
            print(f"\n   📝 {data.get('summary', 'N/A')}")
            
            return True
        else:
            print_result(False, f"HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  ATS CV MAKER - API ENDPOINT TESTING")
    print("=" * 80)
    print(f"\nTesting API at: {API_BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Health Endpoint": test_health_endpoint(),
        "Root Endpoint": test_root_endpoint(),
        "Analyze Endpoint": test_analyze_endpoint(),
        "Improve Endpoint": test_improve_endpoint(),
        "Match Skills Endpoint": test_match_skills_endpoint(),
    }
    
    # Summary
    print_section("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'=' * 80}")
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'=' * 80}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
