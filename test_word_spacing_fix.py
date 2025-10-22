"""
Test the improved word spacing function
"""
import re

def format_claude_response(text: str) -> str:
    """
    Fix Claude API responses that are missing spaces between words.
    
    Only adds spaces where genuinely missing (after punctuation without space),
    but preserves proper nouns, technical terms, and acronyms.
    """
    # Add space after period before capital letter (only if no space already)
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    
    # Add space after comma before any letter (only if no space already)
    text = re.sub(r',([A-Za-z])', r', \1', text)
    
    # Add space after colon before any letter (only if no space already)
    text = re.sub(r':([A-Za-z])', r': \1', text)
    
    # Add space before opening parenthesis if preceded by letter/digit (only if no space already)
    text = re.sub(r'([A-Za-z0-9])\(', r'\1 (', text)
    
    # Add space after closing parenthesis before capital (only if no space already)
    text = re.sub(r'\)([A-Z])', r') \1', text)
    
    # Add space after exclamation/question mark before capital (only if no space already)
    text = re.sub(r'([!?])([A-Z])', r'\1 \2', text)
    
    # Don't add spaces between camelCase or technical terms
    # (removed the aggressive lowercase-to-uppercase pattern)
    
    return text


# Test cases
test_cases = [
    # Missing spaces after punctuation
    ("Hello.World", "Hello. World"),
    ("Hi,there", "Hi, there"),
    ("Note:Important", "Note: Important"),
    
    # Preserve technical terms
    ("FastAPI", "FastAPI"),
    ("JavaScript", "JavaScript"),
    ("PostgreSQL", "PostgreSQL"),
    ("WebSocket", "WebSocket"),
    
    # Already correct
    ("Hello, world! How are you?", "Hello, world! How are you?"),
    
    # Mixed cases
    ("Using FastAPI.You can build APIs", "Using FastAPI. You can build APIs"),
    ("Hello(World)", "Hello (World)"),
    ("Great!Let's go", "Great! Let's go"),
]

print("?? Testing Word Spacing Fix\n")
print("=" * 60)

all_passed = True
for i, (input_text, expected) in enumerate(test_cases, 1):
    result = format_claude_response(input_text)
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "?" if passed else "?"
    print(f"\nTest {i}: {status}")
    print(f"  Input:    '{input_text}'")
    print(f"  Expected: '{expected}'")
    print(f"  Got:      '{result}'")
    if not passed:
        print(f"  ??  MISMATCH!")

print("\n" + "=" * 60)
if all_passed:
    print("? All tests passed!")
else:
    print("? Some tests failed")
