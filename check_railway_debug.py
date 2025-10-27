import os
import requests

BASE_URL = os.getenv('RAILWAY_BASE_URL', 'https://web-production-3ba7e.up.railway.app')
URL = f"{BASE_URL.rstrip('/')}/_debug"

try:
    r = requests.get(URL, timeout=10)
    print('STATUS', r.status_code)
    print('BODY', r.text)
    try:
        data = r.json()
        print('auto_create_on_ws:', data.get('auto_create_on_ws'))
        print('auto_create_on_join:', data.get('auto_create_on_join'))
        print('auto_user_on_join:', data.get('auto_user_on_join'))
    except Exception:
        pass
except Exception as e:
    print('ERROR', repr(e))
