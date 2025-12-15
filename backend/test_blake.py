from app.services.style_analysis import analyze_user_style
import os

# Target the specific uploaded image
# Note: In a real scenario, this would be the path where the API saved the upload.
# Here we point to the artifact path provided in metadata.
TEST_IMAGE_PATH = r"C:/Users/somis/.gemini/antigravity/brain/bd557c17-c5a2-42b0-9675-21c23fa5775f/uploaded_image_1765798972473.jpg"

def test_blake_lively():
    print("🧪 TEST: Blake Lively (Spring Check)")
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
        
        print("\n📊 extracted features (Debug Info):")
        info = result.get("debug_info", {})
        print(f" - Skin L: {info.get('skin_l')}")
        print(f" - Skin B: {info.get('skin_b')} (Positive = Warm, Negative = Cool)")
        print(f" - Hair L: {info.get('hair_l')} (Higher = Lighter)")
        print(f" - Chroma: {info.get('chroma')}")
        print(f" - Contrast: {info.get('contrast')}")
        
        print("\n📝 Explanation:")
        for line in result.get("explanation", []):
            print(f" - {line}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    test_blake_lively()
