import re

# Standardized Categories
CATEGORY_MAP = {
    # Tops
    "top": "Top", "shirt": "Top", "t-shirt": "Top", "blouse": "Top", 
    "sweater": "Top", "hoodie": "Top", "jacket": "Outerwear", "coat": "Outerwear",
    "blazer": "Outerwear", "cardigan": "Top", "vest": "Top", "tank": "Top",
    "bodysuit": "Top", "sweatshirt": "Top",
    
    # Bottoms
    "bottom": "Bottom", "jeans": "Bottom", "pants": "Bottom", "trousers": "Bottom",
    "skirt": "Bottom", "shorts": "Bottom", "leggings": "Bottom", "joggers": "Bottom",
    
    # One-Piece
    "one-piece": "OnePiece", "dress": "OnePiece", "jumpsuit": "OnePiece", 
    "romper": "OnePiece", "gown": "OnePiece",
    
    # Footwear
    "footwear": "Footwear", "shoe": "Footwear", "shoes": "Footwear", 
    "sneakers": "Footwear", "boots": "Footwear", "sandals": "Footwear",
    
    # Accessories
    "accessory": "Accessory", "bag": "Accessory", "hat": "Accessory", 
    "scarf": "Accessory", "jewelry": "Accessory"
}

# Repair Rules: (Trigger, Corrected Category)
REPAIR_RULES = {
    "jeans": "Bottom",
    "skirt": "Bottom",
    "dress": "OnePiece",
    "sneaker": "Footwear",
    "boot": "Footwear",
    "jacket": "Outerwear",
    "coat": "Outerwear"
}

def normalize_category(raw_category: str, raw_subcategory: str = None) -> str:
    """
    Normalizes category using mapping and repair heuristics.
    """
    if not raw_category:
        return "Uncategorized"
    
    clean_cat = raw_category.lower().strip()
    clean_sub = raw_subcategory.lower().strip() if raw_subcategory else ""
    
    # 1. Map Category directly
    normalized = "Uncategorized"
    for key, value in CATEGORY_MAP.items():
        if key in clean_cat:
            normalized = value
            break
            
    # 2. Repair based on Subcategory (Stronger signal)
    # If category is generic "Top" or "Uncategorized" but subcategory is specific
    for key, correct_cat in REPAIR_RULES.items():
        if key in clean_sub:
            # Override if previously weak or wrong (e.g. AI said "Top" for "Jeans")
            normalized = correct_cat
            break
            
    return normalized

def normalize_text(text: str) -> str:
    if not text:
        return "Unknown"
    return text.title().strip()
