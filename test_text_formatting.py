"""
Test script to verify text formatting is working properly
"""
import re

def format_claude_response(text: str) -> str:
    """
    Fix Claude API responses that are missing spaces between words.
    """
    # Add space after period before capital letter
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    
    # Add space after comma before capital letter
    text = re.sub(r',([A-Z])', r', \1', text)
    
    # Add space between lowercase and capital (camelCase/word boundaries)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Add space after closing parenthesis before capital
    text = re.sub(r'\)([A-Z])', r') \1', text)
    
    # Add space after colon before capital
    text = re.sub(r':([A-Z])', r': \1', text)
    
    # Add space before opening parenthesis after lowercase
    text = re.sub(r'([a-z])\(', r'\1 (', text)
    
    # Fix number followed by capital letter
    text = re.sub(r'(\d)([A-Z])', r'\1 \2', text)
    
    # Additional fix: Handle consecutive capital letters better
    text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', text)
    
    return text

def test_text_formatting():
    """Test the text formatting function"""
    
    test_cases = [
        # Original -> Expected
        ("Hello.World", "Hello. World"),
        ("Yes,Alice", "Yes, Alice"),
        ("FastAPIApplication", "Fast API Application"),
        ("(note)This", "(note) This"),
        ("Note:Important", "Note: Important"),
        ("function(args)", "function (args)"),
        ("Version2Update", "Version 2 Update"),
        ("ThisIsATest.Please,CheckThis:Working(Perfect)Version3", "This Is A Test. Please, Check This: Working (Perfect) Version 3"),
    ]
    
    print("?? Testing Text Formatting Function:")
    print("=" * 60)
    
    all_passed = True
    
    for i, (original, expected) in enumerate(test_cases, 1):
        result = format_claude_response(original)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "? PASS" if passed else "? FAIL"
        print(f"Test {i}: {status}")
        print(f"  Input:    '{original}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        print()
    
    print("=" * 60)
    if all_passed:
        print("?? All tests PASSED! Text formatting is working correctly.")
    else:
        print("??  Some tests FAILED. Text formatting needs attention.")
    
    return all_passed

if __name__ == "__main__":
    test_text_formatting()