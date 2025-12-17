"""
Fallback classifier for when Gemini AI is unavailable or returns null.
Uses simple visual and keyword-based heuristics.
"""
from PIL import Image
import os


def extract_keywords_from_filename(filename: str) -> list[str]:
    """Extract potential keywords from filename"""
    filename = filename.lower()
    # Remove uuid and extensions
    import re
    filename = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '', filename)
    filename = re.sub(r'\.(jpg|jpeg|png|webp)$', '', filename)
    # Extract words
    words = re.findall(r'[a-z]+', filename)
    return [w for w in words if len(w) > 2]


def classify_by_keywords(keywords: list[str]) -> str | None:
    """Classify based on keywords in filename"""
    keywords_str = ' '.join(keywords)
    
    # Accessories
    if any(k in keywords_str for k in ['bag', 'purse', 'belt', 'jewelry', 'earring', 'necklace', 'hat', 'cap', 'scarf']):
        return 'Accessory'
    
    # Footwear
    if any(k in keywords_str for k in ['shoe', 'sneaker', 'boot', 'heel', 'sandal', 'loafer']):
        return 'Footwear'
    
    # Outerwear
    if any(k in keywords_str for k in ['jacket', 'coat', 'hoodie', 'sweater', 'blazer', 'cardigan']):
        return 'Outerwear'
    
    # OnePiece
    if any(k in keywords_str for k in ['dress', 'gown', 'jumpsuit', 'romper']):
        return 'OnePiece'
    
    # Bottoms
    if any(k in keywords_str for k in ['pant', 'jean', 'trouser', 'skirt', 'short', 'legging', 'cargo']):
        return 'Bottom'
    
    # Tops
    if any(k in keywords_str for k in ['shirt', 'top', 'blouse', 'tee', 'tank', 'crop', 'camisole']):
        return 'Top'
    
    return None


def classify_by_aspect_ratio(image_path: str) -> str | None:
    """
    VERY conservative shape-based classification.
    Only use for obvious cases.
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        aspect = width / height if height > 0 else 1.0
        
        # Very wide objects are often shoes laid side-by-side
        if aspect > 1.8:
            return 'Footwear'
        
        # Very tall might be a dress
        if aspect < 0.5:
            return 'OnePiece'
            
    except:
        pass
    
    return None


def analyze_image_properties(image_path: str) -> dict:
    """Analyze basic image properties for classification"""
    try:
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        aspect = width / height if height > 0 else 1.0
        
        # Resize for faster analysis
        img_small = img.resize((100, 100))
        pixels = list(img_small.getdata())
        
        # Calculate average brightness
        brightness = sum(sum(p) for p in pixels) / (len(pixels) * 3)
        
        # Detect if background is very uniform (product photo style)
        # Check corners for similar colors
        corners = [
            img_small.getpixel((5, 5)),
            img_small.getpixel((95, 5)),
            img_small.getpixel((5, 95)),
            img_small.getpixel((95, 95))
        ]
        corner_variance = sum(abs(c1[i] - c2[i]) for c1 in corners for c2 in corners for i in range(3)) / 12
        is_clean_bg = corner_variance < 30
        
        return {
            'aspect': aspect,
            'brightness': brightness,
            'is_clean_bg': is_clean_bg,
            'width': width,
            'height': height
        }
    except:
        return {'aspect': 1.0, 'brightness': 128, 'is_clean_bg': False, 'width': 0, 'height': 0}


def smart_classify(image_path: str) -> str | None:
    """
    Intelligent classification using multiple signals
    """
    props = analyze_image_properties(image_path)
    aspect = props['aspect']
    
    # Footwear detection (shoes are often wider than tall)
    if 1.3 < aspect < 2.5 and props['is_clean_bg']:
        return 'Footwear'
    
    # Accessories (bags, jewelry, belts are often square-ish on clean backgrounds)
    if 0.7 < aspect < 1.4 and props['is_clean_bg']:
        # Small items on clean bg = likely accessories
        if props['width'] < 800 and props['height'] < 800:
            return 'Accessory'
    
    # OnePiece (dresses are tall and narrow)
    if aspect < 0.55:
        return 'OnePiece'
    
    # Outerwear (hoodies, jackets are often slightly wide)
    if 1.1 < aspect < 1.5:
        return 'Outerwear'
    
    # Bottoms (pants/jeans are tall but not as tall as dresses)
    if 0.55 <= aspect < 0.85:
        return 'Bottom'
    
    # Tops (wide and short)
    if 1.5 <= aspect < 2.0:
        return 'Top'
    
    return None


def fallback_classify(image_path: str, filename: str = None) -> str | None:
    """
    Last-resort classifier when AI fails.
    Returns a category or None.
    """
    if not filename:
        filename = os.path.basename(image_path)
    
    # Try keywords first (most reliable)
    keywords = extract_keywords_from_filename(filename)
    result = classify_by_keywords(keywords)
    if result:
        return result
    
    # Try intelligent image analysis
    if os.path.exists(image_path):
        result = smart_classify(image_path)
        if result:
            return result
    
    return None
