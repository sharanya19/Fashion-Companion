import hashlib
import random
import math
from typing import Dict, List, Any, Tuple
from .cv_engine import FeatureExtractor
from .interpretation_layer import interpret_eye_color, interpret_hair_color, interpret_skin_tone, generate_explanation
from .palette_db import get_static_palette
import os

# Initialize CV Engine globally to save load time
extractor = FeatureExtractor()

# --- ARCHETYPE DATABASE (Reference Only) ---
ARCHETYPES = [
    # WINTER
    {"season": "Winter", "subtype": "True Winter", "skin_l": 60, "skin_b": -2, "hair_l": 15, "eye_l": 25, "chroma": 55, "contrast": 60},
    {"season": "Winter", "subtype": "Deep Winter", "skin_l": 40, "skin_b": 2, "hair_l": 10, "eye_l": 20, "chroma": 50, "contrast": 50},
    {"season": "Winter", "subtype": "Bright Winter", "skin_l": 75, "skin_b": -4, "hair_l": 15, "eye_l": 55, "chroma": 65, "contrast": 70},
    # SUMMER
    {"season": "Summer", "subtype": "True Summer", "skin_l": 70, "skin_b": -5, "hair_l": 60, "eye_l": 50, "chroma": 30, "contrast": 25},
    {"season": "Summer", "subtype": "Light Summer", "skin_l": 85, "skin_b": -3, "hair_l": 75, "eye_l": 65, "chroma": 25, "contrast": 15},
    {"season": "Summer", "subtype": "Soft Summer", "skin_l": 65, "skin_b": 2, "hair_l": 55, "eye_l": 45, "chroma": 20, "contrast": 15},
    # AUTUMN
    {"season": "Autumn", "subtype": "True Autumn", "skin_l": 60, "skin_b": 18, "hair_l": 30, "eye_l": 35, "chroma": 30, "contrast": 35},
    {"season": "Autumn", "subtype": "Deep Autumn", "skin_l": 45, "skin_b": 15, "hair_l": 20, "eye_l": 25, "chroma": 40, "contrast": 45},
    {"season": "Autumn", "subtype": "Soft Autumn", "skin_l": 68, "skin_b": 10, "hair_l": 50, "eye_l": 45, "chroma": 20, "contrast": 20},
    # SPRING
    {"season": "Spring", "subtype": "True Spring", "skin_l": 75, "skin_b": 20, "hair_l": 65, "eye_l": 60, "chroma": 55, "contrast": 35},
    {"season": "Spring", "subtype": "Light Spring", "skin_l": 88, "skin_b": 12, "hair_l": 80, "eye_l": 70, "chroma": 40, "contrast": 15},
    {"season": "Spring", "subtype": "Bright Spring", "skin_l": 70, "skin_b": 15, "hair_l": 25, "eye_l": 65, "chroma": 65, "contrast": 60}
]

