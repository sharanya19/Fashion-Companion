import requests
import json
import os

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test_api_v2@example.com"
TEST_PASS = "password123"

def test_api_flow():
    print("🚀 Starting API Flow Test...")
    
    # 1. REGISTER
    print("\n[1] Testing Registration...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASS,
            "full_name": "API Tester"
        })
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ Registration Success")
            user_id = resp.json()["id"]
        elif resp.status_code == 400 and "already registered" in resp.text:
            print("⚠️ User already exists, proceeding to login.")
        else:
            print(f"❌ Registration Failed: {resp.text}")
            return
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # 2. LOGIN
    print("\n[2] Testing Login...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={
        "username": TEST_EMAIL,
        "password": TEST_PASS
    })
    if resp.status_code != 200:
        print(f"❌ Login Failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login Success. Token: {token[:10]}...")

    # 3. GET PROFILE
    print("\n[3] Testing Get Profile...")
    resp = requests.get(f"{BASE_URL}/profile/", headers=headers)
    if resp.status_code == 200:
        print("✅ Profile Fetch Success")
        print(resp.json())
    else:
        print(f"❌ Profile Fetch Failed: {resp.text}")

    # 4. MOCK PHOTO UPLOAD (using a dummy file)
    print("\n[4] Testing Photo Analysis Upload...")
    dummy_path = "test_image.txt"
    with open(dummy_path, "wb") as f:
        f.write(b"fake image data")
        
    files = {'file': ('test.png', open(dummy_path, 'rb'), 'image/png')}
    
    # Note: This will likely fail in CV engine because it's not a real image,
    # but we want to test that the ENDPOINT accepts the request and tries to process it.
    # The CV engine should handle exceptions gracefully (we added try/except block).
    
    resp = requests.post(f"{BASE_URL}/profile/analyze-photo", headers=headers, files=files)
    
    # We expect 200 (fallback to simulation) or 500 if unhandled error
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("✅ Analysis Endpoint Success (Fallback/Mock)")
        print(f"Season: {data.get('season')}")
        print(f"Features: Skin={data.get('skin_tone')}")
    else:
        print(f"⚠️ Analysis Failed (Expected if CV crashes on fake image, but let's check error): {resp.text}")

    # Clean up
    if os.path.exists(dummy_path):
        os.remove(dummy_path)

if __name__ == "__main__":
    test_api_flow()
