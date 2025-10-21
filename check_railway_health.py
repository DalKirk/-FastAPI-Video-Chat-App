import requests
url = 'https://web-production-3ba7e.up.railway.app/health'
try:
    r = requests.get(url, timeout=10)
    print('STATUS', r.status_code)
    print('BODY', r.text)
except Exception as e:
    print('ERROR', repr(e))

