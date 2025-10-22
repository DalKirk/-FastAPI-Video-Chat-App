"""
Test script to diagnose Claude API grammar/spacing issues
Run this to see exactly where spacing is being lost
"""
import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_claude_response():
    """Test Claude API response for spacing issues"""
    
    # Check if API key exists
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("? ANTHROPIC_API_KEY not found in environment")
        print("   Set it in .env file or environment variables")
        return
    
    print("? API key found")
    print(f"  Key starts with: {api_key[:15]}...")
    
    # Import after checking API key
    try:
        from utils.claude_client import get_claude_client
    except ImportError as e:
        print(f"? Failed to import claude_client: {e}")
        return
    
    # Initialize client
    print("\n?? Initializing Claude client...")
    claude = get_claude_client()
    
    if not claude.is_enabled:
        print("? Claude client not enabled")
        return
    
    print(f"? Claude client initialized")
    print(f"  Model: {claude.active_model}")
    
    # Test prompt
    test_prompt = "Write a short sentence about Python programming."
    
    print(f"\n?? Sending test prompt: '{test_prompt}'")
    print("=" * 60)
    
    # Generate response
    try:
        response = claude.generate_response(
            prompt=test_prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        print("\n?? RESPONSE RECEIVED")
        print("=" * 60)
        
        # Detailed analysis
        print(f"\n?? RESPONSE ANALYSIS:")
        print(f"   Length: {len(response)} characters")
        print(f"   Has spaces: {' ' in response}")
        print(f"   Space count: {response.count(' ')}")
        print(f"   Word count: {len(response.split())}")
        print(f"   Has periods: {'.' in response}")
        print(f"   Has commas: {',' in response}")
        
        print(f"\n?? RAW RESPONSE (first 300 chars):")
        print("-" * 60)
        print(response[:300])
        print("-" * 60)
        
        print(f"\n?? CHARACTER BREAKDOWN (first 50 chars):")
        for i, char in enumerate(response[:50]):
            if char == ' ':
                print(f"   [{i}]: SPACE")
            elif char == '\n':
                print(f"   [{i}]: NEWLINE")
            elif char == '\t':
                print(f"   [{i}]: TAB")
            else:
                print(f"   [{i}]: '{char}'")
        
        # Test formatting function
        print(f"\n?? TESTING FORMAT FUNCTION:")
        print("-" * 60)
        
        try:
            from utils.streaming_ai_endpoints import format_claude_response
            formatted = format_claude_response(response)
            
            print(f"Original length: {len(response)}")
            print(f"Formatted length: {len(formatted)}")
            print(f"Changes made: {response != formatted}")
            
            if response != formatted:
                print(f"\n? FORMATTING CHANGED TEXT:")
                print(f"Original:  {response[:200]}...")
                print(f"Formatted: {formatted[:200]}...")
            else:
                print(f"? No formatting changes needed (text already correct)")
                
        except ImportError as e:
            print(f"??  Could not import format function: {e}")
        
        # Check for common issues
        print(f"\n?? ISSUE DETECTION:")
        issues = []
        
        # Check for missing spaces after punctuation
        import re
        if re.search(r'\.[A-Z]', response):
            issues.append("Missing space after period")
        if re.search(r',[A-Za-z]', response):
            issues.append("Missing space after comma")
        if re.search(r':[A-Za-z]', response):
            issues.append("Missing space after colon")
        
        if issues:
            print("   ? Issues found:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ? No spacing issues detected")
        
        print("\n" + "=" * 60)
        print("? TEST COMPLETE")
        
    except Exception as e:
        print(f"\n? ERROR during response generation:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


def test_streaming_response():
    """Test streaming response for spacing issues"""
    print("\n" + "=" * 60)
    print("?? TESTING STREAMING RESPONSE")
    print("=" * 60)
    
    try:
        from utils.claude_client import get_claude_client
        import anthropic
        
        claude = get_claude_client()
        
        if not claude.is_enabled or not claude.client:
            print("? Claude client not available for streaming test")
            return
        
        test_prompt = "Count from 1 to 5."
        print(f"\n?? Prompt: '{test_prompt}'")
        print("\n?? Streaming response:")
        print("-" * 60)
        
        full_response = ""
        chunk_count = 0
        
        with claude.client.messages.stream(
            model=claude.active_model,
            max_tokens=100,
            messages=[{"role": "user", "content": test_prompt}]
        ) as stream:
            for text in stream.text_stream:
                chunk_count += 1
                full_response += text
                print(f"[Chunk {chunk_count}] '{text}'", end='', flush=True)
        
        print("\n" + "-" * 60)
        print(f"\n?? STREAMING ANALYSIS:")
        print(f"   Total chunks: {chunk_count}")
        print(f"   Total length: {len(full_response)}")
        print(f"   Has spaces: {' ' in full_response}")
        print(f"   Space count: {full_response.count(' ')}")
        
        print(f"\n?? FULL RESPONSE:")
        print(full_response)
        
    except Exception as e:
        print(f"\n? Streaming test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("?? CLAUDE API GRAMMAR/SPACING DIAGNOSTIC")
    print("=" * 60)
    
    # Test regular response
    test_claude_response()
    
    # Test streaming response
    test_streaming_response()
    
    print("\n" + "=" * 60)
    print("?? NEXT STEPS:")
    print("=" * 60)
    print("1. Check the logs above for spacing issues")
    print("2. If spaces are present in backend but missing in frontend:")
    print("   - Check frontend JavaScript/TypeScript code")
    print("   - Look for text processing/sanitization")
    print("   - Check CSS (white-space property)")
    print("3. If spaces are missing in backend response:")
    print("   - Contact Anthropic support")
    print("   - Try different model version")
    print("4. Check Railway logs with: railway logs --tail")
    print("=" * 60)
