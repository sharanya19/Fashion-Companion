import asyncio
import os
import httpx
from app.services import vision_service
from app.config import settings

# specific images from user metadata
FILES_TO_TEST = [
    "uploaded_image_0_1765811734564.jpg",
    "uploaded_image_1_1765811734564.jpg",
    "uploaded_image_2_1765811734564.jpg",
    "uploaded_image_3_1765811734564.jpg"
]
UPLOAD_DIR = "C:/Users/somis/.gemini/antigravity/brain/6f449b4d-55ec-4311-864c-dab63564af4f"

async def run_simulation():
    print(f"🔬 Starting Auto-Tagging Simulation...")
    print(f"🔑 API Key Configured: {'Yes' if settings.GEMINI_API_KEY else 'No'}")
    
    # Check model availability first
    print("\n📡 Checking Available Models...")
    models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.GEMINI_API_KEY}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(models_url)
            if resp.status_code == 200:
                data = resp.json()
                print("✅ API Connection Successful. Available Models:")
                models = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
                for m in models:
                    print(f"   - {m}")
            else:
                print(f"❌ Failed to list models. Status: {resp.status_code}")
                print(f"   Body: {resp.text[:500]}")
    except Exception as e:
        print(f"❌ Network Error checking models: {e}")

    print("\n📸 Processing Test Images...")
    for filename in FILES_TO_TEST:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {filename}")
            continue
            
        print(f"\n------------------------------------------------")
        print(f"🖼️ Analyzing: {filename}")
        
        try:
            # We call the service function directly
            # Note: We need to ensure vision_service is using the updated code
            result = await vision_service.analyze_clothing_image(file_path)
            
            if result:
                print("✅ Success!")
                print(f"   Category:    {result.get('category')}")
                print(f"   Subcategory: {result.get('subcategory')}")
                print(f"   Color Name:  {result.get('color_primary')}")
                print(f"   Raw JSON:    {result}")
            else:
                print("❌ Failed: Result is None")
                
        except Exception as e:
            print(f"🔥 Exception during analysis: {e}")
            
        # Add delay to avoid Rate Limits (429) if that's the issue
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_simulation())
