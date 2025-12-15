"""
Production Pipeline Test
Tests the complete analysis flow with quality checks
"""
import sys
sys.path.append('.')

from app.services.production_pipeline import ProductionAnalysisPipeline

def test_production_pipeline():
    """Test the production-ready analysis pipeline"""
    
    # Initialize pipeline
    pipeline = ProductionAnalysisPipeline()
    
    print("🚀 PRODUCTION PIPELINE TEST")
    print("="*80)
    
    # Test image (Anne Hathaway)
    test_image = r"C:/Users/somis/.gemini/antigravity/brain/bd557c17-c5a2-42b0-9675-21c23fa5775f/uploaded_image_1765800239272.jpg"
    
    print(f"\n📸 Testing with: {test_image.split('/')[-1]}")
    print("="*80)
    
    # Run analysis
    result = pipeline.analyze_with_quality_check(
        file_path=test_image,
        force_analysis=True  # Analyze even if quality is poor
    )
    
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    
    if result.get('success'):
        print(f"\n✅ ANALYSIS SUCCESSFUL")
        print(f"\n🎨 Season: {result['season']}")
        print(f"✨ Subtype: {result['season_subtype']}")
        print(f"🌡️  Undertone: {result['undertone']}")
        print(f"📊 Confidence: {result['confidence_score']*100:.1f}%")
        print(f"📸 Photo Quality: {result['photo_quality_score']:.1f}/100")
        
        if result.get('original_confidence') != result.get('confidence_score'):
            print(f"   (Original: {result['original_confidence']*100:.1f}%, adjusted for photo quality)")
        
        print(f"\n📝 Explanation:")
        for line in result.get('explanation', []):
            print(f"   - {line}")
        
        print(f"\n🎨 Best Colors (Top 5):")
        for i, color in enumerate(result.get('best_colors', [])[:5], 1):
            print(f"   {i}. {color['name']:20s} {color['hex']}")
        
        # Quality details
        quality = result.get('quality_check', {})
        if quality.get('warnings'):
            print(f"\n⚠️  Photo Quality Warnings:")
            for warning in quality['warnings']:
                print(f"   - {warning}")
    
    else:
        print(f"\n❌ ANALYSIS FAILED")
        print(f"Error: {result.get('error')}")
        
        if result.get('recommendations'):
            print(f"\n📋 Recommendations:")
            for rec in result['recommendations'][:5]:
                print(f"   {rec}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    
    # Show user guidelines
    print("\n📚 USER GUIDELINES FOR BEST RESULTS:")
    print("="*80)
    guidelines = pipeline.get_user_guidelines()
    
    print("\n📸 Photo Guidelines:")
    for tip in guidelines['photo_guidelines'][:5]:
        print(f"   {tip}")
    
    print("\n💡 Lighting Tips:")
    for tip in guidelines['lighting_tips']:
        print(f"   • {tip}")

if __name__ == "__main__":
    test_production_pipeline()
