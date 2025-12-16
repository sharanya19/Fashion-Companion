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

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-preview-02-05:generateContent?key={settings.GEMINI_API_KEY}",
            json=payload
        )

    raw = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(raw.replace("```json", "").replace("```", "").strip())
