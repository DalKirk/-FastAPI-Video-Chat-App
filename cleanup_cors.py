"""
Script to clean up CORS configuration in main.py
Removes temporary preview URLs and keeps only stable production URLs
"""

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new CORS configuration
new_cors_config = '''# CORS middleware - Production URLs only (stable, won't change)
allowed_origins = [
  # Local development
  "http://localhost:3000",
  "http://localhost:3001",
  "https://localhost:3000",
  
  # Production Vercel deployments (stable URLs only - no preview deployments)
  "https://next-js-14-front-end-for-chat-plast.vercel.app",
  "https://next-js-14-front-end-for-chat-plast-kappa.vercel.app",
  "https://video-chat-frontend-ruby.vercel.app",
]

# Log CORS configuration on startup'''

# Find the old CORS section
start_marker = '# CORS middleware'
end_marker = 'if os.getenv("ENVIRONMENT") != "production":'

start_index = content.find(start_marker)
end_index = content.find(end_marker)

if start_index != -1 and end_index != -1:
    # Replace the CORS section
    before = content[:start_index]
    after = '\n\n' + end_marker + content[end_index + len(end_marker):]
    
    new_content = before + new_cors_config + after
    
    # Write the updated content
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('? CORS configuration updated successfully!')
    print('? Removed 2 temporary preview URLs')
    print('? Kept 3 stable production URLs')
    print('\n?? New allowed origins:')
    print('  - http://localhost:3000 (local)')
    print('  - http://localhost:3001 (local)')
    print('  - https://localhost:3000 (local HTTPS)')
    print('  - https://next-js-14-front-end-for-chat-plast.vercel.app')
    print('  - https://next-js-14-front-end-for-chat-plast-kappa.vercel.app')
    print('  - https://video-chat-frontend-ruby.vercel.app')
else:
    print('? Could not find CORS section to update')
    print(f'   Start marker found: {start_index != -1}')
    print(f'   End marker found: {end_index != -1}')
