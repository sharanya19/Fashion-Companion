"""
Quick API Test Script
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("🧪 TESTING BACKEND API")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n[1] Testing Root Endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"✅ Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    
    # Test 2: Login (use existing user)
    print("\n[2] Testing Login...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/token", data={
            "username": "somisetty@example.com",
            "password": "password123"
        })
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"✅ Login successful")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Login failed: {resp.status_code}")
            print(f"   Response: {resp.text}")
            return
    except Exception as e:
        print(f"❌ Failed: {e}")
        return
    
    # Test 3: Get Profile
    print("\n[3] Testing Profile...")
    try:
        resp = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print(f"✅ Status: {resp.status_code}")
        if resp.status_code == 200:
            profile = resp.json()
            print(f"   User: {profile.get('email')}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4: Get Wardrobe
    print("\n[4] Testing Wardrobe...")
    try:
        resp = requests.get(f"{BASE_URL}/wardrobe/", headers=headers)
        print(f"✅ Status: {resp.status_code}")
        if resp.status_code == 200:
            items = resp.json()
            print(f"   Total items: {len(items)}")
            
            # Show category breakdown
            categories = {}
            for item in items:
                cat = item['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            print("\n   Category Breakdown:")
            for cat, count in sorted(categories.items()):
                print(f"   - {cat}: {count}")
                
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
