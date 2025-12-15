import math

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    rmean = (c1[0] + c2[0]) / 2
    r = c1[0] - c2[0]
    g = c1[1] - c2[1]
    b = c1[2] - c2[2]
    return math.sqrt((((512+rmean)*r*r)>>8) + 4*g*g + (((767-rmean)*b*b)>>8))

def determine_match_level(item_hex: str, best_colors: list, neutral_colors: list, worst_colors: list) -> str:
    if not item_hex:
        return "neutral"
        
    try:
        item_rgb = hex_to_rgb(item_hex)
    except:
        return "neutral"
    
    threshold = 100 # Adjust as needed
    
    # Check best
    for color in best_colors:
        if color_distance(item_rgb, hex_to_rgb(color)) < threshold:
            return "best"
            
    # Check worst
    for color in worst_colors:
        if color_distance(item_rgb, hex_to_rgb(color)) < threshold:
            return "worst"
            
    # Check neutral
    for color in neutral_colors:
        if color_distance(item_rgb, hex_to_rgb(color)) < threshold:
            return "neutral"
            
    return "neutral"
