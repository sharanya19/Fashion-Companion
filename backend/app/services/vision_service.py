import base64
import json
import httpx
from ..config import settings

async def analyze_clothing_image(image_path: str) -> dict:
    if not settings.GEMINI_API_KEY:
        return None

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    PROMPT = """
You are a professional fashion vision analyst.

Return STRICT JSON only.

RULES:
- ONE clothing item only
- Category must match structure
- Tops ≠ Bottoms ≠ OnePiece
- Jeans/skirts → Bottom
- Dresses/jumpsuits → OnePiece
- Color = fabric color only (no background)

ENUM:
Top, Bottom, OnePiece, Outerwear, Footwear, Accessory

OUTPUT:
{
  "category": "",
  "subcategory": "",
  "type": "",
  "color_primary": "",
  "pattern": "",
  "fabric": "",
  "fit": "",
  "seasonality": [],
  "occasion_tags": [],
  "style_tags": []
}
"""

    payload = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-preview-02-05:generateContent?key={settings.GEMINI_API_KEY}",
                json=payload
            )
        
        # Check response status before parsing JSON
        res.raise_for_status()
        
        # Safely parse response JSON
        response_data = res.json()
        if "candidates" not in response_data or not response_data["candidates"]:
            print("⚠️ Gemini API returned empty candidates")
            return None
        
        candidate = response_data["candidates"][0]
        if "content" not in candidate or "parts" not in candidate["content"]:
            print("⚠️ Gemini API response missing content/parts")
            return None
        
        raw = candidate["content"]["parts"][0].get("text", "")
        if not raw:
            print("⚠️ Gemini API returned empty text")
            return None
        
        # Clean and parse JSON response
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
        
    except httpx.HTTPStatusError as e:
        print(f"⚠️ Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"⚠️ Gemini API response parsing error: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Gemini API request failed: {e}")
        return None
