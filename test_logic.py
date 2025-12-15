import requests
import random
import string

BASE_URL = "http://localhost:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def test_signup_and_analysis():
    email = f"test_{get_random_string()}@example.com"
    password = "password123"
    full_name = "Test User"

    print(f"1. Registering user: {email}")
    payload = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        response.raise_for_status()
        user_data = response.json()
        print("   -> Registration Successful")
        
        # Login to get token (though not needed if we check DB, but let's use API)
        print("2. Logging in to get token")
        data = {
            "username": email,
            "password": password
        }
        token_res = requests.post(f"{BASE_URL}/auth/token", data=data)
        token_res.raise_for_status()
        token = token_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("3. Fetching Analysis Result")
        analysis_res = requests.get(f"{BASE_URL}/profile/analysis", headers=headers)
        analysis_res.raise_for_status()
        result = analysis_res.json()
        
        print("\n--- ANALYSIS RESULT ---")
        print(f"Season: {result['season']}")
        print(f"Subtype: {result['season_subtype']}")
        print(f"Skin Tone (Debug): {result['skin_tone']}")
        print(f"Undertone: {result['undertone']}")
        print(f"Eye Color: {result['eye_color']}")
        print("-----------------------")
        
        # Validation
        if result['season'] and result['season_subtype']:
             print("\n✅ TEST PASSED: Analysis generated valid season data.")
        else:
             print("\n❌ TEST FAILED: Missing season data.")
             
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response Content: {e.response.text}")

if __name__ == "__main__":
    test_signup_and_analysis()
