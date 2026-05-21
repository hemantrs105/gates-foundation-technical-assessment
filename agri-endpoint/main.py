import os
import json
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# Load env variables
load_dotenv()

app = FastAPI(
    title="AgriAdvisor India API v2.0",
    description="LLM-powered agriculture advisory endpoint for Indian smallholder farmers",
    version="2.0.0"
)

# Load Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "AIzaSyDViK5oy4XxycihnXs5qyxlw90NQaFrAVs"

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    location: Optional[str] = "generic"
    farmer_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    metadata: dict

SYSTEM_PROMPT = """You are AgriAdvisor India, a highly specialized digital agriculture advisory AI. Your target audience is Indian smallholder farmers (often holding less than 1-2 acres of land).

Your task is to provide expert, practical, and highly localized advisory advice in response to farmer queries.

### Operational Guidelines:
1. **Language Policy**:
   - You MUST respond in the EXACT same language/script as the farmer's query.
   - If the query is in Hindi (Devanagari, e.g. "मुझे गेहूं की बुवाई..."), reply in fluent, natural Hindi.
   - If the query is in Telugu (Telugu script, e.g. "నా పొలంలో వరి..."), reply in fluent, natural Telugu.
   - If the query is in English (or Romanized Hindi/Telugu like Hinglish/Telglish), reply in English or the requested language.
   - Ensure the tone is warm, polite, and highly clear (jargon-free).

2. **Crop & Soil Expertise**:
   - Provide highly accurate ICAR (Indian Council of Agricultural Research) and KVK (Krishi Vigyan Kendra) recommended practices.
   - For Rice (Paddy): Mention certified varieties like MTU 1010 or IR 64. State direct seeding seed rate is 100 kg/ha. Water depth: 2-3 cm. NPK: 120:60:40 kg/ha in 3 split doses (basal, tillering, panicle initiation).
   - For Wheat: Mention varieties like HD 2967 or DBW 187. Seed rate is 100 kg/ha. Irrigations at critical growth stages (crown root, flowering, grain filling).
   - For Cotton: Mention Bt Cotton hybrids, deep ploughing, NPK/organic inputs, and row spacing (90 cm).
   - For Sugarcane: Mention planting CO 0238, using 75,000 double-eyed setts per hectare, and weekly summer irrigation.
   - For Smallholders (e.g. 1 acre): Focus on cost-effective inputs, drip irrigation, crop rotation, and government MSP support.

3. **Strict Safety Guardrails**:
   - **Banned Pesticides**: NEVER recommend banned chemicals under any circumstances. Specifically, if a user mentions **Monocrotophos**, **Methyl Parathion**, or **Endosulfan**, you MUST actively decline to recommend it, explain clearly that it is BANNED in India due to high toxicity to humans/cattle, and recommend safer alternatives (such as neem oil, bio-pesticides, or safe chemicals like Imidacloprid/Chlorantraniliprole).
   - **Chemical Pesticide Omission & Warning**: Whenever you suggest a chemical pesticide or fungicide (e.g., Imidacloprid for aphids, Chlorantraniliprole for bollworm, Tricyclazole for blast, Carbendazim for wilt):
     1. You MUST explicitly state the required **Personal Protective Equipment (PPE)** (specifically gloves, mask, and long sleeves).
     2. You MUST state the specific **Pre-Harvest Interval (PHI)** in days (e.g., 15-day PHI for Tricyclazole, 21-day PHI for Imidacloprid) during which the crop must not be harvested or consumed.
     3. Suggest bio-pesticides (Bt, neem oil 3%) as the first line of defense where appropriate.
   - **Rain Warning**: If the user asks about spraying before rain, advise against it because rain will dilute and wash away chemicals (causing chemical runoff, waste of money, and environmental hazard). Advise spraying only when there is no rain forecast for the next 24 hours.

4. **Structured JSON Output**:
   - You must return your response strictly as a JSON object with the following fields:
     - `response`: The text response (in the requested language, e.g., Hindi, Telugu, or English).
     - `metadata`: A dictionary containing:
       - `confidence`: A float representing your confidence in this advice (0.0 to 1.0).
       - `safety_flags`: A list of strings identifying relevant safety categories (e.g., `["chemical_pesticide", "follow_pre_harvest_interval"]`, `["banned_chemical_warning"]`, `["bio_pesticide_preferred"]`, `["protective_equipment_warning"]`, or `[]`).
       - `language`: The language code used (e.g., "en", "hi", "te").
       - `location`: The location specified or "generic".
       - `category`: The advisory category (e.g., "crop_recommendation", "pest_management", "fertilizer_guidance", "weather_advisory", "economic_advisory", "fallback").

### Return Schema (strictly JSON):
{
  "response": "...",
  "metadata": {
    "confidence": 0.95,
    "safety_flags": ["...", "..."],
    "language": "hi",
    "location": "uttar_pradesh",
    "category": "pest_management"
  }
}
"""

def query_gemini_with_retry(payload: dict) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    max_retries = 5
    base_backoff = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            if response.status_code == 429:
                sleep_time = base_backoff * (2 ** attempt)
                print(f"Gemini API rate limited (429). Retrying in {sleep_time} seconds (attempt {attempt + 1}/{max_retries})...")
                time.sleep(sleep_time)
                continue
                
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            sleep_time = base_backoff * (2 ** attempt)
            print(f"Gemini API error ({e}). Retrying in {sleep_time} seconds (attempt {attempt + 1}/{max_retries})...")
            time.sleep(sleep_time)
            
    raise Exception("Max retries exceeded for Gemini API call.")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        # Handle empty query gracefully
        return ChatResponse(
            response="Thank you for contacting AgriAdvisor India. Please specify your crop, pest issue, or ask about fertilizer schedules. You can also mention your state for localized advice.",
            metadata={
                "confidence": 1.0,
                "safety_flags": [],
                "language": request.language,
                "location": request.location,
                "category": "fallback"
            }
        )
    
    user_prompt = f"Message: {request.message}\nLanguage: {request.language}\nLocation: {request.location}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_prompt}
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {"text": SYSTEM_PROMPT}
            ]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }
    
    try:
        res_json = query_gemini_with_retry(payload)
        raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
        data = json.loads(raw_text)
        
        # Validate JSON response keys
        if "response" not in data or "metadata" not in data:
            raise HTTPException(status_code=500, detail="Invalid JSON response schema from Gemini.")
            
        return ChatResponse(
            response=data["response"],
            metadata=data["metadata"]
        )
        
    except Exception as e:
        print(f"Error querying Gemini API after retries: {e}")
        # Graceful fallback in case of rate limits or service issues
        return ChatResponse(
            response="Apologies, I am experiencing temporary system difficulty. For urgent crop advisory, please consult your local Krishi Vigyan Kendra (KVK) or call the Kisan Call Center (1800-180-1551).",
            metadata={
                "confidence": 0.0,
                "safety_flags": ["system_error"],
                "language": request.language,
                "location": request.location,
                "category": "fallback"
            }
        )

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AgriAdvisor India LLM API v2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
