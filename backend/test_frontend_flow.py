"""
Direct frontend simulation test - mimics what browser does
"""
import requests

# Simulating the frontend flow
BASE_URL = "http://127.0.0.1:8000"

print("Step 1: Login (get token)")
resp = requests.post(f"{BASE_URL}/auth/token", data={
    "username": "somisetty@example.com",
    "password": "password123"
})
token = resp.json()["access_token"]
print(f"✅ Token: {token[:20]}...")

headers = {
    "Authorization": f"Bearer {token}",
}

print("\nStep 2: Get wardrobe items")
resp = requests.get(f"{BASE_URL}/wardrobe/", headers=headers)
items = resp.json()
print(f"✅ Found {len(items)} items")

if items:
    item_id = items[0]['id']
    print(f"\nStep 3: Delete item {item_id}")
    resp = requests.delete(f"{BASE_URL}/wardrobe/{item_id}", headers=headers)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
    
    print(f"\nStep 4: Verify deletion")
    resp = requests.get(f"{BASE_URL}/wardrobe/", headers=headers)
    new_items = resp.json()
    print(f"   Items before: {len(items)}")
    print(f"   Items after: {len(new_items)}")
    
    if len(new_items) < len(items):
        print("✅ DELETE WORKS PERFECTLY")
    else:
        print("❌ Item not deleted")
        
    # Check what the user is logged in as in browser
    print(f"\n📌 Make sure browser is logged in as: somisetty@example.com")
    print(f"📌 Frontend URL: http://localhost:5173")
    print(f"📌 Backend logs should show DELETE request when you click trash icon")
