from __future__ import annotations
import requests

API_URL = "http://127.0.0.1:8000"

for _ in range(3):
    resp = requests.post(f"{API_URL}/scan", timeout=20)
    resp.raise_for_status()

print("Demo data generated successfully.")
