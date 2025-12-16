from typing import List, Dict
import json
import httpx
import asyncio
from ..models import User, WardrobeItem
from ..config import settings

class StylistService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        # Use Lite model for speed/efficiency
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite-preview-02-05:generateContent?key={self.api_key}"

    async def generate_outfit(self, user: User, request: Dict) -> Dict:
        """
        Generates an outfit based on user's wardrobe and request context.
        """
        if not self.api_key:
            print("⚠️ Helper: API Key missing. Using fallback.")
            return self.generate_fallback_outfit(user.wardrobe_items)

        # 1. Fetch Wardrobe
        wardrobe_items = user.wardrobe_items
        if not wardrobe_items:
            return {"error": "Wardrobe is empty! Upload items first."}

        # 2. Format Wardrobe Inventory
        inventory = []
        for item in wardrobe_items:
            inventory.append({
                "item_id": item.id,
                "category": item.category,
                "subcategory": item.subcategory,
                "color_primary": item.color_primary,
                "color_name": item.color_name,
                "pattern": item.pattern,
                "seasonality": item.seasonality, # JSON string
                "occasion_tags": item.occasion_tags, # JSON string
                "match_level": item.match_level
            })
            
        # 3. User Profile
        analysis = user.style_analysis
        profile_summary = {
            "season": analysis.season if analysis else "Unknown",
            "subtype": analysis.season_subtype if analysis else "Unknown",
            "undertone": analysis.undertone if analysis else "Unknown"
        }

        # 4. Construct MASTER PROMPT
        prompt = f"""
        You are a professional AI Fashion Stylist.
        
        CONTEXT:
        User Profile: {json.dumps(profile_summary)}
        Request: {json.dumps(request)}
        
        WARDROBE INVENTORY:
        {json.dumps(inventory)}
        
        TASK:
        Generate a complete outfit recommendation using ONLY the items in the wardrobe inventory.
        
        RULES:
        1. Respect the user's Color Season ({profile_summary['season']}). Prefer 'best' match items.
        2. Account for the user's request (Occasion: {request.get('occasion')}, Weather: {request.get('weather')}).
        3. Do NOT hallucinate items. If a category is missing (e.g. no shoes), explicitly state it in 'missing_items'.
        4. Return strictly valid JSON.
        
        OUTPUT FORMAT:
        {{
            "outfit_name": "Name of look",
            "items": [
                {{
                    "item_id": 123,
                    "reason": "Why this item works..."
                }}
            ],
            "explanation": "Why this outfit works for the occasion and season...",
            "missing_categories": ["Shoes", "Bag"]
        }}
        """

        # 5. Call LLM
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        max_retries = 3
        
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries + 1):
                try:
                    response = await client.post(self.api_url, json=payload, timeout=60.0)
                    
                    if response.status_code == 429:
                        if attempt < max_retries:
                            wait = 2 * (2 ** attempt)
                            print(f"Stylist Rate Limit. Waiting {wait}s...")
                            await asyncio.sleep(wait)
                            continue
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    raw_json = result["candidates"][0]["content"]["parts"][0]["text"]
                    raw_json = raw_json.replace("```json", "").replace("```", "").strip()
                    return json.loads(raw_json)
                    
                except Exception as e:
                    if attempt == max_retries:
                        print(f"Stylist Error: {e}")
                        return self.generate_fallback_outfit(wardrobe_items)
                
    def generate_fallback_outfit(self, items: List[WardrobeItem]) -> Dict:
        """
        Simple rule-based fallback when AI is offline.
        """
        import random
        
        tops = [i for i in items if i.category == 'Top']
        bottoms = [i for i in items if i.category == 'Bottom']
        shoes = [i for i in items if i.category == 'Footwear']
        
        if not tops or not bottoms:
            return {
                "outfit_name": "Wardrobe Audit Required",
                "items": [],
                "explanation": "Not enough items (Tops/Bottoms) for auto-generation. Please upload more clothes!",
                "missing_categories": ["Tops", "Bottoms"]
            }
            
        # Simple Random Selection
        top = random.choice(tops)
        bottom = random.choice(bottoms)
        outfit_items = [
            {"item_id": top.id, "reason": "Selected from your wardrobe (Offline Mode)"},
            {"item_id": bottom.id, "reason": "Selected from your wardrobe (Offline Mode)"}
        ]
        
        if shoes:
            shore_item = random.choice(shoes)
            outfit_items.append({"item_id": shore_item.id, "reason": "Matching footwear"})
            
        return {
            "outfit_name": "Offline Shuffle",
            "items": outfit_items,
            "explanation": "AI Brain is offline. Here is a random shuffle of your items! Add GEMINI_API_KEY for smart recommendations.",
            "missing_categories": []
        }

stylist = StylistService()
