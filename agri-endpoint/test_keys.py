import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Test Gemini 2.0 Flash Key
gemini_key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
headers = {"Content-Type": "application/json"}
payload = {"contents": [{"parts": [{"text": "Hello, reply in one word."}]}]}
try:
    r = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Gemini 2.0 Flash Status: {r.status_code}")
    print(f"Gemini 2.0 Flash Response: {r.json()}")
except Exception as e:
    print(f"Gemini 2.0 Flash Error: {e}")
