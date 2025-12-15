"""
Photo Quality Checker for Color Season Analysis
Validates photo quality before analysis to ensure accurate results
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple

class PhotoQualityChecker:
    """Validates photo quality for color season analysis"""
    
    def __init__(self):
        self.quality_thresholds = {
            'min_brightness': 40,
            'max_brightness': 220,
            'min_contrast': 30,
            'max_blur': 100,
            'min_face_size': 0.15,  # 15% of image
        }
    
    def check_photo_quality(self, image_path: str) -> Dict:
        """
        Comprehensive photo quality check
        Returns: {
            'is_valid': bool,
            'quality_score': float (0-100),
            'issues': List[str],
            'warnings': List[str],
            'metrics': Dict
        }
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'is_valid': False,
                    'quality_score': 0,
                    'issues': ['Failed to load image'],
                    'warnings': [],
                    'metrics': {}
                }
            
            issues = []
            warnings = []
            metrics = {}
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # 1. BRIGHTNESS CHECK
            avg_brightness = np.mean(gray)
            metrics['brightness'] = float(avg_brightness)
            
            if avg_brightness < self.quality_thresholds['min_brightness']:
                issues.append(f"Photo too dark (brightness: {avg_brightness:.1f}/255)")
            elif avg_brightness > self.quality_thresholds['max_brightness']:
                issues.append(f"Photo overexposed (brightness: {avg_brightness:.1f}/255)")
            elif avg_brightness < 60:
                warnings.append("Photo is slightly dark - use better lighting")
            elif avg_brightness > 200:
                warnings.append("Photo is slightly bright - avoid direct flash")
            
            # 2. CONTRAST CHECK
            contrast = gray.std()
            metrics['contrast'] = float(contrast)
            
            if contrast < self.quality_thresholds['min_contrast']:
                issues.append(f"Low contrast (contrast: {contrast:.1f}) - photo appears washed out")
            elif contrast < 40:
                warnings.append("Moderate contrast - natural lighting recommended")
            
            # 3. BLUR DETECTION (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            metrics['sharpness'] = float(laplacian_var)
            
            if laplacian_var < self.quality_thresholds['max_blur']:
                issues.append(f"Photo too blurry (sharpness: {laplacian_var:.1f})")
            elif laplacian_var < 150:
                warnings.append("Photo slightly blurry - hold camera steady")
            
            # 4. COLOR SATURATION CHECK
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            saturation = hsv[:, :, 1].mean()
            metrics['saturation'] = float(saturation)
            
            if saturation < 30:
                warnings.append("Low color saturation - avoid filters/heavy editing")
            
            # 5. LIGHTING UNIFORMITY
            # Check if lighting is too uneven (harsh shadows)
            brightness_std = gray.std()
            metrics['lighting_uniformity'] = float(brightness_std)
            
            if brightness_std > 70:
                warnings.append("Uneven lighting detected - use diffused/natural light")
            
            # 6. FACE DETECTION (basic check)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                issues.append("No face detected - ensure face is clearly visible")
            elif len(faces) > 1:
                warnings.append("Multiple faces detected - use photo with single person")
            else:
                # Check face size
                (x, y, fw, fh) = faces[0]
                face_area = (fw * fh) / (w * h)
                metrics['face_coverage'] = float(face_area)
                
                if face_area < self.quality_thresholds['min_face_size']:
                    warnings.append("Face too small - move closer to camera")
                elif face_area > 0.7:
                    warnings.append("Face too close - step back slightly")
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(metrics, issues, warnings)
            
            return {
                'is_valid': len(issues) == 0,
                'quality_score': quality_score,
                'issues': issues,
                'warnings': warnings,
                'metrics': metrics
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'quality_score': 0,
                'issues': [f'Error analyzing photo: {str(e)}'],
                'warnings': [],
                'metrics': {}
            }
    
    def _calculate_quality_score(self, metrics: Dict, issues: List, warnings: List) -> float:
        """Calculate 0-100 quality score"""
        score = 100.0
        
        # Deduct for issues
        score -= len(issues) * 25
        
        # Deduct for warnings
        score -= len(warnings) * 10
        
        # Bonus for good metrics
        if metrics.get('brightness', 0) >= 100 and metrics.get('brightness', 0) <= 180:
            score += 5
        if metrics.get('contrast', 0) >= 50:
            score += 5
        if metrics.get('sharpness', 0) >= 200:
            score += 5
        
        return max(0, min(100, score))
    
    def get_photo_recommendations(self) -> List[str]:
        """Return list of photo guidelines for users"""
        return [
            "📸 Use natural daylight (near window, outdoors in shade)",
            "🚫 Avoid direct flash or harsh overhead lights",
            "👤 Face should fill 20-50% of frame",
            "🎨 No makeup or minimal natural makeup",
            "👕 Wear neutral colors (white, gray, beige)",
            "🖼️ Use plain, neutral background",
            "📱 Hold camera at eye level",
            "😊 Neutral expression, face camera directly",
            "🔍 Ensure photo is sharp and in focus",
            "☀️ Avoid backlighting (light should be in front)"
        ]
