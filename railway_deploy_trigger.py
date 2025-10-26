"""
Force Railway redeploy by updating this trigger file.
Railway will detect the change and rebuild the container.
"""

# Deployment trigger - Updated: 2025-01-26 06:35:00
DEPLOYMENT_VERSION = "6d059f6-chat-endpoint-fix"
TIMESTAMP = "2025-01-26T06:35:00Z"

# This file change will trigger Railway to rebuild with latest code
print(f"? Deployment trigger updated: {DEPLOYMENT_VERSION}")
