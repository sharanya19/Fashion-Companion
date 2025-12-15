"""
Real Photo Testing Suite - Simplified
"""
import sys
sys.path.append('.')

from app.services.style_analysis import analyze_user_style
import json

# Test subjects with expert consensus
test_subjects = [
    {
        "name": "Priyanka Chopra",
        "file": "uploads/priyanka_chopra.jpg",
        "expert": "Autumn - Deep or True",
    },
    {
        "name": "Hailey Bieber",  
        "file": "uploads/hailey_bieber.jpg",
        "expert": "Spring - Light",
    },
    {
        "name": "Taylor Swift",
        "file": "uploads/taylor_swift.jpg",
        "expert": "Summer - Light or Soft",
    },
    {
        "name": "Blake Lively",
        "file": "uploads/blake_lively.jpg",
        "expert": "Spring - Light",
    },
    {
        "name": "Your Photo",
        "file": "uploads/user_photo.jpg",
        "expert": "Unknown - First analysis",
    }
]

print("\n" + "="*80)
print("REAL PHOTO COLOR ANALYSIS TEST")
print("="*80)
print(f"\nTesting {len(test_subjects)} subjects\n")

results = []

for i, subject in enumerate(test_subjects, 1):
    print(f"\n{'='*80}")
    print(f"#{i} - {subject['name']}")
    print(f"{'='*80}")
    print(f"Expert: {subject['expert']}")
    print(f"\nRunning Analysis...")
    
    try:
        analysis = analyze_user_style(
            email=None,
            file_path=subject['file'],
            manual_signal=None
        )
        
        result = {
            "name": subject['name'],
            "expected": subject['expert'],
            "actual": f"{analysis['season']} - {analysis['season_subtype']}",
            "season": analysis['season'],
            "subtype": analysis['season_subtype'],
            "confidence": float(analysis['confidence_score']),
            "undertone": analysis['undertone']
        }
        
        if 'debug_info' in analysis:
            result['debug'] = {
                "skin_l": float(analysis['debug_info'].get('skin_l', 0)),
                "skin_b": float(analysis['debug_info'].get('skin_b', 0)),
                "hair_l": float(analysis['debug_info'].get('hair_l', 0)),
                "chroma": float(analysis['debug_info'].get('chroma', 0)),
                "contrast": float(analysis['debug_info'].get('contrast', 0))
            }
        
        results.append(result)
        
        print(f"\nRESULTS:")
        print(f"  Season: {analysis['season']}")
        print(f"  Subtype: {analysis['season_subtype']}")
        print(f"  Confidence: {analysis['confidence_score']*100:.1f}%")
        print(f"  Undertone: {analysis['undertone']}")
        
        if 'debug_info' in analysis:
            debug = analysis['debug_info']
            print(f"\n  Debug:")
            print(f"    Skin L={debug.get('skin_l', 0):.1f}, B={debug.get('skin_b', 0):.1f}")
            print(f"    Hair L={debug.get('hair_l', 0):.1f}")
            print(f"    Chroma={debug.get('chroma', 0):.1f}, Contrast={debug.get('contrast', 0):.1f}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        result = {
            "name": subject['name'],
            "expected": subject['expert'],
            "error": str(e)
        }
        results.append(result)

# Summary
print(f"\n\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}\n")

for i, result in enumerate(results, 1):
    if 'error' in result:
        print(f"{i}. {result['name']}: FAILED - {result['error']}")
    else:
        print(f"{i}. {result['name']}")
        print(f"   Expert: {result['expected']}")
        print(f"   System: {result['actual']} ({result['confidence']*100:.0f}%)")
        print(f"   Undertone: {result['undertone']}")
        if 'debug' in result:
            d = result['debug']
            print(f"   Values: L={d['skin_l']:.0f}, B={d['skin_b']:.0f}, H={d['hair_l']:.0f}, C={d['chroma']:.0f}")
        print()

# Save results
with open('real_photo_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: real_photo_test_results.json")
print(f"\n{'='*80}\n")
