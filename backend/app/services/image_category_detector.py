# backend/app/services/image_category_detector.py

def detect_category_from_image(file_path: str) -> str | None:
    """
    VERY RESTRICTED image-based detector.
    Only allowed to detect Footwear.
    Never Top / Bottom / OnePiece.
    """

    filename = file_path.lower()

    # Only footwear is visually reliable
    footwear_keywords = [
        "shoe", "shoes", "heel", "heels",
        "sneaker", "sneakers", "boot", "boots",
        "sandal", "sandals", "loafer", "loafers",
        "flat", "flats"
    ]

    for kw in footwear_keywords:
        if kw in filename:
            return "Footwear"

    # ❌ DO NOT GUESS OTHER CATEGORIES
    return None