# Standard Palette Generator (Unchanged)
def generate_palette(season: str, subtype: str):
    # Shortened for file size
    palettes = {
        "Spring": {
            "metals": ["Gold", "Rose Gold", "Bright Bronze"],
            "stones": ["Turquoise", "Coral"],
            "base_colors": [{"hex": "#FF7F50", "name": "Coral", "category": "Power"}, {"hex": "#FFD700", "name": "Golden Yellow", "category": "Power"}, {"hex": "#98FB98", "name": "Pale Green", "category": "Everyday"}],
            "worst": [{"hex": "#000000", "name": "Black", "category": "Avoid"}]
        },
        "Summer": {
            "metals": ["Silver", "White Gold"],
            "stones": ["Pearl", "Rose Quartz"],
            "base_colors": [{"hex": "#E6E6FA", "name": "Lavender", "category": "Everyday"}, {"hex": "#ADD8E6", "name": "Powder Blue", "category": "Everyday"}],
            "worst": [{"hex": "#FFA500", "name": "Orange", "category": "Avoid"}]
        },
        "Autumn": {
            "metals": ["Gold", "Copper"],
             "stones": ["Amber", "Jasper"],
             "base_colors": [{"hex": "#8B4513", "name": "Rust", "category": "Power"}, {"hex": "#556B2F", "name": "Olive", "category": "Everyday"}],
             "worst": [{"hex": "#FF69B4", "name": "Hot Pink", "category": "Avoid"}]
        },
        "Winter": {
             "metals": ["Silver", "Platinum"],
             "stones": ["Diamond", "Ruby"],
             "base_colors": [{"hex": "#000000", "name": "Black", "category": "Power"}, {"hex": "#FFFFFF", "name": "Pure White", "category": "Neutral"}],
             "worst": [{"hex": "#D2B48C", "name": "Tan", "category": "Avoid"}]
        }
    }
    base = palettes.get(season, palettes["Spring"])
    data = {"best": base["base_colors"], "neutral": [], "worst": base["worst"], "complementary": [], "metals": base["metals"], "stones": base["stones"]}
    
    # Enriching palette slightly
    if season == "Spring":
        data["best"].extend([{"hex": "#40E0D0", "name": "Turquoise", "category": "Statement"}, {"hex": "#F4A460", "name": "Sandy Brown", "category": "Neutral"}])
        data["neutral"] = [{"hex": "#FFF8DC", "name": "Cornsilk", "category": "Neutral"}]
    if season == "Summer":
        data["best"].extend([{"hex": "#DB7093", "name": "Pale Violet Red", "category": "Power"}, {"hex": "#778899", "name": "Slate Gray", "category": "Neutral"}])
    if season == "Autumn":
        data["best"].extend([{"hex": "#DAA520", "name": "Goldenrod", "category": "Statement"}, {"hex": "#D2691E", "name": "Chocolate", "category": "Neutral"}])
    if season == "Winter":
        data["best"].extend([{"hex": "#FF0000", "name": "True Red", "category": "Power"}, {"hex": "#0000FF", "name": "Royal Blue", "category": "Statement"}])

    return data

def calculate_distance(signal: Dict, archetype: Dict) -> float:
    # Weighted Euclidean distance
    diff = 0
    diff += abs(signal["skin_l"] - archetype["skin_l"]) * 1.0 # Lightness
    diff += abs(signal["skin_b"] - archetype["skin_b"]) * 2.5 # Undertone (Critical)
    diff += abs(signal["chroma"] - archetype["chroma"]) * 1.5 # Chroma (High priority)
    return diff

