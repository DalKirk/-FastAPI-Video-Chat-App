#!/usr/bin/env python3
"""
Quick verification that all modules can be imported correctly
Run this locally to verify the fix before Railway deployment
"""

import sys

def test_imports():
    """Test all critical imports"""
    print("?? Testing module imports...\n")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import utils
    try:
        import utils
        print("? import utils - SUCCESS")
        tests_passed += 1
    except Exception as e:
        print(f"? import utils - FAILED: {e}")
        tests_failed += 1
    
    # Test 2: Import utils.ai_endpoints
    try:
        from utils.ai_endpoints import ai_router
        print("? from utils.ai_endpoints import ai_router - SUCCESS")
        tests_passed += 1
    except Exception as e:
        print(f"? from utils.ai_endpoints import ai_router - FAILED: {e}")
        tests_failed += 1
    
    # Test 3: Import utils.claude_client
    try:
        from utils.claude_client import get_claude_client
        print("? from utils.claude_client import get_claude_client - SUCCESS")
        tests_passed += 1
    except Exception as e:
        print(f"? from utils.claude_client import get_claude_client - FAILED: {e}")
        tests_failed += 1
    
    # Test 4: Import middleware
    try:
        import middleware
        print("? import middleware - SUCCESS")
        tests_passed += 1
    except Exception as e:
        print(f"? import middleware - FAILED: {e}")
        tests_failed += 1
    
    # Test 5: Import database
    try:
        import database
        print("? import database - SUCCESS")
        tests_passed += 1
    except Exception as e:
        print(f"? import database - FAILED: {e}")
        tests_failed += 1
    
    # Test 6: Import backend
    try:
        import backend
        print("? import backend - SUCCESS")
        tests_passed += 1
    except Exception as e:
        print(f"? import backend - FAILED: {e}")
        tests_failed += 1
    
    # Test 7: Import main application
    try:
        import main
        print("? import main - SUCCESS")
        tests_passed += 1
    except Exception as e:
        print(f"? import main - FAILED: {e}")
        tests_failed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"{'='*50}\n")
    
    if tests_failed == 0:
        print("? ALL IMPORTS SUCCESSFUL!")
        print("Your application should work on Railway.")
        return 0
    else:
        print("? SOME IMPORTS FAILED!")
        print("Fix these issues before deploying to Railway.")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
