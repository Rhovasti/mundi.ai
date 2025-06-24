#!/usr/bin/env python3
"""Simple API test via curl"""

import subprocess
import json

def test_api():
    # Test basic endpoint first
    print("Testing basic API...")
    result = subprocess.run([
        "curl", "-s", "http://localhost:8000/api/basemaps"
    ], capture_output=True, text=True)
    
    print(f"Status code check: curl -I http://localhost:8000/api/basemaps")
    status_result = subprocess.run([
        "curl", "-I", "http://localhost:8000/api/basemaps"
    ], capture_output=True, text=True)
    
    print(status_result.stdout.split('\n')[0])
    
    if result.returncode == 0:
        print(f"✅ GET /api/basemaps works: {result.stdout}")
    else:
        print(f"❌ GET failed: {result.stderr}")

if __name__ == "__main__":
    test_api()