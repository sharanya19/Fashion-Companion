from app.services.style_analysis import analyze_user_style
import json

def test_deep_autumn_image():
    print("🧪 TEST: Real Image -> Signal Simulation")
    print("---------------------------------------")
    print("Target Image: 'Deep Autumn' (User uploaded)")
    print("Visual Estimates:")
    print(" -  Skin: Medium-Deep, Warm/Olive (L~50, B~15)")
    print(" -  Hair: Deep/Black (L~15)")
    print(" -  Eyes: Deep Brown (L~20)")
    print(" -  Chroma: Moderate/Rich (C~40)")
    
    # Construct the "Computer Vision" signal package
    real_image_signals = {
        "skin_l": 50,    # Medium-Deep
        "skin_b": 15,    # Distinctly Warm
        "chroma": 40,    # Moderate saturation
        "hair_l": 15,    # Very dark hair
        "eye_l": 20      # Dark eyes
    }
    
    # Run the engine
    result = analyze_user_style(manual_signal=real_image_signals)
    
    print("\n🚀 ENGINE RESULT:")
    print(f"Season: {result['season']}")
    print(f"Subtype: {result['season_subtype']}")
    print(f"Debug String: {result['skin_tone']}")
    print(f"Confidence: {result['confidence_score']}")
    
    # Verification
    if result['season_subtype'] == "Deep Autumn":
        print("\n✅ SUCCESS: Engine safely identified Deep Autumn.")
    else:
        print("\n❌ FAILURE: Engine misidentified.")
        # Diagnostics
        if result['season'] == "Winter":
            print("  -> Reason: Allowed Warm skin into Winter?")
        if result['season'] == "Spring":
            print("  -> Reason: Failed Depth Gate (Spring allowed for Deep skin).")

if __name__ == "__main__":
    test_deep_autumn_image()
