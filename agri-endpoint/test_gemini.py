import requests
import json
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyDViK5oy4XxycihnXs5qyxlw90NQaFrAVs"
headers = {"Content-Type": "application/json"}
payload = {"contents": [{"parts": [{"text": "Hello, reply in one word."}]}]}
try:
    r = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.json()}")
except Exception as e:
    print(f"Error: {e}")
