#!/usr/bin/env python3
"""
Quick deployment verification script
Tests all critical endpoints and CORS configuration
"""

import requests
import sys

# Configuration
BACKEND_URL = "https://natural-presence-production.up.railway.app"
FRONTEND_URLS = [
    "https://next-js-14-front-end-for-chat-plast.vercel.app",
    "https://video-chat-frontend-ruby.vercel.app",
    "https://next-js-14-front-end-for-chat-plaster-repository-7vb273qqo.vercel.app",
]

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"? {description}: OK")
            return True
        else:
            print(f"? {description}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"? {description}: {str(e)}")
        return False

def test_cors(backend_url, frontend_url):
    """Test CORS headers"""
    try:
        headers = {"Origin": frontend_url}
        response = requests.options(f"{backend_url}/health", headers=headers, timeout=10)
        
        if "access-control-allow-origin" in response.headers:
            print(f"? CORS for {frontend_url}: OK")
            return True
        else:
            print(f"??  CORS for {frontend_url}: Headers not found")
            return False
    except Exception as e:
        print(f"? CORS for {frontend_url}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("FastAPI Video Chat - Deployment Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test backend endpoints
    print("?? Testing Backend Endpoints...")
    all_passed &= test_endpoint(f"{BACKEND_URL}/", "Root endpoint")
    all_passed &= test_endpoint(f"{BACKEND_URL}/health", "Health check")
    all_passed &= test_endpoint(f"{BACKEND_URL}/docs", "API docs")
    all_passed &= test_endpoint(f"{BACKEND_URL}/chat", "Chat interface")
    print()
    
    # Test CORS
    print("?? Testing CORS Configuration...")
    for frontend_url in FRONTEND_URLS:
        all_passed &= test_cors(BACKEND_URL, frontend_url)
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("? ALL TESTS PASSED - Deployment is healthy!")
        sys.exit(0)
    else:
        print("??  SOME TESTS FAILED - Check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()
