# Quick Fix Guide for main.py

## Current Issues:

Your `main.py` has these duplicate sections that need to be removed:

### 1. **Lines 228-230** - Duplicate router registrations
```python
app.include_router(streaming_ai_router)  # ? DELETE
app.include_router(chat_router)          # ? DELETE  
app.include_router(vision_router)        # ? DELETE
```
**These are already registered at lines 207-210!**

---

### 2. **Lines 284-295** - Duplicate endpoints
```python
@app.get("/ai/health")                   # ? DELETE
async def ai_health_redirect():          # ? DELETE
    from api.routes.chat import chat_health_check
    return await chat_health_check()

@app.post("/api/ai-proxy")               # ? DELETE
async def ai_proxy(request: Request):    # ? DELETE
    try:
        from api.routes.chat import chat_endpoint, get_ai_service
        ai_service = get_ai_service()
        return await chat_endpoint(request, ai_service)
    except Exception as e:
        logger.error(f"AI proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```
**These are already defined at lines 232-245!**

---

### 3. **Line 557** - Duplicate static files mount
```python
app.mount("/static", StaticFiles(directory="static"), name="static")  # ? DELETE
```
**This is already mounted at line 212!**

---

## How to Fix:

### Option 1: Manual Fix (Recommended)
1. **Open `main.py` in your IDE**
2. **Delete lines 228-230**
3. **Delete lines 284-295** (will shift to ~279-290 after step 2)
4. **Delete the last line** (duplicate static mount)
5. **Save the file** (Ctrl+S)
6. **Run:** `commit_fixed_main.bat`

### Option 2: Search and Replace
1. Open main.py
2. Search for the **second occurrence** of each duplicate
3. Delete them
4. Save

---

## After Fixing:

Run this to commit and push:
```cmd
cd C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python
git add main.py
git commit -m "fix: remove duplicate endpoints and router registrations"
git push origin main
```

---

## Verification:

After pushing, Railway will redeploy. Test with:
```sh
curl https://web-production-3ba7e.up.railway.app/health
curl https://web-production-3ba7e.up.railway.app/
curl https://web-production-3ba7e.up.railway.app/api/v1/3d/health
```

All should return 200 OK!

---

**Fix these 3 duplicate sections and you're done!** ?
