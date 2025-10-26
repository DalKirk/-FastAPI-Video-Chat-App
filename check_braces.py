import re

# Read the file with proper encoding
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all unmatched braces
brace_count = 0
for i, char in enumerate(content):
    if char == '{':
        brace_count += 1
    elif char == '}':
        brace_count -= 1
        if brace_count < 0:
            print(f'Unmatched closing brace at position {i}')
            # Show context
            start = max(0, i-100)
            end = min(len(content), i+100)
            print('Context:')
            print(content[start:end])
            break

print(f'Final brace count: {brace_count}')