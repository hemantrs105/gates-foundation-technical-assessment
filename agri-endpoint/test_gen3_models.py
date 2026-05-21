import os
import requests
from dotenv import load_dotenv
load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
models = [
    "gemini-3.1-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3-pro-preview"
]

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": "Hello, reply in one word."}]}]}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5)
        print(f"Model: {m} -> Status: {r.status_code}")
        if r.status_code == 200:
            print(f"  Success: {r.json()['candidates'][0]['content']['parts'][0]['text'].strip()}")
        else:
            print(f"  Error: {r.json().get('error', {}).get('message', '')[:100]}")
    except Exception as e:
        print(f"  Exception: {e}")
