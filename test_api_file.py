#!/usr/bin/env python3
import time
import json
import urllib.request
import urllib.error

time.sleep(3)

result = {}
try:
    response = urllib.request.urlopen('http://localhost:8000/api/items?skip=0&limit=1', timeout=10)
    data = json.loads(response.read().decode())
    result['status'] = 'success'
    result['total'] = data.get('total', 0)
    result['sample'] = data.get('items', [])[0] if data.get('items') else None
except urllib.error.HTTPError as e:
    result['status'] = 'http_error'
    result['code'] = e.code
except Exception as e:
    result['status'] = 'error'
    result['message'] = str(e)

with open('api_test_result.txt', 'w') as f:
    json.dump(result, f, indent=2, default=str)
