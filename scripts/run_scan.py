from __future__ import annotations
import json
import requests

API_URL = "http://127.0.0.1:8000"

response = requests.post(f"{API_URL}/scan", timeout=20)
response.raise_for_status()
print(json.dumps(response.json(), indent=2))
