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
You are a fashion product classification expert.

Your task is to analyze a single clothing or fashion item image and return
STRICT, SEMANTIC fashion metadata.

IMPORTANT RULES (MANDATORY):
- Categories are SEMANTIC, not based on image shape or size.
- Do NOT guess categories based on silhouette or orientation.
- Accessories (belt, bag, jewelry) are NEVER Tops or Bottoms.
- Dresses, gowns, jumpsuits are ALWAYS OnePiece.
- Shoes, heels, sandals, boots are ALWAYS Footwear.
- Hoodies, jackets, blazers, sweaters are Outerwear.
- Pants, jeans, skirts, shorts are Bottom.
- Shirts, tops, blouses, crop tops are Top.

DO NOT:
- Infer category from image position
- Infer category from body location
- Infer category from aspect ratio
- Guess if unsure

If unsure, return null for the category.

Analyze the provided image of a fashion item.

Return a JSON object with the following keys ONLY:

{
  "category": one of [
    "Top",
    "Bottom",
    "OnePiece",
    "Outerwear",
    "Footwear",
    "Accessory",
    null
  ],
  "subcategory": short human-friendly name (e.g. "Crop Top", "Denim Jacket", "Handbag"),
  "item_type": more specific type if applicable,
  "color_primary": common color name,
  "color_hex": hex color if confident,
  "pattern": pattern name or null,
  "fabric": fabric name or null,
  "fit": fit description or null,
  "seasonality": array of seasons if applicable,
  "style_tags": array of style keywords,
  "occasion_tags": array of occasion keywords
}

STRICT REQUIREMENTS:
- category MUST be null if not 100% confident
- Never output invalid categories
- JSON only, no explanation text
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

    import asyncio
    
    # Retry loop for 429
    temp_delay = 2
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
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
            if e.response.status_code == 429:
                print(f"⚠️ Gemini Rate Limit. Retrying in {temp_delay}s...")
                await asyncio.sleep(temp_delay)
                temp_delay *= 2
                continue
            
            print(f"⚠️ Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"⚠️ Gemini API response parsing error: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Gemini API request failed: {e}")
            return None
    
    return None
