from app.services.style_analysis import analyze_user_style
import os

# Target Anne Hathaway image
TEST_IMAGE_PATH = r"C:/Users/somis/.gemini/antigravity/brain/bd557c17-c5a2-42b0-9675-21c23fa5775f/uploaded_image_1765800239272.jpg"

def test_anne():
    print("🧪 TEST: Anne Hathaway (Expected: True Winter)")
    print(f"Target Image: {TEST_IMAGE_PATH}")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print("❌ Image file not found")
        return

    try:
        result = analyze_user_style(file_path=TEST_IMAGE_PATH)
        
        print("\n" + "="*60)
        print("🚀 ANALYSIS RESULT")
        print("="*60)
        
        print(f"\n🎨 SEASON: {result['season']}")
        print(f"✨ SUBTYPE: {result['season_subtype']}")
        print(f"🌡️  UNDERTONE: {result['undertone']}")
        print(f"📊 CONFIDENCE: {result['confidence_score']*100:.1f}%")
        
        print("\n" + "-"*60)
        print("📊 RAW EXTRACTED VALUES (DEBUG)")
        print("-"*60)
        info = result.get("debug_info", {})
        print(f"Skin L: {info.get('skin_l'):.1f} (Expected: 60-70 for Anne)")
        print(f"Skin B: {info.get('skin_b'):.1f} (Expected: -5 to +5 for cool/neutral)")
        print(f"Hair L: {info.get('hair_l'):.1f} (Expected: 10-20 for dark brown)")
        print(f"Eye L: {info.get('eye_l'):.1f}")
        print(f"Chroma: {info.get('chroma'):.1f} (Expected: 40+ for Winter)")
        print(f"Contrast: {info.get('contrast'):.1f} (Expected: 45+ for Winter)")
        
        print("\n" + "-"*60)
        print("🔍 DIAGNOSIS")
        print("-"*60)
        
        skin_l = info.get('skin_l', 0)
        skin_b = info.get('skin_b', 0)
        chroma = info.get('chroma', 0)
        contrast = info.get('contrast', 0)
        
        issues = []
        if skin_l < 55:
            issues.append(f"❌ Skin too dark ({skin_l:.1f} < 55) - blocks Winter")
        if chroma < 38:
            issues.append(f"❌ Chroma too low ({chroma:.1f} < 38) - blocks Winter")
        if contrast < 45:
            issues.append(f"⚠️  Contrast borderline ({contrast:.1f} < 45)")
        if skin_b > 8:
            issues.append(f"❌ Undertone too warm ({skin_b:.1f} > 8) - blocks Winter")
        
        if issues:
            print("BLOCKING ISSUES:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ All Winter gates should pass!")
        
        print("\n" + "="*60)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_anne()
