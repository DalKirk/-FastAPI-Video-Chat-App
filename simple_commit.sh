#!/bin/bash
# Simple Git commit script for WebSocket fixes

echo "?? Committing WebSocket fixes to GitHub..."
echo ""

# Add the essential files
git add main.py
git add static/chat.html

# Commit with simple message  
git commit -m "fix: WebSocket room connection handling"

# Push to GitHub
git push origin main

echo ""
echo "? Done! Check GitHub and Railway for deployment."