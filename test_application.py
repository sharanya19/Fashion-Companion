"""
Comprehensive Application Testing Suite
Tests API endpoints, validation logic, and system functionality
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if API is running"""
    print("\n" + "="*80)
    print("🏥 TESTING API HEALTH")
    print("="*80)
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("\n" + "="*80)
    print("👤 TESTING USER REGISTRATION")
    print("="*80)
    
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ User registered successfully")
            data = response.json()
            print(f"   Access Token: {data.get('access_token', 'N/A')[:30]}...")
            return data.get('access_token')
        elif response.status_code == 400:
            print(f"ℹ️  User already exists (expected if already registered)")
            # Try login instead
            response = requests.post(f"{BASE_URL}/auth/login", data=test_user)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Logged in successfully")
                return data.get('access_token')
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return None

def test_profile_access(token):
    """Test profile access"""
    print("\n" + "="*80)
    print("📋 TESTING PROFILE ACCESS")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile retrieved successfully")
            print(f"   Full Name: {data.get('full_name', 'Not set')}")
            print(f"   Age: {data.get('age', 'Not set')}")
            return True
        else:
            print(f"❌ Profile access failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
        return False

def test_analysis_access(token):
    """Test analysis access"""
    print("\n" + "="*80)
    print("🎨 TESTING STYLE ANALYSIS ACCESS")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile/analysis", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis retrieved successfully")
            print(f"   Season: {data.get('season', 'Unknown')}")
            print(f"   Subtype: {data.get('season_subtype', 'Unknown')}")
            print(f"   Undertone: {data.get('undertone', 'Unknown')}")
            print(f"   Confidence: {data.get('confidence_score', 0):.2%}")
            print(f"   Best Colors: {len(data.get('best_colors', []))} colors")
            print(f"   Neutral Colors: {len(data.get('neutral_colors', []))} colors")
            print(f"   Accent Colors: {len(data.get('accent_colors', []))} colors")
            return data
        elif response.status_code == 404:
            print(f"ℹ️  No analysis found (need to upload photo first)")
            return None
        else:
            print(f"❌ Analysis access failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Analysis test failed: {e}")
        return None

def test_validation_statistics():
    """Test validation dataset statistics"""
    print("\n" + "="*80)
    print("📊 VALIDATION DATASET STATISTICS")
    print("="*80)
    
    import sys
    sys.path.append('./backend')
    from validation_dataset import get_dataset_stats, get_all_test_cases
    
    stats = get_dataset_stats()
    test_cases = get_all_test_cases()
    
    print(f"   Total Test Cases: {stats['total_cases']}")
    print(f"\n   Season Distribution:")
    for season, count in stats['season_distribution'].items():
        print(f"      {season}: {count}")
    
    print(f"\n   Subtype Distribution:")
    for subtype, count in sorted(stats['subtype_distribution'].items()):
        print(f"      {subtype}: {count}")
    
    return stats

def test_validation_results():
    """Analyze validation test results"""
    print("\n" + "="*80)
    print("🎯 VALIDATION RESULTS ANALYSIS")
    print("="*80)
    
    results_file = Path('./backend/validation_results.json')
    
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        total = len(results)
        season_matches = sum(1 for r in results if r['season_match'])
        subtype_matches = sum(1 for r in results if r['subtype_match'])
        
        print(f"   Total Tests: {total}")
        print(f"   Season Accuracy: {season_matches}/{total} ({season_matches/total*100:.1f}%)")
        print(f"   Subtype Accuracy: {subtype_matches}/{total} ({subtype_matches/total*100:.1f}%)")
        
        print(f"\n   ❌ Failed Cases:")
        for r in results:
            if not r['season_match']:
                print(f"      {r['name']}: {r['expected']} → {r['actual']}")
        
        return {
            'total': total,
            'season_accuracy': season_matches/total,
            'subtype_accuracy': subtype_matches/total
        }
    else:
        print("   ⚠️  No validation results found. Run: python backend/run_validation.py")
        return None

def run_full_test_suite():
    """Run all tests"""
    print("\n" + "█"*80)
    print("🚀 FASHION COMPANION APPLICATION TEST SUITE")
    print("█"*80)
    
    results = {}
    
    # Test 1: API Health
    results['api_health'] = test_api_health()
    
    if not results['api_health']:
        print("\n❌ API is not running. Please start the backend server.")
        return results
    
    # Test 2: User Registration/Login
    token = test_user_registration()
    results['auth'] = token is not None
    
    if token:
        # Test 3: Profile Access
        results['profile'] = test_profile_access(token)
        
        # Test 4: Analysis Access
        analysis = test_analysis_access(token)
        results['analysis'] = analysis is not None
    
    # Test 5: Validation Dataset
    results['validation_stats'] = test_validation_statistics()
    
    # Test 6: Validation Results
    results['validation_results'] = test_validation_results()
    
    # Summary
    print("\n" + "█"*80)
    print("📈 TEST SUITE SUMMARY")
    print("█"*80)
    
    passed = sum(1 for v in [results['api_health'], results.get('auth', False), 
                              results.get('profile', False)] if v)
    total = 3
    
    print(f"\n   Core Functionality: {passed}/{total} tests passed")
    
    if results.get('validation_results'):
        vr = results['validation_results']
        print(f"\n   Validation Performance:")
        print(f"      Season Accuracy: {vr['season_accuracy']*100:.1f}%")
        print(f"      Subtype Accuracy: {vr['subtype_accuracy']*100:.1f}%")
    
    print("\n" + "█"*80)
    
    return results

if __name__ == "__main__":
    run_full_test_suite()
