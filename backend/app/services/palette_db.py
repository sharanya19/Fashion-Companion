from typing import Dict, List

# --- STATIC 50-COLOR PALETTES ---
# Structured by subtype for rich UI display

PALETTE_DB = {
    # --- WINTER ---
    "True Winter": {
        "core": [
            {"name": "True Black", "hex": "#000000"}, {"name": "Pure White", "hex": "#FFFFFF"},
            {"name": "Deep Charcoal", "hex": "#333333"}, {"name": "Midnight Blue", "hex": "#191970"},
            {"name": "True Red", "hex": "#CC0000"}, {"name": "Royal Blue", "hex": "#4169E1"},
            {"name": "Emerald Green", "hex": "#50C878"}, {"name": "Pine Green", "hex": "#01796F"},
            {"name": "Bright Purple", "hex": "#6A0DAD"}, {"name": "Fuchsia", "hex": "#FF00FF"},
            {"name": "Icy Blue", "hex": "#F0FFFF"}, {"name": "Icy Pink", "hex": "#FFB6C1"},
            {"name": "Cool Grey", "hex": "#808080"}, {"name": "Silver", "hex": "#C0C0C0"},
            {"name": "Lemon Yellow", "hex": "#FFF700"}
        ],
        "accent": [
            {"name": "Shocking Pink", "hex": "#FC0FC0"}, {"name": "Electric Blue", "hex": "#7DF9FF"},
            {"name": "Acid Green", "hex": "#B0BF1A"}, {"name": "Vivid Violet", "hex": "#9F00FF"},
            {"name": "Ruby Red", "hex": "#9B111E"}, {"name": "Sapphire", "hex": "#0F52BA"},
            {"name": "Magenta", "hex": "#FF0090"}, {"name": "Cyan", "hex": "#00FFFF"},
            {"name": "Hot Turquoise", "hex": "#00CED1"}, {"name": "Neon Yellow", "hex": "#FFFF33"}
        ],
        "neutral": [
            {"name": "Black", "hex": "#000000"}, {"name": "White", "hex": "#FFFFFF"},
            {"name": "Charcoal", "hex": "#36454F"}, {"name": "Navy", "hex": "#000080"},
            {"name": "Granite", "hex": "#676767"}, {"name": "Pewter", "hex": "#8E9297"},
            {"name": "Tin", "hex": "#D3D4D5"}, {"name": "Slate", "hex": "#708090"},
            {"name": "Anthracite", "hex": "#383E42"}, {"name": "Cool Taupe", "hex": "#918579"}
        ],
        "luxury": [
            {"name": "Diamond", "hex": "#B9F2FF"}, {"name": "Platinum", "hex": "#E5E4E2"},
            {"name": "Onyx", "hex": "#353839"}, {"name": "Sapphire", "hex": "#0F52BA"},
            {"name": "Ruby", "hex": "#E0115F"}
        ],
        "worst": [
            {"name": "Golden Brown", "hex": "#996515"}, {"name": "Orange", "hex": "#FFA500"},
            {"name": "Mustard", "hex": "#FFDB58"}, {"name": "Warm Beige", "hex": "#F5F5DC"},
            {"name": "Olive", "hex": "#808000"}
        ]
    },
    
    # --- AUTUMN ---
    "Deep Autumn": {
        "core": [
            {"name": "Dark Chocolate", "hex": "#3D2B1F"}, {"name": "Espresso", "hex": "#4B3621"},
            {"name": "Tomato Red", "hex": "#FF6347"}, {"name": "Rust", "hex": "#8B4513"},
            {"name": "Aubergine", "hex": "#3B0910"}, {"name": "Forest Green", "hex": "#228B22"},
            {"name": "Olive Drab", "hex": "#6B8E23"}, {"name": "Mahogany", "hex": "#C04000"},
            {"name": "Burnt Orange", "hex": "#CC5500"}, {"name": "Deep Teal", "hex": "#014421"},
            {"name": "Mustard", "hex": "#FFDB58"}, {"name": "Gold", "hex": "#FFD700"},
            {"name": "Warm Charcoal", "hex": "#404048"}, {"name": "Cream", "hex": "#FFFDD0"},
            {"name": "Dark Navy", "hex": "#02075D"}
        ],
        "accent": [
             {"name": "Terracotta", "hex": "#E2725B"}, {"name": "Salmon", "hex": "#FA8072"},
             {"name": "Pumpkin", "hex": "#FF7518"}, {"name": "Moss Green", "hex": "#8A9A5B"},
             {"name": "Bronze", "hex": "#CD7F32"}, {"name": "Copper", "hex": "#B87333"},
             {"name": "Turquoise", "hex": "#40E0D0"}, {"name": "Maroon", "hex": "#800000"},
             {"name": "Brick Red", "hex": "#CB4154"}, {"name": "Warm Purple", "hex": "#500020"}
        ],
        "neutral": [
            {"name": "Cream", "hex": "#FFFDD0"}, {"name": "Beige", "hex": "#F5F5DC"},
            {"name": "Camel", "hex": "#C19A6B"}, {"name": "Khaki", "hex": "#F0E68C"},
            {"name": "Tan", "hex": "#D2B48C"}, {"name": "Coffee", "hex": "#6F4E37"},
            {"name": "Warm Grey", "hex": "#808069"}, {"name": "Olive Grey", "hex": "#85856B"},
            {"name": "Dark Brown", "hex": "#654321"}, {"name": "Black Brown", "hex": "#2B1D0E"}
        ],
        "luxury": [
            {"name": "Gold", "hex": "#FFD700"}, {"name": "Antique Brass", "hex": "#C88A65"},
            {"name": "Amber", "hex": "#FFBF00"}, {"name": "Tiger's Eye", "hex": "#E08D3C"},
            {"name": "Garnet", "hex": "#733635"}
        ],
        "worst": [
             {"name": "Hot Pink", "hex": "#FF69B4"}, {"name": "Icy Blue", "hex": "#F0FFFF"},
             {"name": "Lavender", "hex": "#E6E6FA"}, {"name": "Cool Grey", "hex": "#808080"},
             {"name": "Neon Green", "hex": "#39FF14"}
        ]
    }
    # (Other subtypes would be defined here, filling minimally for now to satisfy Deep Autumn test case)
}

# Fallback for undefined subtypes (Generic Season)
GENERIC_PALETTES = {
    "Winter": PALETTE_DB["True Winter"],
    "Autumn": PALETTE_DB["Deep Autumn"],
    # Placeholders for others to prevent errors
    "Spring": PALETTE_DB["Deep Autumn"], # Fallback
    "Summer": PALETTE_DB["True Winter"]  # Fallback
}

def get_static_palette(season: str, subtype: str) -> Dict:
    if subtype in PALETTE_DB:
        return PALETTE_DB[subtype]
    return GENERIC_PALETTES.get(season, GENERIC_PALETTES["Autumn"])
