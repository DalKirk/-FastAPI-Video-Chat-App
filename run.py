"""
run.py - helper to start the app using the venv python/uvicorn in-process.
This avoids uvicorn's spawn/reload child process issues on Windows when using --reload.
Usage: python run.py [module:app] [--host H] [--port P]
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    module_app = os.environ.get("APP_MODULE", "main_optimized:app")
    host = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("HOST", "127.0.0.1")
    port = int(sys.argv[2]) if len(sys.argv) > 2 else int(os.environ.get("PORT", "8000"))

    # Import here after load_dotenv so apps can read env at import time
    module, app_name = module_app.split(":")
    mod = __import__(module, fromlist=[app_name])
    app = getattr(mod, app_name)

    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")
