from typing import List, Dict
import json
import random
import httpx
from ..models import User, WardrobeItem
from ..config import settings

BASE_REQUIRED = [["OnePiece"], ["Top", "Bottom"]]
ALWAYS_REQUIRED = ["Footwear", "Accessory"]
OPTIONAL = ["Outerwear"]

class StylistService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.api_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.0-flash-lite-preview-02-05:generateContent"
            f"?key={self.api_key}"
        )

    # --------------------------------------------------
    async def generate_outfit(self, user: User, request: Dict) -> Dict:
        wardrobe = user.wardrobe_items
        if not wardrobe:
            return self._incomplete(["Top", "Bottom", "OnePiece"])

        # Try Gemini (optional)
        ai_outfit = None
        if self.api_key:
            try:
                ai_outfit = await self._generate_with_gemini(wardrobe, request)
            except Exception as e:
                print("⚠️ Gemini failed:", e)

        # Always enforce completion
        return self._force_complete(ai_outfit, wardrobe)

    # --------------------------------------------------
    async def _generate_with_gemini(self, wardrobe, request):
        inventory = [
            {"item_id": i.id, "category": i.category, "match_level": i.match_level}
            for i in wardrobe
        ]

        prompt = f"""
You are a professional fashion stylist.

WARDROBE:
{json.dumps(inventory)}

REQUEST:
{json.dumps(request)}

RULES:
- Use ONLY wardrobe items
- Build a COMPLETE outfit
- Either OnePiece OR Top + Bottom
- MUST include Footwear and Accessory
- JSON only
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        async with httpx.AsyncClient(timeout=60) as client:
            res = await client.post(self.api_url, json=payload)
            res.raise_for_status()
            
            # Safely parse response JSON with error handling
            try:
                response_data = res.json()
                if "candidates" not in response_data or not response_data["candidates"]:
                    raise ValueError("Gemini API returned empty candidates")
                
                candidate = response_data["candidates"][0]
                if "content" not in candidate or "parts" not in candidate["content"]:
                    raise ValueError("Gemini API response missing content/parts")
                
                raw = candidate["content"]["parts"][0].get("text", "")
                if not raw:
                    raise ValueError("Gemini API returned empty text")
                
                # Clean and parse JSON response
                cleaned = raw.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned)
            except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ Gemini API response parsing error: {e}")
                raise

    # --------------------------------------------------
    def _force_complete(self, outfit: Dict | None, wardrobe: List[WardrobeItem]) -> Dict:
        items = outfit["items"] if outfit and "items" in outfit else []
        selected_ids = {i["item_id"] for i in items}
        selected_items = [i for i in wardrobe if i.id in selected_ids]
        categories = {i.category for i in selected_items}

        def pick(cat):
            pool = [i for i in wardrobe if i.category == cat and i.id not in selected_ids]
            return random.choice(pool) if pool else None

        final_items = list(items)
        missing = []

        # ---- Base outfit ----
        if "OnePiece" not in categories:
            if not {"Top", "Bottom"}.issubset(categories):
                top = pick("Top")
                bottom = pick("Bottom")
                if top and bottom:
                    final_items += [
                        {"item_id": top.id, "reason": "Base top"},
                        {"item_id": bottom.id, "reason": "Base bottom"},
                    ]
                else:
                    missing += ["Top", "Bottom"]

        # ---- Required extras ----
        for cat in ALWAYS_REQUIRED:
            if cat not in categories:
                item = pick(cat)
                if item:
                    final_items.append({"item_id": item.id, "reason": f"{cat} match"})
                else:
                    missing.append(cat)

        # ---- Optional ----
        for cat in OPTIONAL:
            if cat not in categories:
                item = pick(cat)
                if item:
                    final_items.append({"item_id": item.id, "reason": f"{cat} layer"})

        return {
            "outfit_name": outfit.get("outfit_name", "Styled Outfit") if outfit else "Styled Outfit",
            "items": final_items,
            "explanation": "Complete outfit assembled from your wardrobe.",
            "missing_categories": list(set(missing)),
        }

    # --------------------------------------------------
    def _incomplete(self, cats):
        return {
            "outfit_name": "Incomplete Wardrobe",
            "items": [],
            "explanation": "Please upload missing items.",
            "missing_categories": cats,
        }


stylist = StylistService()
