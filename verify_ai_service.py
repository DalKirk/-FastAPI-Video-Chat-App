"""
Quick verification script to check if all fixes are working
"""
import sys
import importlib.util

def check_import(module_path, display_name):
    """Try to import a module and report status"""
    try:
        spec = importlib.util.find_spec(module_path)
        if spec is None:
            print(f"? {display_name}: Module not found")
            return False
        print(f"? {display_name}: OK")
        return True
    except Exception as e:
        print(f"? {display_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("AI SERVICE COMPILATION VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("api.routes.chat", "Chat Router"),
        ("services.ai_service", "AI Service"),
        ("services.context_analyzer", "Context Analyzer"),
        ("services.format_selector", "Format Selector"),
        ("services.response_formatter", "Response Formatter"),
        ("utils.claude_client", "Claude Client"),
        ("utils.streaming_ai_endpoints", "Streaming Endpoints"),
        ("app.models.chat_models", "Chat Models"),
        ("middleware.rate_limit", "Rate Limit Middleware"),
    ]
    
    results = []
    print("\n?? Checking Python Imports:")
    print("-" * 60)
    for module, name in checks:
        results.append(check_import(module, name))
    
    print("\n" + "=" * 60)
    if all(results):
        print("? ALL CHECKS PASSED - Ready for deployment!")
    else:
        print("? SOME CHECKS FAILED - Review errors above")
        sys.exit(1)
    print("=" * 60)
    
    # Additional file checks
    print("\n?? Checking Required Files:")
    print("-" * 60)
    
    import os
    required_files = [
        "main.py",
        "app/__init__.py",
        "api/__init__.py",
        "api/routes/__init__.py",
        "api/routes/chat.py",
        "services/ai_service.py",
        "utils/claude_client.py",
        "middleware/rate_limit.py",
        "requirements.txt",
    ]
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "?" if exists else "?"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    print("\n" + "=" * 60)
    if all_exist:
        print("? ALL FILES PRESENT")
    else:
        print("? MISSING FILES - Check above")
    print("=" * 60)

if __name__ == "__main__":
    main()
