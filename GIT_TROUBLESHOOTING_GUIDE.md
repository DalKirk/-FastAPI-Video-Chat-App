# Git Commit Issue Resolution Guide

## Problem
Git commands are hanging or being canceled when trying to commit to GitHub.

## Common Causes
1. PowerShell execution policy blocking scripts
2. File locks (especially `__pycache__`, `.pyc`, `.log` files)
3. Large files in the repository
4. Git credential issues
5. OneDrive sync conflicts

## Solutions (Try in Order)

### Solution 1: Use Simple Batch File (RECOMMENDED)
```cmd
git_commit_clean.bat
```
This script:
- Removes problematic cache files
- Adds all changes
- Commits with a message
- Pushes to GitHub

### Solution 2: Use Git Bash
```bash
bash git_commit_bash.sh
```

### Solution 3: Manual Command Prompt Steps
```cmd
cd C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python

# Clean up
del /s /q *.pyc
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

# Git operations
git status
git add .
git commit -m "Update main.py"
git push origin main
```

### Solution 4: Check for File Locks
1. Close Visual Studio Code completely
2. Close any Python processes
3. Temporarily pause OneDrive sync
4. Try committing again

### Solution 5: Check Git Credentials
```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git credential-manager-core erase
```

### Solution 6: Reset Git State (LAST RESORT)
```cmd
# Backup your changes first!
git reset --soft HEAD~1
git add .
git commit -m "Fresh commit"
git push origin main --force
```

## Files That Can Cause Issues

### Remove These Before Committing:
- `__pycache__/` directories
- `*.pyc` files
- `*.log` files
- `*.lock` files
- Large binary files (videos, images > 50MB)
- `node_modules/` if present
- Virtual environment folders (`venv/`, `.venv/`)

### Already Ignored in .gitignore:
All the above are already in your `.gitignore` file.

## Quick Diagnostic

### Check what's being committed:
```cmd
git status
```

### See file sizes:
```cmd
git ls-files -z | xargs -0 du -h | sort -h
```

### Check for large files:
```cmd
git ls-files | xargs ls -lh | sort -k 5 -h -r | head -20
```

## OneDrive Specific Issues

If your project is in OneDrive:

1. **Pause OneDrive sync temporarily:**
   - Right-click OneDrive icon in system tray
   - Click "Pause syncing"
   - Try git operations
   - Resume sync after

2. **Move project outside OneDrive:**
   ```cmd
   xcopy /E /I /Y "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python" "C:\Projects\FastAPI_Python"
   cd C:\Projects\FastAPI_Python
   git push origin main
   ```

## Recommended Workflow

1. **Always clean before commit:**
   ```cmd
   git_commit_clean.bat
   ```

2. **If that fails, use Git Bash:**
   ```bash
   bash git_commit_bash.sh
   ```

3. **If both fail, manual steps in CMD:**
   - See "Manual Command Prompt Steps" above

## Check Repository Health
```cmd
# Check remote connection
git remote -v

# Test connection to GitHub
git fetch origin

# Check branch
git branch -a

# Check log
git log --oneline -5
```

## Success Indicators
- ? "git status" shows "working tree clean"
- ? "git push" shows "Everything up-to-date"
- ? Changes visible on GitHub website

## Still Having Issues?

### Check GitHub Authentication:
```cmd
git remote set-url origin https://github.com/DalKirk/-FastAPI-Video-Chat-App.git
git push origin main
```

### Use GitHub Desktop (Alternative):
1. Download GitHub Desktop
2. Open your repository
3. Commit and push from GUI

## Your Repository Details
- **Path:** C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python
- **Remote:** https://github.com/DalKirk/-FastAPI-Video-Chat-App
- **Branch:** main
