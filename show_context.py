with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
# Show context around the error
start = 21800
end = 21900
print('Context around unmatched brace:')
print(content[start:end])