import asyncio
import os
import json
from app.services import vision_service, clothing_normalizer
from app.config import settings

# Test files from recent user uploads
FILES = [
    "uploaded_image_1765968663555.png", # The one from the latest request
    "uploaded_image_0_1765968355676.png",
    "uploaded_image_1_1765968355676.png"
]
BASE_DIR = "C:/Users/somis/.gemini/antigravity/brain/14745207-71d2-4df2-99f2-89b20fb63e91"

async def diagnose():
    print("🔬 DIAGNOSTIC RUN START")
    print(f"🔑 API Key: {'Set' if settings.GEMINI_API_KEY else 'MISSING'}")
    
    for filename in FILES:
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            print(f"⚠️ File missing: {path}")
            continue
            
        print(f"\n📸 Analyzing: {filename}")
        try:
            # 1. Raw AI Output
            ai_data = await vision_service.analyze_clothing_image(path)
            print(f"   🤖 AI Raw Output: {json.dumps(ai_data, indent=2)}")
            
            if not ai_data:
                print("   ❌ AI returned None")
                continue

            # 2. Normalization Check
            cat_input = [
                ai_data.get("category"),
                ai_data.get("subcategory"),
                ai_data.get("type"),
                ai_data.get("item_type"),
            ]
            print(f"   📥 Normalizer Inputs: {cat_input}")
            
            normalized = clothing_normalizer.normalize_category(*cat_input)
            print(f"   🏷️ Normalized Category: {normalized}")
            
            # 3. Allowed Check
            ALLOWED = {"Top", "Bottom", "OnePiece", "Outerwear", "Footwear", "Accessory"}
            is_allowed = normalized in ALLOWED
            print(f"   ✅ Allowed? {is_allowed}")
            
            # 4. Color Check
            hex_code = ai_data.get("color_hex")
            print(f"   🎨 Color Hex: {hex_code}")
            
        except Exception as e:
            print(f"   🔥 Error: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose())
