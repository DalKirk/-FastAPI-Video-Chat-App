#!/bin/bash
# Simple Git Commit Script for Git Bash

cd "/c/Users/g-kd/OneDrive/Desktop/My_FastAPI_Python"

# Clean up problematic files
echo "Cleaning up..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.log" -delete 2>/dev/null
find . -type f -name "*.lock" -delete 2>/dev/null

echo ""
echo "Current Git Status:"
git status --short

echo ""
echo "Adding all files..."
git add .

echo ""
echo "Committing changes..."
git commit -m "Update FastAPI Video Chat Application v2.0.0"

echo ""
echo "Pushing to GitHub..."
git push origin main

echo ""
echo "Done!"
