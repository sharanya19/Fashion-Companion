"""
Automated Validation Test Suite
Tests system accuracy against known celebrity color seasons
"""
import sys
sys.path.append('.')

from validation_dataset import get_all_test_cases, get_dataset_stats
from app.services.style_analysis import analyze_user_style
from typing import Dict, List
import json

class ValidationTester:
    """Automated validation testing"""
    
    def __init__(self):
        self.test_cases = get_all_test_cases()
        self.results = []
    
    def simulate_analysis(self, test_case: Dict) -> Dict:
        """
        Simulate analysis based on expected characteristics
        Since we don't have actual photos, we'll create manual signals
        """
        char = test_case['characteristics']
        
        # Map characteristics to signal values
        signal = self._characteristics_to_signal(char)
        
        # Run analysis with manual signal
        try:
            result = analyze_user_style(manual_signal=signal)
            return {
                'success': True,
                'season': result['season'],
                'subtype': result['season_subtype'],
                'confidence': result['confidence_score'],
                'undertone': result['undertone']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _characteristics_to_signal(self, char: Dict) -> Dict:
        """Convert text characteristics to numerical signal"""
        
        # Parse skin tone
        skin_desc = char['skin'].lower()
        if 'fair' in skin_desc or 'light' in skin_desc:
            skin_l = 75
        elif 'medium-deep' in skin_desc or 'deep' in skin_desc:
            skin_l = 45
        elif 'medium' in skin_desc:
            skin_l = 60
        else:
            skin_l = 65
        
        # Parse undertone
        if 'cool' in skin_desc:
            skin_b = -2
        elif 'warm' in skin_desc:
            skin_b = 18
        elif 'neutral' in skin_desc:
            skin_b = 5
        else:
            skin_b = 0
        
        # Parse hair
        hair_desc = char['hair'].lower()
        if 'black' in hair_desc or 'dark brown' in hair_desc:
            hair_l = 15
        elif 'auburn' in hair_desc or 'red' in hair_desc:
            hair_l = 35
        elif 'light brown' in hair_desc or 'ash' in hair_desc:
            hair_l = 50
        elif 'blonde' in hair_desc:
            hair_l = 70
        else:
            hair_l = 40
        
        # Parse eyes
        eye_desc = char['eyes'].lower()
        if 'dark brown' in eye_desc:
            eye_l = 20
        elif 'brown' in eye_desc or 'hazel' in eye_desc:
            eye_l = 35
        elif 'green' in eye_desc:
            eye_l = 45
        elif 'blue' in eye_desc or 'gray' in eye_desc:
            eye_l = 55
        else:
            eye_l = 40
        
        # Parse contrast
        contrast_desc = char['contrast'].lower()
        if 'very high' in contrast_desc:
            # Adjust hair to create high contrast
            if skin_l > 60:
                hair_l = 15
        elif 'high' in contrast_desc:
            if skin_l > 60:
                hair_l = 20
        elif 'low' in contrast_desc:
            # Make hair closer to skin
            hair_l = skin_l - 10
        
        # Estimate chroma based on season hints
        notes = char.get('notes', '').lower()
        if 'bright' in notes or 'clear' in notes:
            chroma = 55
        elif 'muted' in notes or 'soft' in notes:
            chroma = 25
        elif 'rich' in notes:
            chroma = 35
        else:
            chroma = 40
        
        return {
            'skin_l': skin_l,
            'skin_b': skin_b,
            'hair_l': hair_l,
            'eye_l': eye_l,
            'chroma': chroma
        }
    
    def run_validation(self) -> Dict:
        """Run validation on all test cases"""
        print("="*80)
        print("🧪 CELEBRITY COLOR SEASON VALIDATION TEST")
        print("="*80)
        
        stats = get_dataset_stats()
        print(f"\n📊 Dataset: {stats['total_cases']} celebrities")
        print(f"   Seasons: {stats['season_distribution']}")
        print(f"   Subtypes: {len(stats['subtype_distribution'])} different subtypes")
        
        print("\n" + "="*80)
        print("RUNNING TESTS...")
        print("="*80 + "\n")
        
        correct_season = 0
        correct_subtype = 0
        total = len(self.test_cases)
        
        for i, test_case in enumerate(self.test_cases, 1):
            name = test_case['name']
            expected_season = test_case['expected_season']
            expected_subtype = test_case['expected_subtype']
            
            print(f"[{i}/{total}] Testing: {name}")
            print(f"   Expected: {expected_season} - {expected_subtype}")
            
            result = self.simulate_analysis(test_case)
            
            if not result['success']:
                print(f"   ❌ ERROR: {result['error']}\n")
                self.results.append({
                    'name': name,
                    'expected': f"{expected_season} - {expected_subtype}",
                    'actual': 'ERROR',
                    'match': False
                })
                continue
            
            actual_season = result['season']
            actual_subtype = result['subtype']
            
            season_match = actual_season == expected_season
            subtype_match = actual_subtype == expected_subtype
            
            if season_match:
                correct_season += 1
            if subtype_match:
                correct_subtype += 1
            
            status = "✅" if subtype_match else ("⚠️" if season_match else "❌")
            print(f"   {status} Got: {actual_season} - {actual_subtype} ({result['confidence']*100:.0f}%)")
            
            if not subtype_match:
                print(f"      → Season match: {season_match}, Subtype match: {subtype_match}")
            
            print()
            
            self.results.append({
                'name': name,
                'expected': f"{expected_season} - {expected_subtype}",
                'actual': f"{actual_season} - {actual_subtype}",
                'season_match': season_match,
                'subtype_match': subtype_match,
                'confidence': result['confidence']
            })
        
        # Calculate accuracy
        season_accuracy = (correct_season / total) * 100
        subtype_accuracy = (correct_subtype / total) * 100
        
        print("="*80)
        print("📊 VALIDATION RESULTS")
        print("="*80)
        print(f"\n✅ Season Accuracy: {correct_season}/{total} ({season_accuracy:.1f}%)")
        print(f"✅ Subtype Accuracy: {correct_subtype}/{total} ({subtype_accuracy:.1f}%)")
        
        # Show mismatches
        mismatches = [r for r in self.results if not r.get('subtype_match', False)]
        if mismatches:
            print(f"\n❌ Mismatches ({len(mismatches)}):")
            for m in mismatches:
                print(f"   • {m['name']}: Expected {m['expected']}, Got {m['actual']}")
        
        # Grade the system
        print(f"\n📈 OVERALL GRADE:")
        if subtype_accuracy >= 85:
            grade = "A (Excellent)"
        elif subtype_accuracy >= 75:
            grade = "B (Good)"
        elif subtype_accuracy >= 65:
            grade = "C (Fair)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"   {grade} - Subtype Accuracy: {subtype_accuracy:.1f}%")
        
        return {
            'total_tests': total,
            'season_accuracy': season_accuracy,
            'subtype_accuracy': subtype_accuracy,
            'correct_season': correct_season,
            'correct_subtype': correct_subtype,
            'mismatches': mismatches,
            'grade': grade
        }
    
    def save_results(self, filename='validation_results.json'):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")

if __name__ == "__main__":
    tester = ValidationTester()
    summary = tester.run_validation()
    tester.save_results()
    
    print("\n" + "="*80)
    print("✅ VALIDATION COMPLETE")
    print("="*80)