def analyze_user_style(email: str = None, file_path: str = None, manual_signal: Dict = None):
    # Palette v6.4 - ABSOLUTE SUB-SEASON GATING
    
    # 1. SIGNAL ACQUISITION (REAL CV or SIMULATION)
    
    # Defaults (Simulation Range)
    # We will compute these if CV not present
    
    # A. REAL COMPUTER VISION PATH
    if file_path and os.path.exists(file_path):
        try:
            print(f"👁️ Start CV Analysis for: {file_path}")
            features = extractor.process_image(file_path)
            
            skin_l = features["skin_l"]
            skin_b = features["skin_b"]
            chroma = features["chroma"]
            hair_l = features["hair_l"]
            eye_l = features["eye_l"]
            contrast = abs(skin_l - hair_l)
            
            print(f"   -> Extracted: L={int(skin_l)} B={int(skin_b)} C={int(chroma)}")
            
        except Exception as e:
            print(f"⚠️ CV Failed: {e}. Falling back to hash simulation.")
            # Fallthrough to seeding logic below for safety
            seed_key = file_path
    
    # B. MANUAL OVERRIDE (Testing)
    elif manual_signal:
        # Fallback values if not provided in manual dict
        skin_l = manual_signal.get("skin_l", 70)
        skin_b = manual_signal.get("skin_b", 10)
        chroma = manual_signal.get("chroma", 40)
        hair_l = manual_signal.get("hair_l", 30)
        eye_l = manual_signal.get("eye_l", 30)
        contrast = abs(skin_l - hair_l)

    # C. SIMULATION FALLBACK (If no real signal)
    # Checks: No file OR File exists but CV failed (features undefined) matches logic
    if (not file_path or 'features' not in locals()) and not manual_signal:
        seed_key = email if email else (file_path if file_path else "default")
        seed_val = int(hashlib.md5(seed_key.encode()).hexdigest(), 16)
        random.seed(seed_val)
        cohort = seed_val % 12
        
        # COHORT BIASING (Standardized to ensure reach)
        if cohort < 3: # WINTER
            skin_b_min, skin_b_max = -8, 0
            skin_l_min, skin_l_max = 40, 70
            chroma_min, chroma_max = 45, 75
        elif cohort < 6: # SUMMER
            skin_b_min, skin_b_max = -6, 2
            skin_l_min, skin_l_max = 60, 90
            chroma_min, chroma_max = 15, 40
        elif cohort < 9: # AUTUMN
            skin_b_min, skin_b_max = 10, 25
            skin_l_min, skin_l_max = 40, 65
            chroma_min, chroma_max = 20, 50
        else: # SPRING
            skin_b_min, skin_b_max = 10, 25
            skin_l_min, skin_l_max = 60, 90
            chroma_min, chroma_max = 45, 70

        # SIGNAL GEN
        skin_l = random.randint(skin_l_min, skin_l_max)
        skin_b = random.randint(skin_b_min, skin_b_max)
        chroma = random.randint(chroma_min, chroma_max)
        hair_l = random.randint(5, 90)
        eye_l = random.randint(15, 80)
        
        contrast = abs(skin_l - hair_l)
        
        # Force High Contrast for Winters in cohort
        if cohort < 3 and contrast < 40:
            hair_l = max(5, skin_l - 50)
            contrast = abs(skin_l - hair_l)

    # --- FIX 3: CORRECT CONTRAST FORMULA ---
    # Weighted average: Skin vs Hair (50%), Skin vs Eyes (30%), Hair vs Eyes (20%)
    contrast = (
        abs(skin_l - hair_l) * 0.5 +
        abs(skin_l - eye_l) * 0.3 +
        abs(hair_l - eye_l) * 0.2
    )

    # --- FIX 1: NEUTRALIZE SKIN UNDERTONE ---
    if skin_b > 12:
        undertone = "Warm"
    elif skin_b < -8:
        undertone = "Cool"
    else:
        undertone = "Neutral"

    # --- FIX 6: VISUAL DEBUGGING ---
    print({
        "skin_l": skin_l,
        "skin_b": skin_b,
        "hair_l": hair_l,
        "eye_l": eye_l,
        "chroma": chroma,
        "contrast": contrast,
        "undertone": undertone
    })

    signal = {"skin_l": skin_l, "skin_b": skin_b, "chroma": chroma, "contrast": contrast, "hair_l": hair_l, "eye_l": eye_l}
    
    # 2. THE HARD SUB-SEASON FILTER (CRITICAL FIX)
    filtered_archetypes = []
    
    for arch in ARCHETYPES:
        subtype = arch["subtype"]
        season = arch["season"]
        valid = True
        
        # --- GLOBAL HARD RULES ---
        if season == "Winter" and chroma < 38: valid = False # Relaxed from 45 - Fix 4
        if season == "Summer" and contrast > 40: valid = False # Strict Low Contrast for Summer
        if season == "Spring" and contrast < 15: valid = False # Spring needs some pop
        
        # --- SUB-SEASON HARD GATES ---
        
        # 🌸 SPRING
        if subtype == "True Spring":
            if contrast > 45: valid = False # Too high contrast -> Bright Spring
            if skin_l >= 70: valid = False # Too Light -> Light Spring (relaxed from 75)
            if chroma < 45: valid = False # Too Muted
            if hair_l > 50: valid = False # Hair too light -> Light Spring
            
        if subtype == "Bright Spring":
            if chroma < 52: valid = False # Relaxed from 60 - Fix 4
            if contrast < 40: valid = False # Must be high contrast
            
        if subtype == "Light Spring":
            if skin_l < 75: valid = False # Must be Light
            if contrast > 45: valid = False # Relaxed from 40 for real-world photos
            if chroma < 20: valid = False # Minimum brightness (lower than True Spring)
            
        # 🌊 SUMMER
        if subtype == "Light Summer":
            if skin_l < 70: valid = False
            if chroma > 40: valid = False
            
        if subtype == "True Summer":
            if contrast > 30: valid = False # CRITICAL FIX: True Summer is Soft/Cool
            if chroma > 40: valid = False # Not Bright
            if skin_b > 8: valid = False # Strictly Cool (Relaxed from 0 to 8 for sRGB bias)

        if subtype == "Soft Summer":
            if chroma > 35: valid = False # Strictly Muted
            
        # 🍂 AUTUMN
        if subtype == "Soft Autumn":
            if chroma > 45: valid = False # Strictly Muted
            if contrast > 40: valid = False
            
        if subtype == "Deep Autumn":
            if skin_l > 60: valid = False # Must be Deep (relaxed from 55)
            if contrast < 30: valid = False # Must have some depth contrast
            
        if subtype == "True Autumn":
             if skin_b < 15: valid = False # Must be Warm
             if skin_l > 70: valid = False # Cannot be too light (that's Light Spring territory)
             if skin_l < 50: valid = False # Cannot be too deep (that's Deep Autumn)
             
        # ❄️ WINTER
        if subtype == "True Winter":
            if skin_b > 8: valid = False # Strictly Cool (Relaxed from 0 to 8 for sRGB bias)
            if contrast < 45: valid = False
            if chroma < 35: valid = False # Must have some saturation (prevents Bright Winter confusion)
            
        if subtype == "Bright Winter":
            if chroma < 55: valid = False # Must be very bright/saturated
            if contrast < 50: valid = False # Must be very high contrast
            
        if subtype == "Deep Winter":
            if skin_l > 55: valid = False
            
        # --- END RULES ---
        
        if valid:
            filtered_archetypes.append(arch)
            
    # 3. SCORING
    scored_archetypes = []
    for arch in filtered_archetypes:
        dist = calculate_distance(signal, arch)
        
        # Bias Logic (Soft Priority)
        if arch["subtype"] == "Light Spring" and skin_l > 80: dist -= 10
        if arch["subtype"] == "Bright Spring" and chroma > 65 and contrast > 50: dist -= 15
        if arch["subtype"] == "Light Summer" and skin_l > 80 and chroma < 35: dist -= 10
        if arch["subtype"] == "Deep Autumn" and skin_l < 50: dist -= 10
        
        scored_archetypes.append((dist, arch))
        
    scored_archetypes.sort(key=lambda x: x[0])
    
    # 4. FINAL SELECTION
    if not scored_archetypes:
        # Fallback: Find closest ARCHETYPE irrespective of strict gates 
        # (prevents crash, marks low confidence)
        raw_scored = [(calculate_distance(signal, a), a) for a in ARCHETYPES]
        raw_scored.sort(key=lambda x: x[0])
        selected = raw_scored[0][1]
        confidence = 0.3 # Low confidence
    else:
        selected = scored_archetypes[0][1]
        confidence = 0.95
        
    # --- PHASE 3: SUBTYPE REINFORCEMENT (Deep Autumn Protection) ---
    # If system picked Soft Autumn but physics scream Deep Autumn, force Deep Autumn
    if selected["subtype"] == "Soft Autumn":
        if skin_l < 55 and hair_l < 30:
            print(f"🛡️ Reinforcement Triggered: Soft Autumn -> Deep Autumn (L={skin_l}, H={hair_l})")
            selected = next((a for a in ARCHETYPES if a["subtype"] == "Deep Autumn"), selected)
            confidence = 0.88 # Slightly lower as it was a correction

    # --- FIX 5: REINFORCEMENT FOR OTHER SEASONS ---
    
    # Bright Spring -> Bright Winter protection (Blue spike + High Contrast)
    if selected["subtype"] == "Bright Spring":
        if skin_b < 0 and contrast > 50:
             print(f"🛡️ Reinforcement Triggered: Bright Spring -> Bright Winter (B={skin_b}, C={contrast})")
             selected = next((a for a in ARCHETYPES if a["subtype"] == "Bright Winter"), selected)
             confidence = 0.88

    # Deep Autumn -> True Winter protection (Cooler undertone + High Chroma)
    if selected["subtype"] == "Deep Autumn":
        if skin_b < -2 and chroma > 50: 
             print(f"🛡️ Reinforcement Triggered: Deep Autumn -> True Winter (B={skin_b}, C={chroma})")
             selected = next((a for a in ARCHETYPES if a["subtype"] == "True Winter"), selected)
             confidence = 0.88

    # Soft Autumn -> True Winter rescue (for overexposed/washed-out photos)
    # If contrast is VERY low (<20) and undertone is neutral, photo is likely overexposed
    # and person might be Winter with dark hair that's reading as light
    if selected["subtype"] == "Soft Autumn":
        if contrast < 20 and abs(skin_b) < 12 and skin_l > 75:
             print(f"🛡️ Reinforcement Triggered: Soft Autumn -> True Winter (Overexposed photo rescue: C={contrast:.1f}, L={skin_l:.1f})")
             selected = next((a for a in ARCHETYPES if a["subtype"] == "True Winter"), selected)
             confidence = 0.75  # Lower confidence due to photo quality issues

    # Light Spring -> True Autumn rescue (for red/auburn hair)
    # Fair skin + warm undertone + red/auburn hair (L=30-40) = True Autumn, not Light Spring
    # BUT: Only if skin is not too light (True Spring can also have auburn hair)
    if selected["subtype"] == "Light Spring":
        if skin_b > 15 and hair_l >= 30 and hair_l <= 45 and skin_l < 70:
             print(f"🛡️ Reinforcement Triggered: Light Spring -> True Autumn (Red/Auburn hair: H={hair_l:.1f}, B={skin_b:.1f}, L={skin_l:.1f})")
             selected = next((a for a in ARCHETYPES if a["subtype"] == "True Autumn"), selected)
             confidence = 0.88

    # --- PHASE 1 & 4: INTERPRETATION & EXPLANATION ---
    
    # 1. Feature Interpretation
    eye_interpretaion = interpret_eye_color(eye_l)
    hair_interpretation = interpret_hair_color(hair_l)
    skin_interpretation = interpret_skin_tone(skin_l)
    
    # 2. Decision Explanation
    explanation = generate_explanation(selected["season"], selected["subtype"], signal, undertone)
    
    # 3. Static Palette Retrieval (Phase 2)
    palette_data = get_static_palette(selected["season"], selected["subtype"])
    
    face_shapes = ["Oval", "Square", "Round", "Heart", "Diamond"]
    
    return {
        "season": selected["season"],
        "season_subtype": selected["subtype"],
        
        # UI-Ready Feature Objects
        "skin_tone": skin_interpretation,   
        "eye_color": eye_interpretaion,
        "hair_color": hair_interpretation,
        
        # Debug / Raw Data (Hidden in UI usually)
        "debug_info": {
            "skin_l": skin_l,
            "skin_b": skin_b,
            "chroma": chroma,
            "contrast": contrast,
            "hair_l": hair_l,
            "eye_l": eye_l
        },
        
        "undertone": undertone,
        "confidence_score": confidence,
        "explanation": explanation, # NEW: Why we chose this
        
        # Rich Palette Data
        "best_colors": palette_data["core"],
        "neutral_colors": palette_data["neutral"],
        "accent_colors": palette_data["accent"], # NEW category
        "luxury_colors": palette_data["luxury"], # NEW category
        "worst_colors": palette_data["worst"],
        "jewelry_metals": [{"name": "Gold", "hex": "#FFD700"}], # Simplify for now or fetch from DB
        "jewelry_stones": [], # Placeholder
        
        "face_shape": random.choice(face_shapes)
    }
