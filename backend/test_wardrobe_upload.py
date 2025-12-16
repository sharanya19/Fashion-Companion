"""
Test script for wardrobe upload functionality
"""
import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_wardrobe_upload():
    """Test wardrobe upload with a test image"""
    
    # First, login to get token
    print("🔐 Logging in...")
    login_data = {
        "username": "testuser@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Check if we have a test image
    test_images = [
        "backend/uploads/blake_lively.jpg",
        "backend/uploads/taylor_swift.jpg",
        "backend/uploads/user_photo.jpg"
    ]
    
    test_image = None
    for img_path in test_images:
        if os.path.exists(img_path):
            test_image = img_path
            break
    
    if not test_image:
        print("⚠️ No test image found. Creating a simple test...")
        # Try to get wardrobe items to verify endpoint works
        try:
            response = requests.get(f"{BASE_URL}/wardrobe/", headers=headers)
            print(f"✅ Wardrobe endpoint accessible: {response.status_code}")
            print(f"   Items: {len(response.json())}")
            return True
        except Exception as e:
            print(f"❌ Wardrobe endpoint error: {e}")
            return False
    
    # Test upload
    print(f"\n📤 Testing upload with: {test_image}")
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (os.path.basename(test_image), f, 'image/jpeg')}
            data = {'category': 'Top'}
            
            print("   Uploading... (this may take up to 15 seconds)")
            response = requests.post(
                f"{BASE_URL}/wardrobe/",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Item ID: {result.get('id')}")
                print(f"   Category: {result.get('category')}")
                print(f"   Color: {result.get('color_name', 'N/A')}")
                print(f"   Match Level: {result.get('match_level')}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ Upload timed out (>30s)")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 WARDROBE UPLOAD TEST")
    print("="*60)
    test_wardrobe_upload()
    print("\n" + "="*60)

