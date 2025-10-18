import requests, time, json

base='http://127.0.0.1:8000'
s = requests.Session()

print('GET', base + '/_debug')
try:
    r = s.get(base + '/_debug', timeout=10)
    print('->', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text[:1000])
except Exception as e:
    print('-> ERROR', e)

print('\nGET', base + '/health')
try:
    r = s.get(base + '/health', timeout=10)
    print('->', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text[:1000])
except Exception as e:
    print('-> ERROR', e)

# create user
uname = f'smoke-{int(time.time())}'
print('\nPOST /users', uname)
try:
    r = s.post(base + '/users', json={'username': uname}, timeout=10)
    print('->', r.status_code)
    udata = r.json() if r.headers.get('Content-Type','').startswith('application/json') else {'text': r.text}
    print(json.dumps(udata, indent=2))
    user_id = udata.get('id')
except Exception as e:
    print('-> ERROR', e); user_id = None

# create room
rname = f'smoke-room-{int(time.time())}'
print('\nPOST /rooms', rname)
try:
    r = s.post(base + '/rooms', json={'name': rname}, timeout=10)
    print('->', r.status_code)
    rdata = r.json() if r.headers.get('Content-Type','').startswith('application/json') else {'text': r.text}
    print(json.dumps(rdata, indent=2))
    room_id = rdata.get('id')
except Exception as e:
    print('-> ERROR', e); room_id = None

# POST video-upload
if room_id:
    print(f'\nPOST /rooms/{room_id}/video-upload')
    try:
        payload = {'title': 'smoke test', 'description': 'smoke-run'}
        r = s.post(f"{base}/rooms/{room_id}/video-upload", json=payload, timeout=20)
        print('->', r.status_code)
        try:
            vdata = r.json()
            print(json.dumps(vdata, indent=2))
        except Exception:
            print('NON-JSON RESPONSE:\n', r.text[:2000])
            vdata = None
    except Exception as e:
        print('-> ERROR', e); vdata = None

    # attempt PUT to upload_url if present
    if vdata and isinstance(vdata, dict) and 'upload_url' in vdata:
        upload_url = vdata['upload_url']
        print('\nAttempting PUT to upload_url (server-side test)')
        try:
            r = s.put(upload_url, data=b'test-bytes', headers={'Content-Type': 'application/octet-stream'}, timeout=30)
            print('-> PUT', r.status_code)
            print(r.text[:1000])
        except Exception as e:
            print('-> PUT ERROR', e)
else:
    print('\nSkipping video-upload: no room_id available')
