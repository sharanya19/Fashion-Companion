import requests
import random
import string
import time

BASE_URL = "http://localhost:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def run_simulation(iterations=15):
    print(f"🚀 Starting Palette v6 Diversity Simulation ({iterations} users)...")
    
    results = []
    
    for i in range(iterations):
        email = f"user_{get_random_string()}@test.com"
        password = "password123"
        
        # Register
        try:
            res = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "full_name": "Sim User"})
            res.raise_for_status()
            
            # Login
            token_res = requests.post(f"{BASE_URL}/auth/token", data={"username": email, "password": password})
            token = token_res.json()["access_token"]
            
            # Get Analysis
            analysis_res = requests.get(f"{BASE_URL}/profile/analysis", headers={"Authorization": f"Bearer {token}"})
            data = analysis_res.json()
            
            results.append(data['season_subtype'])
            print(f"User {i+1}: {data['season_subtype']} (Skin: {data['skin_tone']})")
            
        except Exception as e:
            print(f"❌ Error: {e}")

    # Diversity Check
    unique_seasons = set(results)
    print("\n📊 SIMULATION STATS")
    print(f"Total Simulations: {iterations}")
    print(f"Unique Results: {len(unique_seasons)}")
    print("Distribution:")
    for season in unique_seasons:
        count = results.count(season)
        print(f"  - {season}: {count} ({round(count/iterations*100)}%)")
        
    if len(unique_seasons) < 4:
        print("\n❌ FAILURE: Low diversity detected!")
        exit(1)
    else:
        print("\n✅ SUCCESS: High diversity confirmed.")

if __name__ == "__main__":
    time.sleep(2) # wait for server
    run_simulation()
