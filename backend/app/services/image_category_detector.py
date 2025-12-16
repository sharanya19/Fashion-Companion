"""
Image-based category detection for clothing items
Uses image analysis to determine if item is Top, Bottom, OnePiece, etc.
"""
from PIL import Image
import numpy as np

def detect_category_from_image(image_path: str) -> str:
    """
    Analyzes image to detect clothing category based on visual features.
    Returns: "Top", "Bottom", "OnePiece", "Outerwear", "Footwear", "Accessory", or None
    """
    try:
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        aspect_ratio = width / height if height > 0 else 1.0
        
        # Convert to numpy array for analysis
        img_array = np.array(img)
        
        # Analyze image characteristics
        # 1. Aspect ratio analysis
        # Tops are usually wider than tall (horizontal)
        # Bottoms (pants) are usually taller than wide (vertical)
        # Dresses are usually vertical but have different color distribution
        
        if aspect_ratio > 1.3:
            # Very wide - likely a top or accessory laid flat
            return "Top"
        elif aspect_ratio < 0.7:
            # Very tall - likely pants or a dress
            # Check for pants characteristics (two leg-like structures)
            return detect_pants_vs_dress(img_array, width, height)
        elif 0.7 <= aspect_ratio <= 1.3:
            # Square-ish - could be anything, check other features
            return detect_from_features(img_array, width, height)
        else:
            return None
            
    except Exception as e:
        print(f"⚠️ Image category detection failed: {e}")
        return None

def detect_pants_vs_dress(img_array: np.ndarray, width: int, height: int) -> str:
    """Detect if vertical item is pants or dress"""
    # Pants typically have two distinct leg areas (left and right)
    # Dresses are more uniform in the middle
    
    # Check left and right halves for color similarity
    left_half = img_array[:, :width//2]
    right_half = img_array[:, width//2:]
    
    # Calculate average colors
    left_avg = np.mean(left_half, axis=(0, 1))
    right_avg = np.mean(right_half, axis=(0, 1))
    
    # If halves are very similar, likely a dress (uniform)
    # If different, might be pants (two legs)
    color_diff = np.abs(left_avg - right_avg).mean()
    
    if color_diff > 30:  # Significant difference suggests pants
        return "Bottom"
    else:
        # Check if it's long enough to be a dress
        if height > width * 1.5:
            return "OnePiece"
        return "Bottom"

def detect_from_features(img_array: np.ndarray, width: int, height: int) -> str:
    """Detect category from image features"""
    # Check for common patterns
    # Tops: Often have sleeves, neckline area
    # Bottoms: Often have waistband, leg openings
    
    # Analyze vertical distribution
    top_third = img_array[:height//3]
    middle_third = img_array[height//3:2*height//3]
    bottom_third = img_array[2*height//3:]
    
    # Calculate color variance (more variance = more features)
    top_var = np.var(top_third)
    middle_var = np.var(middle_third)
    bottom_var = np.var(bottom_third)
    
    # Tops often have more variation in top third (neckline, sleeves)
    # Bottoms have more variation in middle/bottom (waist, legs)
    if top_var > middle_var and top_var > bottom_var:
        return "Top"
    elif bottom_var > top_var:
        return "Bottom"
    else:
        # Could be dress or one-piece
        return "OnePiece"

