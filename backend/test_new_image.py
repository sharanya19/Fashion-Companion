from app.services.style_analysis import analyze_user_style
import os

# Target the new uploaded image
TEST_IMAGE_PATH = r"C:/Users/somis/.gemini/antigravity/brain/bd557c17-c5a2-42b0-9675-21c23fa5775f/uploaded_image_1765799740435.jpg"

def test_new_image():
    print("🧪 TEST: New Celebrity Image Analysis")
    print(f"Target Image: {TEST_IMAGE_PATH}")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print("❌ Image file not found at path. Please check the path.")
        return

    try:
        # Run Analysis
        result = analyze_user_style(file_path=TEST_IMAGE_PATH)
        
        print("\n🚀 ENGINE RESULT:")
        print(f"Season: {result['season']}")
        print(f"Subtype: {result['season_subtype']}")
        print(f"Undertone: {result['undertone']}")
        print(f"Confidence: {result['confidence_score']}")
        
        print("\n📊 Extracted Features (Debug Info):")
        info = result.get("debug_info", {})
        print(f" - Skin L: {info.get('skin_l'):.1f} (0=Black, 100=White)")
        print(f" - Skin B: {info.get('skin_b'):.1f} (Negative=Cool, Positive=Warm)")
        print(f" - Hair L: {info.get('hair_l'):.1f} (Higher = Lighter)")
        print(f" - Eye L: {info.get('eye_l'):.1f}")
        print(f" - Chroma: {info.get('chroma'):.1f} (Color saturation)")
        print(f" - Contrast: {info.get('contrast'):.1f}")
        
        print("\n🎨 Interpreted Features:")
        print(f" - Skin: {result['skin_tone']['name']} ({result['skin_tone']['hex']})")
        print(f" - Eyes: {result['eye_color']['name']}")
        print(f" - Hair: {result['hair_color']['name']}")
        
        print("\n📝 Explanation:")
        for line in result.get("explanation", []):
            print(f" - {line}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_image()
