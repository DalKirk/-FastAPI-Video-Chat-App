with open('main.py', 'r') as f:
    lines = f.readlines()
    for i in range(700, 710):
        if i < len(lines):
            print(f'{i+1:3}: {lines[i].rstrip()}')