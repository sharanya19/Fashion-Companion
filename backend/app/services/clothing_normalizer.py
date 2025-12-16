import re

CATEGORY_MAP = {
    # Tops
    "top": "Top",
    "shirt": "Top",
    "crop": "Top",
    "blouse": "Top",
    "tank": "Top",

    # Bottoms
    "skirt": "Bottom",
    "jean": "Bottom",
    "pant": "Bottom",
    "trouser": "Bottom",
    "short": "Bottom",
    "legging": "Bottom",
    "cargo": "Bottom",

    # One-Piece
    "dress": "OnePiece",
    "gown": "OnePiece",
    "jumpsuit": "OnePiece",
    "romper": "OnePiece",

    # Outerwear
    "jacket": "Outerwear",
    "coat": "Outerwear",
    "hoodie": "Outerwear",
    "sweater": "Outerwear",
    "blazer": "Outerwear",

    # Footwear
    "shoe": "Footwear",
    "sneaker": "Footwear",
    "boot": "Footwear",
    "heel": "Footwear",

    # Accessories
    "bag": "Accessory",
    "belt": "Accessory",
    "scarf": "Accessory",
    "jewelry": "Accessory",
    "purse": "Accessory",
}


def normalize_category(*raw_inputs: str | None) -> str:
    """
    Accepts multiple signals (category, subcategory, type, item_type).
    Strongest keyword wins.
    """
    combined = " ".join([x.lower() for x in raw_inputs if x])

    for key, value in CATEGORY_MAP.items():
        if key in combined:
            return value

    return "Uncategorized"


def normalize_text(text: str | None) -> str | None:
    return text.strip().title() if text else None
