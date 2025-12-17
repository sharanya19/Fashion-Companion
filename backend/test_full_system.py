import requests
import json
import os
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = f"test_full_{int(time.time())}@example.com"  # Unique email each run
TEST_PASS = "password123"

def print_step(msg):
    print(f"\n{'='*50}")
    print(f">>> {msg}")
    print(f"{'='*50}")

def print_result(success, msg, data=None):
    icon = "[OK]" if success else "[FAIL]"
    print(f"{icon} {msg}")
    if data:
        print(f"   Data: {str(data)[:100]}...")

def run_tests():
    print_step("STARTING FULL SYSTEM TEST")
    
    # 1. AUTHENTICATION
    print_step("Testing Authentication")
    
    # Register
    print("[1.1] Registering specific test user...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASS,
        "full_name": "Full Tester"
    })
    if resp.status_code not in [200, 400]:
        print_result(False, f"Registration failed: {resp.status_code} - {resp.text}")
        return
    print_result(True, "Registration completed or user exists")

    # Login
    print("[1.2] Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={
        "username": TEST_EMAIL,
        "password": TEST_PASS
    })
    if resp.status_code != 200:
        print_result(False, f"Login failed: {resp.text}")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result(True, "Login success", token)

    # 2. PROFILE
    print_step("Testing Profile & Style Analysis")
    resp = requests.get(f"{BASE_URL}/profile/", headers=headers)
    if resp.status_code == 200:
        print_result(True, "Get Profile success")
    else:
        print_result(False, f"Get Profile failed: {resp.text}")

    # Mock Photo Analysis
    print("[2.1] Testing Photo Analysis (Mock)...")
    dummy_path = "test_image_full.txt"
    with open(dummy_path, "wb") as f:
        f.write(b"fake image data")
    
    try:
        with open(dummy_path, 'rb') as f_img:
            files = {'file': ('test_mock.png', f_img, 'image/png')}
            resp = requests.post(f"{BASE_URL}/profile/analyze-photo", headers=headers, files=files)
        
        # Note: This might fail with 500 if CV engine tries to process 'fake image data'
        # But we check if the endpoint is reachable.
        print(f"   Analysis Status: {resp.status_code}")
        if resp.status_code == 200:
             print_result(True, "Analysis endpoint returned success (Fallback)")
        else:
             print_result(False, "Analysis endpoint returned error (Expected for fake img)", resp.text)
    finally:
        if os.path.exists(dummy_path):
            try:
                os.remove(dummy_path)
            except Exception as e:
                print(f"Warning: Could not remove {dummy_path}: {e}")

    # 3. WARDROBE
    print_step("Testing Wardrobe Management")
    
    # Upload Item
    print("[3.1] Uploading Wardrobe Item...")
    dummy_item_path = "test_shirt.txt"
    with open(dummy_item_path, "wb") as f:
        f.write(b"fake shirt image")
        
    item_id = None
    try:
        data = {
            "category": "Top", 
            "color_hex": "#FF0000",
            "color_name": "Red"
        }
        with open(dummy_item_path, 'rb') as f_img:
            files = {'file': ('shirt.png', f_img, 'image/png')}
            resp = requests.post(f"{BASE_URL}/wardrobe/", headers=headers, files=files, data=data)

        if resp.status_code == 200:
            item_data = resp.json()
            item_id = item_data["id"]
            print_result(True, "Wardrobe Upload success", item_data)
        else:
            print_result(False, f"Wardrobe Upload failed: {resp.text}")
    finally:
         if os.path.exists(dummy_item_path):
            try:
                os.remove(dummy_item_path)
            except Exception as e:
                print(f"Warning: Could not remove {dummy_item_path}: {e}")

    # Get Items
    print("[3.2] Getting Wardrobe Items...")
    resp = requests.get(f"{BASE_URL}/wardrobe/", headers=headers)
    if resp.status_code == 200:
        items = resp.json()
        print_result(True, f"Get Wardrobe success. Count: {len(items)}")
        
        # Verify the item we just uploaded is there
        found = False
        if item_id:
            for item in items:
                if item["id"] == item_id:
                    found = True
                    break
            if found:
                print("   [OK] Created item verified in list")
            else:
                print("   [FAIL] Created item NOT found in list")
    else:
        print_result(False, f"Get Wardrobe failed: {resp.text}")

    # Delete Item (Cleanup)
    if item_id:
        print(f"[3.3] Deleting Item ID {item_id}...")
        resp = requests.delete(f"{BASE_URL}/wardrobe/{item_id}", headers=headers)
        if resp.status_code == 200:
            print_result(True, "Delete Item success")
        else:
             print_result(False, f"Delete Item failed: {resp.text}")

    # 4. STYLIST CHAT
    print_step("Testing Stylist Chat")
    print("[4.1] Sending chat message...")
    chat_payload = {"message": "Hello, I need help with fashion."}
    resp = requests.post(f"{BASE_URL}/stylist/chat", headers=headers, json=chat_payload)
    if resp.status_code == 200:
         print_result(True, "Chat success", resp.json())
    elif resp.status_code == 500:
         print_result(False, "Chat failed with 500 (Likely Missing API Key or Error)", resp.text)
    else:
         print_result(False, f"Chat failed: {resp.status_code}", resp.text)

    # 5. OUTFITS
    print_step("Testing Outfit Generation")
    print("[5.1] Generating outfit...")
    outfit_payload = {
        "event_type": "Casual",
        "weather": "Sunny",
        "preferences": "Comfortable"
    }
    resp = requests.post(f"{BASE_URL}/outfits/generate", headers=headers, json=outfit_payload)
    if resp.status_code == 200:
         print_result(True, "Outfit Gen success", resp.json())
    elif resp.status_code == 500:
         print_result(False, "Outfit Gen failed with 500 (Likely Missing API Key or Error)", resp.text)
    else:
         print_result(False, f"Outfit Gen failed: {resp.status_code}", resp.text)

    print("\nAPI VERIFICATION COMPLETE")

if __name__ == "__main__":
    run_tests()
