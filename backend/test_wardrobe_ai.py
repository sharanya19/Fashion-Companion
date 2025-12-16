import requests
import json
import os

BASE_URL = "http://localhost:8002"
TEST_USER = "test@example.com"
TEST_PASS = "password123"

# Your specific images
IMAGES = [
    r"C:/Users/somis/.gemini/antigravity/brain/6f449b4d-55ec-4311-864c-dab63564af4f/uploaded_image_0_1765808799370.jpg",
    r"C:/Users/somis/.gemini/antigravity/brain/6f449b4d-55ec-4311-864c-dab63564af4f/uploaded_image_1_1765808799370.jpg",
    r"C:/Users/somis/.gemini/antigravity/brain/6f449b4d-55ec-4311-864c-dab63564af4f/uploaded_image_2_1765808799370.jpg",
    r"C:/Users/somis/.gemini/antigravity/brain/6f449b4d-55ec-4311-864c-dab63564af4f/uploaded_image_3_1765808799370.jpg",
    r"C:/Users/somis/.gemini/antigravity/brain/6f449b4d-55ec-4311-864c-dab63564af4f/uploaded_image_4_1765808799370.jpg"
]

def login():
    session = requests.Session()
    try:
        response = session.post(f"{BASE_URL}/auth/token", data={"username": TEST_USER, "password": TEST_PASS})
        if response.status_code != 200:
            print("Creating test user...")
            session.post(f"{BASE_URL}/auth/register", json={"email": TEST_USER, "password": TEST_PASS, "full_name": "Test User"})
            response = session.post(f"{BASE_URL}/auth/token", data={"username": TEST_USER, "password": TEST_PASS})
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_upload_images(token):
    print("\n📸 Testing AI Auto-Tagging on Your Images...")
    headers = {"Authorization": f"Bearer {token}"}
    
    for i, img_path in enumerate(IMAGES):
        print(f"\n--- Uploading Image {i+1} ---")
        if not os.path.exists(img_path):
            print(f"❌ File not found: {img_path}")
            continue
            
        try:
            with open(img_path, "rb") as f:
                # Basic fallback category (AI should override/refine)
                data = {"category": "Top"} 
                files = {"file": (os.path.basename(img_path), f, "image/jpeg")}
                
                response = requests.post(f"{BASE_URL}/wardrobe/", files=files, data=data, headers=headers)
                
                if response.status_code == 200:
                    item = response.json()
                    ai_meta = item.get("ai_metadata")
                    if ai_meta:
                        print("✅ AI Analysis Success!")
                        print(f"   Category: {ai_meta.get('category')} > {ai_meta.get('subcategory')}")
                        print(f"   Color: {ai_meta.get('color_primary')}")
                        print(f"   Vibe: {ai_meta.get('style_tags')}")
                        print(f"   Season: {ai_meta.get('seasonality')}")
                    else:
                        print("⚠️ Uploaded, but No AI Metadata returned.")
                else:
                    print(f"❌ Upload Failed: {response.text}") # Prints detail now
        except Exception as e:
            print(f"❌ Error: {e}")

def test_stylist(token):
    print("\n👗 Testing AI Stylist (Outfit Gen)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Request an outfit specifically using these items
    payload = {
        "occasion": "Casual University Day",
        "weather": "Cool",
        "vibe": "Comfortable"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/outfits/generate", json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("\n✨ Generated Outfit:")
            print(f"   Name: {data.get('outfit_name')}")
            print(f"   Items Used:")
            for item in data.get('items', []):
                print(f"    - ID {item.get('item_id')}: {item.get('reason')}")
            print(f"   Explanation: {data.get('explanation')}")
        else:
            print(f"❌ Stylist Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    token = login()
    if token:
        test_upload_images(token)
        test_stylist(token)
