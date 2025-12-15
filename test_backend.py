import requests
import json

def test_register():
    url = "http://localhost:8000/auth/register"
    payload = {
        "email": "debug_user_final@example.com",
        "password": "password123",
        "full_name": "Debug User"
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_register()
