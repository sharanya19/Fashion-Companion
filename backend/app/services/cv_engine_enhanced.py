"""
Enhanced CV Feature Extractor with Lighting Normalization
Production-ready version with robustness improvements
"""
import cv2
import numpy as np
import mediapipe as mp
import math
from sklearn.cluster import KMeans
from collections import Counter
from typing import Dict, Tuple

class EnhancedFeatureExtractor:
    """Production-grade feature extractor with lighting correction"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
    
    def normalize_lighting(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize lighting using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        Helps with overexposed/underexposed photos
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_normalized = clahe.apply(l)
        
        # Merge back
        lab_normalized = cv2.merge([l_normalized, a, b])
        normalized = cv2.cvtColor(lab_normalized, cv2.COLOR_LAB2RGB)
        
        return normalized
    
    def get_dominant_color(self, image: np.ndarray, k: int = 3) -> Tuple[float, float, float]:
        """Extract dominant color using K-Means clustering, returning LAB."""
        pixels = image.reshape(-1, 3)
        if len(pixels) == 0:
            return (0, 0, 0)
        
        # Ensure pixels are in valid range
        pixels = np.clip(pixels, 0, 255).astype(np.uint8)
            
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        counts = Counter(kmeans.labels_)
        center_colors = kmeans.cluster_centers_
        
        # Get most frequent color
        dominant_idx = counts.most_common(1)[0][0]
        dominant_rgb = center_colors[dominant_idx]
        
        # Ensure RGB is in valid uint8 range
        dominant_rgb = np.clip(dominant_rgb, 0, 255).astype(np.uint8)
        
        # Convert RGB to LAB for analysis
        rgb_pixel = np.array([[dominant_rgb]], dtype=np.uint8)
        lab_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2LAB)[0][0]
        
        # Convert to standard CIE LAB
        l_std = float(lab_pixel[0]) * 100.0 / 255.0
        a_std = float(lab_pixel[1]) - 128.0
        b_std = float(lab_pixel[2]) - 128.0
        
        return (l_std, a_std, b_std)
    
    def process_image(self, image_path: str, apply_lighting_correction: bool = True) -> Dict:
        """
        Process image to extract skin, hair, and eye LAB features
        
        Args:
            image_path: Path to image file
            apply_lighting_correction: Whether to apply CLAHE normalization
        
        Returns:
            Dict with extracted features
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image")
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply lighting correction if enabled
        if apply_lighting_correction:
            image_rgb_normalized = self.normalize_lighting(image_rgb)
            print("[INFO] Applied lighting normalization")
        else:
            image_rgb_normalized = image_rgb
        
        # Process with MediaPipe
        results = self.face_mesh.process(image_rgb_normalized)
        
        if not results.multi_face_landmarks:
            raise ValueError("No face detected")
            
        landmarks = results.multi_face_landmarks[0]
        h, w, _ = image_rgb_normalized.shape
        
        # 1. SKIN EXTRACTION (Cheek area)
        skin_mask = np.zeros((h, w), dtype=np.uint8)
        cheek_pts = np.array([
            [landmarks.landmark[116].x * w, landmarks.landmark[116].y * h],
            [landmarks.landmark[117].x * w, landmarks.landmark[117].y * h],
            [landmarks.landmark[118].x * w, landmarks.landmark[118].y * h],
            [landmarks.landmark[100].x * w, landmarks.landmark[100].y * h]
        ], np.int32)
        cv2.fillPoly(skin_mask, [cheek_pts], 255)
        skin_pixels = cv2.bitwise_and(image_rgb_normalized, image_rgb_normalized, mask=skin_mask)
        valid_skin = skin_pixels[np.where((skin_pixels != [0,0,0]).all(axis=2))]
        
        print(f"[DEBUG] Skin pixels extracted: {len(valid_skin)}")
        
        if len(valid_skin) == 0: 
            valid_skin = image_rgb_normalized[h//2-20:h//2+20, w//2-20:w//2+20]
            print(f"[DEBUG] Using center fallback")
        
        skin_l, skin_a, skin_b = self.get_dominant_color(valid_skin)
        print(f"[DEBUG] Skin LAB: L={skin_l:.1f}, A={skin_a:.1f}, B={skin_b:.1f}")
        
        # 2. EYE EXTRACTION (Iris)
        eye_center = landmarks.landmark[468] 
        ex, ey = int(eye_center.x * w), int(eye_center.y * h)
        eye_crop = image_rgb_normalized[max(0, ey-5):min(h, ey+5), max(0, ex-5):min(w, ex+5)]
        eye_l, eye_a, eye_b = self.get_dominant_color(eye_crop, k=2)
        
        # 3. HAIR EXTRACTION (Multi-point with intelligent selection)
        left_point = landmarks.landmark[234]
        lx, ly = int(left_point.x * w), int(left_point.y * h)
        left_hair = image_rgb_normalized[max(0, ly-40):min(h, ly+40), max(0, lx-60):min(w, lx-20)]
        
        right_point = landmarks.landmark[454]
        rx, ry = int(right_point.x * w), int(right_point.y * h)
        right_hair = image_rgb_normalized[max(0, ry-40):min(h, ry+40), min(w, rx+20):min(w, rx+60)]
        
        # Also sample from top of head for additional data point
        top_point = landmarks.landmark[10]
        tx, ty = int(top_point.x * w), int(top_point.y * h)
        top_hair = image_rgb_normalized[max(0, ty-80):max(0, ty-20), max(0, tx-40):min(w, tx+40)]
        
        hair_samples = []
        if left_hair.size > 0 and np.mean(left_hair) > 5:
            hair_samples.append(self.get_dominant_color(left_hair, k=3))
        if right_hair.size > 0 and np.mean(right_hair) > 5:
            hair_samples.append(self.get_dominant_color(right_hair, k=3))
        if top_hair.size > 0 and np.mean(top_hair) > 5:
            hair_samples.append(self.get_dominant_color(top_hair, k=3))
        
        # Intelligent hair sample selection
        if hair_samples:
            # Use median L value to avoid outliers
            l_values = [s[0] for s in hair_samples]
            median_l = np.median(l_values)
            
            # Find sample closest to median
            closest_idx = np.argmin([abs(l - median_l) for l in l_values])
            hair_l, hair_a, hair_b = hair_samples[closest_idx]
            
            print(f"[DEBUG] Hair samples: {len(hair_samples)}, Median L={median_l:.1f}, Selected L={hair_l:.1f}")
        else:
            hair_l, hair_a, hair_b = (20, 0, 0)
            print(f"[DEBUG] Hair sampling failed, using fallback")
        
        # 4. CHROMA CALCULATION
        chroma = math.sqrt(skin_a**2 + skin_b**2)
        
        # 5. LIGHTING QUALITY ASSESSMENT
        brightness = np.mean(image_rgb_normalized)
        contrast_std = np.std(cv2.cvtColor(image_rgb_normalized, cv2.COLOR_RGB2GRAY))
        
        return {
            "skin_l": skin_l,
            "skin_b": skin_b,
            "skin_a": skin_a,
            "hair_l": hair_l,
            "eye_l": eye_l,
            "chroma": chroma,
            "photo_quality": {
                "brightness": float(brightness),
                "contrast": float(contrast_std),
                "lighting_corrected": apply_lighting_correction
            }
        }
