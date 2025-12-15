from app.services.style_analysis import analyze_user_style
import os

# Target the new uploaded image
TEST_IMAGE_PATH = r"C:/Users/somis/.gemini/antigravity/brain/bd557c17-c5a2-42b0-9675-21c23fa5775f/uploaded_image_1765799911356.jpg"

def test_user_image():
    print("🧪 TEST: User Image Analysis")
    print(f"Target Image: {TEST_IMAGE_PATH}")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print("❌ Image file not found at path. Please check the path.")
        return

    try:
        # Run Analysis
        result = analyze_user_style(file_path=TEST_IMAGE_PATH)
        
        print("\n" + "="*60)
        print("🚀 YOUR COLOR SEASON ANALYSIS")
        print("="*60)
        
        print(f"\n🎨 SEASON: {result['season']}")
        print(f"✨ SUBTYPE: {result['season_subtype']}")
        print(f"🌡️  UNDERTONE: {result['undertone']}")
        print(f"📊 CONFIDENCE: {result['confidence_score']*100:.1f}%")
        
        print("\n" + "-"*60)
        print("📊 EXTRACTED FEATURES")
        print("-"*60)
        info = result.get("debug_info", {})
        print(f"Skin Lightness: {info.get('skin_l'):.1f}/100 (0=Dark, 100=Light)")
        print(f"Skin Undertone: {info.get('skin_b'):.1f} ({'Warm' if info.get('skin_b', 0) > 0 else 'Cool'})")
        print(f"Hair Lightness: {info.get('hair_l'):.1f}/100")
        print(f"Eye Lightness: {info.get('eye_l'):.1f}/100")
        print(f"Chroma (Saturation): {info.get('chroma'):.1f}")
        print(f"Contrast: {info.get('contrast'):.1f}")
        
        print("\n" + "-"*60)
        print("🎨 YOUR FEATURES")
        print("-"*60)
        print(f"👁️  Eyes: {result['eye_color']['name']}")
        print(f"💇 Hair: {result['hair_color']['name']}")
        print(f"🧴 Skin: {result['skin_tone']['name']} ({result['skin_tone']['hex']})")
        
        print("\n" + "-"*60)
        print("📝 WHY THIS SEASON?")
        print("-"*60)
        for i, line in enumerate(result.get("explanation", []), 1):
            print(f"{i}. {line}")
        
        print("\n" + "-"*60)
        print("🎨 YOUR BEST COLORS (Sample)")
        print("-"*60)
        for i, color in enumerate(result.get("best_colors", [])[:5], 1):
            print(f"{i}. {color['name']:20s} {color['hex']}")
        
        print("\n" + "="*60)
        print("✅ Analysis Complete!")
        print("="*60)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_image()
