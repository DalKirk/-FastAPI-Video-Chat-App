#!/usr/bin/env python3
"""
Diagnostic script to test Anthropic API and identify 404 errors
"""
import os
import sys

def test_anthropic_connection():
    """Test Anthropic API connection and model availability"""
    print("?? Anthropic API Diagnostic Tool\n")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("? ERROR: ANTHROPIC_API_KEY not found in environment")
        print("\nTo fix:")
        print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'  # Linux/Mac")
        print("  set ANTHROPIC_API_KEY=sk-ant-api03-...       # Windows CMD")
        print("  $env:ANTHROPIC_API_KEY='sk-ant-api03-...'    # PowerShell")
        return False
    
    print(f"? API Key found: {api_key[:20]}...")
    
    # Try to import anthropic
    try:
        import anthropic
        print(f"? Anthropic SDK imported successfully (version: {anthropic.__version__ if hasattr(anthropic, '__version__') else 'unknown'})")
    except ImportError as e:
        print(f"? ERROR: Cannot import anthropic: {e}")
        print("\nTo fix:")
        print("  pip install anthropic>=0.19.0")
        return False
    
    # Test API connection with different models
    print("\n" + "=" * 60)
    print("Testing Claude Models:")
    print("=" * 60 + "\n")
    
    models_to_test = [
        ("claude-sonnet-4-5-20250929", "Latest Claude 4.5 Sonnet (Sept 2025)"),
        ("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet (Oct 2024)"),
        ("claude-3-5-sonnet-20240620", "Claude 3.5 Sonnet (June 2024)"),
        ("claude-3-haiku-20240307", "Claude 3 Haiku (Cost-effective)"),
    ]
    
    client = anthropic.Anthropic(api_key=api_key)
    
    for model_name, description in models_to_test:
        print(f"\n?? Testing: {model_name}")
        print(f"   Description: {description}")
        
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Say 'test'"}
                ]
            )
            print(f"   ? SUCCESS - Model is available")
            print(f"   Response: {response.content[0].text}")
            
        except anthropic.NotFoundError as e:
            print(f"   ? 404 ERROR - Model not found")
            print(f"   Error: {e}")
            
        except anthropic.AuthenticationError as e:
            print(f"   ? AUTH ERROR - Invalid API key")
            print(f"   Error: {e}")
            return False
            
        except anthropic.RateLimitError as e:
            print(f"   ??  RATE LIMIT - Too many requests")
            print(f"   Error: {e}")
            
        except Exception as e:
            print(f"   ? ERROR: {type(e).__name__}")
            print(f"   Message: {e}")
    
    print("\n" + "=" * 60)
    print("? Diagnostic Complete")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_anthropic_connection()
    sys.exit(0 if success else 1)
