from typing import Dict, List, Any

# --- FEATURE INTERPRETATION LAYER ---

def interpret_eye_color(eye_l: float) -> Dict[str, Any]:
    if eye_l < 25:
        return {"name": "Deep Brown", "hex": "#3B2A1A", "depth": "Deep"}
    elif eye_l < 45:
        return {"name": "Medium Brown", "hex": "#6B4A2E", "depth": "Medium"}
    elif eye_l < 65:
        return {"name": "Light Brown / Hazel", "hex": "#A67C52", "depth": "Medium-Light"}
    else:
        return {"name": "Light Blue / Green", "hex": "#87CEEB", "depth": "Light"}

def interpret_hair_color(hair_l: float) -> Dict[str, Any]:
    if hair_l < 20:
        return {"name": "Soft Black", "hex": "#1C1B1A", "depth": "Deep"}
    elif hair_l < 40:
        return {"name": "Dark Brown", "hex": "#3A2A1A", "depth": "Deep-Medium"}
    elif hair_l < 60:
        return {"name": "Medium Brown", "hex": "#6B4A2E", "depth": "Medium"}
    elif hair_l < 80:
        return {"name": "Light Brown / Dark Blonde", "hex": "#C4A484", "depth": "Light-Medium"}
    else:
        return {"name": "Blonde", "hex": "#F0E68C", "depth": "Light"}

def interpret_skin_tone(skin_l: float) -> Dict[str, Any]:
    if skin_l < 45:
        return {"name": "Deep", "hex": "#5C3E2E", "depth": "Deep"} # Approx Hex
    elif skin_l < 60:
        return {"name": "Medium-Deep", "hex": "#8D5524", "depth": "Medium-Deep"}
    elif skin_l < 75:
        return {"name": "Medium", "hex": "#C68642", "depth": "Medium"}
    elif skin_l < 88:
        return {"name": "Medium-Light", "hex": "#E0AC69", "depth": "Medium-Light"}
    else:
        return {"name": "Light", "hex": "#F1C27D", "depth": "Light"}

# --- EXPLANATION GENERATOR ---

def generate_explanation(season: str, subtype: str, signal: Dict, undertone: str) -> List[str]:
    reasons = []
    
    # 1. Undertone Reason
    if undertone == "Warm":
        reasons.append(f"Primary characteristic is Warm Undertone (B={int(signal['skin_b'])})")
    else:
        reasons.append(f"Primary characteristic is Cool Undertone (B={int(signal['skin_b'])})")
        
    # 2. Depth/Lightness Reason
    if signal['skin_l'] < 50:
        reasons.append("Skin depth is Deep, anchoring the season")
    elif signal['skin_l'] > 80:
        reasons.append("Skin depth is Light, requiring delicate colors")
    else:
        reasons.append("Skin depth is Medium, allowing versatility")
        
    # 3. Contrast Reason
    if signal['contrast'] > 50:
        reasons.append("High contrast between hair and skin creates intensity")
    elif signal['contrast'] < 25:
        reasons.append("Low contrast creates a soft, blended appearance")
        
    # 4. Chroma Reason for specific subtypes
    if "Bright" in subtype:
        reasons.append("High clarity (Chroma) demands vibrant colors")
    elif "Soft" in subtype:
        reasons.append("Muted chroma requires dusty, desaturated colors")
        
    # 5. Archetype Match
    reasons.append(f"Profile closest to {subtype} archetype physics")
    
    return reasons

