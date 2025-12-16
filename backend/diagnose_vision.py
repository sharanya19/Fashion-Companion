import asyncio
from app.services import vision_service
from app.config import settings
import os

# Use an existing large file from uploads
UPLOAD_DIR = "uploads/wardrobe"
TEST_FILE = None

# Find a file
if os.path.exists(UPLOAD_DIR):
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.jpg')]
    if files:
        TEST_FILE = os.path.join(UPLOAD_DIR, files[0])

async def test_vision():
    print(f"🔑 API Key Present: {bool(settings.GEMINI_API_KEY)}")
    if not settings.GEMINI_API_KEY:
        print("❌ NO API KEY FOUND. This is the problem.")
        return

    if not TEST_FILE:
        print("❌ No test file found.")
        return

    # List models
    print("Checking available models...")
    models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.GEMINI_API_KEY}"
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(models_url)
            if resp.status_code == 200:
                data = resp.json()
                print("Available Models:")
                for m in data.get('models', []):
                    if 'generateContent' in m.get('supportedGenerationMethods', []):
                        print(f" - {m['name']}")
            else:
                print(f"Failed to list models: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Model list failed: {e}")

    print(f"📸 Analyzing {TEST_FILE}...")
    try:
        result = await vision_service.analyze_clothing_image(TEST_FILE)
        print("\n--- RAW RESULT ---")
        print(result)
        print("------------------")
        
        if result:
            print(f"Category: {result.get('category')}")
            print(f"Subcategory: {result.get('subcategory')}")
        else:
            print("Result is None (Vision Failed).")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_vision())
