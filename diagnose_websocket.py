#!/usr/bin/env python3
"""
Diagnose WebSocket implementation issues
"""
import ast
import sys
import os

def analyze_websocket_code():
    """Analyze the WebSocket implementation for common issues"""
    print("?? Analyzing WebSocket Implementation")
    print("=" * 50)
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check for syntax issues
        try:
            tree = ast.parse(content)
            print("? Python syntax is valid")
        except SyntaxError as e:
            print(f"? Syntax error: {e}")
            return False
        
        # Check for key WebSocket components
        checks = [
            ("WebSocket import", "from fastapi import FastAPI, WebSocket"),
            ("ConnectionManager class", "class ConnectionManager:"),
            ("WebSocket endpoint", "@app.websocket"),
            ("WebSocket accept", "await websocket.accept()"),
            ("WebSocket disconnect handling", "except WebSocketDisconnect:"),
            ("Message broadcasting", "broadcast_to_room"),
            ("Manager instance", "manager = ConnectionManager()"),
        ]
        
        issues_found = []
        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"? {check_name}")
            else:
                print(f"? Missing: {check_name}")
                issues_found.append(check_name)
        
        # Check for specific problematic patterns
        problem_patterns = [
            ("self.active_connections", "ConnectionManager methods should use self."),
            ("room_id not in rooms", "Room validation"),
            ("user_id not in users", "User validation"),
        ]
        
        for pattern_name, pattern in problem_patterns:
            if pattern in content:
                print(f"? Has {pattern_name}")
            else:
                print(f"??  Missing pattern: {pattern_name}")
        
        # Check imports
        required_imports = [
            "import json",
            "import uuid",
            "import asyncio",
            "from fastapi import WebSocket, WebSocketDisconnect",
            "from datetime import datetime, timezone",
        ]
        
        print("\n?? Import Analysis:")
        for imp in required_imports:
            if imp in content:
                print(f"? {imp}")
            else:
                print(f"? Missing: {imp}")
        
        # Look for specific error patterns
        print("\n?? Common Error Patterns:")
        error_patterns = [
            ("Undefined variables", ["BUNNY_API_KEY", "BUNNY_LIBRARY_ID", "BUNNY_PULL_ZONE"]),
            ("Missing model definitions", ["User", "Message", "Room", "ConnectionManager"]),
        ]
        
        for error_name, patterns in error_patterns:
            missing = []
            for pattern in patterns:
                if pattern not in content:
                    missing.append(pattern)
            
            if missing:
                print(f"? {error_name}: {', '.join(missing)}")
            else:
                print(f"? {error_name} - all present")
        
        if issues_found:
            print(f"\n? Found {len(issues_found)} issues that need fixing")
            return False
        else:
            print("\n? WebSocket implementation looks good!")
            return True
            
    except FileNotFoundError:
        print("? main.py not found")
        return False
    except Exception as e:
        print(f"? Analysis error: {e}")
        return False

def check_middleware_file():
    """Check if rate limit middleware exists"""
    print("\n?? Checking middleware dependency")
    middleware_path = "middleware/rate_limit.py"
    if os.path.exists(middleware_path):
        print("? Rate limit middleware exists")
        return True
    else:
        print(f"? Missing: {middleware_path}")
        return False

def check_ai_routes():
    """Check if AI routes exist"""
    print("\n?? Checking AI routes dependency")
    
    routes = [
        "utils/streaming_ai_endpoints.py",
        "api/routes/chat.py"
    ]
    
    all_exist = True
    for route in routes:
        if os.path.exists(route):
            print(f"? {route}")
        else:
            print(f"? Missing: {route}")
            all_exist = False
    
    return all_exist

def main():
    """Main diagnostic function"""
    print("?? WebSocket Diagnostics")
    print("=" * 50)
    
    code_ok = analyze_websocket_code()
    middleware_ok = check_middleware_file()
    routes_ok = check_ai_routes()
    
    print("\n" + "=" * 50)
    print("?? SUMMARY:")
    
    if code_ok and middleware_ok and routes_ok:
        print("?? All checks passed! WebSocket should work.")
        print("\n?? To test, run:")
        print("python -m uvicorn main:app --reload")
        print("Then visit: http://localhost:8000/chat")
        return 0
    else:
        print("? Issues found that need fixing:")
        if not code_ok:
            print("  - WebSocket implementation issues")
        if not middleware_ok:
            print("  - Missing rate limit middleware")
        if not routes_ok:
            print("  - Missing AI route files")
        return 1

if __name__ == '__main__':
    sys.exit(main())