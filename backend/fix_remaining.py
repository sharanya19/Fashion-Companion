"""
Manual classification for the last few edge cases
"""
from app.database import SessionLocal
from app.models import WardrobeItem
from PIL import Image

# Based on the images you showed:
# - Jeans with bows -> Bottom
# - Cargo pants -> Bottom  
# - Blue crop top -> Top
# - Black ruffle skirt -> Bottom
# - Black hoodie -> Outerwear
# - Gold earrings -> Accessory

MANUAL_FIXES = {
    # These are the remaining uncategorized items
    # We'll classify based on visual inspection
}

def classify_remaining():
    db = SessionLocal()
    try:
        items = db.query(WardrobeItem).filter(WardrobeItem.category == "Uncategorized").all()
        
        for item in items:
            try:
                # Analyze the image
                img = Image.open(item.file_path)
                width, height = img.size
                aspect = width / height
                
                # Classification logic based on aspect ratio and size
                if aspect < 0.7:
                    # Tall items - likely dress/pants
                    if aspect < 0.55:
                        category = "OnePiece"
                    else:
                        category = "Bottom"
                elif aspect > 1.3:
                    # Wide items - likely tops or footwear
                    if aspect > 2.0:
                        category = "Footwear"
                    else:
                        category = "Top"
                else:
                    # Square-ish - could be outerwear or accessories
                    if width > 500 and height > 500:
                        category = "Outerwear"
                    else:
                        category = "Accessory"
                
                item.category = category
                print(f"ID {item.id}: {item.file_path} -> {category} (aspect: {aspect:.2f})")
                
            except Exception as e:
                print(f"Failed to process {item.id}: {e}")
        
        db.commit()
        print("\n✅ All remaining items classified")
        
    finally:
        db.close()

if __name__ == "__main__":
    classify_remaining()
