# backend/app/services/wardrobe_logic.py

import math
from typing import List, Union, Dict, Any


# -------------------------------
# Color utilities
# -------------------------------

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color (#RRGGBB) to RGB tuple.
    """
    if not hex_color:
        raise ValueError("Empty hex color")

    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")

    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """
    Perceptual color distance (weighted Euclidean).
    This is intentionally used instead of simple RGB distance.
    """
    rmean = (c1[0] + c2[0]) / 2
    r = c1[0] - c2[0]
    g = c1[1] - c2[1]
    b = c1[2] - c2[2]

    return math.sqrt(
        (((512 + rmean) * r * r) >> 8) +
        4 * g * g +
        (((767 - rmean) * b * b) >> 8)
    )


# -------------------------------
# Palette helpers
# -------------------------------

def extract_hex(color: Union[str, Dict[str, Any]]) -> str | None:
    """
    Extract hex color from palette entry.
    Supports:
      - "#AABBCC"
      - {"hex": "#AABBCC"}
      - {"color": "#AABBCC"}
    """
    if isinstance(color, str):
        return color.strip()

    if isinstance(color, dict):
        return (
            color.get("hex")
            or color.get("color")
            or None
        )

    return None


def normalize_hex(hex_color: str | None) -> str | None:
    """
    Validate and normalize hex color.
    """
    if not hex_color:
        return None

    hex_color = hex_color.strip()
    if not hex_color.startswith("#"):
        hex_color = f"#{hex_color}"

    if len(hex_color) != 7:
        return None

    try:
        hex_to_rgb(hex_color)
        return hex_color
    except Exception:
        return None


# -------------------------------
# Match logic
# -------------------------------

def determine_match_level(
    item_hex: str | None,
    best_colors: List[Union[str, Dict[str, Any]]],
    neutral_colors: List[Union[str, Dict[str, Any]]],
    worst_colors: List[Union[str, Dict[str, Any]]]
) -> str:
    """
    Determines match level of a wardrobe item color against
    user's seasonal palette.

    Returns:
      - "best"
      - "neutral"
      - "worst"
    """

    # Safety: no fabric color → neutral
    item_hex = normalize_hex(item_hex)
    if not item_hex:
        return "neutral"

    try:
        item_rgb = hex_to_rgb(item_hex)
    except Exception:
        return "neutral"

    # Relaxed threshold (as agreed)
    THRESHOLD = 120

    # 1️⃣ BEST colors (highest priority)
    for color in best_colors or []:
        hex_candidate = normalize_hex(extract_hex(color))
        if not hex_candidate:
            continue

        try:
            if color_distance(item_rgb, hex_to_rgb(hex_candidate)) < THRESHOLD:
                return "best"
        except Exception:
            continue

    # 2️⃣ WORST colors (second priority)
    for color in worst_colors or []:
        hex_candidate = normalize_hex(extract_hex(color))
        if not hex_candidate:
            continue

        try:
            if color_distance(item_rgb, hex_to_rgb(hex_candidate)) < THRESHOLD:
                return "worst"
        except Exception:
            continue

    # 3️⃣ NEUTRAL colors (fallback)
    for color in neutral_colors or []:
        hex_candidate = normalize_hex(extract_hex(color))
        if not hex_candidate:
            continue

        try:
            if color_distance(item_rgb, hex_to_rgb(hex_candidate)) < THRESHOLD:
                return "neutral"
        except Exception:
            continue

    # Default safe fallback
    return "neutral"
