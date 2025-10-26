import re

# Read the file
with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix JavaScript syntax line by line
fixes = [
    (r'\.trim\(\)', '.strip()'),  # .trim() -> .strip()
    (r'\s*\|\|\s*', ' or '),  # || -> or
    (r'try\s*\{', 'try:'),  # try { -> try:
    (r'\}\s*catch\s*\(Exception\s+\w+\)\s*\{', 'except Exception as e:'),  # } catch (Exception e) {
    (r'\}\s*catch\s*\(Exception\)\s*\{', 'except Exception:'),  # } catch (Exception) {
    (r'throw\s+', 'raise '),  # throw -> raise
    (r'\/\/ ', '# '),  # // -> #
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content)

# Write back
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('? Fixed JavaScript syntax in main.py')
