"""
Production-Ready Color Season Analysis Pipeline
Integrates photo quality checking, enhanced CV extraction, and robust classification
"""
import os
from typing import Dict, Optional
from .photo_quality import PhotoQualityChecker
from .cv_engine_enhanced import EnhancedFeatureExtractor
from .style_analysis import analyze_user_style as legacy_analyze

class ProductionAnalysisPipeline:
    """
    Production-grade analysis pipeline with quality controls
    """
    
    def __init__(self):
        self.quality_checker = PhotoQualityChecker()
        self.enhanced_extractor = EnhancedFeatureExtractor()
        self.min_quality_score = 40  # Minimum acceptable quality score
    
    def analyze_with_quality_check(
        self, 
        file_path: str,
        force_analysis: bool = False
    ) -> Dict:
        """
        Perform complete analysis with quality pre-check
        
        Args:
            file_path: Path to uploaded photo
            force_analysis: If True, analyze even if quality is poor (with warnings)
        
        Returns:
            Complete analysis result with quality metadata
        """
        
        # Step 1: Photo Quality Check
        print("="*60)
        print("STEP 1: Photo Quality Assessment")
        print("="*60)
        
        quality_result = self.quality_checker.check_photo_quality(file_path)
        
        print(f"Quality Score: {quality_result['quality_score']:.1f}/100")
        
        if quality_result['issues']:
            print("\n❌ ISSUES FOUND:")
            for issue in quality_result['issues']:
                print(f"  - {issue}")
        
        if quality_result['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in quality_result['warnings']:
                print(f"  - {warning}")
        
        # Decide whether to proceed
        should_proceed = (
            quality_result['is_valid'] or 
            force_analysis or 
            quality_result['quality_score'] >= self.min_quality_score
        )
        
        if not should_proceed:
            return {
                "success": False,
                "error": "Photo quality too low for accurate analysis",
                "quality_check": quality_result,
                "recommendations": self.quality_checker.get_photo_recommendations()
            }
        
        # Step 2: Enhanced Feature Extraction
        print("\n" + "="*60)
        print("STEP 2: Feature Extraction (with lighting correction)")
        print("="*60)
        
        try:
            # Use enhanced extractor with lighting correction
            features = self.enhanced_extractor.process_image(
                file_path, 
                apply_lighting_correction=True
            )
            
            print(f"✅ Extraction successful")
            print(f"   Skin L={features['skin_l']:.1f}, B={features['skin_b']:.1f}")
            print(f"   Hair L={features['hair_l']:.1f}")
            print(f"   Chroma={features['chroma']:.1f}")
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return {
                "success": False,
                "error": f"Feature extraction failed: {str(e)}",
                "quality_check": quality_result
            }
        
        # Step 3: Season Classification
        print("\n" + "="*60)
        print("STEP 3: Season Classification")
        print("="*60)
        
        try:
            # Use the existing style_analysis with extracted features
            analysis_result = legacy_analyze(
                file_path=file_path,
                manual_signal=None  # Let it use CV extraction
            )
            
            print(f"✅ Classification: {analysis_result['season']} - {analysis_result['season_subtype']}")
            print(f"   Confidence: {analysis_result['confidence_score']*100:.1f}%")
            
            # Adjust confidence based on photo quality
            quality_penalty = max(0, (70 - quality_result['quality_score']) / 100)
            adjusted_confidence = analysis_result['confidence_score'] * (1 - quality_penalty)
            
            # Add quality metadata to result
            analysis_result['quality_check'] = quality_result
            analysis_result['original_confidence'] = analysis_result['confidence_score']
            analysis_result['confidence_score'] = adjusted_confidence
            analysis_result['photo_quality_score'] = quality_result['quality_score']
            analysis_result['success'] = True
            
            # Add quality warnings to explanation
            if quality_result['warnings']:
                if 'explanation' not in analysis_result:
                    analysis_result['explanation'] = []
                analysis_result['explanation'].insert(0, 
                    f"⚠️ Photo quality: {quality_result['quality_score']:.0f}/100 - Results may vary with better lighting"
                )
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Classification failed: {e}")
            return {
                "success": False,
                "error": f"Classification failed: {str(e)}",
                "quality_check": quality_result
            }
    
    def get_user_guidelines(self) -> Dict:
        """Return comprehensive user guidelines"""
        return {
            "photo_guidelines": self.quality_checker.get_photo_recommendations(),
            "what_to_wear": [
                "White or light gray top (shows skin tone clearly)",
                "Hair down and natural (no hats/headbands)",
                "Minimal or no makeup",
                "Remove glasses if possible"
            ],
            "lighting_tips": [
                "Best: Outdoors in open shade (cloudy day ideal)",
                "Good: Near large window, indirect sunlight",
                "Avoid: Direct sun, overhead lights, flash"
            ],
            "camera_tips": [
                "Hold camera at eye level",
                "Face camera directly",
                "Fill 30-50% of frame with face",
                "Ensure photo is sharp and in focus"
            ]
        }
