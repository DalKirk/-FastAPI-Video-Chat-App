Quick run instructions (Windows PowerShell)

Activate venv (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run using helper script (recommended for dev on Windows):

```powershell
# Run with defaults main_optimized:app host 127.0.0.1 port 8000
.\run_server.ps1

# Or specify module and host/port
.\run_server.ps1 -Module main_optimized:app -BindHost 127.0.0.1 -Port 8000
```

Or run uvicorn directly with the venv Python:

```powershell
$env:APP_MODULE = 'main_optimized:app'
$env:HOST = '127.0.0.1'
$env:PORT = '8000'
.venv\Scripts\python.exe -m uvicorn main_optimized:app --host 127.0.0.1 --port 8000
```

Run tests:

```powershell
. .\.venv\Scripts\Activate.ps1
.venv\Scripts\pytest.exe -q
```
