import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
try:
    r = requests.get(url, timeout=10)
    with open("models.json", "w") as f:
        json.dump(r.json(), f, indent=2)
    print("Models saved successfully to models.json")
except Exception as e:
    print(f"Error: {e}")
