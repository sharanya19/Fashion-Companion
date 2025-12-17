"""
Script to fix existing Uncategorized items in the database using fallback logic
"""
import sys
import os
from app.services.fallback_classifier import fallback_classify
from app.services.clothing_normalizer import normalize_category
from app.database import SessionLocal
from app.models import WardrobeItem
import json

ALLOWED_CATEGORIES = {"Top", "Bottom", "OnePiece", "Outerwear", "Footwear", "Accessory"}

def fix_uncategorized_items():
    db = SessionLocal()
    try:
        items = db.query(WardrobeItem).filter(WardrobeItem.category == "Uncategorized").all()
        
        print(f"Found {len(items)} uncategorized items")
        
        for item in items:
            print(f"\nProcessing ID {item.id}: {item.file_path}")
            
            # Try to get category from AI metadata if exists
            new_category = None
            if item.ai_metadata:
                try:
                    ai_data = json.loads(item.ai_metadata)
                    if isinstance(ai_data, dict) and "ai" in ai_data:
                        ai_data = ai_data["ai"]
                    
                    # Try normalize from AI data
                    normalized = normalize_category(
                        ai_data.get("category"),
                        ai_data.get("subcategory"),
                        ai_data.get("type")
                    )
                    if normalized in ALLOWED_CATEGORIES:
                        new_category = normalized
                        print(f"  ✓ Fixed from AI metadata: {new_category}")
                except:
                    pass
            
            # If still nothing, use fallback classifier
            if not new_category:
                if os.path.exists(item.file_path):
                    new_category = fallback_classify(item.file_path, item.file_path)
                    if new_category and new_category in ALLOWED_CATEGORIES:
                        print(f"  ✓ Fixed from fallback: {new_category}")
            
            # Update if we found something
            if new_category:
                item.category = new_category
                print(f"  → Updated to: {new_category}")
            else:
                print(f"  ✗ Could not classify")
        
        # Commit all changes
        db.commit()
        print(f"\n✅ Database updated successfully")
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_uncategorized_items()
