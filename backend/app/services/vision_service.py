import base64
import json
import httpx
from ..config import settings
import os

async def analyze_clothing_image(image_path: str) -> dict:
    """
    Uses Gemini 1.5 Flash Vision to analyze a clothing item.
    Returns structured JSON with attributes.
    """
    if not settings.GEMINI_API_KEY:
        print("⚠️ Gemini API Key missing. Skipping Vision Analysis.")
        return None

    # Encode image
    try:
        with open(image_path, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Failed to read image: {e}")
        return None

    # Construct Prompt
    prompt_text = """
    Analyze this fashion item image. Return strictly valid JSON.
    Identify:
    - category (Top, Bottom, One-Piece, Outerwear, Footwear, Accessory)
    - subcategory (e.g. T-Shirt, Jeans, Maxi Dress)
    - type (e.g. V-neck, Skinny, Sleeveless)
    - color_primary (General name, e.g. Navy Blue)
    - color_secondary (if any)
    - pattern (Solid, Striped, Floral, etc.)
    - fabric (Cotton, Silk, Denim, Leather, etc. guess based on texture)
    - fit (Tight, Regular, Loose, Oversized)
    - seasonality (List: Spring, Summer, Autumn, Winter)
    - occasion_tags (List: Work, Party, Casual, Gym, etc.)
    - style_tags (List: Minimal, Boho, Streetwear, etc.)

    Output Format:
    {
      "category": "...",
      "subcategory": "...",
      "type": "...",
      "color_primary": "...",
      "color_secondary": "...",
      "pattern": "...",
      "fabric": "...",
      "fit": "...",
      "seasonality": ["..."],
      "occasion_tags": ["..."],
      "style_tags": ["..."]
    }
    """

    
    # Use Lite model for speed
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-preview-02-05:generateContent?key={settings.GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_image}}
            ]
        }],
        "generationConfig": {"response_mime_type": "application/json"}
    }

    import asyncio
    
    # Reduced retries for better UX (Fail fast, fallback to local color)
    max_retries = 3
    base_delay = 2
    
    ai_result = None
    
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries + 1):
            try:
                response = await client.post(url, json=payload, timeout=20.0)
                
                if response.status_code == 429:
                    if attempt < max_retries:
                        wait = base_delay * (2 ** attempt)
                        print(f"⚠️ Gemini Rate Limit (429). Retrying in {wait}s...")
                        await asyncio.sleep(wait)
                        continue
                
                if response.status_code == 200:
                    result = response.json()
                    raw_json = result["candidates"][0]["content"]["parts"][0]["text"]
                    raw_json = raw_json.replace("```json", "").replace("```", "").strip()
                    ai_result = json.loads(raw_json)
                    break # Success
                    
            except Exception as e:
                print(f"❌ Gemini Attempt {attempt} Error: {e}")
                
    # --- HYBRID FALLBACK ---
    # If AI failed, or AI missed color, use Local Extraction
    from PIL import Image
    from collections import Counter
    
    local_hex = None
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((50, 50))
        pixels = list(img.getdata())
        # Filter vague background pixels (White/Black)
        filtered = [p for p in pixels if not (p[0]>245 and p[1]>245 and p[2]>245) and not (p[0]<15 and p[1]<15 and p[2]<15)]
        if not filtered: filtered = pixels
        
        if filtered:
            most_common = Counter(filtered).most_common(1)[0][0]
            local_hex = "#{:02x}{:02x}{:02x}".format(*most_common)
            print(f"🎨 Local Color Extracted: {local_hex}")
    except Exception as ex:
        print(f"Local Color Failed: {ex}")
        
    if ai_result:
        # Augment AI result with exact hex
        if local_hex:
            ai_result['color_primary'] = ai_result.get('color_primary') or "Unknown"
            # We inject hex into a custom field or overwrite name? 
            # Wardrobe router handles 'color_hex' from form, but we can pass it in metadata
            ai_result['local_hex'] = local_hex
        return ai_result
    
    # If AI completely failed, return partial result with local color
    if local_hex:
        print("⚠️ AI Failed, returning Local Color Fallback.")
        return {
            "category": "Uncategorized", # Let user fix
            "subcategory": "Auto-Color Detected",
            "color_primary": local_hex, # Will act as name
            "local_hex": local_hex,
            "seasonality": [],
            "occasion_tags": ["AI_OFFLINE"]
        }
        
    return None
