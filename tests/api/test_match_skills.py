#!/usr/bin/env python3
"""Quick test for match-skills endpoint"""

import requests
import time

API_URL = "http://localhost:8000/api/v1/match-skills"

payload = {
    "cv_content": "Python, JavaScript, React, Node.js, Docker",
    "job_description": "Looking for Python, React, TypeScript, and AWS skills",
    "normalize_skills": False  # Disable normalization for speed
}

print("Testing /api/v1/match-skills endpoint (without normalization)...")
print("Sending request...")

start = time.time()
try:
    response = requests.post(API_URL, json=payload, timeout=30)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS (took {elapsed:.1f}s)")
        print(f"\nResults:")
        print(f"  Match Percentage: {data.get('skill_match_percentage', 0):.1f}%")
        print(f"  CV Skills: {len(data.get('cv_skills', []))}")
        print(f"  JD Skills: {len(data.get('jd_skills', []))}")
        print(f"  Matched: {len(data.get('matched_skills', []))}")
        print(f"  Missing: {len(data.get('missing_skills', []))}")
        
        if data.get('matched_skills'):
            print(f"\n  Matched Skills:")
            for m in data['matched_skills'][:5]:
                if isinstance(m, dict):
                    print(f"    - {m.get('cv_skill', m)} → {m.get('jd_skill', '')}")
                else:
                    print(f"    - {m}")
        
        if data.get('missing_skills'):
            print(f"\n  Missing Skills:")
            for m in data['missing_skills'][:5]:
                print(f"    - {m}")
    else:
        print(f"\n❌ FAILED: HTTP {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    elapsed = time.time() - start
    print(f"\n❌ FAILED after {elapsed:.1f}s: {str(e)}")
