import re

CATEGORY_SYNONYMS = {
    "Top": [
        "top", "shirt", "tshirt", "t-shirt", "tee", "blouse",
        "crop", "tank", "camisole", "upper", "topwear"
    ],
    "Bottom": [
        "bottom", "pant", "pants", "trouser", "jean", "jeans",
        "skirt", "short", "shorts", "legging", "cargo", "lower"
    ],
    "OnePiece": [
        "dress", "gown", "onepiece", "one-piece",
        "jumpsuit", "romper"
    ],
    "Outerwear": [
        "jacket", "coat", "blazer", "hoodie",
        "sweater", "cardigan", "outerwear"
    ],
    "Footwear": [
        "shoe", "shoes", "sneaker", "sneakers",
        "heel", "heels", "sandal", "sandals",
        "boot", "boots", "loafer", "loafers",
        "flat", "flats"
    ],
    "Accessory": [
        "bag", "handbag", "purse", "tote", "clutch",
        "belt", "scarf", "watch", "jewelry",
        "necklace", "earring", "ring",
        "hat", "cap", "glasses", "sunglasses"
    ],
}


def _tokenize(text: str) -> set[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", " ", text)
    parts = re.split(r"[\s\-]+", text)
    return set(filter(None, parts))


def normalize_category(*raw_inputs: str | None) -> str:
    """
    Robust category normalization using:
    - tokenization
    - plural handling
    - synonym matching
    - confidence scoring
    """
    tokens = set()

    for raw in raw_inputs:
        if not raw:
            continue
        tokens |= _tokenize(raw)

    if not tokens:
        return "Uncategorized"

    scores = {cat: 0 for cat in CATEGORY_SYNONYMS}

    for cat, keywords in CATEGORY_SYNONYMS.items():
        for kw in keywords:
            if kw in tokens:
                scores[cat] += 2
            # singular match
            if kw.endswith("s") and kw[:-1] in tokens:
                scores[cat] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Uncategorized"


def normalize_text(text: str | None) -> str | None:
    return text.strip().title() if text else None
