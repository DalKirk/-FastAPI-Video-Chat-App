# Manual Git Push Instructions

## ?? Git is Hanging in VS Code Terminal

The VS Code integrated terminal is having issues with Git commands. Here's how to fix it:

---

## ? Solution: Use Command Prompt or Git Bash

### **Option 1: Run the Batch File (Easiest)**

1. **Close VS Code** (or keep it open, doesn't matter)
2. **Open File Explorer**
3. **Navigate to:** `C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python`
4. **Double-click:** `git_push_fix.bat`
5. **Wait** for it to complete
6. **Done!** ?

---

### **Option 2: Use Command Prompt Manually**

1. **Press** `Windows + R`
2. **Type:** `cmd` and press Enter
3. **Copy and paste these commands one at a time:**

```cmd
cd C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python

git add main.py static\chat.html

git commit -m "fix: WebSocket room connection error handling"

git push origin main
```

4. **Wait** for each command to complete
5. **Done!** ?

---

### **Option 3: Use Git Bash**

1. **Right-click** in your project folder
2. **Select** "Git Bash Here"
3. **Run these commands:**

```bash
git add main.py static/chat.html

git commit -m "fix: WebSocket room connection error handling"

git push origin main
```

4. **Done!** ?

---

## ?? What Gets Committed

### Essential Files Only:
- ? `main.py` - Fixed embedded chat HTML
- ? `static/chat.html` - Fixed joinRoom() function

### NOT Committed (optional files):
- Documentation files (*.md)
- Test scripts (*.py, *.ps1, *.bat)

**These 2 files are all you need to fix the WebSocket connection issue!**

---

## ?? After Pushing

1. **Go to GitHub:**
   - https://github.com/DalKirk/-FastAPI-Video-Chat-App
   - Verify you see the commit

2. **Check Railway:**
   - Go to https://railway.app/dashboard
   - Wait 2-3 minutes for auto-deploy
   - Check deployment logs

3. **Test Production:**
   - https://web-production-3ba7e.up.railway.app/chat
   - Try creating user, room, and joining

---

## ? Why is Git Hanging?

**Cause:** VS Code's PowerShell terminal has issues with interactive Git commands, especially:
- Long commit messages
- Commands that open editors
- Commands that require authentication

**Solution:** Use regular Command Prompt or Git Bash instead.

---

## ? Success Indicators

After running the commands, you should see:

```
[main abc1234] fix: WebSocket room connection error handling
 2 files changed, 50 insertions(+), 10 deletions(-)
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Writing objects: 100% (3/3), 1.2 KiB | 1.2 MiB/s, done.
To https://github.com/DalKirk/-FastAPI-Video-Chat-App
   def5678..abc1234  main -> main
```

**That means it worked!** ?

---

## ?? If You Get Errors

### Error: "fatal: not a git repository"
**Fix:** Make sure you're in the right directory:
```cmd
cd C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python
```

### Error: "Permission denied"
**Fix:** You might need to authenticate with GitHub:
```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Error: "rejected - non-fast-forward"
**Fix:** Pull first, then push:
```cmd
git pull origin main
git push origin main
```

---

## ?? Quick Reference

**Project Directory:**
```
C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python
```

**GitHub Repository:**
```
https://github.com/DalKirk/-FastAPI-Video-Chat-App
```

**Files to Commit:**
- `main.py`
- `static/chat.html`

**Commit Message:**
```
fix: WebSocket room connection error handling
```

---

**Just run `git_push_fix.bat` and you're done!** ??
