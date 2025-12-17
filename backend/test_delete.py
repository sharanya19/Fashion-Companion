"""
Test delete functionality directly
"""
import requests

BASE_URL = "http://localhost:8000"

# Login first
resp = requests.post(f"{BASE_URL}/auth/token", data={
    "username": "somisetty@example.com",
    "password": "password123"
})

if resp.status_code != 200:
    print(f"❌ Login failed: {resp.status_code}")
    print(resp.text)
    exit(1)

token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get first item
resp = requests.get(f"{BASE_URL}/wardrobe/", headers=headers)
items = resp.json()

if not items:
    print("No items in wardrobe")
    exit(0)

first_item = items[0]
item_id = first_item['id']
print(f"Testing delete for item ID: {item_id}")
print(f"Category: {first_item['category']}")

# Test DELETE
resp = requests.delete(f"{BASE_URL}/wardrobe/{item_id}", headers=headers)
print(f"\nDELETE Status: {resp.status_code}")
print(f"Response: {resp.json()}")

# Verify it's gone
resp = requests.get(f"{BASE_URL}/wardrobe/", headers=headers)
new_items = resp.json()
print(f"\nItems before: {len(items)}")
print(f"Items after: {len(new_items)}")

if len(new_items) < len(items):
    print("✅ Delete successful!")
else:
    print("❌ Delete failed - item still exists")
