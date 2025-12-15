import cv2
import numpy as np
import mediapipe as mp
import math
from sklearn.cluster import KMeans
from collections import Counter
from typing import Dict, Tuple

class FeatureExtractor:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

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
        # Create a 1x1 image with the dominant color
        rgb_pixel = np.array([[dominant_rgb]], dtype=np.uint8)
        lab_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2LAB)[0][0]
        
        # OpenCV LAB ranges: L [0, 255], A [0, 255], B [0, 255]
        # Convert to standard CIE LAB: L [0, 100], A [-128, 127], B [-128, 127]
        l_std = float(lab_pixel[0]) * 100.0 / 255.0
        a_std = float(lab_pixel[1]) - 128.0
        b_std = float(lab_pixel[2]) - 128.0
        
        return (l_std, a_std, b_std)

    def process_image(self, image_path: str) -> Dict:
        """Process image to extract skin, hair, and eye LAB features."""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image")
            
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        
        if not results.multi_face_landmarks:
            raise ValueError("No face detected")
            
        landmarks = results.multi_face_landmarks[0]
        h, w, _ = image.shape
        
        # Define Regions of Interest (ROI) using Mesh Landmarks
        
        # 1. Skin (Cheek area) - avoiding highlights/shadows if possible
        # Check landmarks: 116, 117, 118 (Left cheek) | 345, 346, 347 (Right cheek)
        skin_mask = np.zeros((h, w), dtype=np.uint8)
        cheek_pts = np.array([
            [landmarks.landmark[116].x * w, landmarks.landmark[116].y * h],
            [landmarks.landmark[117].x * w, landmarks.landmark[117].y * h],
            [landmarks.landmark[118].x * w, landmarks.landmark[118].y * h],
            [landmarks.landmark[100].x * w, landmarks.landmark[100].y * h]
        ], np.int32)
        cv2.fillPoly(skin_mask, [cheek_pts], 255)
        skin_pixels = cv2.bitwise_and(image_rgb, image_rgb, mask=skin_mask)
        # Extract only non-black pixels
        valid_skin = skin_pixels[np.where((skin_pixels != [0,0,0]).all(axis=2))]
        
        print(f"[DEBUG] Skin pixels extracted: {len(valid_skin)}")
        
        if len(valid_skin) == 0: 
            valid_skin = image_rgb[h//2-20:h//2+20, w//2-20:w//2+20] # Center fallback
            print(f"[DEBUG] Using center fallback, pixels: {valid_skin.shape}")
        
        skin_l, skin_a, skin_b = self.get_dominant_color(valid_skin)
        print(f"[DEBUG] Skin LAB: L={skin_l:.1f}, A={skin_a:.1f}, B={skin_b:.1f}")
        
        # 2. Eyes (Iris) - Landmarks 468 (Left Iris), 473 (Right Iris)
        # Using refined landmarks
        eye_center = landmarks.landmark[468] 
        ex, ey = int(eye_center.x * w), int(eye_center.y * h)
        # Crop small radius around iris center
        eye_crop = image_rgb[max(0, ey-5):min(h, ey+5), max(0, ex-5):min(w, ex+5)]
        eye_l, eye_a, eye_b = self.get_dominant_color(eye_crop, k=2) # k=2 to separate pupil/iris
        
        # 3. Hair (Multi-point sampling to avoid shadows)
        # Sample from both sides and take the lighter value (avoids shadow bias)
        
        # Left side (Landmark 234)
        left_point = landmarks.landmark[234]
        lx, ly = int(left_point.x * w), int(left_point.y * h)
        left_hair = image_rgb[max(0, ly-40):min(h, ly+40), max(0, lx-60):min(w, lx-20)]
        
        # Right side (Landmark 454 - mirror of 234)
        right_point = landmarks.landmark[454]
        rx, ry = int(right_point.x * w), int(right_point.y * h)
        right_hair = image_rgb[max(0, ry-40):min(h, ry+40), min(w, rx+20):min(w, rx+60)]
        
        # Get both samples
        hair_samples = []
        if left_hair.size > 0 and np.mean(left_hair) > 5:
            hair_samples.append(self.get_dominant_color(left_hair, k=3))
        if right_hair.size > 0 and np.mean(right_hair) > 5:
            hair_samples.append(self.get_dominant_color(right_hair, k=3))
        
        # Use intelligent sample selection:
        # If skin is light (L>70), person likely has light hair -> use lightest sample
        # If skin is medium-dark (L<70), person likely has dark hair -> use darkest sample
        if hair_samples:
            if skin_l > 70:
                # Light skin -> likely blonde/light hair
                hair_l, hair_a, hair_b = max(hair_samples, key=lambda x: x[0])
                print(f"[DEBUG] Hair LAB (lightest, light skin): L={hair_l:.1f}")
            else:
                # Medium/dark skin -> likely dark hair
                hair_l, hair_a, hair_b = min(hair_samples, key=lambda x: x[0])
                print(f"[DEBUG] Hair LAB (darkest, medium/dark skin): L={hair_l:.1f}")
        else:
            # Fallback
            hair_l, hair_a, hair_b = (20, 0, 0)
            print(f"[DEBUG] Hair sampling failed, using fallback")
        
        # 4. Chroma Calculation
        chroma = math.sqrt(skin_a**2 + skin_b**2)
        
        return {
            "skin_l": skin_l,
            "skin_b": skin_b,
            "skin_a": skin_a,
            "hair_l": hair_l,
            "eye_l": eye_l,
            "chroma": chroma
        }


